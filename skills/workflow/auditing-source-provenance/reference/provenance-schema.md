# Provenance Schema and Transform-Survival Rules

The minimum-viable per-record provenance schema, plus the rules every downstream transform must obey to preserve it.

## Minimum-viable schema (v1)

Attach this JSON object to every ingested record under the field name `provenance`. Either as an inline field on the row, or as a sidecar JSON keyed by row ID.

```json
{
  "source_repo": "string (URL or repo identifier)",
  "source_ref": "string (tag, branch name, or version label)",
  "source_sha": "string (commit SHA or content hash)",
  "pull_date": "string (ISO-8601 UTC, e.g., 2026-05-23T14:32:00Z)",
  "adapter_version": "string (ingest-script identifier @ version)",
  "fetch_method": "git-clone | http-api | s3 | scrape | file-upload",
  "license": "string (SPDX identifier or short text)",
  "row_locator": "string (path / ID within the source)"
}
```

### Field rules

| Field | Required | Rule |
|---|---|---|
| source_repo | yes | Stable, resolvable identifier. URL, git remote, S3 bucket+key, or DOI. Not a local path. |
| source_ref | yes | Explicit ref. `main` / `latest` / `HEAD` are findings — re-pin to a tag, SHA, or pinned API version. |
| source_sha | yes | The actual content SHA at pull time. For Git: `git rev-parse HEAD` after clone. For HTTP API: response `ETag` or `Last-Modified`. For S3: object version-id. |
| pull_date | yes | UTC ISO-8601 with Z suffix. Comes from a single source (env var or `_utc_now_iso()`), not `datetime.now()` per call. |
| adapter_version | yes | The ingest script's identifier plus SemVer. Bump on any schema-mapping change. |
| fetch_method | yes | One of the allowed values. Useful for replay and for compliance ("scraped" carries different legal weight than "API call"). |
| license | yes | SPDX identifier if available (CC-BY-4.0, MIT, Apache-2.0). If proprietary, the contract clause that allows ingest. |
| row_locator | yes | Sufficient to point a reviewer at the exact upstream row. Path, ID, query string, or coordinate. |

## Transform-survival rules

Every downstream transform must preserve provenance per these rules:

### Filter / select

Pass `provenance` through unchanged. If you `df[df.severity > 5]`, the surviving rows keep their original provenance.

### Map / rename

Pass `provenance` through unchanged. Renaming a domain column does not change which upstream row produced it.

### Merge / join (record-level)

If joining two rows from two sources, the result row carries a LIST of two provenance entries:

```json
{
  "provenance": [
    { "source_repo": "...", "source_sha": "...", ... },
    { "source_repo": "...", "source_sha": "...", ... }
  ]
}
```

NOT a single overwritten value. NOT the first one. List-of-entries.

### Dedupe / collapse

If `N` rows collapse to 1, the survivor carries the union of the N provenance entries as a list. Order: keep stable (e.g., by `pull_date` ascending), so audits across runs are deterministic.

### Aggregate / groupby

When a groupby produces a summary row from many input rows, the summary carries an `aggregate_provenance` field listing all contributing provenance entries. Per-source counts are useful: `{"AIID": 12, "OECD-AIM": 4, "AIAAIC": 1}`. The full list goes in a sidecar if it would bloat the row.

### Augment / derive (new computed columns)

If a new column is derived from existing columns (e.g., `severity_score = f(severity, asset_value)`), `provenance` does NOT change. The derivation is internal; the upstream attribution is unchanged.

### Augment / derive (new column from external lookup)

If a new column is filled from an external source (e.g., `cve_cvss = lookup(cve_id)`), the derived column's source goes into a SEPARATE provenance entry alongside the row's existing one:

```json
{
  "provenance": [{ "source_repo": "...", ... }],
  "field_provenance": {
    "cve_cvss": { "source_repo": "https://nvd.nist.gov", "pull_date": "...", ... }
  }
}
```

## Anti-patterns

**Stamping at transform time, not ingest time.** Every merged row carries `pull_date == build_date`. Loses the actual upstream snapshot time.

**Floating ref.** `git clone` without `--branch <tag>` resolves to default-branch HEAD at clone time. Re-running 30 days later silently pulls different content.

**Single provenance after merge.** Two records merged → result keeps the first source's provenance and silently drops the second. Audit cannot reconstruct.

**Dropping `provenance` in a select.** `df[['id', 'text', 'severity']]` drops the `provenance` column. Audit-trail loss.

**Provenance written to a separate file with no row-key linkage.** "We have an ingest log" is not provenance. Each row must point at its own provenance entry, deterministically.

**`source_sha` = SHA of the ingest script** (copy-paste from `adapter_version`). Re-derive: the adapter SHA tells you what code ran; the source SHA tells you what data was ingested. Both are needed; they are not the same.

## Verification queries

Run these against the dataset to confirm provenance is intact:

```python
import pandas as pd

df = pd.read_parquet("data/corpus.parquet")

# 1. Every row has provenance
assert df["provenance"].notna().all(), "rows missing provenance"

# 2. Every provenance has the required keys
required = {"source_repo", "source_ref", "source_sha", "pull_date", "adapter_version"}
for p in df["provenance"]:
    if isinstance(p, list):
        for entry in p:
            assert required <= set(entry.keys()), f"missing keys: {required - set(entry.keys())}"
    else:
        assert required <= set(p.keys()), f"missing keys: {required - set(p.keys())}"

# 3. No floating refs
floating = {"main", "master", "latest", "HEAD", ""}
for p in df["provenance"]:
    entries = p if isinstance(p, list) else [p]
    for e in entries:
        assert e["source_ref"] not in floating, f"floating ref: {e['source_ref']}"

# 4. Pull dates are in the past
import datetime as dt
now = dt.datetime.now(dt.timezone.utc)
for p in df["provenance"]:
    entries = p if isinstance(p, list) else [p]
    for e in entries:
        pd_date = dt.datetime.fromisoformat(e["pull_date"].replace("Z", "+00:00"))
        assert pd_date <= now, f"future pull_date: {e['pull_date']}"
```
