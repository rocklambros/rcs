"""Command line for the Codex skill port.

Version 0.1.0, owner Rock Lambros.

Builds the skills named in ``tools/codex_port/manifest.toml`` (plus the
gitignored ``local/manifest.toml`` overlay when present) into the Codex
skills directory the ChatGPT app reads, and reports drift on demand.

    uv run python -m tools.port_to_codex build
    uv run python -m tools.port_to_codex check
    uv run python -m tools.port_to_codex diff NAME
    uv run python -m tools.port_to_codex capture NAME

Exit codes: 0 every skill ok, 1 any skill failed or stale, 2 manifest or
usage error.
"""
from __future__ import annotations

import dataclasses
from datetime import date
from pathlib import Path

import click

from tools.codex_port.install import InstallError
from tools.codex_port.manifest import Manifest, ManifestError, SkillEntry, load_manifest
from tools.codex_port.pipeline import build_skill, capture_skill, check_skill, diff_skill
from tools.codex_port.validate import ToolchainError

PACKAGE_DIR = Path(__file__).resolve().parent / "codex_port"
DEFAULT_MANIFEST = PACKAGE_DIR / "manifest.toml"
DEFAULT_LOCAL_MANIFEST = PACKAGE_DIR / "local" / "manifest.toml"
EXIT_OK = 0
EXIT_STALE = 1
EXIT_USAGE = 2


@click.group()
@click.option("--manifest", "manifest_path", type=click.Path(path_type=Path), default=DEFAULT_MANIFEST, show_default=True,
              help="Tracked manifest.")
@click.option("--local-manifest", type=click.Path(path_type=Path), default=DEFAULT_LOCAL_MANIFEST, show_default=True,
              help="Gitignored overlay for private skills, used only when it exists.")
@click.option("--codex-home", type=click.Path(path_type=Path), default=None, help="Override defaults.codex_home.")
@click.pass_context
def main(ctx: click.Context, manifest_path: Path, local_manifest: Path, codex_home: Path | None) -> None:
    """Port claude.ai and RCS skills into the Codex skills directory."""
    ctx.obj = {"manifest_path": manifest_path, "local_manifest": local_manifest, "codex_home": codex_home}


def _manifest(ctx: click.Context) -> Manifest:
    try:
        manifest = load_manifest(ctx.obj["manifest_path"], ctx.obj["local_manifest"])
    except ManifestError as exc:
        click.echo(f"error: {exc}", err=True)
        ctx.exit(EXIT_USAGE)
    if ctx.obj["codex_home"] is not None:
        manifest = dataclasses.replace(manifest, codex_home=ctx.obj["codex_home"].expanduser().resolve())
    return manifest


def _select(ctx: click.Context, manifest: Manifest, only: tuple[str, ...]) -> list[SkillEntry]:
    unknown = [name for name in only if name not in manifest.skills]
    if unknown:
        click.echo(f"error: unknown skill(s): {', '.join(unknown)}", err=True)
        ctx.exit(EXIT_USAGE)
    names = list(only) if only else list(manifest.skills)
    return [manifest.skills[name] for name in names]


def _today() -> str:
    return date.today().isoformat()


def _row(name: str, status: str, message: str) -> None:
    click.echo(f"{name}  {status}  {message}")


@main.command()
@click.option("--only", multiple=True, metavar="NAME", help="Build only these skills. Repeatable.")
@click.option("--force", is_flag=True, help="Replace an installed copy that was edited after its last build.")
@click.pass_context
def build(ctx: click.Context, only: tuple[str, ...], force: bool) -> None:
    """Build and install the manifest skills."""
    manifest = _manifest(ctx)
    today = _today()
    all_ok = True
    for entry in _select(ctx, manifest, only):
        try:
            result = build_skill(entry, manifest, force=force, today=today)
        except ToolchainError as exc:
            click.echo(f"error: {exc}", err=True)
            ctx.exit(EXIT_STALE)
        _row(result.name, "ok" if result.ok else "failed", result.message)
        all_ok = all_ok and result.ok
    ctx.exit(EXIT_OK if all_ok else EXIT_STALE)


@main.command()
@click.option("--only", multiple=True, metavar="NAME", help="Check only these skills. Repeatable.")
@click.pass_context
def check(ctx: click.Context, only: tuple[str, ...]) -> None:
    """Report drift between sources, port data, and the installed skills."""
    manifest = _manifest(ctx)
    today = _today()
    all_ok = True
    for entry in _select(ctx, manifest, only):
        try:
            report = check_skill(entry, manifest, today=today)
        except ToolchainError as exc:
            click.echo(f"error: {exc}", err=True)
            ctx.exit(EXIT_STALE)
        _row(report.name, report.status.value, report.details)
        for line in report.info:
            click.echo(f"    info: {line}")
        all_ok = all_ok and report.status.value == "ok"
    ctx.exit(EXIT_OK if all_ok else EXIT_STALE)


@main.command()
@click.argument("name")
@click.pass_context
def diff(ctx: click.Context, name: str) -> None:
    """Show what build would change for one skill."""
    manifest = _manifest(ctx)
    entry = _select(ctx, manifest, (name,))[0]
    text = diff_skill(entry, manifest, today=_today())
    if text:
        click.echo(text, nl=False)
    else:
        _row(name, "ok", "no changes pending")


@main.command()
@click.argument("name")
@click.pass_context
def capture(ctx: click.Context, name: str) -> None:
    """Save hand edits in the installed copy as that skill's patch file.

    Build first, edit the installed skill, then capture. The patch lands
    beside the skill's notes (local overlay or tracked).
    """
    manifest = _manifest(ctx)
    entry = _select(ctx, manifest, (name,))[0]
    try:
        changed, out = capture_skill(entry, manifest, today=_today())
    except InstallError as exc:
        click.echo(f"error: {exc}", err=True)
        ctx.exit(EXIT_STALE)
    if changed == 0:
        _row(name, "ok", "no differences, nothing written")
    else:
        _row(name, "captured", f"{changed} file(s) -> {out}")


if __name__ == "__main__":
    main()
