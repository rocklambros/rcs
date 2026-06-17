---
name: auditing-notebook-narrative
description: >
  Audits a Jupyter notebook's markdown narrative against the rendered code-cell
  outputs, flagging claims in prose (e.g., "Figure 3 shows accuracy increasing")
  that the adjacent figure or printed value contradicts. Walks markdown cells,
  parses directional claims (increased / decreased / improved / declined /
  highest / lowest / converged), matches each to the nearest output, and reports
  any prose-vs-output mismatch with cell indices. Use when a notebook is about
  to be shared, submitted, graded, published, or promoted to a model card or
  paper figure, when reviewing a teammate's analysis, or whenever the narrative
  was written days before the model was retrained and may no longer match.
  Skip for pure-code notebooks with no narrative markdown.
version: 0.1.0
status: shipped
track: workflow
audience: [data-scientist, ml-engineer, instructor, stats-student, technical-writer]
evidence:
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - DU-MSDSAI-4432-OptimalClusteringComparison
  - llm-toxicity-visual-analysis
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Auditing notebook narrative

## When to use

Trigger this skill when one of these is true:

- A notebook with **both code outputs AND markdown narrative** is about to be shared, submitted, graded, published, or promoted to a model card / paper figure
- The notebook was **retrained or re-run** after the narrative was originally drafted (common: write the writeup Monday, retrain Friday, ship without re-reading)
- A reviewer asks "does the writeup still match the figures?"
- A pset or report has narrative claims of the form *"the model improved as X"*, *"loss decreased"*, *"accuracy is highest for class K"* and the user wants those claims verified against the actual outputs

This skill is a **prose-vs-output consistency audit**. It is complementary to `auditing-jupyter-execution-order` (which checks the kernel-state side) and `auditing-data-quality` (which checks the data side).

## When NOT to use

Skip and hand off when:

- The notebook is **pure code** — no markdown cells (or only header markdown like `# Setup`) — there is no narrative to audit
- The narrative is **forward-looking** — *"we will compare A vs B"* — not a claim about a rendered result
- The notebook's outputs were **cleared** — no rendered values to compare against; the narrative cannot be verified statically; recommend re-running first (`auditing-jupyter-execution-order` covers the cleared case)
- The narrative is **non-quantitative** — *"we explored the dataset"* — no falsifiable directional claim is being made

## Quick start

User says: *"Audit this notebook — does the narrative match what the figures actually show?"*

Skill response:

1. Load the `.ipynb` JSON.
2. Walk the cells. For each markdown cell, extract sentences containing **directional claim keywords**: increase / decrease / rise / fall / improve / decline / higher / lower / best / worst / highest / lowest / converge / diverge / outperform / underperform / above / below / exceeds / falls short / monotonic.
3. For each claim, identify the **target output** it refers to: the nearest preceding figure or printed value (heuristic — explicit references like "Figure 3" or "the table above" should be honored when present).
4. Compare the prose claim's **direction** to the actual rendered output. For figures, parse the image's alt text / caption / cell source plot code (best-effort: a real visual comparison requires the user to look at the image, but the skill flags claims that contradict the plot's data source visible in the code cell).
5. Emit a report: one row per claim, columns `markdown_cell · claim · target_output · prose_direction · actual_direction · verdict`.
6. Recommend: revise prose to match outputs, or re-run cells if outputs are stale.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `notebook_path` | string (path to `.ipynb`) | yes | — | The notebook to audit. Read-only. |
| `direction_keywords` | list of strings | no | (built-in set) | Custom keywords beyond the default set (e.g., domain-specific: `recovered`, `degraded`, `saturated`). Appended to the default. |
| `confidence_threshold` | `"strict" \| "lenient"` | no | `"lenient"` | `"strict"` flags any claim it cannot match to an adjacent output. `"lenient"` only flags claims where the matched output's direction is the OPPOSITE of the claim. |
| `report_format` | `"markdown" \| "json"` | no | `"markdown"` | Output shape. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist and check items off as you go:

```
Audit progress:
- [ ] Step 1: Load .ipynb JSON
- [ ] Step 2: Extract markdown cells; tokenize prose into sentences
- [ ] Step 3: Sentence-by-sentence: keyword match for directional claims
- [ ] Step 4: For each claim, find target output (nearest preceding code cell with output, or explicit reference)
- [ ] Step 5: Compare prose direction vs output direction (best-effort)
- [ ] Step 6: Emit report: pass / mismatch / unverifiable per claim
- [ ] Step 7: Recommend fix (revise prose OR re-run cells)
```

### Step 1 — Load the `.ipynb` JSON

Standard `json.loads`. The skill never modifies the notebook.

### Step 2 — Extract markdown cells

For each cell with `cell_type == "markdown"`, join the `source` array and tokenize into sentences (any reasonable sentence splitter — even a regex split on `\. `, `\? `, `! ` works for first-pass).

Skip:

- Heading-only cells (lines starting with `#`)
- Cells with only code blocks (triple-backtick fences)
- Cells with only links / images / TOC markup

### Step 3 — Directional claim detection

Default keyword set (case-insensitive, whole-word boundaries):

| Direction | Keywords |
|---|---|
| increase | increase(s/d/ing), rise(s/n), grow(s/n), climb(s/ed), higher, highest, exceed(s), above, more, gain(s/ed) |
| decrease | decrease(s/d/ing), fall(s/n), drop(s/ped), decline(s/d), lower, lowest, below, less, lose(s/t) |
| comparison | outperform(s/ed), underperform(s/ed), better than, worse than, best, worst |
| convergence | converge(s/d), diverge(s/d), stabilize(s/d), plateau(s/ed) |
| monotonicity | monotonic(ally), strictly increasing, strictly decreasing, non-monotonic |

Honor user-supplied `direction_keywords` by appending them.

For each matched sentence, emit a candidate claim record: `{cell_idx, sentence, direction, keyword}`.

### Step 4 — Target-output matching

For each claim, find the target output:

1. **Explicit reference** in the prose: `"Figure N"`, `"Table N"`, `"the chart above"`, `"the values shown earlier"`, `"the cell below"` — match by lexical pattern
2. **Nearest preceding code cell with an output** — default when no explicit reference. Walk backward from the claim's markdown cell to the nearest code cell with a non-empty `outputs` field
3. **Nearest following code cell with an output** — fall back when no preceding output exists (rare — usually the narrative cell sits between intro markdown and the first figure)

If no output can be matched within ±5 cells, label the claim **unverifiable** and continue.

### Step 5 — Direction comparison

Determining the actual direction of an output is the hardest part. Approaches by output type, ranked by reliability:

1. **Printed scalar values** — e.g., `print("accuracy:", 0.91)` followed later by `print("accuracy:", 0.94)`. Parse the printed text; compare numeric values. RELIABLE.
2. **Table outputs** — pandas `DataFrame` reprs. Parse the column the prose refers to (e.g., "the accuracy column"); read first and last values. MODERATELY RELIABLE.
3. **Plot outputs** — `<img>` PNG in the output. The skill CANNOT see the rendered pixels; it MUST fall back to reading the plot's data source from the code cell (e.g., `plt.plot(x, y)` — direction of `y` over `x`). BEST-EFFORT.
4. **Logged metrics** — printed during training (e.g., `epoch 1: loss=2.3`, `epoch 10: loss=0.8`). Reliable when the prose names the metric.

When the comparison cannot be reduced to numbers (e.g., a categorical plot, a confusion matrix), the skill marks the claim **unverifiable-visual** and recommends a manual review for that claim only.

### Step 6 — Report

For each claim, emit one row:

| Field | Value |
|---|---|
| `markdown_cell` | index in the cells array |
| `sentence` | the matched sentence (first 120 chars) |
| `claim_direction` | increase / decrease / best / worst / converge / etc. |
| `target_output_cell` | index of the matched code cell |
| `actual_direction` | inferred from Step 5, or "unverifiable" / "unverifiable-visual" |
| `verdict` | `match` / `mismatch` / `unverifiable` |

In `strict` mode, `unverifiable` counts as a soft flag (report-but-pass becomes "needs manual review"). In `lenient` mode, only `mismatch` is a hard flag.

### Step 7 — Recommend a fix

For each `mismatch`:

- If the outputs look fresh (cells have recent `execution_count` values and Step 3 of `auditing-jupyter-execution-order` would pass), the prose is wrong — REVISE PROSE
- If the outputs look stale (cells unrun or out-of-order), the outputs are wrong — RE-RUN, then re-audit
- If the user cannot tell, ask: "When did you last edit the markdown vs. last run the code?"

## Outputs

A markdown report (or JSON per `report_format`) with sections:

1. **Summary**: `<count> claims · <count> match · <count> mismatch · <count> unverifiable`
2. **Claims table** with the columns from Step 6
3. **Mismatch detail**: for each mismatch, the markdown cell index, the target output cell index, the prose excerpt, the inferred actual direction, and a one-sentence diagnosis
4. **Recommendation**: REVISE PROSE / RE-RUN AND RE-AUDIT / NEEDS MANUAL REVIEW per claim
5. **Caveats**: which claims required best-effort visual inference (and therefore need a human look)

## Failure modes

- **Visual claims about figures the skill cannot read.** Plot direction is inferred from the cell's plotting code (best-effort), not from pixels. A claim like "the loss curve is U-shaped" cannot be verified without the rendered image. The skill marks these `unverifiable-visual` and asks for human review on those claims rather than guessing.
- **Sarcasm / negation / counterfactuals.** "Accuracy did NOT improve" with the keyword "improve" will be misread as an improvement claim unless the skill detects the negation. The keyword matcher does check for `\bnot\b` and `\bno\b` within 5 tokens of the keyword and inverts the direction in that case. More subtle negations (e.g., "we expected accuracy to improve, but it did not") will still trip the matcher — flagged as `verdict: needs-manual-review` rather than a hard mismatch.
- **Cross-cell narrative.** A single claim split across multiple sentences in different markdown cells defeats the per-sentence matcher. The skill flags long markdown cells (> 10 sentences) and recommends the user check for cross-sentence claims manually.
- **Conflating "highest" in a table with "highest over time."** "Class A has the highest precision" (cross-class comparison) vs. "precision is the highest at epoch 10" (time-series comparison) use the same keyword. The skill disambiguates via the matched output type (table vs. logged metrics over time) but documents the ambiguity in the Caveats section.
- **Reading the wrong target output.** Step 4's "nearest preceding output" heuristic is wrong when the narrative refers to a much later cell. The user can override by adding an explicit `"Figure 3"` / `"the cell below"` reference in the prose; the skill honors explicit references over the heuristic.

## References

- `reference/keyword-matcher.md` — full default keyword set, negation handling, and the regex shape that detects each direction
- `reference/comparison-table.md` — output type → comparison strategy (printed scalar / DataFrame / plot / log)
- `reference/audit-script.py` — drop-in script that runs the narrative audit end-to-end on a `.ipynb`
- [Jupyter nbformat documentation](https://nbformat.readthedocs.io/en/latest/format_description.html) — for parsing `cell_type`, `source`, `outputs`

## Examples

### Example 1: Stale narrative after retraining (happy-path)

Input: A notebook where Cell 5 (markdown) says *"As Figure 1 shows, accuracy improves from 0.78 at epoch 1 to 0.91 at epoch 50."* The adjacent code cell (Cell 6) prints `epoch 1: acc=0.78` and `epoch 50: acc=0.82` (the user retrained with a different learning rate and forgot to update the narrative).

Output: The skill flags Cell 5 with `claim_direction: increase from 0.78 to 0.91`, `actual_direction: increase from 0.78 to 0.82`. Verdict: `mismatch`. The narrative's qualitative direction is right (accuracy did increase) but the numeric end-point is wrong (0.91 vs. 0.82). Recommendation: REVISE PROSE — the figure now shows 0.82 at epoch 50, update the narrative to match. The report names the specific sentence to revise and the specific number to fix.

### Example 2: Reversed direction (edge-case)

Input: A notebook where Cell 8 (markdown) says *"Model B outperforms Model A on the test set."* The adjacent code cell (Cell 9) prints a metrics comparison showing Model A's F1 = 0.84 and Model B's F1 = 0.79.

Output: The skill flags Cell 8 with `claim_direction: B-better-than-A`, `actual_direction: A-better-than-A` (i.e., A wins on F1). Verdict: `mismatch`. Diagnosis: prose claims B outperforms A, but the rendered metric shows A's F1 (0.84) > B's F1 (0.79). Recommendation: REVISE PROSE or, if the user intended a different metric (e.g., recall), name the metric explicitly in the prose. The skill notes that "outperforms" without a named metric is ambiguous and a writeup-quality issue regardless.

### Example 3: Pure-code notebook (anti-trigger)

Input: A notebook with 12 code cells, no markdown cells (or only a single `# Setup` heading).

Output: The skill detects that there is no narrative to audit and EXITS EARLY with the message: *"This notebook has no narrative markdown to audit; the narrative-consistency check does not apply. For an execution-order audit, see `auditing-jupyter-execution-order`. For a data-quality audit, see `auditing-data-quality`."* No claims table, no mismatch report.

## See also

- `workflow/auditing-jupyter-execution-order` — pairs with this skill; together they cover both sides of "is the notebook share-ready?"
- `workflow/building-deterministic-data-pipelines` — upstream of the notebook; eliminates "different numbers on different runs" as a cause of narrative drift
- `ml-datasci/evaluating-binary-classifiers` — when the narrative claims a metric improvement, that skill provides the disciplined report (with CI + direction sentence) that the prose should be quoting

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
