"""Validation for the Codex skill port.

Version 0.1.0, owner Rock Lambros.

Two layers. ``builtin_validate`` applies the rules Codex's bundled
``quick_validate.py`` enforces, with messages that name the exact value,
so a failure is readable without the subprocess. ``run_codex_validator``
then runs Codex's own script when it is installed, because its rules are
the ones that matter and they may move between ChatGPT releases.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from tools.codex_port.manifest import (
    MAX_NAME_LENGTH,
    NAME_PATTERN,
    SHORT_DESCRIPTION_MAX,
    SHORT_DESCRIPTION_MIN,
)
from tools.codex_port.transform import ALLOWED_TOP_LEVEL
from tools.lint_frontmatter import parse_frontmatter

MAX_DESCRIPTION_LENGTH = 1024
CODEX_VALIDATOR_RELATIVE = Path("skills/.system/skill-creator/scripts/quick_validate.py")
IMPORT_FAILURE_MARKERS = ("ModuleNotFoundError", "ImportError")


class ToolchainError(Exception):
    """The Codex validator exists but cannot run under this interpreter.

    This is a toolchain problem, not a skill problem, so the build aborts
    instead of treating every skill as invalid or skipping the validator.
    """


def _picker_errors(skill_dir: Path) -> list[str]:
    picker = skill_dir / "agents" / "openai.yaml"
    if not picker.is_file():
        return ["agents/openai.yaml is missing"]
    try:
        data = yaml.safe_load(picker.read_text())
    except yaml.YAMLError as exc:
        return [f"agents/openai.yaml: {exc}"]
    interface = data.get("interface") if isinstance(data, dict) else None
    short = interface.get("short_description") if isinstance(interface, dict) else None
    if not isinstance(short, str):
        return ["agents/openai.yaml: interface.short_description is missing"]
    if not SHORT_DESCRIPTION_MIN <= len(short) <= SHORT_DESCRIPTION_MAX:
        return [
            f"agents/openai.yaml: short_description is {len(short)} chars, "
            f"Codex requires {SHORT_DESCRIPTION_MIN} to {SHORT_DESCRIPTION_MAX}"
        ]
    return []


def builtin_validate(skill_dir: Path) -> list[str]:
    """Codex's install rules, applied locally. Empty list means valid."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md is missing"]
    data, parse_errors = parse_frontmatter(skill_md.read_text())
    if data is None:
        return [error.message for error in parse_errors]

    errors: list[str] = []
    unexpected = [key for key in data if key not in ALLOWED_TOP_LEVEL]
    if unexpected:
        errors.append(
            f"unexpected top-level frontmatter key(s): {', '.join(unexpected)}, "
            f"allowed: {', '.join(ALLOWED_TOP_LEVEL)}"
        )

    name = data.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name is missing")
    else:
        if not NAME_PATTERN.match(name):
            errors.append(f"name {name!r} must match ^[a-z0-9-]+$")
        if len(name) > MAX_NAME_LENGTH:
            errors.append(f"name is {len(name)} chars, the limit is {MAX_NAME_LENGTH}")
        if name != skill_dir.name:
            errors.append(f"name {name!r} does not equal the directory name {skill_dir.name!r}")

    description = data.get("description")
    if not isinstance(description, str) or not description:
        errors.append("description is missing or not a string")
    else:
        if len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"description is {len(description)} chars, the limit is {MAX_DESCRIPTION_LENGTH}")
        if "<" in description or ">" in description:
            errors.append("description contains angle brackets, which Codex rejects")

    errors.extend(_picker_errors(skill_dir))
    return errors


def find_codex_validator(codex_home: Path) -> Path | None:
    candidate = codex_home / CODEX_VALIDATOR_RELATIVE
    return candidate if candidate.is_file() else None


def run_codex_validator(validator: Path, skill_dir: Path) -> tuple[bool, str]:
    """Run Codex's validator under this interpreter and return (ok, output).

    ``sys.executable`` is deliberate: the system ``python3`` on this Mac has
    no PyYAML, and the validator imports it.
    """
    result = subprocess.run(
        [sys.executable, str(validator), str(skill_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and any(marker in result.stderr for marker in IMPORT_FAILURE_MARKERS):
        last_line = result.stderr.strip().splitlines()[-1]
        raise ToolchainError(f"{validator} cannot import its dependencies under {sys.executable}: {last_line}")
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def validate_skill(skill_dir: Path, codex_home: Path) -> list[str]:
    """Built-in rules first, then Codex's validator if the skill passed them."""
    errors = builtin_validate(skill_dir)
    if errors:
        return errors
    validator = find_codex_validator(codex_home)
    if validator is None:
        return []
    ok, output = run_codex_validator(validator, skill_dir)
    if ok:
        return []
    return [output or f"{validator.name} rejected {skill_dir.name}"]
