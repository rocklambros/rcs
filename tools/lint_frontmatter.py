"""Lint Anthropic-required + RCS-custom frontmatter fields in a SKILL.md."""
from __future__ import annotations
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click
import yaml


RESERVED_NAME_WORDS = {"anthropic", "claude"}
VALID_STATUSES = {"shipped", "drafting", "planned", "deprecated"}
VALID_TRACKS = {"security", "ml-datasci", "workflow", "teaching", "claude-code-meta"}
FIRST_PERSON_PATTERN = re.compile(
    r"\b(I |I'll |I can |I will |you can |you'll |we |we'll )",
    re.IGNORECASE,
)


@dataclass
class LintError:
    message: str
    line: Optional[int] = None

    def format(self, path: Path) -> str:
        loc = f"{path}:{self.line}" if self.line else str(path)
        return f"{loc}: {self.message}"


def parse_frontmatter(text: str) -> tuple[Optional[dict], list[LintError]]:
    """Extract YAML frontmatter block. Returns (data, errors)."""
    if not text.startswith("---\n"):
        return None, [LintError("file does not start with '---' frontmatter delimiter")]
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, [LintError("frontmatter block not closed (missing trailing '---')")]
    fm_block = text[4:end]
    try:
        data = yaml.safe_load(fm_block)
    except yaml.YAMLError as e:
        return None, [LintError(f"YAML parse error in frontmatter: {e}")]
    if not isinstance(data, dict):
        return None, [LintError("frontmatter must be a YAML mapping")]
    return data, []


def lint_frontmatter(path: Path) -> list[LintError]:
    """Return a list of LintErrors. Empty list = pass."""
    text = path.read_text()
    data, errs = parse_frontmatter(text)
    if data is None:
        return errs
    errors: list[LintError] = []

    # name
    name = data.get("name")
    if not name:
        errors.append(LintError("missing required field 'name'"))
    else:
        if not isinstance(name, str):
            errors.append(LintError("'name' must be a string"))
        else:
            if len(name) > 64:
                errors.append(LintError(f"'name' is {len(name)} chars; must be ≤ 64 characters"))
            if name != name.lower():
                errors.append(LintError("'name' must be lowercase (lowercase-kebab)"))
            if not re.fullmatch(r"[a-z0-9-]+", name):
                errors.append(LintError("'name' must contain only lowercase letters, digits, hyphens"))
            for reserved in RESERVED_NAME_WORDS:
                if reserved in name.lower():
                    errors.append(LintError(f"'name' contains reserved word '{reserved}'"))

    # description
    desc = data.get("description")
    if not desc:
        errors.append(LintError("missing required field 'description'"))
    elif not isinstance(desc, str):
        errors.append(LintError("'description' must be a string"))
    else:
        if len(desc) > 1024:
            errors.append(LintError(f"'description' is {len(desc)} chars; must be ≤ 1024 characters"))
        if FIRST_PERSON_PATTERN.search(desc):
            errors.append(LintError(
                "'description' contains first/second-person language; must be third-person "
                "(write 'Walks a decision tree...', not first or second person)"
            ))

    # version
    version = data.get("version")
    if not version:
        errors.append(LintError("missing required field 'version'"))
    elif not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(LintError(f"'version' must be SemVer (e.g. '0.1.0'); got {version!r}"))

    # status
    status = data.get("status")
    if not status:
        errors.append(LintError("missing required field 'status'"))
    elif status not in VALID_STATUSES:
        errors.append(LintError(
            f"'status' must be one of {sorted(VALID_STATUSES)}; got {status!r}"
        ))

    # track
    track = data.get("track")
    if not track:
        errors.append(LintError("missing required field 'track'"))
    elif track not in VALID_TRACKS:
        errors.append(LintError(
            f"'track' must be one of {sorted(VALID_TRACKS)}; got {track!r}"
        ))

    # audience
    audience = data.get("audience")
    if audience is None:
        errors.append(LintError("missing required field 'audience'"))
    elif not isinstance(audience, list) or not all(isinstance(a, str) for a in audience):
        errors.append(LintError("'audience' must be a list of strings"))

    # evidence
    evidence = data.get("evidence")
    if evidence is None:
        errors.append(LintError("missing required field 'evidence'"))
    elif not isinstance(evidence, list) or not all(isinstance(e, str) for e in evidence):
        errors.append(LintError("'evidence' must be a list of strings"))

    # last-updated
    last_updated = data.get("last-updated")
    if not last_updated:
        errors.append(LintError("missing required field 'last-updated'"))
    elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(last_updated)):
        errors.append(LintError(
            f"'last-updated' must be ISO date YYYY-MM-DD; got {last_updated!r}"
        ))

    return errors


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
def main(paths: tuple[Path, ...]) -> None:
    """Lint frontmatter for one or more SKILL.md files."""
    if not paths:
        click.echo("usage: lint_frontmatter <SKILL.md>...", err=True)
        sys.exit(2)
    total = 0
    for path in paths:
        errors = lint_frontmatter(path)
        for err in errors:
            click.echo(err.format(path), err=True)
            total += 1
    if total:
        click.echo(f"\n{total} frontmatter error(s) across {len(paths)} file(s)", err=True)
        sys.exit(1)
    click.echo(f"OK ({len(paths)} file(s))")


if __name__ == "__main__":
    main()
