# Semantic-class Inference Rules

Storage type alone is insufficient to know what a column means. These rules infer the semantic class from storage type plus statistical signals.

## Rule precedence

For each column, evaluate rules in this order. First match wins.

1. Datetime detection
2. Boolean detection
3. ID detection
4. Continuous vs ordinal vs categorical
5. Text detection
6. Default (categorical-with-warning)

## Datetime

A column is **datetime** if any of:

- dtype is `datetime64[ns]` or `pd.Timestamp`
- dtype is `object` AND ≥ 80% of non-null values parse via `pd.to_datetime(..., errors='coerce')`
- dtype is `int64` AND values fall in the plausible Unix-epoch range (1970-01-01 to today) AND column name contains a date-hint (`date`, `time`, `timestamp`, `created`, `updated`, `at`)

Edge cases:

- Mixed formats (ISO + epoch + Excel-serial) — classify as datetime BUT flag in Notes
- 100% NULL — cannot infer; default to unknown

## Boolean

A column is **boolean** if:

- dtype is `bool`, OR
- dtype is `int64` / `object` with exactly 2 unique non-null values from {0, 1}, {True, False}, {'Y', 'N'}, {'yes', 'no'}, {'true', 'false'} (case-insensitive)

Edge cases:

- {0, 1, NA} → boolean nullable
- {0, 1, 2} → not boolean (likely 3-way category)

## ID

A column is **ID** if:

- Unique count == row count (every value is unique), OR
- Unique count ≥ 0.95 × row count AND column name matches `*_id$` / `^id$` / `*_uuid$`, OR
- Values match UUID / hash regex

Edge cases:

- Sequential integers with column name `id` → ID
- Sequential integers without `id`-suffix and unique == row count → still ID with a note "looks like identifier but column name does not advertise it"

## Continuous

A column is **continuous** if:

- dtype is `int64` / `float64` AND unique count > 20 AND values span a non-trivial range, OR
- dtype is `float64` AND values are not all integers (presence of fractional part)

Edge cases:

- Year column (`2010`, `2011`, ...) with unique count 5 → ordinal, not continuous (despite int)
- Discrete count (0, 1, 2, ..., 50) with unique count 51 → continuous-ish; consider ordinal if downstream model treats it differently

## Ordinal

A column is **ordinal** if:

- dtype is `int64` / `float64` AND unique count ≤ 20 AND values are integer-valued AND span is monotonic-looking (e.g., {1, 2, 3, 4, 5}), OR
- dtype is `object` with values that match an ordinal scale (`'low' / 'medium' / 'high'`, `'never' / 'rarely' / 'sometimes' / 'often' / 'always'`)

Edge cases:

- Likert 1-5 → ordinal
- Survey responses encoded as 1-7 → ordinal

## Categorical

A column is **categorical** if:

- dtype is `object` / `category` AND unique count ≤ 50 AND modal frequency > 1%, OR
- dtype is `int64` with unique count ≤ 20 but values are NOT monotonic / not an obvious ordinal scale

Edge cases:

- 50-state US column (unique count 50) → categorical (high but bounded)
- ZIP-code column (unique count > 1000) → text-as-category — flag

## Text

A column is **text** if:

- dtype is `object` AND unique count > 100, OR
- dtype is `object` AND average string length > 30 characters, OR
- dtype is `object` AND ratio of unique to row count > 0.5 (high-cardinality)

Treating text as categorical is the cardinality-explosion anti-pattern; this rule catches it.

## Default

If none of the above match, classify as **categorical-with-warning** and surface the column for human review.

## Combined examples

| Column name | dtype | Unique count | Sample values | Inferred class |
|---|---|---|---|---|
| `patient_id` | int64 | 50000 (= row count) | 100001, 100002, 100003 | ID |
| `age` | int64 | 102 | 23, 45, 67, 250, -1 | continuous (range alarm) |
| `sex` | object | 3 | F, M, U | categorical |
| `is_smoker` | int64 | 2 | 0, 1 | boolean |
| `severity` | int64 | 5 | 1, 2, 3, 4, 5 | ordinal |
| `diagnosis` | object | 4823 | "Type 2 DM", "Hypertension", ... | text |
| `signup_date` | object | 14322 | "2024-01-15", "2024-01-16" | datetime |
| `risk_score` | float64 | 49872 | 0.12, 0.87, 0.45 | continuous (derived-name flag) |
| `state` | object | 50 | CA, NY, TX, ... | categorical |
| `zip` | object | 14021 | "94103", "10001" | text-as-category (flag) |
