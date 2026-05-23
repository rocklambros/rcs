# The max-year-fallback bug pattern

A specific class of bug that appears in any ingest pipeline that text-extracts year fields from free-text source data.

## The bug

A text extractor — regex, NER model, or LLM prompt — is asked: "what year did this incident happen?" When the structured field is missing, the extractor scans the article text for year mentions and picks one.

**Wrong heuristic:** pick the MAX year mentioned. Reasoning: "the most recent year is most likely the event year."

**Why it fails:** articles routinely mention future years in context — "the 2027 election cycle," "the 2030 emissions target," "the upcoming 2026 World Cup." A 2024-disclosed incident article that mentions "the 2027 election" gets stamped with `event_date = 2027` and silently becomes a future-dated record.

## The fix

Two parts:

1. **Reject-future invariant** — any `event_date > today` is an automatic rejection, regardless of how the date was extracted. This catches the bug at the latest possible point.
2. **Min-year-fallback heuristic** — when text-extracting a year and multiple candidates exist, prefer the EARLIEST plausible year (typically the disclosure / publication date of the source itself), not the latest. This catches the bug at extraction time before invariant 1 has to fire.

Even better: when the year is ambiguous, mark the field `null` and send the row to a manual-review queue. Silent inference is the bug; explicit "unknown" is the fix.

## Provenance: genai_agentic_incidents 2.0.0

The 2.0.0 ingest of the AIID (AI Incident Database) corpus into `genai_agentic_incidents` exhibited this exact bug. The original AIID records had clean disclosure dates but the year-extractor on the text body picked the MAX year mentioned in each article. Records about Cambridge Analytica (event year 2014, disclosure 2018) got stamped 2024 because the article body mentioned the 2024 election. Records about 2020-era model launches got stamped 2027 because the body mentioned the 2027 election cycle.

The fix landed in 2.0.0 changelog: reject-future + min-year-fallback + separate event-date / disclosure-date fields.

## Detection: how to find this bug in an existing corpus

```sql
-- any future-dated event is the bug
SELECT * FROM incidents WHERE event_date > CURRENT_DATE;

-- event-after-disclosure is also the bug (text body had later years than the source URL date)
SELECT * FROM incidents WHERE event_date > disclosure_date;

-- year-cluster anomaly: more events in next year than this year
SELECT EXTRACT(YEAR FROM event_date) AS yr, COUNT(*)
  FROM incidents
  GROUP BY yr
  ORDER BY yr DESC
  LIMIT 10;
```

If next year shows ANY events, the max-year extractor is misfiring.

## Related anti-patterns

- **Disclosure-date overwrite by event-date extractor** — when the extractor populates BOTH fields with the same value, the cross-field validator cannot fire. Always populate them from different sources.
- **Free-form date strings** — accepting `"approximately 2024"` as a date. Either reject as `null` or parse to a date with explicit precision (`year_only`, `quarter`, `month`).
