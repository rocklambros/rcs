"""Manifest loading for the Codex skill port.

Version 0.1.0, owner Rock Lambros.

The manifest is TOML. A tracked file lists the public skills, and an
optional gitignored local file overlays private ones. Entry validation
mirrors the rules Codex's own ``quick_validate.py`` applies at install
time, so a bad entry fails here, before any file is written.
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
MAX_NAME_LENGTH = 64
SHORT_DESCRIPTION_MIN = 25
SHORT_DESCRIPTION_MAX = 64
SOURCE_KINDS = ("rcs", "claude_ai", "zip", "dir")
PICKER_FIELDS = ("display_name", "short_description", "default_prompt")
REQUIRED_DEFAULTS = ("codex_home", "rcs_root", "cache_roots")


class ManifestError(Exception):
    """Any problem with the manifest files. The CLI maps this to exit 2."""


def abbreviate_home(path: Path) -> str:
    """Render ``path`` with the home directory as ``~``.

    Provenance strings land in installed files that may be compared across
    machines, so the user name must not appear in them.
    """
    home = Path.home().resolve()
    try:
        return "~/" + path.resolve().relative_to(home).as_posix()
    except ValueError:
        return path.as_posix()


@dataclass(frozen=True)
class SourceSpec:
    kind: str
    track: str | None = None
    profile: str | None = None
    path: Path | None = None

    def label(self, name: str) -> str:
        """Stable provenance string, written to metadata and the sidecar."""
        if self.kind == "rcs":
            return f"rcs:{self.track}/{name}"
        if self.kind == "claude_ai":
            return f"claude.ai:{self.profile}/{name}"
        return f"{self.kind}:{abbreviate_home(self.path)}"


@dataclass(frozen=True)
class SkillEntry:
    name: str
    source: SourceSpec
    display_name: str
    short_description: str
    default_prompt: str
    path_tokens: bool = False


@dataclass(frozen=True)
class Manifest:
    codex_home: Path
    cache_roots: dict[str, Path]
    rcs_root: Path
    skills: dict[str, SkillEntry]
    data_dirs: tuple[Path, ...]
    # Relative paths whose hand edits capture must refuse to turn into a
    # tracked patch, such as a references file that holds published text.
    capture_exclude: tuple[str, ...] = ()


def _read_toml(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ManifestError(f"{path}: {exc}") from exc


def _expand(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _parse_source(name: str, raw: object, cache_roots: dict[str, Path]) -> SourceSpec:
    if not isinstance(raw, dict) or "kind" not in raw:
        raise ManifestError(f"skill {name!r}: source needs a kind")
    kind = raw["kind"]
    if kind not in SOURCE_KINDS:
        raise ManifestError(f"skill {name!r}: unknown source kind {kind!r}, expected one of {', '.join(SOURCE_KINDS)}")
    if kind == "rcs":
        if "track" not in raw:
            raise ManifestError(f"skill {name!r}: rcs source needs a track")
        return SourceSpec(kind="rcs", track=str(raw["track"]))
    if kind == "claude_ai":
        if "profile" not in raw:
            raise ManifestError(f"skill {name!r}: claude_ai source needs a profile")
        profile = str(raw["profile"])
        if profile not in cache_roots:
            raise ManifestError(f"skill {name!r}: profile {profile!r} is not a key of defaults.cache_roots")
        return SourceSpec(kind="claude_ai", profile=profile)
    if "path" not in raw:
        raise ManifestError(f"skill {name!r}: {kind} source needs a path")
    return SourceSpec(kind=kind, path=_expand(str(raw["path"])))


def _parse_entry(name: str, raw: object, cache_roots: dict[str, Path]) -> SkillEntry:
    if not NAME_PATTERN.match(name):
        raise ManifestError(f"skill {name!r}: name must match ^[a-z0-9-]+$")
    if len(name) > MAX_NAME_LENGTH:
        raise ManifestError(f"skill {name!r}: name is {len(name)} chars, the limit is {MAX_NAME_LENGTH}")
    if not isinstance(raw, dict):
        raise ManifestError(f"skill {name!r}: entry must be a table")
    for field_name in PICKER_FIELDS:
        if not isinstance(raw.get(field_name), str) or not raw[field_name]:
            raise ManifestError(f"skill {name!r}: missing {field_name}")
    short = raw["short_description"]
    if not SHORT_DESCRIPTION_MIN <= len(short) <= SHORT_DESCRIPTION_MAX:
        raise ManifestError(
            f"skill {name!r}: short_description is {len(short)} chars, "
            f"Codex requires {SHORT_DESCRIPTION_MIN} to {SHORT_DESCRIPTION_MAX}"
        )
    return SkillEntry(
        name=name,
        source=_parse_source(name, raw.get("source"), cache_roots),
        display_name=raw["display_name"],
        short_description=short,
        default_prompt=raw["default_prompt"],
        path_tokens=bool(raw.get("path_tokens", False)),
    )


def load_manifest(tracked: Path, local: Path | None) -> Manifest:
    """Load the tracked manifest and merge the local overlay over it.

    Overlay rules: ``[defaults]`` keys replace tracked keys one by one, and
    ``[skills.<name>]`` tables replace same-named tracked entries in place
    or append after them. ``data_dirs`` lists the overlay directory first
    so a local note or patch wins over a tracked one.
    """
    tracked_data = _read_toml(tracked)
    defaults = dict(tracked_data.get("defaults", {}))
    skills_raw: dict[str, object] = dict(tracked_data.get("skills", {}))
    data_dirs: tuple[Path, ...] = (tracked.parent,)

    if local is not None and local.exists():
        local_data = _read_toml(local)
        local_defaults = local_data.get("defaults", {})
        for key, value in local_defaults.items():
            if key == "cache_roots" and isinstance(value, dict):
                merged = dict(defaults.get("cache_roots", {}))
                merged.update(value)
                defaults["cache_roots"] = merged
            else:
                defaults[key] = value
        skills_raw.update(local_data.get("skills", {}))
        data_dirs = (local.parent, tracked.parent)

    for key in REQUIRED_DEFAULTS:
        if key not in defaults:
            raise ManifestError(f"defaults.{key} is missing")
    if not isinstance(defaults["cache_roots"], dict):
        raise ManifestError("defaults.cache_roots must be a table of profile = path")

    capture_exclude = defaults.get("capture_exclude", [])
    if not isinstance(capture_exclude, list) or not all(isinstance(item, str) for item in capture_exclude):
        raise ManifestError("defaults.capture_exclude must be a list of relative paths")

    cache_roots = {profile: _expand(str(path)) for profile, path in defaults["cache_roots"].items()}
    skills = {name: _parse_entry(name, raw, cache_roots) for name, raw in skills_raw.items()}
    return Manifest(
        codex_home=_expand(str(defaults["codex_home"])),
        cache_roots=cache_roots,
        rcs_root=_expand(str(defaults["rcs_root"])),
        skills=skills,
        data_dirs=data_dirs,
        capture_exclude=tuple(capture_exclude),
    )
