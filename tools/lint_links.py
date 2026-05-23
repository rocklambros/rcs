"""Lint that SKILL.md references stay one level deep per Anthropic best-practices."""
from __future__ import annotations
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import click


MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass
class LintError:
    message: str
    line: Optional[int] = None

    def format(self, path: Path) -> str:
        loc = f"{path}:{self.line}" if self.line else str(path)
        return f"{loc}: {self.message}"


def extract_local_links(text: str, base_dir: Path) -> list[tuple[str, Path]]:
    """Return list of (display_text, resolved_path) for non-URL markdown links."""
    out: list[tuple[str, Path]] = []
    for match in MARKDOWN_LINK.finditer(text):
        display, target = match.group(1), match.group(2)
        parsed = urlparse(target)
        if parsed.scheme in ("http", "https", "mailto"):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path:
            continue
        resolved = (base_dir / target_path).resolve()
        out.append((display, resolved))
    return out


def lint_links(skill_dir: Path) -> list[LintError]:
    """Lint a single skill directory (containing SKILL.md and reference/)."""
    errors: list[LintError] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(LintError(f"SKILL.md not found in {skill_dir}"))
        return errors

    skill_links = extract_local_links(skill_md.read_text(), skill_dir)
    level_one_files: set[Path] = set()
    for display, target in skill_links:
        if not target.exists():
            errors.append(LintError(f"broken reference: SKILL.md → {target}", None))
            continue
        if not target.is_relative_to(skill_dir.resolve()):
            errors.append(LintError(
                f"reference escapes skill directory: SKILL.md → {target}"
            ))
            continue
        if target.suffix == ".md":
            level_one_files.add(target)

    for ref_file in level_one_files:
        sub_links = extract_local_links(ref_file.read_text(), ref_file.parent)
        for display, target in sub_links:
            if target.exists() and target.suffix == ".md" and target.is_relative_to(skill_dir.resolve()):
                if target.resolve() in {skill_md.resolve(), ref_file.resolve()}:
                    continue
                errors.append(LintError(
                    f"two-level-deep reference: SKILL.md → {ref_file.name} → {target.name}; "
                    f"links must be one level deep from SKILL.md"
                ))

    return errors


@click.command()
@click.argument("skill_dirs", nargs=-1, type=click.Path(exists=True, file_okay=False, path_type=Path))
def main(skill_dirs: tuple[Path, ...]) -> None:
    if not skill_dirs:
        click.echo("usage: lint_links <skill-directory>...", err=True)
        sys.exit(2)
    total = 0
    for d in skill_dirs:
        errors = lint_links(d)
        for err in errors:
            click.echo(err.format(d), err=True)
            total += 1
    if total:
        click.echo(f"\n{total} link error(s) across {len(skill_dirs)} skill(s)", err=True)
        sys.exit(1)
    click.echo(f"OK ({len(skill_dirs)} skill(s))")


if __name__ == "__main__":
    main()
