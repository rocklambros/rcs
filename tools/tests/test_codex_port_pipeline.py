"""End-to-end tests for the Codex port pipeline on synthetic skills.

Every path lives under tmp_path. The pipeline is exercised the way the
CLI calls it: build, build again, change something, check.
"""
from pathlib import Path

import pytest

from tools.codex_port.install import CheckStatus, Gate, installed_sha256, read_sidecar, stage_root
from tools.codex_port.manifest import load_manifest
from tools.codex_port.pipeline import build_skill, check_skill, diff_skill
from tools.codex_port.validate import ToolchainError
from tools.tests.codex_port_fixtures import (
    CLAUDE_SKILL_MD,
    RCS_SKILL_MD,
    entry,
    make_port_env,
    make_skill_dir,
    make_zip,
)

BAD_PATCH = "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -1,1 +1,1 @@\n-this line is not in the file\n+replacement\n"
PORTED_SKILL_MD = (
    "---\nname: a-skill\ndescription: Does a thing.\nmetadata:\n"
    "  ported-from: rcs:workflow/a-skill\n  ported-to-codex: '2026-09-29'\n---\n\n# Old hand copy\n"
)


def rcs_env(tmp_path: Path, body: str = RCS_SKILL_MD, with_source: bool = True):
    env = make_port_env(tmp_path, {"a-skill": entry("a-skill", {"kind": "rcs", "track": "workflow"})})
    if with_source:
        make_skill_dir(env.rcs_root / "workflow", "a-skill", body, {"scripts/x.py": "print(1)\n"})
    return env


def build(env, today="2026-11-06", force=False):
    manifest = load_manifest(env.manifest_path, None)
    return build_skill(manifest.skills["a-skill"], manifest, force=force, today=today)


def check(env, today="2026-11-06"):
    manifest = load_manifest(env.manifest_path, None)
    return check_skill(manifest.skills["a-skill"], manifest, today=today)


def test_build_installs_and_writes_sidecar(tmp_path):
    env = rcs_env(tmp_path)
    result = build(env)
    assert result.ok, result.message
    assert result.gate is Gate.ABSENT
    target = env.skills_root / "a-skill"
    assert (target / "agents" / "openai.yaml").is_file()
    assert (target / "scripts" / "x.py").read_text() == "print(1)\n"
    sidecar = read_sidecar(target)
    assert sidecar.source == "rcs:workflow/a-skill"
    assert sidecar.ported_on == "2026-11-06"
    assert sidecar.output_sha256 == installed_sha256(target)
    skill_md = (target / "SKILL.md").read_text()
    assert "`$other-skill`" in skill_md
    assert skill_md.endswith("\n## Codex runtime notes\n\n- sibling note\n")
    assert not (stage_root(env.codex_home) / "a-skill").exists()


def test_second_build_is_byte_identical(tmp_path):
    env = rcs_env(tmp_path)
    assert build(env).ok
    target = env.skills_root / "a-skill"
    first = installed_sha256(target)
    result = build(env, today="2026-12-01")
    assert result.ok and result.gate is Gate.PORTED_CLEAN
    assert installed_sha256(target) == first
    assert read_sidecar(target).ported_on == "2026-11-06"


def test_source_change_updates_ported_on(tmp_path):
    env = rcs_env(tmp_path)
    assert build(env).ok
    source = env.rcs_root / "workflow" / "a-skill" / "SKILL.md"
    source.write_text(source.read_text() + "\nNew paragraph.\n")
    assert build(env, today="2026-12-01").ok
    target = env.skills_root / "a-skill"
    assert read_sidecar(target).ported_on == "2026-12-01"
    assert "New paragraph." in (target / "SKILL.md").read_text()


def test_failing_patch_leaves_install_untouched(tmp_path):
    env = rcs_env(tmp_path)
    assert build(env).ok
    target = env.skills_root / "a-skill"
    before = installed_sha256(target)
    (env.data_dir / "patches").mkdir()
    (env.data_dir / "patches" / "a-skill.patch").write_text(BAD_PATCH)
    result = build(env)
    assert not result.ok
    assert "does not apply" in result.message
    assert installed_sha256(target) == before
    assert not (stage_root(env.codex_home) / "a-skill").exists()


def test_build_applies_patch_and_pins_tokens_for_zip_source(tmp_path):
    env = make_port_env(
        tmp_path,
        {"a-skill": entry("a-skill", {"kind": "zip", "path": str(tmp_path / "a-skill-portable.zip")}, path_tokens=True)},
    )
    make_zip(tmp_path / "a-skill-portable.zip", "a-skill", {"SKILL.md": CLAUDE_SKILL_MD, "scripts/l.py": "print(1)\n"})
    (env.data_dir / "patches").mkdir()
    # Two context lines each side, so git apply can anchor the hunk even if
    # the frontmatter grows and shifts the line numbers.
    (env.data_dir / "patches" / "a-skill.patch").write_text(
        "\n".join(
            [
                "--- a/SKILL.md",
                "+++ b/SKILL.md",
                "@@ -18,5 +18,5 @@",
                " ```",
                " ",
                "-`SKILLS` stands for the folder that holds this skill's folder.",
                "+The paths above are absolute.",
                " ",
                " ## Codex runtime notes",
                "",
            ]
        )
    )
    result = build(env)
    assert result.ok, result.message
    skill_md = (env.skills_root / "a-skill" / "SKILL.md").read_text()
    assert f"python3 -I {env.skills_root.as_posix()}/a-skill/scripts/l.py DRAFT" in skill_md
    assert "The paths above are absolute." in skill_md
    assert "`SKILLS` stands for" not in skill_md


@pytest.mark.parametrize(
    "case,expected",
    [
        ("not-installed", CheckStatus.NOT_INSTALLED),
        ("legacy", CheckStatus.LEGACY),
        ("stale-source", CheckStatus.STALE_SOURCE),
        ("edited", CheckStatus.EDITED),
        ("patch-fails", CheckStatus.PATCH_FAILS),
        ("missing-source", CheckStatus.MISSING_SOURCE),
        ("port-data-changed", CheckStatus.STALE_SOURCE),
        ("ok", CheckStatus.OK),
    ],
)
def test_check_reports_each_status(tmp_path, case, expected):
    env = rcs_env(tmp_path, with_source=case != "missing-source")
    target = env.skills_root / "a-skill"
    if case == "legacy":
        make_skill_dir(env.skills_root, "a-skill", PORTED_SKILL_MD)
    elif case in ("stale-source", "edited", "patch-fails", "port-data-changed", "ok"):
        assert build(env).ok
    if case == "stale-source":
        source = env.rcs_root / "workflow" / "a-skill" / "SKILL.md"
        source.write_text(source.read_text() + "\nChanged.\n")
    elif case == "edited":
        (target / "SKILL.md").write_text((target / "SKILL.md").read_text() + "Hand edit.\n")
    elif case == "patch-fails":
        (env.data_dir / "patches").mkdir()
        (env.data_dir / "patches" / "a-skill.patch").write_text(BAD_PATCH)
    elif case == "port-data-changed":
        (env.data_dir / "notes" / "_default.md").write_text("- a different note\n")
    before = installed_sha256(target) if target.exists() else None
    report = check(env)
    assert report.status is expected, report
    if case == "port-data-changed":
        assert "port data" in report.details
    assert not (stage_root(env.codex_home) / "check" / "a-skill").exists()
    assert (installed_sha256(target) if target.exists() else None) == before


def test_check_adds_profile_info_line(tmp_path):
    env = make_port_env(tmp_path, {"a-skill": entry("a-skill", {"kind": "claude_ai", "profile": "Claude"})})
    make_skill_dir(env.cache_roots["Claude"] / "u1" / "s1" / "skills", "a-skill", CLAUDE_SKILL_MD)
    make_skill_dir(env.cache_roots["Claude-Zenity"] / "u2" / "s2" / "skills", "a-skill", CLAUDE_SKILL_MD + "Zenity edition.\n")
    assert build(env).ok
    report = check(env)
    assert report.status is CheckStatus.OK
    assert len(report.info) == 1
    assert "Claude-Zenity" in report.info[0]


def test_check_has_no_info_when_profiles_agree(tmp_path):
    env = make_port_env(tmp_path, {"a-skill": entry("a-skill", {"kind": "claude_ai", "profile": "Claude"})})
    make_skill_dir(env.cache_roots["Claude"] / "u1" / "s1" / "skills", "a-skill", CLAUDE_SKILL_MD)
    make_skill_dir(env.cache_roots["Claude-Zenity"] / "u2" / "s2" / "skills", "a-skill", CLAUDE_SKILL_MD)
    assert build(env).ok
    assert check(env).info == []


def test_toolchain_error_propagates(tmp_path):
    env = rcs_env(tmp_path)
    validator = env.codex_home / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    validator.parent.mkdir(parents=True)
    validator.write_text("import sys\nsys.stderr.write(\"ModuleNotFoundError: No module named 'yaml'\\n\")\nsys.exit(1)\n")
    with pytest.raises(ToolchainError):
        build(env)
    assert not (env.skills_root / "a-skill").exists()
    assert not (stage_root(env.codex_home) / "a-skill").exists()


def test_diff_shows_pending_change(tmp_path):
    env = rcs_env(tmp_path)
    assert build(env).ok
    source = env.rcs_root / "workflow" / "a-skill" / "SKILL.md"
    source.write_text(source.read_text() + "\nNew paragraph.\n")
    manifest = load_manifest(env.manifest_path, None)
    text = diff_skill(manifest.skills["a-skill"], manifest, today="2026-12-01")
    assert "+New paragraph." in text
    assert "--- a/SKILL.md" in text


def test_diff_is_empty_when_up_to_date(tmp_path):
    env = rcs_env(tmp_path)
    assert build(env).ok
    manifest = load_manifest(env.manifest_path, None)
    assert diff_skill(manifest.skills["a-skill"], manifest, today="2026-12-01") == ""
