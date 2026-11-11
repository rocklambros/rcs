"""Tests for Codex port patch application and capture.

Patches carry the hand adaptations a port needs beyond the mechanical
layer. They apply with ``git apply`` against a staged skill directory,
and ``capture_patch`` produces one by diffing a generated tree against an
installed one.
"""
import shutil
from pathlib import Path

from tools.codex_port.patching import apply_patch, capture_patch, check_patch, find_patch
from tools.codex_port.sources import tree_sha256
from tools.tests.codex_port_fixtures import MINIMAL_SKILL_MD, make_skill_dir

# Replaces the body line of MINIMAL_SKILL_MD. The empty context line is a
# single space, which is how unified diffs spell a blank line.
SIMPLE_PATCH = "\n".join(
    [
        "--- a/SKILL.md",
        "+++ b/SKILL.md",
        "@@ -6,3 +6,3 @@",
        " # A skill",
        " ",
        "-Body.",
        "+Patched body.",
        "",
    ]
)


def write_patch(tmp_path: Path, text: str = SIMPLE_PATCH) -> Path:
    patch = tmp_path / "patches" / "a-skill.patch"
    patch.parent.mkdir(parents=True, exist_ok=True)
    patch.write_text(text)
    return patch


def test_find_patch_prefers_local_then_tracked(tmp_path):
    local = tmp_path / "local"
    tracked = tmp_path / "tracked"
    assert find_patch("a-skill", (local, tracked)) is None
    tracked_patch = write_patch(tracked)
    assert find_patch("a-skill", (local, tracked)) == tracked_patch
    local_patch = write_patch(local)
    assert find_patch("a-skill", (local, tracked)) == local_patch


def test_apply_patch_changes_file(tmp_path):
    tree = make_skill_dir(tmp_path / "stage", "a-skill", MINIMAL_SKILL_MD)
    result = apply_patch(tree, write_patch(tmp_path))
    assert result.ok, result.output
    assert (tree / "SKILL.md").read_text().endswith("# A skill\n\nPatched body.\n")


def test_check_patch_reports_rejected_hunk_without_writing(tmp_path):
    tree = make_skill_dir(tmp_path / "stage", "a-skill", MINIMAL_SKILL_MD.replace("Body.", "Other."))
    before = (tree / "SKILL.md").read_bytes()
    result = check_patch(tree, write_patch(tmp_path))
    assert not result.ok
    assert "SKILL.md" in result.output
    assert (tree / "SKILL.md").read_bytes() == before
    assert not apply_patch(tree, write_patch(tmp_path)).ok
    assert (tree / "SKILL.md").read_bytes() == before


def test_patch_applies_with_line_offset(tmp_path):
    shifted = MINIMAL_SKILL_MD.replace("\n# A skill", "\nIntro line.\nSecond intro line.\n\n# A skill")
    tree = make_skill_dir(tmp_path / "stage", "a-skill", shifted)
    assert check_patch(tree, write_patch(tmp_path)).ok
    assert apply_patch(tree, write_patch(tmp_path)).ok
    assert "Patched body." in (tree / "SKILL.md").read_text()


def test_capture_patch_roundtrips(tmp_path):
    generated = make_skill_dir(tmp_path / "gen", "a-skill", MINIMAL_SKILL_MD, {"references/r.md": "one\n", "references/gone.md": "x\n"})
    installed = make_skill_dir(
        tmp_path / "inst", "a-skill", MINIMAL_SKILL_MD.replace("Body.", "Edited body."),
        {"references/r.md": "one\ntwo\n", "references/new.md": "new\n"},
    )
    out = tmp_path / "patches" / "a-skill.patch"
    changed = capture_patch(generated, installed, out)
    assert changed == 4
    text = out.read_text()
    assert "--- a/SKILL.md" in text and "+++ b/SKILL.md" in text
    assert "a/s/" not in text and "b/t/" not in text
    fresh = tmp_path / "fresh" / "a-skill"
    shutil.copytree(generated, fresh)
    result = apply_patch(fresh, out)
    assert result.ok, result.output
    assert tree_sha256(fresh) == tree_sha256(installed)


def test_capture_excludes_generated_files(tmp_path):
    generated = make_skill_dir(tmp_path / "gen", "a-skill", MINIMAL_SKILL_MD, {"agents/openai.yaml": "interface:\n  display_name: \"A\"\n"})
    installed = make_skill_dir(
        tmp_path / "inst", "a-skill", MINIMAL_SKILL_MD,
        {"agents/openai.yaml": "interface:\n  display_name: \"B\"\n", ".rcs-port.json": "{}", "__pycache__/x.pyc": ""},
    )
    out = tmp_path / "patches" / "a-skill.patch"
    assert capture_patch(generated, installed, out) == 0
    assert not out.exists()


def test_capture_returns_zero_and_writes_nothing_when_identical(tmp_path):
    generated = make_skill_dir(tmp_path / "gen", "a-skill", MINIMAL_SKILL_MD)
    installed = make_skill_dir(tmp_path / "inst", "a-skill", MINIMAL_SKILL_MD)
    out = tmp_path / "patches" / "a-skill.patch"
    assert capture_patch(generated, installed, out) == 0
    assert not out.exists()
