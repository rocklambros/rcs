"""Audit a Jupyter notebook for execution-order issues.

Reads the .ipynb JSON and emits a report. Read-only — never modifies the notebook.

Usage:
    python audit-script.py path/to/notebook.ipynb [--strict] [--no-name-scan] [--format=markdown|table|json]

Adapt freely. The script is intentionally a single file with no external deps
beyond the standard library so it can drop into pre-commit hooks, CI jobs, or
local invocations without a uv/poetry install step.

The audit logic mirrors the skill's SKILL.md decision tree. When in doubt,
the skill body is the source of truth and this script is the convenience.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CellRow:
    index: int
    execution_count: Optional[int]
    status: str  # "run" | "unrun" | "error"
    source_preview: str
    flags: list[str] = field(default_factory=list)
    defined_names: set[str] = field(default_factory=set)
    referenced_names: set[str] = field(default_factory=set)


def load_notebook(path: Path) -> dict:
    return json.loads(path.read_text())


def is_papermill(nb: dict) -> bool:
    meta = nb.get("metadata", {}).get("papermill")
    return bool(meta)


def cell_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return src


def cell_status(cell: dict) -> str:
    if cell.get("execution_count") is None:
        return "unrun"
    for out in cell.get("outputs", []):
        if out.get("output_type") == "error":
            return "error"
    return "run"


def scan_names(source: str) -> tuple[set[str], set[str]]:
    """Return (defined_names, referenced_names) via ast best-effort.

    Defined = function defs, class defs, top-level assignment targets, imports.
    Referenced = ast.Name loads.

    On a parse error, return empty sets — the caller treats the cell as
    metaprogramming-defeated and reports it as unknown-impact.
    """
    defined: set[str] = set()
    referenced: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return defined, referenced
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    defined.add(tgt.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                defined.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            referenced.add(node.id)
    return defined, referenced


def build_rows(cells: list[dict]) -> list[CellRow]:
    rows: list[CellRow] = []
    for idx, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
        src = cell_source(cell)
        defined, referenced = scan_names(src)
        rows.append(CellRow(
            index=idx,
            execution_count=cell.get("execution_count"),
            status=cell_status(cell),
            source_preview=src.replace("\n", " ")[:80],
            defined_names=defined,
            referenced_names=referenced,
        ))
    return rows


def audit(rows: list[CellRow], *, strict: bool, name_scan: bool) -> list[CellRow]:
    """Annotate rows with flags per the decision tree. Returns rows."""
    last_run_count: Optional[int] = None

    for i, row in enumerate(rows):
        # Step 4 — errored cell
        if row.status == "error":
            row.flags.append("cell-errored")

        # Step 5 — out-of-order
        if row.status == "run":
            if last_run_count is not None and row.execution_count is not None:
                if row.execution_count < last_run_count:
                    row.flags.append("out-of-order")
            last_run_count = row.execution_count

        # Step 6 — gap (an unrun cell between two run cells)
        if row.status == "unrun":
            has_prior_run = any(r.status == "run" for r in rows[:i])
            has_later_run = any(r.status == "run" for r in rows[i + 1:])
            if has_prior_run and has_later_run:
                row.flags.append("gap-in-strict-mode" if strict else "gap-tolerated")

        # Step 3 — unrun with downstream dependent (name scan)
        if row.status == "unrun":
            if not name_scan:
                row.flags.append("unrun-unknown-impact")
            elif row.defined_names:
                downstream_refs: set[str] = set()
                for later in rows[i + 1:]:
                    if later.status == "run":
                        downstream_refs |= later.referenced_names
                hit = row.defined_names & downstream_refs
                if hit:
                    row.flags.append(
                        f"unrun-with-downstream-dependent:{','.join(sorted(hit))}"
                    )
                else:
                    row.flags.append("unrun-no-impact")
            else:
                row.flags.append("unrun-no-impact")

    return rows


def verdict(rows: list[CellRow]) -> str:
    fail_flags = {
        "out-of-order",
        "cell-errored",
        "gap-in-strict-mode",
    }
    for row in rows:
        for flag in row.flags:
            if flag in fail_flags or flag.startswith("unrun-with-downstream-dependent"):
                return "RE-RUN REQUIRED"
    return "OK"


def render_markdown(rows: list[CellRow], v: str, note: str = "") -> str:
    n_run = sum(1 for r in rows if r.status == "run")
    n_unrun = sum(1 for r in rows if r.status == "unrun")
    n_err = sum(1 for r in rows if r.status == "error")
    lines = [
        f"## Audit: {len(rows)} code cells · {n_run} run · {n_unrun} unrun · {n_err} error · verdict: **{v}**",
        "",
    ]
    if note:
        lines += [f"_{note}_", ""]
    lines += [
        "| idx | exec_count | status | source | flags |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        flags = "; ".join(r.flags) if r.flags else ""
        ec = r.execution_count if r.execution_count is not None else "null"
        lines.append(f"| {r.index} | {ec} | {r.status} | `{r.source_preview}` | {flags} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("notebook_path", type=Path)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--no-name-scan", action="store_true")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = p.parse_args(argv)

    nb = load_notebook(args.notebook_path)

    if is_papermill(nb) and not args.strict:
        note = ("This notebook was produced by papermill; the execution-order audit "
                "does not apply. Re-run with --strict to override.")
        if args.format == "json":
            print(json.dumps({"verdict": "skipped-papermill", "note": note}))
        else:
            print(f"# {args.notebook_path.name}\n\n{note}")
        return 0

    cells = nb.get("cells", [])
    rows = build_rows(cells)

    all_unrun_no_output = all(
        r.status == "unrun" and not cells[r.index].get("outputs")
        for r in rows
    ) if rows else False
    if all_unrun_no_output and rows:
        note = "All cells unrun and no outputs — notebook appears to have been cleared. Re-run top-to-bottom before sharing."
        if args.format == "json":
            print(json.dumps({"verdict": "notebook-was-cleared", "note": note}))
        else:
            print(f"# {args.notebook_path.name}\n\n{note}")
        return 0

    rows = audit(rows, strict=args.strict, name_scan=not args.no_name_scan)
    v = verdict(rows)

    if args.format == "json":
        payload = {
            "verdict": v,
            "cells": [
                {
                    "index": r.index,
                    "execution_count": r.execution_count,
                    "status": r.status,
                    "source_preview": r.source_preview,
                    "flags": r.flags,
                }
                for r in rows
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_markdown(rows, v))

    return 0 if v == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
