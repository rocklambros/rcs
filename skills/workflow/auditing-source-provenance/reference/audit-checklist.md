# Provenance Audit Checklist

A printable per-source checklist. Run through this for every upstream source the ingest pipeline touches.

## Per-source intake

For each upstream source:

- [ ] Source identifier captured (URL / repo / S3 bucket+key / API endpoint / DOI)
- [ ] Ref is pinned (tag, SHA, or pinned API version) — NOT `main` / `latest` / `HEAD`
- [ ] SHA is the upstream's actual content SHA, NOT the ingest script's SHA
- [ ] Pull date is UTC ISO-8601 from a single source (env var or single `_utc_now_iso()` call), NOT `datetime.now()` per call
- [ ] Adapter version follows SemVer; bumped on every schema-mapping change
- [ ] Fetch method is one of: git-clone, http-api, s3, scrape, file-upload
- [ ] License recorded as SPDX identifier (or proprietary-clause reference)
- [ ] Row locator points to the specific upstream row (path / ID / query)

## Per-transform survival

For each downstream transform:

- [ ] `provenance` column is explicitly included in the column-select / aggregate-spec
- [ ] Merge / join: result row carries a LIST of provenance entries (not single overwritten value)
- [ ] Dedupe / collapse: survivor carries the union as a list, ordered deterministically
- [ ] Groupby summary: `aggregate_provenance` field lists all contributing provenance entries
- [ ] External lookups: derived column's source goes into `field_provenance`, not main `provenance`

## Per-output validation

For 5+ randomly sampled output rows:

- [ ] `provenance` exists and is non-empty
- [ ] All required keys present (`source_repo`, `source_ref`, `source_sha`, `pull_date`, `adapter_version`)
- [ ] `pull_date` is in the past (rule out year-fallback / clock-skew bugs)
- [ ] `source_sha` differs from `adapter_version`'s SHA (copy-paste sanity)
- [ ] `source_ref` is NOT a floating ref (`main` / `latest` / `HEAD` / empty)
- [ ] `license` is recorded

## CI gate

- [ ] Pytest / GitHub Actions check fails the build if any row in the dataset lacks provenance
- [ ] Check runs on every PR that touches the ingest pipeline OR the data files
- [ ] Check failure messages name the offending row(s) so the author can fix immediately

## Recovery / backfill (for existing datasets)

If auditing an existing dataset that lacks provenance:

- [ ] Identify which fields can be backfilled from git history (e.g., `pull_date` from the ingest commit date)
- [ ] Identify which fields can be backfilled from the upstream (e.g., `source_sha` from the upstream's git log around the pull date)
- [ ] Identify which fields are unrecoverable
- [ ] Quarantine unrecoverable rows under `provenance_completeness: partial`
- [ ] Re-ingest forward with the full schema
