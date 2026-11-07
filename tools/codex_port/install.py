"""Install layer for the Codex skill port.

Version 0.1.0, owner Rock Lambros.

Three concerns live here. The sidecar records which source hash produced
which output hash, so drift is a comparison and never a timestamp. The
gate decides whether a target directory may be replaced, and refuses
anything the tool did not build. The swap moves a staged skill into place
with one rename and puts the old copy back if that rename fails.
"""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

from tools.codex_port.sources import tree_sha256
from tools.lint_frontmatter import parse_frontmatter

SIDECAR = ".rcs-port.json"
SIDECAR_SCHEMA = 1
STAGE_DIRNAME = ".rcs-port-stage"
SYSTEM_DIRNAME = ".system"


class InstallError(Exception):
    """The target cannot be replaced safely."""


@dataclass(frozen=True)
class Sidecar:
    name: str
    source: str
    source_sha256: str
    output_sha256: str
    ported_on: str
    schema: int = SIDECAR_SCHEMA


def read_sidecar(skill_dir: Path) -> Sidecar | None:
    path = skill_dir / SIDECAR
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
        return Sidecar(**data)
    except (ValueError, TypeError) as exc:
        raise InstallError(f"{path} is not a valid sidecar: {exc}") from exc


def write_sidecar(skill_dir: Path, sidecar: Sidecar) -> None:
    path = skill_dir / SIDECAR
    path.write_text(json.dumps(asdict(sidecar), indent=2, sort_keys=True) + "\n")


def installed_sha256(skill_dir: Path) -> str:
    """Hash of the installed tree. The sidecar is a dotfile, so it is excluded."""
    return tree_sha256(skill_dir)


def stage_root(codex_home: Path) -> Path:
    # Outside the skills root on purpose: Codex globs skills/*/SKILL.md
    # and would pick up a half-built stage.
    return codex_home / STAGE_DIRNAME


class Gate(Enum):
    ABSENT = "absent"
    PORTED_LEGACY = "ported-legacy"
    PORTED_CLEAN = "ported-clean"
    PORTED_EDITED = "ported-edited"
    FOREIGN = "foreign"
    SYMLINK = "symlink"
    SYSTEM = "system"


def _carries_provenance(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    data, _ = parse_frontmatter(skill_md.read_text())
    metadata = data.get("metadata") if isinstance(data, dict) else None
    return isinstance(metadata, dict) and "ported-from" in metadata


def gate(target: Path) -> Gate:
    if target.name == SYSTEM_DIRNAME:
        return Gate.SYSTEM
    if target.is_symlink():
        return Gate.SYMLINK
    if not target.exists():
        return Gate.ABSENT
    if not _carries_provenance(target):
        return Gate.FOREIGN
    sidecar = read_sidecar(target)
    if sidecar is None:
        return Gate.PORTED_LEGACY
    if sidecar.output_sha256 == installed_sha256(target):
        return Gate.PORTED_CLEAN
    return Gate.PORTED_EDITED


def install(stage: Path, target: Path, force: bool) -> Gate:
    """Swap ``stage`` into ``target`` if the gate allows it.

    The displaced copy is parked next to the stage as ``<name>.old`` for
    the length of the swap. ``os.replace`` is called through the module so
    a test can make the second rename fail and prove the rollback.
    """
    decision = gate(target)
    if decision is Gate.SYSTEM:
        raise InstallError(f"{target} is Codex's {SYSTEM_DIRNAME} directory and is never touched")
    if decision is Gate.SYMLINK:
        raise InstallError(f"{target} is a symlink, refusing to replace it")
    if decision is Gate.FOREIGN:
        raise InstallError(f"{target} was not built by this tool (no metadata.ported-from), refusing to replace it")
    if decision is Gate.PORTED_EDITED and not force:
        raise InstallError(f"{target} was edited after its last build, pass --force to replace it")

    old = stage.parent / f"{target.name}.old"
    if old.exists():
        shutil.rmtree(old)
    target.parent.mkdir(parents=True, exist_ok=True)
    had_target = decision is not Gate.ABSENT
    if had_target:
        os.replace(target, old)
    try:
        os.replace(stage, target)
    except OSError:
        if had_target:
            os.replace(old, target)
        raise
    if had_target:
        shutil.rmtree(old)
    return decision


class CheckStatus(Enum):
    OK = "ok"
    NOT_INSTALLED = "not-installed"
    LEGACY = "legacy"
    STALE_SOURCE = "stale-source"
    PATCH_FAILS = "patch-fails"
    EDITED = "edited"
    MISSING_SOURCE = "missing-source"
    INVALID = "invalid"


@dataclass
class CheckReport:
    name: str
    status: CheckStatus
    details: str = ""
    info: list[str] = field(default_factory=list)
