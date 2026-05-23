# Semantic-class detection — extended heuristics

These heuristics are deliberately conservative: when in doubt, flag the column as `ask user` rather than committing to a guess. The cost of a wrong inference (one-hot-encoding a high-cardinality ID, treating an ordinal severity scale as continuous) is high.

## ID

Signals:

- Cardinality equals row count (one-per-row) or matches a known grouping (one-per-patient, one-per-order)
- Column name contains `id`, `uuid`, `key`, `_pk`, `_fk`
- Values match a structured format (UUID v4, integer ascending, alphanumeric with fixed length)

Decision rule: if cardinality ≥ 0.95 × row count AND name signals ID → class = ID with high confidence.

## Categorical (nominal)

Signals:

- Cardinality ≤ 50 distinct values
- Values are strings or low-cardinality integers
- No inherent order
- Same set of values appears repeatedly across rows

Decision rule: if cardinality ≤ 50 AND not numeric-continuous → class = categorical.

Risk: a "categorical" column with cardinality > 100 is almost certainly not categorical — see the cardinality alarm.

## Continuous

Signals:

- Numeric dtype (float, int)
- Cardinality is high relative to row count (e.g. ≥ 100 distinct values on a 10k-row dataset)
- Values form a continuous-looking distribution

Decision rule: if numeric AND cardinality ≥ 100 AND not ID-named → class = continuous.

Edge case: integer columns with cardinality 30–100 may be ordinal (Likert, severity scores) rather than continuous — flag as ask-user.

## Ordinal

Signals (the audit cannot reliably detect ordinal from data alone):

- Numeric or string with a known scale (Likert 1–5, severity low/medium/high, education level)
- Column name hints (`severity`, `grade`, `level`, `rating`, `priority`)
- Distinct values are few and seem ordered

Decision rule: if numeric cardinality between 3 and 30, OR name signals an ordering → flag as `ask user — could be ordinal`. Never auto-assign.

## Text

Signals:

- String dtype, high cardinality
- Long mean character length (> 50)
- Irregular structure — no fixed format

Decision rule: if string AND mean length > 50 AND cardinality > 50% of row count → class = text.

Risk: a text column ingested as "categorical" leads to cardinality explosion downstream.

## Datetime

Signals:

- Parseable as date or datetime by the data library (pandas `to_datetime`, polars, R `as.POSIXct`)
- Column name contains `date`, `time`, `_at`, `_on`, `created`, `updated`, `modified`

Decision rule: if name signals temporal AND > 90% of values parse cleanly → class = datetime.

Hand off to `workflow/validating-temporal-fields` for the temporal-specific audit (future dates, year-fallback, event vs disclosure).

## Boolean

Signals:

- Exactly 2 distinct values (after dropping nulls)
- Values are commonly-encoded boolean pairs: `{0, 1}`, `{True, False}`, `{"yes", "no"}`, `{"Y", "N"}`, `{"t", "f"}`

Decision rule: if distinct count = 2 AND values match a known pair → class = boolean.

Edge case: a column with exactly 2 distinct values may also be categorical (gender coded as two strings); the boolean class is appropriate only when the values pair-encode a true/false signal.

## When the audit cannot infer

Mark the column `unknown — ask data producer`. This is the right answer more often than people are comfortable with. A wrong inference propagates silently through the modeling pipeline; an `unknown` flag forces the user to make a deliberate decision.
