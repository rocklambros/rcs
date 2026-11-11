"""Tests for the port_to_codex command line.

The CLI is a thin layer: it loads the manifest, selects skills, calls the
pipeline, prints one line per skill, and maps outcomes to exit codes.
"""
from pathlib import Path

from click.testing import CliRunner

from tools.port_to_codex import main
from tools.tests.codex_port_fixtures import RCS_SKILL_MD, entry, make_port_env, make_skill_dir

BAD_PATCH = "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -1,1 +1,1 @@\n-this line is not in the file\n+replacement\n"


def env_with_rcs_skill(tmp_path: Path):
    env = make_port_env(tmp_path, {"a-skill": entry("a-skill", {"kind": "rcs", "track": "workflow"})})
    make_skill_dir(env.rcs_root / "workflow", "a-skill", RCS_SKILL_MD)
    return env


def invoke(env, *args, local_manifest: Path | None = None):
    argv = ["--manifest", str(env.manifest_path)]
    argv += ["--local-manifest", str(local_manifest or (env.data_dir / "local" / "manifest.toml"))]
    argv += list(args)
    return CliRunner().invoke(main, argv)


def test_build_exit_codes(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    result = invoke(env, "build")
    assert result.exit_code == 0, result.output
    assert "a-skill  ok" in result.output
    (env.data_dir / "patches").mkdir()
    (env.data_dir / "patches" / "a-skill.patch").write_text(BAD_PATCH)
    result = invoke(env, "build")
    assert result.exit_code == 1
    assert "a-skill  failed" in result.output


def test_only_unknown_name_exits_2_and_writes_nothing(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    result = invoke(env, "build", "--only", "nope")
    assert result.exit_code == 2
    assert "nope" in result.output
    assert not env.skills_root.exists() or list(env.skills_root.iterdir()) == []


def test_manifest_error_exits_2(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    env.manifest_path.write_text("this is not = toml [\n")
    result = invoke(env, "check")
    assert result.exit_code == 2


def test_check_exit_1_when_stale(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    assert invoke(env, "build").exit_code == 0
    assert invoke(env, "check").exit_code == 0
    source = env.rcs_root / "workflow" / "a-skill" / "SKILL.md"
    source.write_text(source.read_text() + "\nChanged.\n")
    result = invoke(env, "check")
    assert result.exit_code == 1
    assert "a-skill  stale-source" in result.output
    assert invoke(env, "build").exit_code == 0
    assert invoke(env, "check").exit_code == 0


def test_diff_prints_pending_change(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    assert invoke(env, "build").exit_code == 0
    source = env.rcs_root / "workflow" / "a-skill" / "SKILL.md"
    source.write_text(source.read_text() + "\nChanged.\n")
    result = invoke(env, "diff", "a-skill")
    assert result.exit_code == 0
    assert "+Changed." in result.output


def test_capture_writes_patch_file(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    assert invoke(env, "build").exit_code == 0
    installed = env.skills_root / "a-skill" / "SKILL.md"
    installed.write_text(installed.read_text() + "Hand edit for Codex.\n")
    result = invoke(env, "capture", "a-skill")
    assert result.exit_code == 0, result.output
    patch = env.data_dir / "patches" / "a-skill.patch"
    assert patch.is_file()
    assert "+Hand edit for Codex." in patch.read_text()
    assert invoke(env, "build", "--force").exit_code == 0
    assert "Hand edit for Codex." in installed.read_text()
    assert invoke(env, "check").exit_code == 0


def test_capture_targets_local_dir_when_notes_live_there(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    local = env.data_dir / "local"
    (local / "notes").mkdir(parents=True)
    (local / "notes" / "a-skill.md").write_text("- local note\n")
    (local / "manifest.toml").write_text("[skills]\n")
    assert invoke(env, "build").exit_code == 0
    installed = env.skills_root / "a-skill" / "SKILL.md"
    installed.write_text(installed.read_text() + "Private edit.\n")
    assert invoke(env, "capture", "a-skill").exit_code == 0
    assert (local / "patches" / "a-skill.patch").is_file()
    assert not (env.data_dir / "patches" / "a-skill.patch").exists()


def test_local_manifest_used_only_when_present(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    make_skill_dir(env.rcs_root / "teaching", "private-skill", RCS_SKILL_MD.replace("name: a-skill", "name: private-skill"))
    result = invoke(env, "build")
    assert result.exit_code == 0
    assert "private-skill" not in result.output
    local = env.data_dir / "local" / "manifest.toml"
    local.parent.mkdir(parents=True)
    local.write_text(
        "[skills.private-skill]\n"
        'source = { kind = "rcs", track = "teaching" }\n'
        'display_name = "Private Skill"\n'
        'short_description = "Does one private thing for a test"\n'
        'default_prompt = "Use $private-skill to do the thing."\n'
    )
    result = invoke(env, "build")
    assert result.exit_code == 0, result.output
    assert "private-skill  ok" in result.output
    assert (env.skills_root / "private-skill" / "SKILL.md").is_file()


def test_codex_home_override(tmp_path):
    env = env_with_rcs_skill(tmp_path)
    other = tmp_path / "other-codex"
    result = invoke(env, "--codex-home", str(other), "build")
    assert result.exit_code == 0, result.output
    assert (other / "skills" / "a-skill" / "SKILL.md").is_file()
    assert not env.skills_root.exists()
