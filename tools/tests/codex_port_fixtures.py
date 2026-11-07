"""Fixture helpers for the Codex port tests.

Version 0.1.0, owner Rock Lambros.

Everything here builds synthetic skills, manifests, and archives under a
pytest ``tmp_path`` so no test reads or writes the real home directory.
"""
from __future__ import annotations

from pathlib import Path


def defaults_for(tmp_path: Path) -> dict:
    """A ``[defaults]`` block whose every path lives under ``tmp_path``."""
    return {
        "codex_home": str(tmp_path / "codex"),
        "rcs_root": str(tmp_path / "rcs"),
        "cache_roots": {
            "Claude": str(tmp_path / "cache-claude"),
            "Claude-Zenity": str(tmp_path / "cache-zenity"),
        },
    }


def entry(name: str, source: dict, **picker) -> dict:
    """A manifest skill entry with valid picker text unless overridden.

    The default short description is exactly 30 characters, inside the
    25 to 64 window Codex enforces, so a test that wants a failure has to
    ask for one explicitly.
    """
    data = {
        "source": source,
        "display_name": name.replace("-", " ").title(),
        "short_description": "Does one thing well for a test",
        "default_prompt": f"Use ${name} to do the thing.",
    }
    data.update(picker)
    return data


def _toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _toml_string(value)
    if isinstance(value, dict):
        inner = ", ".join(f"{k} = {_toml_value(v)}" for k, v in value.items())
        return "{ " + inner + " }"
    raise TypeError(f"unsupported manifest value: {value!r}")


def write_manifest(path: Path, defaults: dict, skills: dict) -> Path:
    """Serialize the manifest dict shape as TOML by hand.

    The repository has no TOML writer dependency and does not need one for
    a fixture, so this emits the small subset the loader reads: scalar
    defaults, one nested ``[defaults.<table>]`` per dict default, and one
    ``[skills.<name>]`` table per entry with inline-table sources.
    """
    lines = ["[defaults]"]
    for key, value in defaults.items():
        if not isinstance(value, dict):
            lines.append(f"{key} = {_toml_value(value)}")
    for key, value in defaults.items():
        if isinstance(value, dict):
            lines.append(f"[defaults.{key}]")
            for sub_key, sub_value in value.items():
                lines.append(f"{sub_key} = {_toml_value(sub_value)}")
    for name, data in skills.items():
        lines.append(f"[skills.{name}]")
        for key, value in data.items():
            lines.append(f"{key} = {_toml_value(value)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    return path
