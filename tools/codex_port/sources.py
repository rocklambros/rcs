"""Source materialization and tree hashing for the Codex skill port.

Version 0.1.0, owner Rock Lambros.

A ``SourceSpec`` names where a skill lives. ``materialize`` copies that
skill into a staging directory so every later step works on one layout
regardless of origin. ``tree_sha256`` fingerprints a tree by path and
content, with no timestamps, so two builds from unchanged sources hash
the same and drift is a hash comparison.
"""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

from tools.codex_port.manifest import Manifest, SourceSpec

IGNORED_NAMES = frozenset({"__pycache__", ".DS_Store", "__MACOSX"})


class SourceError(Exception):
    """A source could not be found, read, or trusted."""


def is_ignored(name: str) -> bool:
    # Dotfiles cover editor state, the port's own sidecar, and macOS
    # resource forks (``._x``) inside zips.
    return name in IGNORED_NAMES or name.startswith(".")


def _copytree_ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if is_ignored(name)}


def tree_sha256(root: Path) -> str:
    """Hash every non-ignored file under ``root`` by relative path and bytes."""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root)
        if any(is_ignored(part) for part in rel.parts):
            continue
        digest.update(rel.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def resolve_cache_dir(cache_root: Path, name: str, profile: str | None = None) -> Path:
    """Newest ``*/*/skills/<name>/`` under a Claude desktop profile root.

    The two path segments are session UUIDs the desktop app reassigns, so
    the glob is the only stable way to find the live copy.
    """
    matches = list(cache_root.glob(f"*/*/skills/{name}/SKILL.md"))
    if not matches:
        where = f"profile {profile!r} ({cache_root})" if profile else str(cache_root)
        raise SourceError(f"skill {name!r}: no copy under {where}")
    newest = max(matches, key=lambda p: p.stat().st_mtime)
    return newest.parent


def _copy_dir(src: Path, name: str, dest: Path) -> Path:
    if not (src / "SKILL.md").is_file():
        raise SourceError(f"skill {name!r}: no SKILL.md under {src}")
    target = dest / name
    try:
        shutil.copytree(src, target, symlinks=False, ignore=_copytree_ignore)
    except FileExistsError as exc:
        raise SourceError(f"skill {name!r}: staging directory {target} already exists") from exc
    return target


def _extract_zip(archive: Path, name: str, dest: Path) -> Path:
    if not archive.is_file():
        raise SourceError(f"skill {name!r}: zip {archive} does not exist")
    dest.mkdir(parents=True, exist_ok=True)
    dest_resolved = dest.resolve()
    with zipfile.ZipFile(archive) as zf:
        members = [m for m in zf.infolist() if not m.is_dir()]
        # Trust checks run before the ignore filter, otherwise ``..`` would
        # count as a dotfile and a traversal member would be skipped in
        # silence instead of rejected out loud.
        for member in members:
            parts = Path(member.filename).parts
            if member.filename.startswith("/") or ".." in parts or not (dest / member.filename).resolve().is_relative_to(dest_resolved):
                raise SourceError(f"skill {name!r}: zip member {member.filename!r} escapes the extraction directory")
        top_levels = {Path(m.filename).parts[0] for m in members}
        top_levels = {t for t in top_levels if not is_ignored(t)}
        if top_levels != {name}:
            raise SourceError(
                f"skill {name!r}: zip {archive.name} must hold exactly one top-level folder named {name!r}, "
                f"found {sorted(top_levels)}"
            )
        for member in members:
            if any(is_ignored(part) for part in Path(member.filename).parts):
                continue
            target = dest / member.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, target.open("wb") as out:
                shutil.copyfileobj(src, out)
    return dest / name


def materialize(spec: SourceSpec, name: str, manifest: Manifest, dest: Path) -> Path:
    """Copy the skill named ``name`` from ``spec`` into ``dest/<name>``."""
    dest.mkdir(parents=True, exist_ok=True)
    if spec.kind == "rcs":
        src = manifest.rcs_root / spec.track / name
        if not src.is_dir():
            raise SourceError(f"skill {name!r}: no RCS source at {src}")
        return _copy_dir(src, name, dest)
    if spec.kind == "claude_ai":
        return _copy_dir(resolve_cache_dir(manifest.cache_roots[spec.profile], name, spec.profile), name, dest)
    if spec.kind == "dir":
        src = spec.path
        if src.name != name:
            raise SourceError(f"skill {name!r}: source directory is named {src.name!r}, expected {name!r}")
        if not src.is_dir():
            raise SourceError(f"skill {name!r}: source directory {src} does not exist")
        return _copy_dir(src, name, dest)
    if spec.kind == "zip":
        return _extract_zip(spec.path, name, dest)
    raise SourceError(f"skill {name!r}: unsupported source kind {spec.kind!r}")
