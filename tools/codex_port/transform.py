"""Transform layer for the Codex skill port.

Version 0.1.0, owner Rock Lambros.

Turns a skill as its source wrote it into a skill Codex will load:
frontmatter limited to the keys Codex allows, provenance recorded under
``metadata``, and (in later functions of this module) body rewrites for
sibling references, path tokens, and the runtime-notes section.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from tools.codex_port.manifest import Manifest, SkillEntry
from tools.lint_frontmatter import parse_frontmatter

ALLOWED_TOP_LEVEL = ("name", "description", "license", "allowed-tools", "metadata")
PROVENANCE_KEYS = ("ported-from", "ported-to-codex")
FRONTMATTER_END = "\n---\n"
# RCS skills name siblings as `<track>/<name>`. Codex invokes a skill as
# `$<name>`, so the track prefix goes and the dollar sign comes in.
SIBLING_REF = re.compile(r"`(workflow|claude-code-meta|ml-datasci|security|teaching)/([a-z0-9-]+)`")
RUNTIME_NOTES_HEADING = "## Codex runtime notes"
DEFAULT_NOTES = "_default.md"


class TransformError(Exception):
    """A source cannot be transformed. The fix belongs at the source."""


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the frontmatter mapping and return it with the untouched body."""
    data, errors = parse_frontmatter(text)
    if data is None:
        raise TransformError(errors[0].message)
    end = text.find(FRONTMATTER_END, 4)
    return data, text[end + len(FRONTMATTER_END):]


def normalize_frontmatter(text: str, ported_from: str, ported_on: str) -> str:
    """Rewrite the frontmatter for Codex and leave the body byte-identical.

    Key order is fixed so a rebuild from unchanged sources is byte-identical:
    ``name``, ``description``, other allowed keys in source order, then
    ``metadata`` holding the source's own metadata first, the moved keys in
    source order, and the two provenance keys last.
    """
    data, body = split_frontmatter(text)
    for key in ("name", "description"):
        if key not in data:
            raise TransformError(f"frontmatter is missing {key}")
    existing = data.get("metadata") or {}
    if not isinstance(existing, dict):
        raise TransformError("frontmatter metadata must be a mapping")
    # Drop stale provenance so normalizing an already-ported file converges.
    metadata = {key: value for key, value in existing.items() if key not in PROVENANCE_KEYS}
    ordered: dict = {"name": data["name"], "description": data["description"]}
    for key, value in data.items():
        if key in ("name", "description", "metadata"):
            continue
        if key in ALLOWED_TOP_LEVEL:
            ordered[key] = value
        else:
            metadata[key] = value
    metadata["ported-from"] = ported_from
    metadata["ported-to-codex"] = ported_on
    ordered["metadata"] = metadata
    # A huge width keeps long descriptions on one line, so a reflow never
    # shows up as a diff and grep finds the whole sentence.
    dumped = yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, width=1_000_000)
    return f"---\n{dumped}---\n{body}"


def rewrite_sibling_refs(text: str) -> str:
    """Turn backticked ``<track>/<name>`` references into ``$<name>``."""
    return SIBLING_REF.sub(r"`$\2`", text)


def rewrite_path_tokens(text: str, skills_root: Path, name: str) -> str:
    """Pin the claude.ai placeholder tokens to absolute install paths.

    Only the slash-suffixed forms change. A bare ``SKILLS`` or ``SKILL_DIR``
    in prose is the sentence that explains the token, and a patch rewrites
    that sentence in Codex terms.
    """
    root = skills_root.as_posix()
    return text.replace("SKILL_DIR/", f"{root}/{name}/").replace("SKILLS/", f"{root}/")


def append_runtime_notes(text: str, notes_body: str) -> str:
    """Append the runtime-notes section exactly once."""
    if RUNTIME_NOTES_HEADING in text:
        raise TransformError(f"SKILL.md already contains a '{RUNTIME_NOTES_HEADING}' section")
    base = text if text.endswith("\n") else text + "\n"
    body = notes_body.rstrip("\n")
    return f"{base}\n{RUNTIME_NOTES_HEADING}\n\n{body}\n"


def load_notes(name: str, data_dirs: tuple[Path, ...]) -> str:
    """First ``notes/<name>.md`` across the data dirs, else the first default."""
    for data_dir in data_dirs:
        candidate = data_dir / "notes" / f"{name}.md"
        if candidate.is_file():
            return candidate.read_text()
    for data_dir in data_dirs:
        candidate = data_dir / "notes" / DEFAULT_NOTES
        if candidate.is_file():
            return candidate.read_text()
    searched = ", ".join(str(d / "notes") for d in data_dirs) or "(no data dirs)"
    raise TransformError(f"skill {name!r}: no notes/{name}.md and no notes/{DEFAULT_NOTES} under {searched}")


def transform_tree(skill_dir: Path, entry: SkillEntry, manifest: Manifest, ported_on: str) -> None:
    """Apply every mechanical transform in place on a materialized skill."""
    skills_root = manifest.codex_home / "skills"
    skill_md = skill_dir / "SKILL.md"
    notes = load_notes(entry.name, manifest.data_dirs)
    normalized = normalize_frontmatter(skill_md.read_text(), entry.source.label(entry.name), ported_on)
    for markdown in sorted(skill_dir.rglob("*.md")):
        content = normalized if markdown == skill_md else markdown.read_text()
        content = rewrite_sibling_refs(content)
        if entry.path_tokens:
            content = rewrite_path_tokens(content, skills_root, entry.name)
        if markdown == skill_md:
            content = append_runtime_notes(content, notes)
        markdown.write_text(content)


PICKER_KEYS = ("display_name", "short_description", "default_prompt")


def _yaml_double_quoted(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_picker(skill_dir: Path, entry: SkillEntry) -> Path:
    """Write ``agents/openai.yaml`` in the exact shape the September port used.

    Hand-formatted rather than dumped by PyYAML so the file stays byte-stable
    and readable, with the three keys in the order the Codex picker shows them.
    """
    target = skill_dir / "agents" / "openai.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = ["interface:"] + [f"  {key}: {_yaml_double_quoted(getattr(entry, key))}" for key in PICKER_KEYS]
    target.write_text("\n".join(lines) + "\n")
    return target
