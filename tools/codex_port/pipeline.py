"""Pipeline for the Codex skill port.

Version 0.1.0, owner Rock Lambros.

One skill at a time: materialize the source into a stage, apply the
mechanical transforms, apply the hand patch, validate, record the sidecar,
install. ``check_skill`` runs the same steps into a scratch stage and
compares instead of installing, so it never writes under ``skills/``.
"""
from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from tools.codex_port.install import (
    CheckReport,
    CheckStatus,
    Gate,
    InstallError,
    Sidecar,
    gate,
    install,
    installed_sha256,
    read_sidecar,
    stage_root,
    write_sidecar,
)
from tools.codex_port.manifest import Manifest, SkillEntry
from tools.codex_port.patching import apply_patch, capture_patch, check_patch, find_patch
from tools.codex_port.sources import SourceError, materialize, resolve_cache_dir, tree_sha256
from tools.codex_port.transform import TransformError, transform_tree, write_picker
from tools.codex_port.validate import validate_skill

CHECK_DIRNAME = "check"


@dataclass(frozen=True)
class BuildResult:
    name: str
    ok: bool
    gate: Gate | None
    message: str


@dataclass(frozen=True)
class Prepared:
    stage: Path
    source_sha256: str
    ported_on: str
    installed_sidecar: Sidecar | None


def target_for(manifest: Manifest, name: str) -> Path:
    return manifest.codex_home / "skills" / name


def _clear(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _installed_sidecar(target: Path) -> Sidecar | None:
    if target.is_dir() and not target.is_symlink():
        return read_sidecar(target)
    return None


def prepare_stage(entry: SkillEntry, manifest: Manifest, today: str, root: Path) -> Prepared:
    """Materialize and apply the mechanical layer into ``root/<name>``.

    The ported-on date is reused from the installed sidecar when the source
    hash is unchanged, which is what makes a rebuild byte-identical.
    """
    root.mkdir(parents=True, exist_ok=True)
    stage = root / entry.name
    _clear(stage)
    materialize(entry.source, entry.name, manifest, root)
    source_sha256 = tree_sha256(stage)
    sidecar = _installed_sidecar(target_for(manifest, entry.name))
    ported_on = sidecar.ported_on if sidecar and sidecar.source_sha256 == source_sha256 else today
    transform_tree(stage, entry, manifest, ported_on)
    write_picker(stage, entry)
    return Prepared(stage=stage, source_sha256=source_sha256, ported_on=ported_on, installed_sidecar=sidecar)


def build_skill(entry: SkillEntry, manifest: Manifest, force: bool, today: str) -> BuildResult:
    """Build one skill and install it. A ``ToolchainError`` propagates."""
    name = entry.name
    target = target_for(manifest, name)
    root = stage_root(manifest.codex_home)
    stage = root / name
    try:
        prepared = prepare_stage(entry, manifest, today, root)
        patch = find_patch(name, manifest.data_dirs)
        if patch is not None:
            result = apply_patch(prepared.stage, patch)
            if not result.ok:
                return BuildResult(name, False, None, f"patch {patch.name} does not apply: {result.output}")
        errors = validate_skill(prepared.stage, manifest.codex_home)
        if errors:
            return BuildResult(name, False, None, "invalid: " + " | ".join(errors))
        write_sidecar(
            prepared.stage,
            Sidecar(
                name=name,
                source=entry.source.label(name),
                source_sha256=prepared.source_sha256,
                output_sha256=installed_sha256(prepared.stage),
                ported_on=prepared.ported_on,
            ),
        )
        decision = install(prepared.stage, target, force)
        return BuildResult(name, True, decision, f"installed ({decision.value})")
    except (SourceError, TransformError, InstallError) as exc:
        return BuildResult(name, False, None, str(exc))
    finally:
        # After a successful install the stage has moved, so this is a no-op.
        _clear(stage)


def _profile_info(entry: SkillEntry, manifest: Manifest, source_sha256: str) -> list[str]:
    if entry.source.kind != "claude_ai":
        return []
    info: list[str] = []
    for profile, cache_root in manifest.cache_roots.items():
        if profile == entry.source.profile:
            continue
        try:
            other = resolve_cache_dir(cache_root, entry.name, profile)
        except SourceError:
            continue
        if tree_sha256(other) != source_sha256:
            info.append(f"profile {profile!r} holds a different copy of {entry.name}")
    return info


def check_skill(entry: SkillEntry, manifest: Manifest, today: str) -> CheckReport:
    """Report what ``build`` would do without touching the install."""
    name = entry.name
    target = target_for(manifest, name)
    check_root = stage_root(manifest.codex_home) / CHECK_DIRNAME
    stage = check_root / name
    try:
        try:
            prepared = prepare_stage(entry, manifest, today, check_root)
        except SourceError as exc:
            return CheckReport(name, CheckStatus.MISSING_SOURCE, str(exc))
        except (TransformError, InstallError) as exc:
            return CheckReport(name, CheckStatus.INVALID, str(exc))
        info = _profile_info(entry, manifest, prepared.source_sha256)
        decision = gate(target)
        if decision is Gate.ABSENT:
            return CheckReport(name, CheckStatus.NOT_INSTALLED, "not installed, run build", info)
        if decision is Gate.PORTED_LEGACY:
            return CheckReport(name, CheckStatus.LEGACY, "installed by hand before this tool, run build once to record a sidecar", info)
        if decision is Gate.PORTED_EDITED:
            return CheckReport(
                name, CheckStatus.EDITED,
                "installed copy was edited after its last build, run capture to keep the edit or build --force to drop it",
                info,
            )
        if decision is not Gate.PORTED_CLEAN:
            return CheckReport(name, CheckStatus.INVALID, f"target is {decision.value} and will not be replaced", info)
        sidecar = prepared.installed_sidecar
        if sidecar is None or sidecar.source_sha256 != prepared.source_sha256:
            return CheckReport(name, CheckStatus.STALE_SOURCE, "source changed since the last build", info)
        patch = find_patch(name, manifest.data_dirs)
        if patch is not None:
            result = check_patch(prepared.stage, patch)
            if not result.ok:
                return CheckReport(name, CheckStatus.PATCH_FAILS, f"patch {patch.name} does not apply: {result.output}", info)
            apply_patch(prepared.stage, patch)
        errors = validate_skill(prepared.stage, manifest.codex_home)
        if errors:
            return CheckReport(name, CheckStatus.INVALID, " | ".join(errors), info)
        if installed_sha256(prepared.stage) != sidecar.output_sha256:
            return CheckReport(
                name, CheckStatus.STALE_SOURCE,
                "port data (notes, patch, or picker text) changed since the last build",
                info,
            )
        return CheckReport(name, CheckStatus.OK, "up to date", info)
    finally:
        _clear(stage)


def diff_skill(entry: SkillEntry, manifest: Manifest, today: str) -> str:
    """Unified diff from the installed copy to what ``build`` would install."""
    name = entry.name
    target = target_for(manifest, name)
    check_root = stage_root(manifest.codex_home) / CHECK_DIRNAME
    stage = check_root / name
    try:
        prepared = prepare_stage(entry, manifest, today, check_root)
        header = ""
        patch = find_patch(name, manifest.data_dirs)
        if patch is not None:
            result = apply_patch(prepared.stage, patch)
            if not result.ok:
                header = f"# patch {patch.name} does not apply, diff shows the unpatched build: {result.output}\n"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pending.patch"
            if target.is_dir() and not target.is_symlink():
                base = target
            else:
                base = Path(tmp) / "empty"
                base.mkdir()
            changed = capture_patch(base, prepared.stage, out)
            return header + (out.read_text() if changed else "")
    finally:
        _clear(stage)


def capture_dir(name: str, manifest: Manifest) -> Path:
    """Where a captured patch belongs: beside the skill's notes, else tracked."""
    for data_dir in manifest.data_dirs:
        if (data_dir / "notes" / f"{name}.md").is_file():
            return data_dir
    return manifest.data_dirs[-1]


def capture_skill(entry: SkillEntry, manifest: Manifest, today: str) -> tuple[int, Path]:
    """Diff the mechanical build against the installed copy into a patch file."""
    name = entry.name
    target = target_for(manifest, name)
    if not target.is_dir() or target.is_symlink():
        raise InstallError(f"{target} is not an installed skill directory, build it first")
    check_root = stage_root(manifest.codex_home) / CHECK_DIRNAME
    stage = check_root / name
    try:
        prepared = prepare_stage(entry, manifest, today, check_root)
        out = capture_dir(name, manifest) / "patches" / f"{name}.patch"
        return capture_patch(prepared.stage, target, out), out
    finally:
        _clear(stage)
