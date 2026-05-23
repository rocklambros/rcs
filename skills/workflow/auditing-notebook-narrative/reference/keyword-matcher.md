# Keyword matcher — directional claim detection

The audit's hit rate depends entirely on the keyword set. This file documents the default set, the regex shapes, and the negation-handling rule.

## Default direction categories

| Category | Keywords (regex-safe stems) | Direction |
|---|---|---|
| Increase | `increase`, `rise`, `grow`, `climb`, `gain`, `improve(d)?`, `go(es)? up`, `trend(s|ing|ed)? up(ward)?`, `higher`, `highest`, `exceed(s|ed)?`, `above`, `more`, `expand(s|ed)?` | up |
| Decrease | `decrease`, `fall`, `drop`, `decline`, `lose`, `lost`, `go(es)? down`, `trend(s|ing|ed)? down(ward)?`, `lower`, `lowest`, `below`, `less`, `shrink(s)?`, `shrank` | down |
| Comparison | `outperform(s|ed)?`, `underperform(s|ed)?`, `better than`, `worse than`, `best`, `worst` | comparison (target-dependent) |
| Convergence | `converge(s|d)?`, `diverge(s|d)?`, `stabilize(s|d)?`, `plateau(s|ed)?`, `saturate(s|d)?` | converge / diverge |
| Monotonicity | `monotonic(ally)?`, `strictly (in\|de)creasing`, `non-monotonic` | monotonicity claim |

All matched on **whole-word, case-insensitive** boundaries. Use `\b` around each pattern.

## Negation handling

For each matched keyword, scan the **5 tokens preceding** for any of:

- `not`, `n't`, `no`, `never`, `without`, `failed to`, `did not`, `does not`, `cannot`, `was not`

If a negation is found, **invert the direction** (up → down, down → up, comparison → ambiguous). Mark the claim as `negated: true` in the record so the report can show the original prose alongside the inverted interpretation.

5 tokens is a heuristic. Cross-clause negations (*"we expected accuracy to improve, but it did not"*) defeat it; in those cases the audit emits `verdict: needs-manual-review` and lets the user adjudicate.

## Magnitude extraction

When the prose includes a numeric value adjacent to the keyword (e.g., `"accuracy improved from 0.78 to 0.91"`), extract both numbers and the comparison direction. The audit can then compare against numeric outputs.

Regex sketch:

- `from\s+([\d.eE+-]+)\s+to\s+([\d.eE+-]+)` — explicit from/to pair
- `(by|of)\s+([\d.eE+-]+%?)` — magnitude only
- `([\d.eE+-]+)\s+(higher|lower|more|less)\s+than\s+([\d.eE+-]+)` — comparative

Use Python's `re.finditer` so a single sentence with multiple numbers contributes multiple records.

## False-positive guards

- **Generic English uses**: "we lower the learning rate" — `lower` matches but the claim is procedural, not a result. Suppress when the sentence subject is the **author** (first-person plural `we`) and the keyword is the **verb in an action clause**, not a comparison. Default rule: if the matched keyword is preceded by `we`, `I`, or `our team` within the same clause, mark the claim as `procedural` rather than a comparison.
- **Quotations / definitions**: a sentence inside a code block (triple backticks within markdown) should be skipped. The matcher walks markdown but excludes fenced-code regions.
- **Citations**: "Smith et al. (2021) found that X improved" — this is reporting other people's results, not a claim about THIS notebook. Suppress when an attribution pattern (`<Name> et al`, `<Name> \(\d{4}\)`, `cited in`, `per <ref>`) is in the same sentence. The audit flags these as `cited` rather than `claim`.

## Adding custom keywords

The skill accepts `direction_keywords` as a list of strings. Each string is appended to the default set under a synthetic category. The user may write:

```yaml
direction_keywords:
  - recovered
  - degraded
  - saturated
```

The matcher treats these as `up`, `down`, `converge` respectively if their stems match the default semantic — otherwise they default to `comparison`. For full control, users can author a custom matcher and pass it explicitly; the audit script in `audit-script.py` shows the override point.
