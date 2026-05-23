# `provenance.json` schema

Every output artifact gets a sibling `provenance.json`. The schema is intentionally small so reviewers can read it without scrolling.

## Required fields

| Field | Type | Meaning |
|---|---|---|
| `source_url` | string | The canonical URL the source data came from. API endpoint, git URL, S3 URI, etc. |
| `source_commit_sha` | string \| null | Git SHA of the source when available. `null` when the source has no commit notion (e.g., a public API without versioned snapshots). |
| `pulled_at` | string (ISO 8601 UTC) | When the source was fetched. The ONE legitimate floating timestamp in the system; tolerate it in the drift check. |
| `adapter_version` | string (SemVer) | The version of the ingest adapter that produced this artifact. Bump when the adapter's canonicalization rules change. |
| `input_hashes` | object | Mapping from input file path → `sha256:<hex>`. Reviewers can verify the inputs without re-downloading. |
| `output_hash` | string | `sha256:<hex>` of the canonicalized output artifact. Redundant with `hashes.txt` but convenient for human inspection. |
| `row_count` | integer | Number of records in the output. Cheap to compute; catches "the artifact silently truncated" failures. |

## Optional fields

| Field | When to include |
|---|---|
| `source_schema_version` | When the source publishes a schema version (e.g., OpenAPI version). Catches "source added a field" as source drift, not pipeline drift. |
| `transform_chain` | Ordered list of transform names applied (e.g., `["normalize_dates", "dedupe", "sort_by_id"]`). Useful when the same source feeds multiple downstream artifacts and reviewers need to know which steps produced this one. |
| `notes` | Freeform text — typically a one-line description of what changed since the last bump. Manual, but cheap. |

## Example

```json
{
  "source_url": "https://incidentdatabase.ai/api/v1/incidents",
  "source_commit_sha": null,
  "pulled_at": "2026-05-23T10:00:00Z",
  "adapter_version": "0.3.1",
  "input_hashes": {
    "incidents.json": "sha256:7a8f3b2..."
  },
  "output_hash": "sha256:abc1234...",
  "row_count": 12348,
  "source_schema_version": "v2.1",
  "transform_chain": ["normalize_dates", "dedupe_on_incident_id", "sort_by_incident_id"],
  "notes": "Added GenAI incident filter; row_count up from previous run because of newly-published incidents."
}
```

## What NOT to put here

- The actual data records — those go in the artifact, not the provenance
- A timestamp inside the data — see SKILL.md Step 5; this is the one place timestamps are tolerated
- Author or operator name — privacy hazard for shared artifacts; use git commits for that

## Versioning the schema

`provenance.json` itself is versioned via the `adapter_version` field. When you change the schema (add or remove required fields), bump the major version of the adapter. Reviewers can then immediately see which schema generation produced any given artifact.

## How the drift check uses this

The drift check:

1. Re-runs the pipeline
2. Compares the new `output_hash` against the previously-committed `output_hash`
3. Honors the `tolerate` argument to exclude specific fields (default: `["pulled_at"]`)
4. Fails if any non-tolerated field changed

When the drift check FAILS, the first place to look is the new `provenance.json` vs. the old one: `source_schema_version` changed? Source drift. `adapter_version` changed? Adapter bumped (the change is intentional; rebase the committed hash). Neither changed? Real determinism violation; debug.
