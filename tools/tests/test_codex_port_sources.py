"""Tests for Codex port source materialization and tree hashing.

A source spec names where a skill lives (RCS track, claude.ai desktop
cache, portable zip, or plain directory). ``materialize`` copies it into
a staging directory and ``tree_sha256`` fingerprints a tree so drift can
be detected later without timestamps.
"""
import os
import time
from pathlib import Path

import pytest

from tools.codex_port.manifest import Manifest, SourceSpec
from tools.codex_port.sources import SourceError, materialize, resolve_cache_dir, tree_sha256
from tools.tests.codex_port_fixtures import MINIMAL_SKILL_MD, make_skill_dir, make_zip


def manifest_for(tmp_path: Path) -> Manifest:
    return Manifest(
        codex_home=tmp_path / "codex",
        cache_roots={"Claude": tmp_path / "cache-claude", "Claude-Zenity": tmp_path / "cache-zenity"},
        rcs_root=tmp_path / "rcs",
        skills={},
        data_dirs=(),
    )


def test_rcs_source_copies_track_dir(tmp_path):
    make_skill_dir(tmp_path / "rcs" / "workflow", "a-skill", MINIMAL_SKILL_MD, {"scripts/x.py": "print(1)\n"})
    out = materialize(SourceSpec("rcs", track="workflow"), "a-skill", manifest_for(tmp_path), tmp_path / "stage")
    assert out == tmp_path / "stage" / "a-skill"
    assert (out / "SKILL.md").read_text() == MINIMAL_SKILL_MD
    assert (out / "scripts" / "x.py").read_text() == "print(1)\n"


def test_rcs_source_missing_raises(tmp_path):
    with pytest.raises(SourceError, match=r"a-skill"):
        materialize(SourceSpec("rcs", track="workflow"), "a-skill", manifest_for(tmp_path), tmp_path / "stage")


def test_dir_source_follows_symlinked_root(tmp_path):
    real = make_skill_dir(tmp_path / "real", "a-skill", MINIMAL_SKILL_MD, {"references/r.md": "ref\n"})
    link = tmp_path / "links" / "a-skill"
    link.parent.mkdir()
    link.symlink_to(real, target_is_directory=True)
    out = materialize(SourceSpec("dir", path=link), "a-skill", manifest_for(tmp_path), tmp_path / "stage")
    assert (out / "references" / "r.md").read_text() == "ref\n"
    assert not (out / "SKILL.md").is_symlink()
    assert tree_sha256(out) == tree_sha256(real)


def test_dir_basename_must_equal_name(tmp_path):
    other = make_skill_dir(tmp_path / "src", "other", MINIMAL_SKILL_MD)
    with pytest.raises(SourceError, match=r"other.*a-skill|a-skill.*other"):
        materialize(SourceSpec("dir", path=other), "a-skill", manifest_for(tmp_path), tmp_path / "stage")


def test_claude_ai_picks_newest_match(tmp_path):
    root = tmp_path / "cache-claude"
    old = make_skill_dir(root / "u1" / "s1" / "skills", "a-skill", "old\n")
    new = make_skill_dir(root / "u2" / "s2" / "skills", "a-skill", "new\n")
    stale = time.time() - 1000
    os.utime(old / "SKILL.md", (stale, stale))
    assert resolve_cache_dir(root, "a-skill") == new
    out = materialize(SourceSpec("claude_ai", profile="Claude"), "a-skill", manifest_for(tmp_path), tmp_path / "stage")
    assert (out / "SKILL.md").read_text() == "new\n"


def test_claude_ai_missing_raises(tmp_path):
    (tmp_path / "cache-claude").mkdir()
    with pytest.raises(SourceError, match=r"a-skill.*Claude|Claude.*a-skill"):
        materialize(SourceSpec("claude_ai", profile="Claude"), "a-skill", manifest_for(tmp_path), tmp_path / "stage")


def test_zip_extracts_single_top_folder(tmp_path):
    archive = make_zip(tmp_path / "z.zip", "a-skill", {"SKILL.md": MINIMAL_SKILL_MD, "scripts/x.py": "print(1)\n"})
    out = materialize(SourceSpec("zip", path=archive), "a-skill", manifest_for(tmp_path), tmp_path / "stage")
    assert out == tmp_path / "stage" / "a-skill"
    assert (out / "SKILL.md").read_text() == MINIMAL_SKILL_MD
    assert (out / "scripts" / "x.py").read_text() == "print(1)\n"


def test_zip_top_folder_must_equal_name(tmp_path):
    archive = make_zip(tmp_path / "z.zip", "other", {"SKILL.md": MINIMAL_SKILL_MD})
    with pytest.raises(SourceError, match=r"other.*a-skill|a-skill.*other"):
        materialize(SourceSpec("zip", path=archive), "a-skill", manifest_for(tmp_path), tmp_path / "stage")


def test_zip_with_two_top_folders_raises(tmp_path):
    archive = make_zip(tmp_path / "z.zip", "a-skill", {"SKILL.md": MINIMAL_SKILL_MD}, extra_members={"b/SKILL.md": "x"})
    with pytest.raises(SourceError, match=r"exactly one top-level folder"):
        materialize(SourceSpec("zip", path=archive), "a-skill", manifest_for(tmp_path), tmp_path / "stage")


def test_zip_rejects_path_traversal(tmp_path):
    archive = make_zip(tmp_path / "z.zip", "a-skill", {"SKILL.md": MINIMAL_SKILL_MD, "../../evil.txt": "pwned\n"})
    with pytest.raises(SourceError, match=r"evil\.txt"):
        materialize(SourceSpec("zip", path=archive), "a-skill", manifest_for(tmp_path), tmp_path / "stage" / "inner")
    assert list(tmp_path.rglob("evil.txt")) == []


def test_ignored_names_not_copied_or_hashed(tmp_path):
    clean = make_skill_dir(tmp_path / "clean", "a-skill", MINIMAL_SKILL_MD, {"scripts/y.py": "1\n"})
    before = tree_sha256(clean)
    noisy = make_skill_dir(
        tmp_path / "noisy", "a-skill", MINIMAL_SKILL_MD,
        {"scripts/y.py": "1\n", "__pycache__/x.pyc": "", ".DS_Store": "", "scripts/__pycache__/y.pyc": ""},
    )
    assert tree_sha256(noisy) == before
    out = materialize(SourceSpec("dir", path=noisy), "a-skill", manifest_for(tmp_path), tmp_path / "stage")
    assert not (out / "__pycache__").exists()
    assert not (out / ".DS_Store").exists()
    assert not (out / "scripts" / "__pycache__").exists()
    assert tree_sha256(out) == before


def test_tree_sha256_changes_on_rename(tmp_path):
    one = make_skill_dir(tmp_path / "one", "a-skill", MINIMAL_SKILL_MD, {"references/a.md": "same\n"})
    two = make_skill_dir(tmp_path / "two", "a-skill", MINIMAL_SKILL_MD, {"references/b.md": "same\n"})
    assert tree_sha256(one) != tree_sha256(two)


def test_tree_sha256_changes_on_content(tmp_path):
    one = make_skill_dir(tmp_path / "one", "a-skill", MINIMAL_SKILL_MD)
    two = make_skill_dir(tmp_path / "two", "a-skill", MINIMAL_SKILL_MD + "more\n")
    assert tree_sha256(one) != tree_sha256(two)


def test_zip_without_skill_md_raises(tmp_path):
    archive = make_zip(tmp_path / "z.zip", "a-skill", {"README.md": "no skill here\n"})
    with pytest.raises(SourceError, match=r"SKILL\.md"):
        materialize(SourceSpec("zip", path=archive), "a-skill", manifest_for(tmp_path), tmp_path / "stage")


def test_dir_with_dangling_symlink_raises_source_error(tmp_path):
    src = make_skill_dir(tmp_path / "src", "a-skill", MINIMAL_SKILL_MD)
    (src / "references").mkdir()
    (src / "references" / "gone.md").symlink_to(tmp_path / "nowhere.md")
    with pytest.raises(SourceError, match=r"gone\.md"):
        materialize(SourceSpec("dir", path=src), "a-skill", manifest_for(tmp_path), tmp_path / "stage")
