"""Tests for the Codex port manifest loader.

The loader reads a tracked TOML manifest, merges an optional gitignored
local overlay over it, expands every path, and validates each skill entry
against the rules Codex enforces on install.
"""
from pathlib import Path

import pytest

from tools.codex_port.manifest import ManifestError, load_manifest
from tools.tests.codex_port_fixtures import defaults_for, entry, write_manifest


def tracked(tmp_path: Path, skills: dict, defaults: dict | None = None) -> Path:
    return write_manifest(tmp_path / "tracked" / "manifest.toml", defaults or defaults_for(tmp_path), skills)


def test_loads_tracked_manifest(tmp_path):
    path = tracked(tmp_path, {"a-skill": entry("a-skill", {"kind": "rcs", "track": "workflow"})})
    m = load_manifest(path, None)
    assert m.skills["a-skill"].source.label("a-skill") == "rcs:workflow/a-skill"
    assert m.codex_home == tmp_path / "codex"
    assert m.rcs_root == tmp_path / "rcs"
    assert m.cache_roots["Claude"] == tmp_path / "cache-claude"
    assert m.data_dirs == (path.parent,)


def test_local_overlay_adds_and_overrides(tmp_path):
    path = tracked(tmp_path, {"a-skill": entry("a-skill", {"kind": "rcs", "track": "workflow"})})
    local = write_manifest(
        tmp_path / "local" / "manifest.toml",
        {},
        {
            "a-skill": entry("a-skill", {"kind": "rcs", "track": "workflow"}, display_name="Overridden"),
            "private-skill": entry("private-skill", {"kind": "rcs", "track": "teaching"}),
        },
    )
    m = load_manifest(path, local)
    assert list(m.skills) == ["a-skill", "private-skill"]
    assert m.skills["a-skill"].display_name == "Overridden"
    assert m.data_dirs == (local.parent, path.parent)


def test_local_overlay_overrides_defaults(tmp_path):
    path = tracked(tmp_path, {"a-skill": entry("a-skill", {"kind": "rcs", "track": "workflow"})})
    local = write_manifest(tmp_path / "local" / "manifest.toml", {"codex_home": str(tmp_path / "codex2")}, {})
    m = load_manifest(path, local)
    assert m.codex_home == tmp_path / "codex2"
    assert m.rcs_root == tmp_path / "rcs"


def test_missing_local_overlay_is_ignored(tmp_path):
    path = tracked(tmp_path, {"a-skill": entry("a-skill", {"kind": "rcs", "track": "workflow"})})
    m = load_manifest(path, tmp_path / "local" / "manifest.toml")
    assert m.data_dirs == (path.parent,)


def test_missing_required_picker_field_raises(tmp_path):
    data = entry("a-skill", {"kind": "rcs", "track": "workflow"})
    del data["default_prompt"]
    path = tracked(tmp_path, {"a-skill": data})
    with pytest.raises(ManifestError, match=r"a-skill.*default_prompt"):
        load_manifest(path, None)


@pytest.mark.parametrize("length,ok", [(24, False), (25, True), (64, True), (65, False)])
def test_short_description_length_enforced(tmp_path, length, ok):
    data = entry("a-skill", {"kind": "rcs", "track": "workflow"}, short_description="x" * length)
    path = tracked(tmp_path, {"a-skill": data})
    if ok:
        assert load_manifest(path, None).skills["a-skill"].short_description == "x" * length
    else:
        with pytest.raises(ManifestError, match=r"short_description"):
            load_manifest(path, None)


def test_unknown_source_kind_raises(tmp_path):
    path = tracked(tmp_path, {"a-skill": entry("a-skill", {"kind": "ftp", "path": "/x"})})
    with pytest.raises(ManifestError, match=r"ftp"):
        load_manifest(path, None)


@pytest.mark.parametrize(
    "source,missing",
    [
        ({"kind": "rcs"}, "track"),
        ({"kind": "claude_ai"}, "profile"),
        ({"kind": "zip"}, "path"),
        ({"kind": "dir"}, "path"),
    ],
)
def test_source_requires_kind_specific_field(tmp_path, source, missing):
    path = tracked(tmp_path, {"a-skill": entry("a-skill", source)})
    with pytest.raises(ManifestError, match=missing):
        load_manifest(path, None)


def test_claude_ai_profile_must_exist_in_cache_roots(tmp_path):
    path = tracked(tmp_path, {"a-skill": entry("a-skill", {"kind": "claude_ai", "profile": "Nope"})})
    with pytest.raises(ManifestError, match=r"Nope"):
        load_manifest(path, None)


@pytest.mark.parametrize("name,fragment", [("Bad_Name", "Bad_Name"), ("x" * 65, "64")])
def test_skill_name_must_match_codex_rules(tmp_path, name, fragment):
    path = tracked(tmp_path, {name: entry(name, {"kind": "rcs", "track": "workflow"})})
    with pytest.raises(ManifestError, match=fragment):
        load_manifest(path, None)


def test_source_label_abbreviates_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    zip_path = tmp_path / "Templates" / "a-skill-portable.zip"
    path = tracked(tmp_path, {"a-skill": entry("a-skill", {"kind": "zip", "path": str(zip_path)})})
    m = load_manifest(path, None)
    assert m.skills["a-skill"].source.label("a-skill") == "zip:~/Templates/a-skill-portable.zip"
