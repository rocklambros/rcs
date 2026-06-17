---
name: auditing-jupyter-execution-order
description: >
  Audits a Jupyter notebook (`.ipynb`) for out-of-order or unrun cells by reading
  the per-cell `execution_count` field. Flags non-monotonic execution_count, unrun
  code cells with downstream cells that ran, and notebooks where the rendered
  outputs reflect a different ordering than the cell layout. Produces a
  cell-by-cell verdict and a recommended re-run plan. Use whenever a notebook is
  about to be shared, submitted, committed, or graded, when results look
  inconsistent between cells, when a teammate reports inability to reproduce the
  numbers, or before promoting a notebook to a model card or paper figure. Does
  NOT apply to papermill / parameterized notebook outputs where a non-canonical
  execution order is intentional.
version: 0.1.0
status: shipped
track: workflow
audience: [data-scientist, ml-engineer, instructor, stats-student]
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-OptimalClusteringComparison
  - llm-toxicity-visual-analysis
last-updated: 2026-05-23
---

# Auditing Jupyter execution order

## When to use

Trigger this skill when one of these is true:

- A notebook is about to be **shared, submitted, committed, or graded** and you have not personally re-run it cleanly top-to-bottom in the same kernel session
- Outputs look **inconsistent across cells** — Cell 12 references a variable that Cell 8 defined, but Cell 8's `execution_count` is greater than Cell 12's
- A teammate reports **"I cannot reproduce your numbers"** when running the same `.ipynb` top-to-bottom
- A notebook is about to be **promoted** to a model card, paper figure, or release artifact
- A graded pset or report is about to land in PR review

This is a static audit. It reads the `execution_count` and `outputs` fields from the `.ipynb` JSON without re-executing anything — safe to run on any notebook.

## When NOT to use

Skip and hand off when:

- The notebook is a **papermill output** or otherwise parameterized — papermill runs cells in a sequence that may be deliberately non-canonical, and the `execution_count` reflects that intent
- The user is **mid-development** and has not yet attempted a clean top-to-bottom run — out-of-order state is normal during iteration; the audit is a pre-share gate, not a per-edit nag
- The artifact is **not a notebook** — for plain `.py` files, the analogue is `auditing-notebook-narrative` (cross-link below) or just running the script
- The user is asking about **execution-environment reproducibility** (pinned deps, OS, GPU) — that is `pinning-reproducible-environments`, not this skill

## Quick start

User says: *"Audit this notebook for execution-order issues."*

Skill response:

1. Load the `.ipynb` as JSON.
2. Walk the `cells` array and emit a row per code cell: `cell_index · execution_count · status (run / unrun / error) · first 80 chars of source`.
3. Compute monotonicity: are the `execution_count` integers strictly increasing in the layout order, with only `null` (unrun) as a permitted gap?
4. Flag every non-monotonic transition (e.g., layout order 1 → 2 → 3 with execution counts 1 → 3 → 2).
5. Flag every **unrun cell that has a downstream-run cell depending on a name defined in it** (best-effort static scan; explicit caveats in Failure modes).
6. Output a verdict (`OK` / `RE-RUN REQUIRED`) and, when not OK, a recommended re-run plan: `Restart kernel → Run All` is the canonical fix; surgical re-runs are listed as an alternative for long-running notebooks.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `notebook_path` | string (path to `.ipynb`) | yes | — | The notebook to audit. Read-only — the skill never modifies the file. |
| `name_scan` | `"on" \| "off"` | no | `"on"` | When `"on"`, the skill does a best-effort static scan to flag unrun cells whose names are referenced by downstream-run cells. Turn off for notebooks with heavy metaprogramming where the scan is unreliable. |
| `strict` | bool | no | `false` | When `true`, ANY non-monotonic transition fails the audit, even if the values eventually converge. When `false`, the skill tolerates a `null` (unrun) cell between two monotonic runs but still reports it. |
| `report_format` | `"table" \| "markdown" \| "json"` | no | `"markdown"` | Output shape. `"json"` is intended for CI consumption. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check items off as you go:

```
Audit progress:
- [ ] Step 1: Load the .ipynb JSON
- [ ] Step 2: Per-cell row: index · execution_count · status · source preview
- [ ] Step 3: Compute execution_count monotonicity (with the null-tolerance rule from `strict`)
- [ ] Step 4: Best-effort static name scan (unrun cells with downstream dependents)
- [ ] Step 5: Cross-check outputs — does a cell with execution_count = N show outputs whose values
       could only have come from a later execution_count?
- [ ] Step 6: Verdict + recommended fix (canonical: Restart kernel → Run All)
```

### Step 1 — Load the `.ipynb` JSON

```python
import json
nb = json.loads(open(notebook_path).read())
cells = nb["cells"]
```

`.ipynb` is JSON; no kernel or runtime is needed.

### Step 2 — Per-cell row

For each cell with `cell_type == "code"`:

- `index` — its 0-based position in the layout
- `execution_count` — integer or `null`
- `status` — `"run"` if integer, `"unrun"` if `null`; `"error"` if any `output` has `output_type == "error"`
- `source_preview` — first 80 chars of `"".join(cell["source"])` with newlines collapsed to spaces

Markdown cells are skipped — they have no `execution_count`.

### Step 3 — Monotonicity check

Walk the run cells in layout order. Their `execution_count` values must form a strictly increasing sequence. Permitted gaps:

- **`null` (unrun) cell between two run cells** — OK in non-`strict` mode (but reported). In `strict` mode, FAIL.
- **Skipped integers** (e.g., 1 → 2 → 4) — always OK; the missing integer belongs to a cell that was later deleted, which is a normal editing artifact.

Forbidden:

- **Decreasing integer** (e.g., layout-position 5 has `execution_count = 3` while layout-position 4 has `execution_count = 7`) — FAIL regardless of mode. This is the canonical "ran cells out of order" signature.

### Step 4 — Best-effort static name scan

For each unrun (`execution_count == null`) code cell, parse its source with `ast.parse` and collect the names it defines (function defs, class defs, top-level assignments, imports). Then walk every downstream-run cell. If a downstream-run cell references one of those names (best-effort `ast.Name` scan), flag the unrun cell as a likely **silent break**: the downstream cell ran against a stale binding, not the current source.

This is best-effort. Dynamic name resolution (string-eval builtins, `globals()`, `getattr` with a string), runtime imports, IPython magics, and `*`-imports defeat the scan. Document each known false-positive class in the report. Honor `name_scan="off"` when the user knows the notebook is heavy on metaprogramming.

### Step 5 — Output cross-check

For each run cell, inspect its `outputs`. If a cell with `execution_count = N` has outputs referring to a state (e.g., a printed value of a variable) that could only have come from running a downstream cell with `execution_count > N`, flag it as **output-stale**. This is rare but it is the only check that catches "ran Cell 4, then went back and edited Cell 2 without re-running, but Cell 4's output now mentions a value Cell 2 defines that the kernel never re-evaluated."

In practice, Step 5 is hard to automate without false positives. The canonical lightweight version: if any cell has `execution_count = N` but its source has changed since (detectable only via git history, not the `.ipynb` itself), flag it. The skill SHOULD note the limit in the report so the user knows what was not checked.

### Step 6 — Verdict + recommended fix

| Verdict | Trigger |
|---|---|
| `OK` | No FAIL flags in Steps 3, 4 (when on), 5 |
| `RE-RUN REQUIRED` | Any FAIL flag |

The canonical recommendation is always: **Kernel → Restart Kernel and Run All Cells**. Surgical re-runs (e.g., "just re-run cells 5 through 9") are offered as an alternative for notebooks where a top-to-bottom run is very expensive (heavy training, large data load); the skill notes that surgical re-runs do not fully validate reproducibility.

## Outputs

A markdown report (or table / JSON per `report_format`) with these sections:

1. **Summary line**: `<count> code cells · <count> run · <count> unrun · <count> error · verdict: OK | RE-RUN REQUIRED`
2. **Per-cell table**: `index · execution_count · status · source_preview · flags`
3. **Flags detail** for each FAIL: which check fired, the evidence (cell indices + execution_count values), and the consequence (e.g., "Cell 12 references `df_clean` defined in Cell 8 [unrun]")
4. **Recommended fix** in priority order: Restart-and-Run-All first; surgical re-run as conditional alternative
5. **Caveats**: which checks were skipped (`name_scan="off"`, output cross-check limits, papermill-detected, etc.)

## Failure modes

- **False negative on dynamic name resolution.** The name scan misses string-eval builtins, `globals()["df"] = ...`, and IPython `%store` retrieval. The skill discloses this in the report's Caveats section and recommends the canonical `Restart Kernel and Run All` as the only sound check when the notebook uses these patterns.
- **False positive on papermill outputs.** Papermill executes cells in a parameterized order; the skill detects papermill by checking `metadata.papermill` on the notebook root and EXITS EARLY with a "papermill notebook — audit not applicable" message. If the user thinks the detection is wrong, they can override with `--strict` (which then audits anyway).
- **False positive on cleared outputs.** A notebook saved after "Cell → All Output → Clear" has `outputs == []` and may have `execution_count == null` for all cells. That is not a FAIL; the skill detects "all cells unrun" and reports `notebook-was-cleared` rather than `out-of-order`. The recommendation is the same — re-run top-to-bottom before sharing — but the framing matches the user's actual situation.
- **Cross-check overreach.** Step 5 is intentionally conservative: without git history or a re-execution, the audit cannot prove a cell's output is stale. The skill states this limit rather than overclaiming.
- **Treating a `null` execution_count gap as fatal in non-`strict` mode.** Common during iterative editing; the skill reports it but does not FAIL the audit unless `strict=true` or a downstream-run cell depends on the unrun cell's names.

## References

- `reference/audit-script.py` — drop-in script that loads a `.ipynb` and emits the audit report. Adapt to your project's CI shape (pre-commit hook, GitHub Actions job, or local script).
- `reference/decision-tree.md` — the canonical decision: when to FAIL the audit vs. report-but-pass
- [Jupyter nbformat documentation](https://nbformat.readthedocs.io/en/latest/format_description.html) — the `.ipynb` JSON schema, including `execution_count` and `outputs` field semantics
- [Papermill documentation](https://papermill.readthedocs.io/en/latest/) — context for the papermill-detection early-exit

## Examples

### Example 1: Notebook with run order 1 / 3 / 2 / 4 (happy-path)

Input: A 4-cell `.ipynb` where the cells appear in layout order with `execution_count` values `1`, `3`, `2`, `4` respectively.

Output: The skill flags Cell 2 (`execution_count = 3`) and Cell 3 (`execution_count = 2`) as **out-of-order**: Cell 3 ran before Cell 2 in the kernel session despite Cell 2 appearing first in the layout. The skill emits `verdict: RE-RUN REQUIRED` and recommends `Kernel → Restart Kernel and Run All Cells`. The per-cell table includes the source preview of each flagged cell so the user can see whether the out-of-order run silently changed any results.

### Example 2: Mixed run + unrun cells with downstream dependency (edge-case)

Input: A notebook where Cell 4 defines `df_clean` and is **unrun** (`execution_count = null`), and Cell 7 (run, `execution_count = 5`) references `df_clean`.

Output: The skill flags Cell 4 as **unrun-with-downstream-dependent** and Cell 7 as **ran-against-stale-binding**. Verdict: `RE-RUN REQUIRED`. The fix recommendation explains that Cell 7's printed output may reflect a different `df_clean` than the current Cell 4 source, since the kernel never re-evaluated Cell 4 against its present source. Canonical fix is Restart-and-Run-All; the report names `df_clean` as the suspect binding so the user can sanity-check the post-rerun output against the pre-rerun output.

### Example 3: Papermill-generated notebook (anti-trigger)

Input: A notebook with `metadata.papermill = {...}` populated and `execution_count` values that are non-monotonic by design (papermill ran cells in an injected parameter order).

Output: The skill detects the `metadata.papermill` block and EXITS EARLY with the message: *"This notebook was produced by papermill; the execution-order audit does not apply (papermill executes cells in an injected sequence by design). If you want a reproducibility check for papermill outputs, validate against the input parameters and the recorded papermill manifest instead."* The skill does NOT emit `RE-RUN REQUIRED` and does NOT walk the cell-by-cell monotonicity check. The user can force the audit with `strict=true` if they have a specific reason.

## See also

- `workflow/auditing-notebook-narrative` — checks whether the markdown narrative claims match the rendered figure outputs (a complementary audit for the same artifact)
- `workflow/building-deterministic-data-pipelines` — covers reproducibility upstream of the notebook (sorted JSON, LF endings, content-hash snapshots) so a re-run produces bit-identical artifacts
- `workflow/enforcing-seed-hygiene` — ensures the notebook's first cell pins all RNG seeds so a Restart-and-Run-All is deterministic

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
