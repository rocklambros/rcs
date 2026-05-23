---
name: generating-data-dictionary
description: >
  Generates a per-column data dictionary for a tabular dataset — type,
  nullability, range, unique-count, semantic class (ID / categorical /
  continuous / ordinal / text / datetime / boolean), sample values, and
  inferred role (feature / target / leakage-risk / PII). Use whenever
  receiving a fresh client / partner / vendor dataset; before fitting
  any model on a dataset whose columns are not already documented;
  whenever a column's purpose is ambiguous; or whenever onboarding a
  teammate to a dataset they have not worked with before.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, data-engineer, ml-engineer, instructor]
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - llm-toxicity-visual-analysis
last-updated: 2026-05-23
---

# Generating a Data Dictionary

## When to use

Trigger this skill when the user asks for or implies one of:

- Receiving a fresh dataset from a client, partner, vendor, or research collaborator and needing to understand what every column is
- About to fit a model on a dataset whose columns are not already documented (no README, no codebook, no schema annotations)
- Onboarding a teammate or a graduate student to a dataset they have not worked with before
- Something seems off in modeling results and the user suspects a column's semantic class or role was misinterpreted
- Preparing a paper / report / regulatory submission that requires per-column documentation (codebook style)
- Generating documentation as the first step in `workflow/auditing-data-quality`

## When NOT to use

Skip this skill and hand off when:

- The dataset is a well-known public benchmark (MNIST, ImageNet, Iris, Titanic) where canonical dictionaries already exist — cite the canonical source rather than regenerating
- The data is unstructured (raw images, raw audio, raw video) with no tabular schema to dictionary
- The user has an existing dictionary and just wants to update one entry (different task: edit, not generate)
- The data is streaming / unbounded and a full-table scan is impractical (different skill: `workflow/auditing-data-quality` covers streaming-friendly metrics)

## Quick start

User says: "Here's a 50K-row patient CSV from our partner hospital. Generate a data dictionary."

Skill response: produces a per-column dictionary with: name, type, nullability, null %, unique count, range (min/max for numeric, top-5 for categorical), semantic class, inferred role, sample values, and a notes column for anomalies.

Output format (Markdown table — see `reference/dictionary-schema.md` for the JSON-Schema variant):

```markdown
| Column | Type | Null % | Unique | Range / Top-5 | Semantic | Role | Notes |
|---|---|---|---|---|---|---|---|
| patient_id | int64 | 0% | 50000 | 100001-150000 | ID | identifier | unique; do not use as feature |
| age | int64 | 0.2% | 102 | 0-250 | continuous | feature | range suspicious; max 250 likely error |
| sex | object | 0% | 3 | F (52%), M (47%), U (1%) | categorical | feature | low cardinality OK |
| diagnosis | object | 0% | 4823 | "Type 2 DM" (12%), ... | text-as-category | feature | cardinality > 100 → free text, not category |
| outcome | int64 | 0% | 2 | 0 (78%), 1 (22%) | boolean | target | binary; class imbalance |
```

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| dataset | path | yes | — | Path to CSV / Parquet / JSON / Excel / SQL connection string. |
| sample_size | int | no | full | If full-table scan is too slow, sample this many rows. Random or stratified sample. |
| target_column | string | no | inferred | The supervised-learning target, if any. The skill marks it explicitly and excludes it from feature-set summaries. |
| pii_policy | "flag" \| "redact" \| "ignore" | no | flag | What to do with columns whose values look like PII (email, phone, SSN, name). `flag` notes in the dictionary; `redact` shows masked samples; `ignore` shows raw samples. |
| output_format | "markdown" \| "json" \| "html" | no | markdown | Output format for the dictionary. JSON is machine-readable per `reference/dictionary-schema.md`. |

## Workflow

Copy this checklist into the response and check off items as the dictionary is built:

```
Data-dictionary generation progress:
- [ ] Load the dataset (or sample) and identify columns
- [ ] For each column: capture type, null %, unique count, range / top values
- [ ] Infer semantic class (ID / categorical / continuous / ordinal / text / datetime / boolean)
- [ ] Infer role (identifier / feature / target / leakage-risk / PII)
- [ ] Flag anomalies (suspicious ranges, high cardinality on "categorical", mixed types, sentinel-value patterns)
- [ ] If pii_policy != "ignore": flag or redact PII-shaped columns
- [ ] Emit the dictionary in the requested format
```

### Step 1: Load and inventory

Read the dataset header + schema. For CSV / Parquet / Excel, get types from the file. For untyped formats (JSON), infer per column from a sample.

### Step 2: Per-column statistics

For each column, compute:

- **Type** — the storage type (`int64`, `float64`, `object`, `category`, `datetime64[ns]`, `bool`)
- **Null count + null %** — Pandas: `df[col].isna().sum()` and `/ len(df)`
- **Unique count** — `df[col].nunique()` (without NA)
- **Range / top values** — for numeric: min, max, mean, median, std; for object/category: top-5 by frequency with %; for datetime: min / max
- **Sample values** — 3-5 sample non-null values for visual inspection

### Step 3: Semantic-class inference

See `reference/semantic-class-rules.md` for the full rule table. Summary:

| Signal | Semantic class |
|---|---|
| dtype int/float, unique count > 100 | continuous |
| dtype int/float, unique count ≤ 20, integer values | ordinal (if monotonic-looking) OR categorical |
| dtype int/float, unique count = 2, values in {0,1} | boolean |
| dtype bool | boolean |
| dtype object, unique count ≤ 50, modal frequency > 1% | categorical |
| dtype object, unique count > 100 AND most values are long strings | text |
| dtype object matching ID regex (UUID, hash, sequential int) | ID |
| dtype datetime OR object matching ISO-8601 / common date format | datetime |

### Step 4: Role inference

For each column, infer the role based on semantic class + context:

| Hint | Role |
|---|---|
| Unique count == row count | identifier (do not use as feature) |
| Name matches target hint (`outcome`, `label`, `y`, `target`, `class`) | target |
| Name matches PII pattern (`email`, `phone`, `ssn`, `name`, `address`, `dob`) | PII (per policy) |
| Datetime AND column name suggests an event-time | feature OR temporal (flag for leakage if model is non-temporal) |
| Numeric, derived-looking name (`*_score`, `*_rank`, `*_predicted`) | possible leakage; investigate before use |

### Step 5: Anomaly flagging

Flag columns where:

- Range is implausible (negative ages, prices < 0, lat/lon out of bounds, percentage > 100)
- Cardinality alarm: a column tagged categorical but with cardinality > 100 — likely free-text masquerading as category
- Sentinel patterns: columns with values like `-1`, `9999`, `1900-01-01` may be encoding missing-as-sentinel; flag for the user to confirm semantics
- Mixed types: numeric columns with stringified numbers, or datetime columns with mixed formats
- Constant or near-constant: a "feature" column with 1 unique value provides no information

### Step 6: PII flagging

For object-typed columns, check regex patterns from `reference/pii-patterns.md`:

- Email-shaped: `[^@\s]+@[^@\s]+\.[^@\s]+`
- Phone-shaped: variants of `+? d{7,15}`
- SSN-shaped (US): `\d{3}-\d{2}-\d{4}`
- Credit-card-shaped: Luhn-checkable 13-19 digit
- Person-name-shaped: heuristic (TitleCase tokens)

Flag matches in the `Notes` column. If `pii_policy: redact`, replace sample values with `***`.

## Outputs

A data dictionary in the requested format:

1. **Markdown table** (default) — one row per column with all fields
2. **JSON** — machine-readable, validates against `reference/dictionary-schema.md` schema
3. **HTML** — styled table for inclusion in a notebook output cell

Plus an **Issues summary** listing the anomalies found, ordered by severity (blocking → warn → info).

## Failure modes

Known pitfalls in data-dictionary generation:

- **Object column treated as categorical when it's free text** — `diagnosis` has 4823 unique values across 50K rows; treating as a categorical feature would explode the model's parameter count and never generalize. Caught by: Step 3 cardinality rule (>100 unique → text, not category); Step 5 cardinality alarm.
- **ID column treated as a numeric feature** — `patient_id` is sequential int with unique-count = row-count; treating as a feature leaks the train/test split. Caught by: Step 4 identifier role infers from uniqueness; Notes column explicitly says "do not use as feature".
- **Sentinel-encoded missing values appear as a valid range** — `age` of `-1` or `999` is a missing sentinel, not a 999-year-old. Caught by: Step 5 sentinel pattern flag; the user is asked to confirm.
- **Target leakage from a `_score` column** — a column named `risk_score` is actually computed from the target post-hoc. Caught by: Step 4 derived-name heuristic flags `*_score` / `*_predicted` for investigation before use.
- **PII columns silently surfaced in samples** — emails / SSNs displayed in plain text in the dictionary output, which gets committed to the repo. Caught by: Step 6 PII flagging; `pii_policy: redact` masks samples.
- **Mixed-format datetime columns** — `'2024-01-15'`, `'01/15/2024'`, `1705276800` all in one column; downstream parsing silently coerces some to NaT. Caught by: Step 5 mixed-types check.

## References

- `reference/semantic-class-rules.md` — full per-class inference table with edge cases
- `reference/pii-patterns.md` — PII regex patterns + policy options
- `reference/dictionary-schema.md` — JSON Schema for the machine-readable output
- [pandas-profiling / ydata-profiling](https://github.com/ydataai/ydata-profiling) — adjacent tool; produces HTML reports with similar information (heavier than the dictionary format this skill emits)

## Examples

### Example 1: Fresh client CSV (happy-path)

Input: "Here's a 50K-row patient CSV from our partner hospital. Generate a data dictionary."

Output: Skill loads the CSV, runs Steps 1-6, and produces a Markdown table with one row per column. Flags `patient_id` as identifier; flags `age` range (0-250) with a Notes entry "max 250 likely error or sentinel"; flags `diagnosis` (cardinality 4823) as text-as-category, not a usable categorical feature; flags `outcome` as the binary target with class imbalance (78/22); flags `email` and `dob` as PII per the default policy.

### Example 2: Mixed-type column flag (edge-case)

Input: "My `signup_date` column has some values like `'2024-01-15'`, some like `1705276800` (Unix epoch), and some that look like Excel serial dates. Generate the dictionary."

Output: Skill flags `signup_date` as a mixed-format column. Notes column reads "mixed datetime formats detected: ISO date, Unix epoch, possible Excel serial. Recommend normalizing to ISO-8601 with timezone before modeling. Naive `pd.to_datetime` will silently coerce some to NaT." Suggests a small reconciliation script that handles each format and asserts non-null on the output.

### Example 3: MNIST (anti-trigger)

Input: "Generate a data dictionary for the MNIST training set."

Output: Skill explicitly does NOT regenerate per-pixel column entries (784 columns of greyscale intensity is not informative as a dictionary). Cites the canonical MNIST dataset documentation (Yann LeCun's MNIST page). Suggests the user reference the canonical citation. Hands off; this skill is for unfamiliar / unstructured datasets, not for the well-documented public canon.

## See also

- `workflow/auditing-data-quality` — the dictionary is the first artifact this skill produces; auditing-data-quality is the broader follow-on review
- `workflow/auditing-source-provenance` — provenance is per-record; the dictionary is per-column; both belong on any new dataset
- `workflow/validating-schema-evolution` — when a dataset's columns change between revisions, regenerate the dictionary and diff it
- `workflow/validating-temporal-fields` — temporal columns flagged here get a deeper audit there
- `ml-datasci/auditing-train-test-split` — uses the dictionary's `role` field (identifier / target / feature) to verify split discipline

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from the DU-MSDSAI-4432-* notebook family (every notebook started modeling without a dictionary; the dictionary would have caught the recurring issues this skill flags), llm-toxicity-visual-analysis (categorical-vs-text disambiguation)
