"""Lint SKILL.md body for required Layer-3 H2 sections and length cap."""
from __future__ import annotations
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click


REQUIRED_SECTIONS_IN_ORDER = [
    "When to use",
    "When NOT to use",
    "Quick start",
    "Inputs / Arguments / Flags",
    "Workflow",
    "Outputs",
    "Failure modes",
    "References",
    "Examples",
    "See also",
    "Status & version",
]
MAX_BODY_LINES = 500
H2_PATTERN = re.compile(r"^## (.+?)\s*$", re.MULTILINE)


@dataclass
class LintError:
    message: str
    line: Optional[int] = None

    def format(self, path: Path) -> str:
        loc = f"{path}:{self.line}" if self.line else str(path)
        return f"{loc}: {self.message}"


def split_frontmatter_and_body(text: str) -> tuple[str, str]:
    """Return (frontmatter_block, body). Body excludes frontmatter."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end < 0:
        return "", text
    return text[4:end], text[end + 5 :]


def lint_skill_md(path: Path) -> list[LintError]:
    text = path.read_text()
    _, body = split_frontmatter_and_body(text)
    errors: list[LintError] = []

    body_line_count = len(body.splitlines())
    if body_line_count > MAX_BODY_LINES:
        errors.append(LintError(
            f"body is {body_line_count} lines; must be ≤ {MAX_BODY_LINES} lines "
            f"(move long content to reference/ files)"
        ))

    found = H2_PATTERN.findall(body)

    for required in REQUIRED_SECTIONS_IN_ORDER:
        if required not in found:
            errors.append(LintError(f"missing required H2 section: '## {required}'"))

    required_indices = [
        (s, found.index(s)) for s in REQUIRED_SECTIONS_IN_ORDER if s in found
    ]
    for i in range(1, len(required_indices)):
        prev_name, prev_idx = required_indices[i - 1]
        curr_name, curr_idx = required_indices[i]
        if curr_idx < prev_idx:
            errors.append(LintError(
                f"section '## {curr_name}' appears before '## {prev_name}' but "
                f"must appear after it (required order: {REQUIRED_SECTIONS_IN_ORDER})"
            ))
            break

    return errors


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
def main(paths: tuple[Path, ...]) -> None:
    if not paths:
        click.echo("usage: lint_skill_md <SKILL.md>...", err=True)
        sys.exit(2)
    total = 0
    for path in paths:
        errors = lint_skill_md(path)
        for err in errors:
            click.echo(err.format(path), err=True)
            total += 1
    if total:
        click.echo(f"\n{total} SKILL.md body error(s) across {len(paths)} file(s)", err=True)
        sys.exit(1)
    click.echo(f"OK ({len(paths)} file(s))")


if __name__ == "__main__":
    main()
