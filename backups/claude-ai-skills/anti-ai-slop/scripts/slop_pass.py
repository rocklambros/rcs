#!/usr/bin/env python3
"""slop_pass: one call runs the whole mechanical pass for anti-ai-slop.

Version 1.0.0, owner Rock Lambros.

One process call replaces three tool calls:
  1. clean_text.py (only with --clean-out): strip invisible Unicode into a new file
  2. slop_lint.py on the cleaned file, or on the input when there is no --clean-out
  3. inspect_text.py on the same file: Unicode inspection, plus the stylometry
     gauge unless --no-stylometry

Steps 2 and 3 run in parallel. The scripts themselves take about 0.1 s each, so
the saving is in model round trips and in report size, not CPU time.

Exit codes:
  0  no HARD findings
  1  HARD findings
  2  slop_pass could not run the lint (bad arguments, missing file, crash)

The clean-user-facing-text scripts are optional. When that skill isn't
installed next to this one, the Unicode and stylometry sections print a skip
line and the lint result still sets the exit code.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

__version__ = "1.0.0"

HERE = Path(__file__).resolve().parent
SLOP_LINT = HERE / "slop_lint.py"
# Skills install as sibling folders (synced/<id>/anti-ai-slop next to
# synced/<id>/clean-user-facing-text, or ~/.claude/skills/<name>), so the
# companion skill resolves relative to this skill's own folder.
DEFAULT_CLEAN_DIR = HERE.parent.parent / "clean-user-facing-text" / "scripts"
PROFILES = ("blog", "technical", "social", "email", "formal", "casual")
TIMEOUT_S = 60
# inspect_text.py prints a block of static "Note:" lines on every run. They
# never change, so dropping them keeps the report short for the reading model.
NOISE_PREFIXES = ("Note:", "=====")


@dataclass(frozen=True)
class Result:
    """Outcome of one child script. rc is None when the script never ran."""

    rc: int | None
    out: str
    err: str


def run(script: Path, args: list[str]) -> Result:
    """Run a sibling script under the same interpreter with -I.

    -I matches how the skills tell sessions to call each script: it keeps
    PYTHON* variables, user site-packages, and the working directory off the
    import path. No shell is involved, so paths with spaces are safe.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-I", str(script), *args],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return Result(None, "", f"timed out after {TIMEOUT_S} s")
    except OSError as exc:
        return Result(None, "", str(exc))
    return Result(proc.returncode, proc.stdout, proc.stderr)


def section(title: str) -> None:
    print(f"\n== {title} ==")


def report_clean(res: Result, out_path: Path) -> bool:
    """Print the clean pass in one line. Return True when OUT was written."""
    section("unicode clean")
    if res.rc != 0:
        print(f"FAILED (rc={res.rc}): {res.err.strip() or res.out.strip()}")
        print("Lint and inspection fall back to the input file.")
        return False
    # clean_text.py writes its --stats JSON to stderr, not stdout.
    raw = res.err.strip() or res.out.strip()
    try:
        stats = json.loads(raw)
        print(
            f"removed={stats.get('removed_count')} "
            f"replaced={stats.get('replaced_count')} -> {out_path}"
        )
    except json.JSONDecodeError:
        print(raw or f"wrote {out_path}")
    return True


def report_inspect(res: Result | None, verbose: bool) -> None:
    section("unicode + stylometry")
    if res is None:
        print("skipped: clean-user-facing-text scripts not found (use --clean-dir)")
        return
    # inspect_text exits 1 when the stylometry score crosses its threshold.
    # That is a reading, not a failure, so only other codes count as errors.
    if res.rc not in (0, 1):
        print(f"FAILED (rc={res.rc}): {res.err.strip() or res.out.strip()}")
        return
    for line in res.out.splitlines():
        if verbose or (line.strip() and not line.startswith(NOISE_PREFIXES)):
            print(line)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slop_pass",
        description="Lint, Unicode check, and stylometry gauge in one call.",
    )
    parser.add_argument("path", help="draft file (write pasted text to a file first)")
    parser.add_argument("--profile", choices=PROFILES, required=True)
    parser.add_argument(
        "--clean-out",
        metavar="OUT",
        help="strip invisible Unicode into OUT first, then lint and score OUT",
    )
    parser.add_argument(
        "--no-stylometry",
        action="store_true",
        help="Unicode inspection only, without the stylometry gauge",
    )
    parser.add_argument(
        "--include-quotes", action="store_true", help="passed through to slop_lint"
    )
    parser.add_argument(
        "--advisory-only",
        action="store_true",
        help="passed through to slop_lint: report HARD findings, exit 0",
    )
    parser.add_argument(
        "--clean-dir",
        type=Path,
        default=DEFAULT_CLEAN_DIR,
        help="folder holding clean_text.py and inspect_text.py",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print inspect_text's static notes too",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    source = Path(args.path).resolve()
    if not source.is_file():
        print(f"slop_pass: no such file: {source}", file=sys.stderr)
        return 2
    if not SLOP_LINT.is_file():
        print(f"slop_pass: slop_lint.py not found next to {__file__}", file=sys.stderr)
        return 2

    clean_dir = args.clean_dir.resolve()
    has_companion = all(
        (clean_dir / name).is_file() for name in ("clean_text.py", "inspect_text.py")
    )

    target = source
    if args.clean_out:
        out_path = Path(args.clean_out).resolve()
        # The skills prefer a new output file so the original stays intact.
        if out_path == source:
            print("slop_pass: --clean-out must name a new file, not the input", file=sys.stderr)
            return 2
        if has_companion:
            cleaned = run(
                clean_dir / "clean_text.py",
                [str(source), "-o", str(out_path), "--stats", "--no-normalize-spaces"],
            )
            if report_clean(cleaned, out_path):
                target = out_path
        else:
            section("unicode clean")
            print("skipped: clean-user-facing-text scripts not found (use --clean-dir)")

    lint_args = [str(target), "--profile", args.profile]
    if args.include_quotes:
        lint_args.append("--include-quotes")
    if args.advisory_only:
        lint_args.append("--advisory-only")
    inspect_args = [str(target)] if args.no_stylometry else ["--stylometry", str(target)]

    with ThreadPoolExecutor(max_workers=2) as pool:
        lint_job = pool.submit(run, SLOP_LINT, lint_args)
        inspect_job = (
            pool.submit(run, clean_dir / "inspect_text.py", inspect_args)
            if has_companion
            else None
        )
        lint = lint_job.result()
        inspect = inspect_job.result() if inspect_job else None

    section(f"slop_lint ({target.name})")
    if lint.rc not in (0, 1):
        # slop_lint uses 2 and 3 for "did not run". Surface its own message.
        print(f"FAILED (rc={lint.rc}): {lint.err.strip() or lint.out.strip()}")
        report_inspect(inspect, args.verbose)
        return 2
    print(lint.out.rstrip())

    report_inspect(inspect, args.verbose)

    match = re.search(r"^HARD: (\d+)", lint.out, re.MULTILINE)
    hard = match.group(1) if match else "?"
    print(f"\nslop_pass {__version__}: HARD={hard} exit={lint.rc} file={target}")
    return lint.rc


if __name__ == "__main__":
    sys.exit(main())
