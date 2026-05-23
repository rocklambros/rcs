"""Audit a Jupyter notebook for narrative-vs-output mismatches.

Reads the .ipynb JSON and emits a report. Read-only — never modifies the notebook.

Usage:
    python audit-script.py path/to/notebook.ipynb [--strict] [--format=markdown|json]

This script is a starter implementation of the SKILL.md decision tree. It is
NOT a substitute for the skill body — the skill names corner cases the script
does not yet handle (e.g., subtle negations, cited claims). Use the report as
a starting point for human review.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Keyword groups — see reference/keyword-matcher.md for the full canonical set.
INCREASE = [
    r"increase", r"rise", r"grow", r"climb", r"gain", r"improve(d)?",
    r"higher", r"highest", r"exceed(s|ed)?", r"above", r"more", r"expand(s|ed)?",
]
DECREASE = [
    r"decrease", r"fall", r"drop", r"decline", r"lose", r"lost",
    r"lower", r"lowest", r"below", r"less", r"shrink(s)?", r"shrank",
]
COMPARISON = [
    r"outperform(s|ed)?", r"underperform(s|ed)?", r"better than", r"worse than",
    r"best", r"worst",
]
CONVERGE = [r"converge(s|d)?", r"diverge(s|d)?", r"stabilize(s|d)?", r"plateau(s|ed)?", r"saturate(s|d)?"]

NEGATION = re.compile(
    r"\b(not|n't|no|never|without|failed to|did not|does not|cannot|was not)\b",
    re.IGNORECASE,
)

ATTRIBUTION = re.compile(
    r"\b([A-Z][a-z]+ et al|[A-Z][a-z]+ \(\d{4}\)|cited in|per [A-Z][a-z]+)\b",
)


@dataclass
class Claim:
    cell_idx: int
    sentence: str
    keyword: str
    direction: str  # up | down | comparison | converge
    negated: bool = False
    cited: bool = False


@dataclass
class AuditRow:
    claim: Claim
    target_cell: Optional[int]
    actual_direction: str  # up | down | match | mismatch | unverifiable | unverifiable-visual
    verdict: str  # match | mismatch | unverifiable | needs-manual-review


def sentences(text: str) -> list[str]:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", "", text)
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def match_direction(sentence: str) -> Optional[tuple[str, str]]:
    """Return (matched_keyword, direction) or None."""
    for pat in INCREASE:
        m = re.search(r"\b" + pat + r"\b", sentence, re.IGNORECASE)
        if m:
            return (m.group(0), "up")
    for pat in DECREASE:
        m = re.search(r"\b" + pat + r"\b", sentence, re.IGNORECASE)
        if m:
            return (m.group(0), "down")
    for pat in COMPARISON:
        m = re.search(r"\b" + pat + r"\b", sentence, re.IGNORECASE)
        if m:
            return (m.group(0), "comparison")
    for pat in CONVERGE:
        m = re.search(r"\b" + pat + r"\b", sentence, re.IGNORECASE)
        if m:
            return (m.group(0), "converge")
    return None


def is_negated(sentence: str, keyword: str) -> bool:
    pre = sentence.lower().split(keyword.lower())[0]
    tokens_before = pre.split()[-5:]
    window = " ".join(tokens_before)
    return bool(NEGATION.search(window))


def is_cited(sentence: str) -> bool:
    return bool(ATTRIBUTION.search(sentence))


def extract_claims(cells: list[dict]) -> list[Claim]:
    out: list[Claim] = []
    for idx, cell in enumerate(cells):
        if cell.get("cell_type") != "markdown":
            continue
        src = "".join(cell.get("source", ""))
        if src.strip().startswith("#") and "\n" not in src.strip():
            continue  # heading-only
        for sent in sentences(src):
            hit = match_direction(sent)
            if not hit:
                continue
            keyword, direction = hit
            negated = is_negated(sent, keyword)
            if negated:
                direction = {"up": "down", "down": "up", "comparison": "comparison", "converge": "diverge"}.get(direction, direction)
            out.append(Claim(
                cell_idx=idx,
                sentence=sent[:240],
                keyword=keyword,
                direction=direction,
                negated=negated,
                cited=is_cited(sent),
            ))
    return out


def nearest_preceding_output(cells: list[dict], from_idx: int) -> Optional[int]:
    for i in range(from_idx - 1, -1, -1):
        cell = cells[i]
        if cell.get("cell_type") == "code" and cell.get("outputs"):
            return i
    return None


def infer_actual_direction(cells: list[dict], cell_idx: int, claim: Claim) -> str:
    """Best-effort. See reference/comparison-table.md for the canonical rules."""
    if cell_idx is None or cell_idx >= len(cells):
        return "unverifiable"
    outputs = cells[cell_idx].get("outputs", [])
    text_parts: list[str] = []
    has_image = False
    for out in outputs:
        if out.get("output_type") == "stream":
            text_parts.append(out.get("text", "") if isinstance(out.get("text"), str) else "".join(out.get("text", [])))
        elif out.get("output_type") in ("display_data", "execute_result"):
            data = out.get("data", {})
            if "text/plain" in data:
                t = data["text/plain"]
                text_parts.append(t if isinstance(t, str) else "".join(t))
            if "image/png" in data:
                has_image = True
    blob = "\n".join(text_parts)

    nums = re.findall(r"[-+]?\d*\.?\d+", blob)
    nums_f = [float(n) for n in nums if n.replace(".", "").replace("-", "").isdigit()]

    if len(nums_f) >= 2:
        first, last = nums_f[0], nums_f[-1]
        if last > first:
            inferred = "up"
        elif last < first:
            inferred = "down"
        else:
            inferred = "converge"
        return inferred

    if has_image and not nums_f:
        return "unverifiable-visual"

    return "unverifiable"


def verdict_for(claim: Claim, actual: str) -> str:
    if claim.cited:
        return "match"  # cited claims describe others' work
    if actual.startswith("unverifiable"):
        return "needs-manual-review"
    if actual == claim.direction:
        return "match"
    if claim.direction in ("up", "down") and actual in ("up", "down") and actual != claim.direction:
        return "mismatch"
    return "needs-manual-review"


def audit(nb: dict, *, strict: bool) -> list[AuditRow]:
    cells = nb.get("cells", [])
    claims = extract_claims(cells)
    rows: list[AuditRow] = []
    for c in claims:
        target = nearest_preceding_output(cells, c.cell_idx)
        actual = infer_actual_direction(cells, target, c) if target is not None else "unverifiable"
        v = verdict_for(c, actual)
        if strict and v == "needs-manual-review":
            v = "mismatch"
        rows.append(AuditRow(claim=c, target_cell=target, actual_direction=actual, verdict=v))
    return rows


def render_markdown(rows: list[AuditRow], notebook_name: str) -> str:
    n_match = sum(1 for r in rows if r.verdict == "match")
    n_mismatch = sum(1 for r in rows if r.verdict == "mismatch")
    n_review = sum(1 for r in rows if r.verdict == "needs-manual-review")
    lines = [
        f"# Narrative audit: {notebook_name}",
        f"{len(rows)} claims · {n_match} match · {n_mismatch} mismatch · {n_review} needs-manual-review",
        "",
        "| md_cell | sentence | direction | target_cell | actual | verdict |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.claim.cell_idx} | `{r.claim.sentence}` | {r.claim.direction}{' (negated)' if r.claim.negated else ''} | "
            f"{r.target_cell} | {r.actual_direction} | {r.verdict} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("notebook_path", type=Path)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = p.parse_args(argv)

    nb = json.loads(args.notebook_path.read_text())
    has_markdown = any(c.get("cell_type") == "markdown" for c in nb.get("cells", []))
    if not has_markdown:
        msg = "Notebook has no narrative markdown to audit; skipping."
        if args.format == "json":
            print(json.dumps({"verdict": "skipped-no-narrative", "note": msg}))
        else:
            print(f"# {args.notebook_path.name}\n\n{msg}")
        return 0

    rows = audit(nb, strict=args.strict)

    if args.format == "json":
        payload = {
            "verdict": "mismatch-found" if any(r.verdict == "mismatch" for r in rows) else "OK",
            "rows": [
                {
                    "md_cell": r.claim.cell_idx,
                    "sentence": r.claim.sentence,
                    "claim_direction": r.claim.direction,
                    "negated": r.claim.negated,
                    "cited": r.claim.cited,
                    "target_cell": r.target_cell,
                    "actual_direction": r.actual_direction,
                    "verdict": r.verdict,
                }
                for r in rows
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_markdown(rows, args.notebook_path.name))

    return 1 if any(r.verdict == "mismatch" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
