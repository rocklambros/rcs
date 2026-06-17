---
name: validating-temporal-fields
description: >
  Validates date/time fields in incident corpora, event logs, or any temporal dataset.
  Catches future-dated records, max-year-fallback bugs, and event-vs-disclosure-date
  confusions. Use whenever the user is ingesting a dataset with year/date fields,
  especially incident registries, vulnerability disclosures, or news-derived corpora
  where the source text may contain spurious future-year mentions (for example,
  'the 2027 election' appearing in a 2024 article). Recommends reject-future,
  min-year-fallback, and event-vs-disclosure-date separation as the three invariants.
version: 0.1.0
status: shipped
track: workflow
audience: [data-engineer, data-scientist, security-eng]
evidence:
  - genai_agentic_incidents
last-updated: 2026-05-23
---

# Validating Temporal Fields

## When to use

Trigger this skill when the user asks for or implies one of:

- Ingesting a dataset with date / year / timestamp fields where the source data is text-derived (incident registries, vulnerability disclosures, news corpora, regulatory filings)
- Reporting a record with a future date that "should not be future-dated"
- Building a schema validator for an event log, audit trail, or registry
- Diagnosing why a recently-ingested record has a date that does not match the source URL's publication date
- Designing a pipeline where the same record could have multiple plausible dates (event date vs. disclosure date vs. reporting date)

## When NOT to use

Skip this skill and hand off when:

- The dataset is forecasting / scheduling / planning data where future dates are legitimate (calendar appointments, scheduled jobs, predicted demand)
- The work is pure datetime arithmetic outside any ingest pipeline (e.g., "what is the difference in days between two dates")
- The dates come from a single authoritative structured field (e.g., a database `created_at` timestamp) where there is no source-text ambiguity

## Quick start

User says: "I'm ingesting the AIID incident corpus into our pipeline. Each record has an `incident_date` field. What validation should I add?"

Skill response: produces a 3-invariant validation block. (1) Reject any row with `incident_date > today()`. (2) When the year cannot be determined from a trustworthy structured field, fall back to the MIN plausible year, never the MAX year mentioned in the text. (3) Maintain `event_date` and `disclosure_date` as separate fields; surface both in the schema. Includes a Pydantic / Pandera example.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| date_fields | list of strings | yes | — | The date / timestamp / year fields in the dataset schema (e.g., `[incident_date, disclosure_date, ingested_at]`). |
| today_source | "env_var" \| "datetime_now" \| "frozen" | no | "env_var" | Source of the "today" boundary. For CI determinism, use an env var (e.g., `PIPELINE_TODAY=2026-05-23`); for production, `datetime_now()` is acceptable. |
| reject_or_warn | "reject" \| "warn" \| "quarantine" | no | "reject" | What to do on a temporal invariant violation. Reject blocks ingest; quarantine sends the row to a review bucket. |
| min_plausible_year | integer | no | 1970 | Lower bound for sanity-checking year fields. Records older than this are flagged as data-entry errors. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as the validation is built:

```
Temporal validation progress:
- [ ] Invariant 1: every date_field has date_field ≤ today (reject future-dated rows)
- [ ] Invariant 2: when year is text-extracted, fall back to MIN plausible year (not MAX)
- [ ] Invariant 3: event_date and disclosure_date are SEPARATE fields, never conflated
- [ ] CI determinism: "today" comes from a single deterministic source per run
- [ ] Per-invariant test cases written and passing
```

### Invariant 1: Reject future-dated rows

For every field that represents an event timestamp:

```python
if record.event_date > pipeline_today:
    raise TemporalValidationError(
        f"event_date {record.event_date} is in the future (today: {pipeline_today})"
    )
```

This catches the most common ingest bug: a text extractor that pulls "2027" from a sentence like "the 2027 election" and stamps it as the event year for a 2024-disclosed incident.

### Invariant 2: Min-year-fallback

When a record's year cannot be determined from a structured field and must be inferred from free text:

- WRONG: take the MAX year mentioned in the text (catches future-year contextual mentions)
- RIGHT: take the MIN plausible year, often the disclosure date, or mark the field as `null` for manual review

See `reference/year-fallback-bug-pattern.md` for the specific genai_agentic_incidents 2027-election bug write-up.

### Invariant 3: Event-date vs. disclosure-date separation

Always maintain BOTH:

```python
class Incident(BaseModel):
    event_date: date | None        # when the incident happened
    disclosure_date: date           # when the incident was publicly reported
    ingested_at: datetime           # when the pipeline saw it

    @model_validator(mode="after")
    def event_le_disclosure(self):
        if self.event_date and self.event_date > self.disclosure_date:
            raise ValueError(f"event_date {self.event_date} > disclosure_date {self.disclosure_date}")
        return self
```

Conflating event date and disclosure date masks Invariant 2 bugs: a 2024-disclosed incident with `event_date = 2027` (from the year-extractor bug) only looks wrong if there is a separate disclosure_date to compare against.

### Step 4: CI determinism

The validator's "today" must come from a single deterministic source per run — an env var like `PIPELINE_TODAY=2026-05-23` is better than `datetime.now()` per call. Otherwise the same input data can pass on one run and fail on the next if it straddles midnight.

## Outputs

A validation schema and a per-record validation report:

1. **Schema definition** — Pydantic / Pandera / dataclass with the 3 invariants encoded as validators
2. **Per-record report** — when validation is run on a batch: `{passed: N, rejected: [...], quarantined: [...]}` with the failing invariant named per rejected row
3. **CI-friendly determinism** — explicit `today` source documented in the pipeline config

## Failure modes

Known pitfalls in temporal validation and how this skill catches them:

- **Max-year-fallback bug** — a text-extractor pulls the MAX year mentioned in source text (e.g., "the 2027 election" in a 2024 article → record stamped 2027). Caught by: Invariant 2 (min-year-fallback) + Invariant 1 (reject-future).
- **Event-disclosure conflation** — a single `date` field used for both event and disclosure masks the year-fallback bug. Caught by: Invariant 3 (separate fields) + cross-field validator `event_date ≤ disclosure_date`.
- **Non-deterministic "today"** — `datetime.now()` called per-row means the same data passes on one run and fails on the next near midnight. Caught by: explicit `today_source` argument; recommendation to use env var in CI.
- **Silent timezone drift** — naive `datetime` objects compared across timezones. Caught by: prefer `date` over `datetime` for human-event fields; if `datetime` is needed, require timezone-aware values.
- **Forecasting / scheduling misclassification** — applying reject-future to legitimate calendar appointments. Caught by: anti-trigger guidance in "When NOT to use".

## References

- `reference/year-fallback-bug-pattern.md` — write-up of the genai_agentic_incidents 2027-election bug (AIID corpus)
- `reference/pydantic-temporal-validator-example.md` — working code template for the 3-invariant validator
- [Pydantic model validators](https://docs.pydantic.dev/latest/concepts/validators/) — upstream reference for cross-field validation
- [Pandera schema validation](https://pandera.readthedocs.io/) — alternative if the pipeline is dataframe-shaped

## Examples

### Example 1: AIID incident corpus ingest (happy-path)

Input: "I'm ingesting the AIID incident corpus into our pipeline. Each record has an `incident_date` field. What validation should I add?"

Output: Skill specifies the 3 invariants. Reject-future on `incident_date`. Maintain `disclosure_date` as a separate field with `incident_date ≤ disclosure_date` cross-field validator. When the year is text-extracted, fall back to MIN year (typically disclosure year), never MAX. Includes a Pydantic snippet from `reference/pydantic-temporal-validator-example.md`.

### Example 2: Suspect future-dated record (edge-case)

Input: "One of our records has incident_date = 2027-11-03 but the disclosure date is 2024-09-15. The text mentioned 'the 2027 election' as context. Is the record valid?"

Output: Skill identifies this as the year-fallback bug pattern. The 2027 mention was contextual / forecast in the source text, not the event year. Recommends correcting `incident_date` to the disclosure year (2024) or marking it `null` pending manual review. Cites the max-year-fallback anti-pattern explicitly.

### Example 3: Scheduling reminder (anti-trigger)

Input: "Schedule a reminder for January 15, 2027 to renew the SSL cert."

Output: Skill does NOT engage the temporal-validation workflow. Explains that future dates in scheduling / planning contexts are legitimate; the reject-future invariant applies to historical event ingest, not to forward-looking scheduling. Hands off.

## See also

- `workflow/auditing-source-provenance` — pairs with this: provenance.json captures the source URL and pull date, which feeds disclosure_date
- `workflow/deduplicating-records` — temporal fields are often used as dedup keys; both skills together harden registry ingest
- `workflow/auditing-data-quality` — broader per-column audit; this skill is the date-specific deep-dive

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from the genai_agentic_incidents CHANGELOG.md 2.0.0 entry documenting the AIID 2027-election year-fallback bug
