---
name: auditing-data-quality
description: >
  Audits a tabular dataset for data quality before any model is fit — per-column
  nulls, ranges, types, semantic class (ID / categorical / continuous / ordinal
  / text / datetime / boolean), cardinality alarms, outlier flags, and row-level
  integrity (duplicate rows, conflicting fact-pairs). Refuses to drop outliers
  without semantic context. Use whenever the user receives a new dataset,
  before fitting any model, when results suddenly look off, or when a dataset
  changed shape between runs.
version: 0.1.0
status: shipped
track: workflow
audience: [data-engineer, data-scientist, security-eng]
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - llm-toxicity-visual-analysis
  - genai_agentic_incidents
last-updated: 2026-05-23
---

# Auditing Data Quality

## When to use

Trigger this skill when the user asks for or implies one of:

- Receiving a new dataset from a colleague, upstream pipeline, vendor, or public source
- About to fit a model and they have not audited the data yet ("I'm going to train a classifier on this CSV")
- Results look "off" — accuracy too high, a feature looks suspiciously predictive, distributions seem wrong
- The dataset's shape (row count, column count) changed between runs and they want to know why
- Phrases like "audit the data", "is this data clean?", "what should I check before modeling?"

## When NOT to use

Skip this skill and use lighter tooling when:

- The dataset is a well-known benchmark with a published data card and prior audits (Iris, MNIST, ImageNet) — read the data card instead
- The pipeline is **streaming / unbounded** and a full-table scan is impractical → use per-batch quality metrics with Great Expectations, Soda, or a custom rolling-window monitor
- The user is asking about **schema validation only** (types and required columns) without distributional concerns → use Pandera / Pydantic / dataclass validation

## Quick start

User says: "I just got a 50,000-row patient dataset for a classification task. Audit it before I model."

Skill response: walks the seven-step audit producing per-column null/range/type/cardinality report, semantic-class detection, outlier flags with context, duplicate-row check, and a final go / no-go-with-blockers verdict.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| dataset | path or DataFrame | yes | — | The data to audit. Tabular (CSV, Parquet, DataFrame). |
| id_columns | list[str] | no | inferred | Columns to treat as identifiers for duplicate-row check. If omitted, the audit infers ID-like columns by name/cardinality. |
| outlier_method | "iqr" \| "zscore" \| "percentile" | no | "iqr" | How to flag outliers. IQR (Tukey 1.5×) is robust; zscore assumes Normality; percentile (>99th or <1st) is purely empirical. |
| cardinality_alarm | int | no | 100 | Categorical columns with cardinality above this go on a "might be free text" alert. |
| max_drop_threshold | float | no | 0.30 | If any column has > this fraction of nulls, flag as blocking — do not silently drop the column. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as the audit progresses:

```
Data-quality audit progress:
- [ ] Step 1: Shape — row count, column count, memory footprint, file size
- [ ] Step 2: Per-column report — type, null count, null %, distinct count, sample values
- [ ] Step 3: Semantic class — ID / categorical / continuous / ordinal / text / datetime / boolean
- [ ] Step 4: Range sanity — domain bounds (ages > 120, prices < 0, lat/lon outside ±90/±180, future event dates)
- [ ] Step 5: Outlier flags — Tukey IQR or z-score; report counts, do NOT drop without semantic context
- [ ] Step 6: Cardinality alarm — "categorical" columns with > 100 unique values may be free text mislabeled
- [ ] Step 7: Row-level integrity — duplicate rows (with and without ID columns), conflicting fact-pairs (same key, different value)
- [ ] Final: Go / no-go-with-blockers verdict + remediation list
```

### Step 2 detail — per-column report

For each column, produce one row:

| Column | dtype | null_count | null_% | distinct_count | min | max | mean | std | sample_values |
|---|---|---|---|---|---|---|---|---|---|

If `null_%` > `max_drop_threshold` (default 30%), flag as blocking — do not silently drop the column without consulting the data producer.

### Step 3 detail — semantic class detection

Per-column heuristic, not just the dtype:

- **ID**: unique-per-row (or per-group) string/int; high cardinality; column name contains `id`, `uuid`, `key`
- **Categorical**: low cardinality (<= 50 distinct), discrete; not ordinal
- **Continuous**: numeric, high cardinality, distribution makes sense as a quantity
- **Ordinal**: numeric or string with an inherent order (Likert scale, severity levels) — the audit cannot detect this from data alone; ask the user
- **Text**: strings with high cardinality, long mean length, irregular structure
- **Datetime**: parseable as date/time; defer to `validating-temporal-fields` for deeper checks
- **Boolean**: exactly two distinct values (often coded as 0/1, true/false, yes/no)

Mislabeled semantic class is a leading cause of downstream bugs: a column named `customer_segment` that's actually free-text notes will explode one-hot-encoded feature count.

### Step 4 detail — range sanity

Apply domain rules. Common examples:

- `age` between 0 and 120
- `price`, `quantity`, `count` ≥ 0
- `latitude` in [−90, 90], `longitude` in [−180, 180]
- `temperature_c` in [−100, 60] (human-survivable plus margin)
- `event_date` ≤ today (see `workflow/validating-temporal-fields`)
- Any percentage in [0, 100] or proportion in [0, 1]

If the dataset is domain-specific (medical labs, financial transactions, sensor readings), ask the user for the domain's expected ranges before running this step.

### Step 5 detail — outlier flags (do NOT auto-drop)

Report outliers; do not drop them. The audit's job is to surface candidates for human inspection:

```
Column: age
Method: IQR (Tukey 1.5×)
Q1: 28, Q3: 64, IQR: 36
Outlier bounds: [-26, 118]
Outlier count: 14 (0.028%)
Sample outlier values: 0, 0, 0, 0, 132, 250, 999
Hypothesis: 0 is likely a missing-value sentinel; 999 is likely a data-entry error; 250 may be a years-vs-months mistake.
Action: REQUIRED — confirm with data producer before dropping or imputing.
```

Auto-dropping outliers without semantic context is the #1 way to silently delete the most informative rows in a dataset (extreme medical cases, fraud, sentinel-coded missing).

### Step 6 detail — cardinality alarm

A "categorical" column with cardinality > `cardinality_alarm` (default 100) is suspicious. Common causes:

- It's actually free text (e.g. `notes`, `description`, `comment`)
- It's a high-cardinality ID misclassified as categorical
- The categorical scheme drifted over time (legacy + new codes coexist)

Flag for the user; do not silently one-hot-encode a 10,000-unique-value column.

### Step 7 detail — row-level integrity

- **Exact duplicates** — `df.duplicated().sum()`; report count and a sample
- **Duplicates ignoring ID column** — `df.drop(columns=id_columns).duplicated().sum()`; same row content under different IDs
- **Conflicting fact-pairs** — same key (or natural ID) appears with different values for the same attribute (e.g. patient 42 has `birth_year = 1980` in one row and `birth_year = 1985` in another)

Conflicting facts are silent corruption; flag as blocking.

## Outputs

The audit produces:

1. **Shape line** — `N rows × M columns; file size; memory footprint`
2. **Per-column report table** — one row per column with the Step 2 fields
3. **Semantic-class table** — column → inferred class + confidence + flags
4. **Range-violations list** — column · expected range · violation count · sample violating values
5. **Outlier report** — column · method · bounds · count · sample values · hypothesis · required action
6. **Cardinality alarms** — flagged columns + likely cause
7. **Row-level integrity report** — exact dups · same-content-different-ID dups · conflicting fact-pairs
8. **Final verdict** — go / no-go-with-blockers / no-go — with a remediation list ordered by blocker severity

## Failure modes

- **Auto-drop outliers** — running an IQR filter and removing rows without semantic context; deletes the most informative records (extreme cases, sentinel-coded missing). Caught by: Step 5 requires "hypothesis + required action", no drop.
- **Silent column drop on high null %** — `df.dropna(axis=1)` removing every high-null column without flagging the data producer. Caught by: Step 2 `max_drop_threshold` blocker.
- **Cardinality blowout** — one-hot-encoding a misclassified free-text column produces 10,000 sparse features. Caught by: Step 6 cardinality alarm.
- **Conflicting facts ignored** — same patient, different birth years across rows; downstream model learns nonsense. Caught by: Step 7 fact-pair check.
- **Mislabeled semantic class** — treating an ordinal severity scale as continuous, or a high-cardinality ID as categorical. Caught by: Step 3 explicit class detection + ask-the-user prompt for ordinal.

## References

- `reference/audit-report-template.md` — copy-pasteable Markdown template for the audit report
- `reference/semantic-class-rules.md` — extended heuristics for the semantic-class detection step
- [Pandera documentation](https://pandera.readthedocs.io/) — schema validation library that pairs well with this audit
- [Great Expectations](https://greatexpectations.io/) — alternative validation framework for ongoing monitoring

## Examples

### Example 1: New patient dataset (happy-path)

Input: "I just got a 50,000-row patient dataset for a classification task. Audit it before I model."

Output: Skill produces the seven-step report — shape (50k × 23 cols), per-column null/range/type/distinct, semantic-class inference (15 continuous, 4 categorical, 2 datetime, 1 ID, 1 boolean), range checks (age column shows 14 values > 120 — flagged), cardinality alarm (none triggered), exact-duplicate check (3 dups found), conflicting fact-pairs (none). Verdict: no-go-with-blockers — confirm the age > 120 rows and the 3 exact dups with the data producer before modeling.

### Example 2: Age outlier dilemma (edge-case)

Input: "My age column has values from 0 to 250. Should I drop the outliers before modeling?"

Output: Skill explicitly refuses to recommend an auto-drop. Asks for semantic context: (a) is 0 a missing-value sentinel? (b) is 250 a data-entry error, a years-vs-months confusion, or a legitimate edge case in a specific domain (centenarians in life-insurance data)? Recommends contacting the data producer before any decision. Notes that auto-dropping outliers silently deletes the most informative rows in many domains.

### Example 3: Streaming pipeline (anti-trigger)

Input: "I have a streaming pipeline ingesting 1 million events/sec. Audit the data quality."

Output: Skill explicitly refuses the full-table-scan workflow. Explains that this audit is designed for bounded tabular datasets, not streaming. Recommends per-batch quality metrics via Great Expectations, Soda, or a custom rolling-window monitor with alerting on threshold violations. Hands off to a streaming-data-quality discipline.

## See also

- `workflow/validating-temporal-fields` — deeper checks for datetime columns flagged in Step 3
- `workflow/deduplicating-records` — pair with this skill when Step 7 finds row-level duplicates that need a multi-key dedup pass
- `workflow/auditing-source-provenance` — record where each row came from so audit findings can be replayed against the source

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored from the DU-MSDSAI-4432-* notebook pattern (every notebook jumped to modeling without a data audit); cross-referenced with `llm-toxicity-visual-analysis` and `genai_agentic_incidents` quality bugs
