"""Tests for the Codex port picker writer and validation.

``write_picker`` emits ``agents/openai.yaml`` byte for byte in the shape
the September port used. ``validate`` applies Codex's install rules
locally and then runs Codex's own ``quick_validate.py`` when it exists.
"""
import sys
from pathlib import Path

import pytest
import yaml

from tools.codex_port.manifest import SkillEntry, SourceSpec
from tools.codex_port.transform import write_picker
from tools.codex_port.validate import (
    ToolchainError,
    builtin_validate,
    find_codex_validator,
    run_codex_validator,
    validate_skill,
)
from tools.tests.codex_port_fixtures import MINIMAL_SKILL_MD, make_skill_dir

GOOD_SHORT = "Does one thing well for a test"


def entry_for(name: str = "a-skill", **overrides) -> SkillEntry:
    fields = {
        "name": name,
        "source": SourceSpec("rcs", track="workflow"),
        "display_name": "A Skill",
        "short_description": GOOD_SHORT,
        "default_prompt": f"Use ${name} to do the thing.",
    }
    fields.update(overrides)
    return SkillEntry(**fields)


def skill_with_picker(tmp_path: Path, name: str = "a-skill", skill_md: str = MINIMAL_SKILL_MD, **overrides) -> Path:
    skill_dir = make_skill_dir(tmp_path / "stage", name, skill_md)
    write_picker(skill_dir, entry_for(name, **overrides))
    return skill_dir


def frontmatter(name: str = "a-skill", description: str = "Does a thing.", extra: str = "") -> str:
    return f"---\nname: {name}\ndescription: {description}\n{extra}---\n\n# Body\n"


def test_write_picker_matches_expected_bytes(tmp_path):
    skill_dir = make_skill_dir(tmp_path / "stage", "coffee-peer-voice", MINIMAL_SKILL_MD)
    entry = SkillEntry(
        name="coffee-peer-voice",
        source=SourceSpec("zip", path=tmp_path / "z.zip"),
        display_name="Coffee Peer Voice",
        short_description="Rewrite prose in a warm, human, peer-to-peer voice",
        default_prompt="Use $coffee-peer-voice to rewrite this draft so it sounds like a real person.",
    )
    out = write_picker(skill_dir, entry)
    assert out == skill_dir / "agents" / "openai.yaml"
    assert out.read_text() == (
        "interface:\n"
        '  display_name: "Coffee Peer Voice"\n'
        '  short_description: "Rewrite prose in a warm, human, peer-to-peer voice"\n'
        '  default_prompt: "Use $coffee-peer-voice to rewrite this draft so it sounds like a real person."\n'
    )


def test_write_picker_escapes_quotes(tmp_path):
    skill_dir = make_skill_dir(tmp_path / "stage", "a-skill", MINIMAL_SKILL_MD)
    out = write_picker(skill_dir, entry_for(display_name='Say "hi" \\ now'))
    data = yaml.safe_load(out.read_text())
    assert data["interface"]["display_name"] == 'Say "hi" \\ now'


def test_builtin_accepts_valid_skill(tmp_path):
    assert builtin_validate(skill_with_picker(tmp_path)) == []


@pytest.mark.parametrize(
    "case,fragment",
    [
        ("extra-top-key", "version"),
        ("bad-name", "Bad_Name"),
        ("name-mismatch", "b-skill"),
        ("long-description", "1025"),
        ("angle-bracket", "angle"),
        ("short-24", "short_description"),
        ("short-65", "short_description"),
        ("missing-picker", "openai.yaml"),
    ],
)
def test_builtin_rejects_each_rule(tmp_path, case, fragment):
    if case == "extra-top-key":
        skill_dir = skill_with_picker(tmp_path, skill_md=frontmatter(extra="version: 1.0\n"))
    elif case == "bad-name":
        skill_dir = skill_with_picker(tmp_path, name="Bad_Name", skill_md=frontmatter(name="Bad_Name"))
    elif case == "name-mismatch":
        skill_dir = skill_with_picker(tmp_path, skill_md=frontmatter(name="b-skill"))
    elif case == "long-description":
        skill_dir = skill_with_picker(tmp_path, skill_md=frontmatter(description="x" * 1025))
    elif case == "angle-bracket":
        skill_dir = skill_with_picker(tmp_path, skill_md=frontmatter(description="Use when x < y."))
    elif case == "short-24":
        skill_dir = skill_with_picker(tmp_path, short_description="x" * 24)
    elif case == "short-65":
        skill_dir = skill_with_picker(tmp_path, short_description="x" * 65)
    else:
        skill_dir = make_skill_dir(tmp_path / "stage", "a-skill", MINIMAL_SKILL_MD)
    errors = builtin_validate(skill_dir)
    assert errors, case
    assert any(fragment in error for error in errors), errors


def test_description_exactly_1024_passes(tmp_path):
    skill_dir = skill_with_picker(tmp_path, skill_md=frontmatter(description="x" * 1024))
    assert builtin_validate(skill_dir) == []


def test_find_codex_validator_none_when_absent(tmp_path):
    assert find_codex_validator(tmp_path / "codex") is None


def test_find_codex_validator_when_present(tmp_path):
    validator = tmp_path / "codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    validator.parent.mkdir(parents=True)
    validator.write_text("print('Skill is valid!')\n")
    assert find_codex_validator(tmp_path / "codex") == validator


def test_run_codex_validator_uses_sys_executable(tmp_path):
    fake = tmp_path / "qv.py"
    fake.write_text("import sys\nprint(sys.executable)\nprint(sys.argv[1])\n")
    ok, output = run_codex_validator(fake, tmp_path / "stage" / "a-skill")
    assert ok
    assert output.splitlines() == [sys.executable, str(tmp_path / "stage" / "a-skill")]


def test_run_codex_validator_reports_failure(tmp_path):
    fake = tmp_path / "qv.py"
    fake.write_text("import sys\nprint('Description is too long (1030 characters).')\nsys.exit(1)\n")
    ok, output = run_codex_validator(fake, tmp_path / "stage" / "a-skill")
    assert not ok
    assert "Description is too long" in output


def test_import_error_raises_toolchain_error(tmp_path):
    fake = tmp_path / "qv.py"
    fake.write_text("import sys\nsys.stderr.write(\"Traceback\\nModuleNotFoundError: No module named 'yaml'\\n\")\nsys.exit(1)\n")
    with pytest.raises(ToolchainError, match=r"yaml"):
        run_codex_validator(fake, tmp_path / "stage" / "a-skill")


def test_validate_skill_runs_codex_validator_when_present(tmp_path):
    codex_home = tmp_path / "codex"
    validator = codex_home / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    validator.parent.mkdir(parents=True)
    validator.write_text("import sys\nprint('fake validator rejected it')\nsys.exit(1)\n")
    skill_dir = skill_with_picker(tmp_path)
    errors = validate_skill(skill_dir, codex_home)
    assert errors == ["fake validator rejected it"]


def test_validate_skill_without_codex_validator_uses_builtin_only(tmp_path):
    assert validate_skill(skill_with_picker(tmp_path), tmp_path / "codex") == []


def test_validate_skill_skips_codex_validator_when_builtin_fails(tmp_path):
    codex_home = tmp_path / "codex"
    validator = codex_home / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    validator.parent.mkdir(parents=True)
    validator.write_text("import sys\nsys.stderr.write('ModuleNotFoundError: x')\nsys.exit(1)\n")
    skill_dir = skill_with_picker(tmp_path, skill_md=frontmatter(description="x" * 1025))
    errors = validate_skill(skill_dir, codex_home)
    assert errors and all("1025" in error for error in errors)
