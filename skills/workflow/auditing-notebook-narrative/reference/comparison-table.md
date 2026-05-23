# Output-type comparison strategies

For each output type, how the audit infers the actual direction. Ranked by reliability.

## 1. Printed scalar values — RELIABLE

Pattern: `print(f"accuracy: {score:.3f}")` produces `"accuracy: 0.913\n"` in the cell's `outputs[].text`.

Strategy:

- Parse the text for `key: value` or `key = value` patterns
- Collect all (key, value) pairs across the matched cell
- Match the prose's named metric (e.g., "accuracy") to the key
- If multiple values are present (e.g., before / after, baseline / final), compare them

False-positive risk: low. The text is right there; the parsing is deterministic.

## 2. Tabular outputs (DataFrames) — MODERATELY RELIABLE

Pattern: `df.head()` or `print(df)` produces a pandas-rendered table in `outputs[].text` or `outputs[].data["text/plain"]`.

Strategy:

- Parse the text as a fixed-width table (the pandas repr is regular)
- Identify the column named in the prose
- Read the first and last values (or min and max if the prose says "highest" / "lowest")
- Compare numerically

False-positive risk: medium. Multi-index headers, wrapped columns, and truncated displays (`...`) can defeat the parser. The audit reports `parsed-with-low-confidence` when the column count is ambiguous.

## 3. Plot outputs — BEST-EFFORT

Pattern: `plt.plot(...); plt.show()` produces a PNG in `outputs[].data["image/png"]`.

Strategy: the audit **cannot read pixels**. Fall back to the cell's source code:

- Find the plotting call (`plt.plot`, `plt.bar`, `sns.lineplot`, `df.plot`, etc.)
- Identify the y-variable
- Trace the y-variable back to its definition in the same notebook (best-effort name lookup)
- Infer the direction from the data source

Limitations:

- Plot transformations (smoothing, log-scale, dual-axis) defeat the inference
- Plots built up via multiple `plt.plot` calls have ambiguous "direction"
- Subplots are too rich for the static audit

When the inference is uncertain, the audit emits `actual_direction: unverifiable-visual` and recommends manual review.

## 4. Logged metrics — RELIABLE

Pattern: A training loop prints `epoch 1: loss=2.3, acc=0.42 / epoch 50: loss=0.6, acc=0.89` across one or more cells.

Strategy:

- Parse each printed epoch / step line for `key=value` pairs
- Build a time-series for each named metric
- Compute direction: first vs. last, or min vs. max

False-positive risk: low when the format is regular. High when the training loop's print format is custom — in that case the parser falls back to "unverifiable" and asks the user to use a standard logger format.

## 5. Confusion matrices and other multi-cell visualizations — UNVERIFIABLE

These cannot be reduced to a single direction. The audit marks claims about them as `unverifiable-visual` and lets the human adjudicate. Common cases:

- Confusion matrix as a heatmap — "the model confuses class A with class C most often"
- t-SNE / UMAP scatter — "the clusters separate cleanly"
- Sankey / network — "most flow concentrates in node 3"

Recommendation: rewrite the narrative claim to reference a printed scalar or table that the audit CAN verify. E.g., "the confusion matrix shows recall_A = 0.92" — now the audit can match `recall_A = 0.92` against a printed value.

## Decision rule

For each claim:

1. Find the target output cell (per Step 4 of the workflow)
2. Pick the comparison strategy by output type, top to bottom
3. If the chosen strategy returns a numeric direction, compare and emit `match` or `mismatch`
4. If the strategy returns `unverifiable*`, the claim is reported but not failed (unless `strict` is on)

This ordering — prefer the most reliable evidence — means the audit's hard FAILs are almost always grounded in parseable text, and the soft "needs-manual-review" flags are concentrated on the genuinely visual claims.
