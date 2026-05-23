# Decision tree — FAIL vs report-but-pass

The audit walks a per-cell decision tree. Each cell either contributes to the audit's overall verdict (FAIL) or appears in the report as informational only (report-but-pass).

## Per-cell tree

1. **Is the cell `cell_type == "markdown"`?**
   - Yes → skip; markdown cells have no `execution_count`
   - No → continue to (2)

2. **Is `execution_count == null` (unrun)?**
   - Yes → continue to (3)
   - No → continue to (4)

3. **Does any downstream-run cell reference a name defined in this cell?**
   - Yes → FAIL: `unrun-with-downstream-dependent`. Flag this cell AND the downstream cell.
   - No → report-but-pass: `unrun-no-impact`. The unrun cell does not affect any rendered output.
   - Caveat: if `name_scan="off"`, this step is skipped and the cell is reported as `unrun-unknown-impact`.

4. **Does this cell have any `outputs` with `output_type == "error"`?**
   - Yes → FAIL: `cell-errored`. The cell ran but threw. Any downstream output assuming the cell completed is suspect.
   - No → continue to (5)

5. **Is this cell's `execution_count` less than the previous run cell's `execution_count` in layout order?**
   - Yes → FAIL: `out-of-order`. The kernel ran this cell BEFORE the layout-previous cell, even though the layout suggests forward execution.
   - No → continue to (6)

6. **Does this cell have a `null` (unrun) run cell between it and the previous run cell in layout order?**
   - In `strict` mode → FAIL: `gap-in-strict-mode`
   - In default mode → report-but-pass: `gap-tolerated`. The unrun cell is reported separately (see step 3).

7. **Default** → no flag; cell is OK.

## Notebook-level early exits

Before walking cells, check the notebook root:

- **`metadata.papermill` present, non-empty** → EXIT EARLY with `papermill-detected`. Print the note from the SKILL's anti-trigger example. Do NOT walk cells unless the user passes `strict=true`.
- **All code cells have `execution_count == null` AND all `outputs == []`** → EXIT EARLY with `notebook-was-cleared`. The notebook had its outputs cleared (Cell → All Output → Clear); the canonical fix is the same (Restart-and-Run-All) but the diagnosis differs.

## Verdict aggregation

| Per-cell flag | Verdict contribution |
|---|---|
| `out-of-order` | FAIL |
| `unrun-with-downstream-dependent` | FAIL |
| `cell-errored` | FAIL |
| `gap-in-strict-mode` | FAIL (strict mode only) |
| `output-stale` (Step 5 cross-check) | FAIL (conservative — only fire with high evidence) |
| `unrun-no-impact` | report-only |
| `unrun-unknown-impact` (name_scan off) | report-only |
| `gap-tolerated` | report-only |

Notebook verdict: `RE-RUN REQUIRED` if any FAIL flag; otherwise `OK`.

## Why the asymmetric defaults

The audit's job is to be a **pre-share gate**, not a per-edit nag. False positives erode trust and the user ignores the audit. The default tolerances (gap allowed in non-`strict`, name-scan caveats, conservative output cross-check) are tuned so:

- A clean Restart-and-Run-All always passes
- An obvious out-of-order sequence (decreasing `execution_count`) always FAILS
- Mid-edit notebooks with a single unrun cell that nothing depends on do NOT fail

`strict=true` exists for the cases where the user wants the audit to enforce "every cell must have been run, no exceptions" — typical for grading pipelines, paper supplements, or release artifacts.
