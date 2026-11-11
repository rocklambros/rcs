"""Fixture helpers for the Codex port tests.

Version 0.1.0, owner Rock Lambros.

Everything here builds synthetic skills, manifests, and archives under a
pytest ``tmp_path`` so no test reads or writes the real home directory.
"""
from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

MINIMAL_SKILL_MD = "---\nname: a-skill\ndescription: Does a thing. Use when asked.\n---\n\n# A skill\n\nBody.\n"

# RCS Layer-3 shape: Anthropic fields plus six custom top-level fields and
# a track-prefixed sibling reference in the body.
RCS_SKILL_MD = """---
name: a-skill
description: Does a thing for a test. Use when a test asks for it.
version: 0.1.0
status: shipped
track: workflow
audience: [skill-author]
evidence: [RCS]
last-updated: 2026-05-24
---

# A skill

See `workflow/other-skill` and `security/third-skill` (planned).

## See also

- `scripts/x.py` is not a sibling reference.
"""

# claude.ai upload shape: loose top-level fields and path placeholder
# tokens the model is told to expand.
CLAUDE_SKILL_MD = """---
name: a-skill
description: Does a thing for a test. Use when a test asks for it.
version: 0.1 (draft)
owner: Rock
---

# A skill

Run the linter first:

```
python3 -I SKILL_DIR/scripts/l.py DRAFT
python3 -I SKILLS/a-skill/scripts/x.py DRAFT
```

`SKILLS` stands for the folder that holds this skill's folder.
"""


def make_skill_dir(root: Path, name: str, skill_md: str, extra: dict[str, str] | None = None) -> Path:
    """Create ``root/<name>/SKILL.md`` plus any extra relative files."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_md)
    for rel, content in (extra or {}).items():
        target = skill_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    return skill_dir


def make_zip(path: Path, top_folder: str, files: dict[str, str], extra_members: dict[str, str] | None = None) -> Path:
    """Write a zip whose ``files`` sit under ``top_folder/``.

    Member names are written verbatim, so a test can plant a traversal
    such as ``../../evil.txt`` to prove the extractor rejects it.
    ``extra_members`` are written with no prefix, for a second top-level
    folder.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        for rel, content in files.items():
            archive.writestr(f"{top_folder}/{rel}", content)
        for rel, content in (extra_members or {}).items():
            archive.writestr(rel, content)
    return path


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
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
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


@dataclass
class PortEnv:
    """Paths of a self-contained port environment under one tmp_path."""

    manifest_path: Path
    data_dir: Path
    codex_home: Path
    rcs_root: Path
    cache_roots: dict[str, Path]

    @property
    def skills_root(self) -> Path:
        return self.codex_home / "skills"


def make_port_env(tmp_path: Path, skills: dict, notes: str = "- sibling note\n") -> PortEnv:
    """Write a manifest plus a default notes file and return every path."""
    data_dir = tmp_path / "data"
    (data_dir / "notes").mkdir(parents=True, exist_ok=True)
    (data_dir / "notes" / "_default.md").write_text(notes)
    defaults = defaults_for(tmp_path)
    manifest_path = write_manifest(data_dir / "manifest.toml", defaults, skills)
    return PortEnv(
        manifest_path=manifest_path,
        data_dir=data_dir,
        codex_home=Path(defaults["codex_home"]),
        rcs_root=Path(defaults["rcs_root"]),
        cache_roots={profile: Path(path) for profile, path in defaults["cache_roots"].items()},
    )
