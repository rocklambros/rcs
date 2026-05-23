# Ordered dedup-rule template

Fill in one row per rule, from highest confidence to lowest. Rules below the `review_threshold` produce **borderline** edges that go to a human reviewer; rules at or above the threshold produce **merge** edges that flow into the connected-components collapse.

| Rule # | Match expression | Confidence (0–1) | Expected precision | Notes |
|---|---|---|---|---|
| 1 | `cve_id` equality | 1.00 | ~1.00 (when both records have a CVE id) | High-recall when populated; low coverage |
| 2 | Canonical URL equality after URL normalization | 0.95 | ~0.98 | Normalize: lowercase host, strip trailing `/`, sort query keys |
| 3 | `doi` equality | 0.90 | ~0.95 | Strip `https://doi.org/` prefix before compare |
| 4 | `Jaro-Winkler(title) ≥ 0.92` AND `abs(event_date_a − event_date_b) ≤ 365 days` | 0.75 | ~0.85 | Compound rule; both clauses must hold |
| 5 | `author` exact match AND `publication_date` exact match | 0.60 | ~0.70 | Borderline — goes to human review |

## Naming conventions

- `Rule N` matches the column header used in the dedup diff JSON's `rules_fired` field
- `Confidence` is the rule's prior — not the per-pair similarity score. The threshold gate uses confidence, not the score.
- `Notes` documents any normalization or pre-processing assumed by the rule. If the assumption breaks, the rule's confidence is invalid.

## When to add a new rule

- A new source contributes a previously-unseen identifier (e.g. ORCID for authors): add a high-confidence rule for the new identifier
- Existing rules produce a high false-negative rate on a known sub-population: add a more permissive rule with a confidence appropriate for the precision

## When to remove a rule

- A rule fires zero times in production for two consecutive runs: it is either unreachable or its data is missing — investigate before deletion
- A rule fires but every match also matches a higher-confidence rule: the lower rule is redundant; delete it

## Versioning

Bump the rule-table version any time a rule is added, removed, or has its confidence changed. The dedup diff JSON's `reproducibility footer` records the rule-table version so a historical merge can be replayed.
