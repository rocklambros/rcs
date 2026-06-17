---
name: auditing-source-provenance
description: >
  Audits a data-ingest pipeline for source provenance — verifies that every
  ingested record carries a structured provenance record (source repo / URL,
  source SHA or version, pull date, adapter version, license, fetch method)
  and that the provenance is preserved through every downstream transform.
  Use whenever ingesting external data into a corpus, registry, or dataset;
  whenever a record's source cannot be traced back to a specific upstream
  revision; whenever auditing a dataset for "where did this come from?";
  or whenever a regulatory request (DSR, FOIA, audit log) requires showing
  the origin of every record.
version: 0.1.0
status: shipped
track: workflow
audience: [data-engineer, data-scientist, security-eng]
evidence:
  - genai_agentic_incidents
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Auditing Source Provenance

## When to use

Trigger this skill when the user asks for or implies one of:

- Ingesting external data (CSV / JSON / API pull / scraped corpus / registry merge) into a project's working dataset
- Building or extending an incident registry, vulnerability corpus, knowledge base, or any multi-source aggregation
- Diagnosing "where did this row come from?" or "why does this record disagree with the upstream?" mid-pipeline
- Preparing a dataset for a regulatory or audit request — DSR, FOIA, SOC 2 evidence, IRB submission, paper-replication
- Reviewing a teammate's ingest script before merge — looking for the absence of provenance attachment
- Hardening an existing pipeline that lost provenance during a transform (groupby / dedupe / join collapsed `source` columns)

## When NOT to use

Skip this skill and hand off when:

- The dataset is pure-synthetic / simulated (provenance is the seed + generator version, not an upstream URL) — different skill: `ml-datasci/auditing-synthetic-data-utility` (planned)
- The dataset is a well-known public benchmark (MNIST, ImageNet, SQuAD) where provenance is the published citation, not a per-record artifact
- The user is asking about training-data attribution for an already-trained model (different skill: `security/verifying-training-data-erasure`, planned)
- The work is throwaway exploration on a single static CSV that the user owns and will not redistribute

## Quick start

User says: "We're merging AIID, OECD AIM, and AIAAIC incident data into one corpus for training a classifier. Audit my ingest script."

Skill response: requests the ingest script + one sample output row. Checks for a `provenance` field (or sidecar `provenance.json`) attached at ingest, carrying source-repo + source-SHA + pull-date + adapter-version + license. Verifies the provenance survives the merge / dedupe / transform steps. Flags any record whose provenance is empty, partial, or stamped at transform-time rather than at ingest-time.

Minimum-viable provenance record (attached to every ingested row, OR as a sidecar JSON keyed by row ID):

```json
{
  "source_repo": "https://github.com/responsible-ai-collaborative/aiid",
  "source_ref": "v3.2.1",
  "source_sha": "a4f1c92b",
  "pull_date": "2026-05-23T14:32:00Z",
  "adapter_version": "ingest_aiid.py@1.4.0",
  "fetch_method": "git-clone",
  "license": "CC-BY-4.0",
  "row_locator": "incidents/aiid-1234.json"
}
```

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| ingest_script | path | yes | — | The script / notebook / pipeline file that pulls data from upstream. |
| sample_output | path | no | — | One representative output row (JSON / CSV row / Parquet sample) so the skill can check whether provenance was actually attached. |
| sources | list | no | inferred | Names of the upstream sources being merged. Inferred from the script if not provided. |
| level | "ingest" \| "row" \| "both" | no | both | Provenance granularity. `ingest` = one record per ingest run; `row` = one record per output row; `both` = recommended (cheap; survives transforms). |
| audit_existing_dataset | path | no | — | If set, also audit an already-built dataset by sampling rows and checking provenance completeness. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as the audit progresses:

```
Provenance audit progress:
- [ ] Inventory every upstream source the script touches (URL, repo, API endpoint)
- [ ] Confirm each ingest call captures source-ref + source-SHA + pull-date + adapter-version
- [ ] Confirm provenance is attached at ingest, not stamped at transform-time
- [ ] Confirm provenance survives downstream transforms (merge / dedupe / groupby / join)
- [ ] Sample 5+ output rows; verify each has a non-empty provenance field
- [ ] Confirm license / redistribution-rights are recorded per source
- [ ] Confirm CI gate fails the build if any new record lacks provenance
```

### Step 1: Inventory upstream sources

Read the ingest script. For every `requests.get(...)`, `pd.read_csv(URL, ...)`, `git clone`, `boto3.s3.get_object`, API client call, or web scrape, record:

- The source identifier (URL, repo, S3 bucket+key, API endpoint)
- The version / ref / SHA / commit / API version being pulled
- The fetch method (git, http, S3, API, scrape)

If the script pulls from `main` / `latest` / a moving tag without pinning, that is a finding (see `reference/provenance-schema.md` for the pinning rule).

### Step 2: Confirm provenance is attached at ingest time

The correct pattern: the function that fetches a record IMMEDIATELY attaches a provenance object before returning. Example (Python):

```python
def fetch_aiid_record(record_id: str, repo_sha: str, adapter_version: str) -> dict:
    raw = _http_get(f"https://api.aiid.example/incidents/{record_id}")
    return {
        **raw,
        "provenance": {
            "source_repo": "https://api.aiid.example",
            "source_ref": "v3.2.1",
            "source_sha": repo_sha,
            "pull_date": _utc_now_iso(),
            "adapter_version": adapter_version,
            "fetch_method": "http-api",
            "license": "CC-BY-4.0",
            "row_locator": f"incidents/{record_id}",
        },
    }
```

Anti-pattern (flag this): provenance stamped in a post-processing step (after dedupe / after merge). By then, the record may have been combined with another source, and the provenance is ambiguous or wrong.

### Step 3: Confirm provenance survives transforms

The most common provenance failure is a `groupby` / `merge` / `dedupe` step that silently drops the `provenance` column. Audit pattern:

- For each transform, check that `provenance` is included in the column-select / aggregate-spec
- For merges of records from multiple sources, the resulting row should carry a LIST of provenance entries (one per contributing source), NOT a single overwritten value
- For dedupe-collapsed groups, the surviving record should carry the union of its members' provenance entries

See `reference/provenance-schema.md` "Transform-survival rules" for the precise pattern per transform.

### Step 4: Sample output rows

Pull 5+ random rows from the final dataset. For each:

- Provenance field exists and is non-empty
- All required keys are present (`source_repo`, `source_ref`, `source_sha`, `pull_date`, `adapter_version`)
- `pull_date` is in the past (rule out year-fallback bugs — see `validating-temporal-fields`)
- `source_sha` matches a real commit in the source repo (if checkable)

### Step 5: Add CI gate

Add a test that fails the build if any new row in the dataset lacks provenance. Example (pytest):

```python
def test_every_row_has_provenance():
    df = pd.read_parquet("data/corpus.parquet")
    missing = df[df["provenance"].isna() | (df["provenance"] == "")]
    assert len(missing) == 0, f"{len(missing)} rows missing provenance"
```

## Outputs

A markdown audit report with:

1. **Source inventory table** — one row per upstream source with repo + ref + SHA-pinning status + license + fetch method
2. **Findings list** — per-finding: location (file:line), severity (blocking / warn / info), the rule violated, the suggested fix
3. **Patch snippets** — for each finding, a minimal code change that resolves it
4. **Suggested provenance schema** — JSON skeleton the user can drop into their ingest code
5. **CI gate snippet** — the pytest / GitHub Actions check that prevents regression

## Failure modes

Known pitfalls in provenance attachment and how this skill catches them:

- **Provenance stamped post-merge** — every merged row carries one identical `pulled_at = today()` even though the rows came from different upstream snapshots. Caught by: Step 2 requires ingest-time attachment; the audit flags any provenance whose `pull_date` matches the build date for every row.
- **Floating ref (`main` / `latest`)** — `git clone repo` without `--depth 1 --branch <tag>` resolves to the head of default-branch at clone time. Caught by: Step 1 requires explicit ref pinning; floating refs are findings.
- **Transform-collapse** — a `groupby(...).agg({"text": "concat"})` drops `provenance`. Caught by: Step 3 explicitly enumerates the `provenance` column in every transform's column-select.
- **Multi-source row carrying single provenance** — A dedupe collapses three duplicate incidents into one row but keeps only the first source's provenance. Caught by: Step 3 transform-survival rule for dedupe; provenance must become a list-of-entries.
- **License not recorded** — re-distribution legality cannot be re-derived later if the license field is empty. Caught by: minimum-viable provenance includes `license`.
- **`source_sha` is the SHA of the ingest script, not the upstream** — common copy-paste bug. Caught by: Step 4 sample check requires `source_sha` to match the upstream repo, not the ingest repo.

## References

- `reference/provenance-schema.md` — complete provenance JSON schema + transform-survival rules
- `reference/audit-checklist.md` — printable per-source audit checklist
- [W3C PROV data model](https://www.w3.org/TR/prov-overview/) — provenance vocabulary used by formal lineage systems (read this if integrating with OpenLineage / Marquez)
- [Dataset Nutrition Labels](https://datanutrition.org/) — adjacent concept: per-dataset (not per-row) provenance + suitability metadata

## Examples

### Example 1: Multi-source incident corpus (happy-path)

Input: "I'm merging AIID, OECD AIM, and AIAAIC incident registries into one corpus. Here's my ingest script. Audit it."

Output: Skill walks Steps 1-5. Finds (a) AIID is pulled from `main` (floating ref — flag), (b) OECD AIM ingest does not stamp `pull_date` (missing field), (c) the post-merge `groupby` drops the `provenance` column (transform-collapse). Produces a patched ingest function for each source with ingest-time provenance attachment, a corrected groupby that preserves `provenance` as a list, and a pytest check that fails the build on any provenance-less row.

### Example 2: Partial-provenance audit on existing dataset (edge-case)

Input: "Our prod dataset has `source` and `source_url` columns but no `source_sha` or `pull_date`. Is that good enough?"

Output: Skill identifies this as partial provenance — sufficient to know "where" but not "when" or "which version." Flags two specific risks: (1) upstream silently rewrote the record after our pull → we cannot detect drift, (2) we cannot reproduce the ingest for a regulator. Recommends backfilling `pull_date` from git-blame on the ingest commit + reconstructing `source_sha` from the upstream's git-log if the repo is reachable. If backfill is impossible, recommends quarantining the affected rows under `provenance_completeness: partial` and re-ingesting going forward with the full schema.

### Example 3: Synthetic dataset (anti-trigger)

Input: "I generated 100K synthetic credit-card transactions using a Bayesian network I trained. Audit my source provenance."

Output: Skill explicitly does NOT engage the upstream-URL workflow. Explains that for synthetic data, "provenance" is the generator code SHA + the seed + the training data's own provenance (transitively). Hands off to `ml-datasci/auditing-synthetic-data-utility` (planned). Names the relevant provenance fields for synthetic data: `generator_repo`, `generator_sha`, `seed`, `training_data_provenance`.

## See also

- `workflow/validating-temporal-fields` — pairs naturally; provenance includes `pull_date`, which must pass temporal validation
- `workflow/deduplicating-records` — dedupe is the most common provenance-loss site; cross-references the transform-survival rules here
- `workflow/validating-schema-evolution` — when upstream schemas change between pulls, provenance lets you detect which records were affected
- `workflow/pinning-reproducible-environments` — adapter version pinning + provenance adapter_version field share the same discipline
- `ml-datasci/generating-data-dictionary` — per-column metadata is the schema-level companion to per-row provenance

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from genai_agentic_incidents (registry-merge bugs documented in its CHANGELOG.md 2.0.0), DU-MSDSAI-4432-* notebook family (ingest without provenance), ai-security-framework-crosswalk (multi-source hub-firewall discipline)
