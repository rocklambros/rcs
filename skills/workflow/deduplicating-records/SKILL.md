---
name: deduplicating-records
description: >
  Deduplicates records in a corpus, dataset, or incident registry with discipline
  that avoids the three classic failure modes: stale in-memory indices after a
  partial merge, transitive-collapse failures (A↔B and B↔C merged but A↔C
  missed), and ID-format mismatches across sources. Produces a multi-key dedup
  plan with documented confidence per rule, a connected-components transitive
  closure, and an auditable diff of merged / borderline / untouched records. Use
  whenever ingesting data from multiple sources, merging registries, or the user
  reports duplicates in a corpus — especially after a recent merge or schema
  change.
version: 0.1.0
status: shipped
track: workflow
audience: [data-engineer, data-scientist, security-eng]
evidence:
  - genai_agentic_incidents
last-updated: 2026-05-23
---

# Deduplicating Records

## When to use

Trigger this skill when the user asks for or implies one of:

- Ingesting a corpus / dataset / incident registry from two or more sources and observing duplicates
- Merging records across registries that use different ID formats (e.g. `AIID-N` vs `AIID-N-OECD`)
- Phrases like "we have duplicates", "dedupe this", "I merged X and Y and now there are dupes", or "why are A and C still flagged as duplicates after we merged A↔B and B↔C?"
- A schema change or source addition where the existing dedup logic was not re-run
- Auditing a previously-deduplicated corpus for missed-merge or over-merge errors

## When NOT to use

Skip this skill and use simpler tooling when:

- The dataset has a single trusted primary key and the goal is exact-match dedup → use SQL `DISTINCT` or pandas `drop_duplicates` on that column
- The data stream is append-only with strong upstream guarantees of uniqueness (e.g. event-sourced logs with a per-event UUID issued at write)
- The user is asking about **record linkage** to a known canonical authority — that is entity resolution, a related but distinct problem

## Quick start

User says: "I have 12,000 records merged from AIID, OECD AIM, and AIAAIC. After ingest I'm seeing duplicates. How should I dedupe?"

Skill response: walks the four-step plan (declare keys → build duplicate graph → connected-components collapse → auditable diff), names index-refresh and transitive-closure as the failure modes to guard against, and emits a per-key confidence table.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| corpus | path or DataFrame | yes | — | The records to deduplicate. Each row is a record with at least one identifier column. |
| key_rules | list of rule specs | yes | — | Ordered list of match rules with documented confidence per rule (see Workflow Step 1). |
| review_threshold | float in [0, 1] | no | 0.85 | Fuzzy-match scores at or above this go to auto-merge; below go to manual review bucket. |
| normalize_ids | bool | no | true | Strip source suffixes / canonicalize ID formats before matching (e.g. `AIID-N-OECD` → `AIID-N`). |
| max_passes | int | no | 5 | Cap on merge passes before refusing to converge — forces inspection of why convergence failed. |

## Workflow

Copy this checklist into the response and check off items as the dedup progresses:

```
Dedup progress:
- [ ] Step 1: Declare ordered match rules with documented confidence per rule
- [ ] Step 2: Normalize IDs across sources (strip suffixes, canonicalize URLs, lowercase emails)
- [ ] Step 3: Build a duplicate graph — nodes = records, edges = rule-matched pairs
- [ ] Step 4: Collapse via connected components (union-find), NOT greedy pairwise merging
- [ ] Step 5: Refresh any in-memory index over the working set between passes
- [ ] Step 6: Emit auditable diff: {merged: [...], borderline: [...], untouched: [...]}
```

### Step 1: Declare ordered match rules

Define rules from highest confidence to lowest. Document the expected precision per rule:

```
Rule 1 (confidence 1.00):  cve_id equality
Rule 2 (confidence 0.95):  canonical_url equality after URL normalization
Rule 3 (confidence 0.90):  doi equality
Rule 4 (confidence 0.75):  fuzzy title (Jaro-Winkler ≥ 0.92) AND event_date within ±365 days
Rule 5 (confidence 0.60):  author + publication_date exact match
```

Rules with confidence below the `review_threshold` go to the manual-review bucket; never silent-collapse low-confidence matches.

### Step 2: Normalize ID formats

Apply the same canonicalization function before any rule fires:

- Strip source suffixes: `AIID-42-OECD` → `AIID-42`
- Lowercase emails, strip plus-addressing: `Alice+spam@Example.com` → `alice@example.com`
- Canonicalize URLs: lowercase host, strip trailing slash, normalize query string ordering
- Trim whitespace and Unicode-normalize titles (NFKC)

The `genai_agentic_incidents` 2.0.0 bug #3 was exactly this: `AIID-N` and `AIID-N-OECD` referred to the same incident but matched as distinct because the source suffix was not stripped.

### Step 3: Build the duplicate graph

For every rule, add an edge between every matching pair of records. Each edge carries its rule's confidence as a weight. Do **not** merge records here — only collect edges.

### Step 4: Connected-components collapse

Run union-find (or any connected-components algorithm) on the graph. Every component is a single deduplicated entity. This is the only safe way to close the transitive case: if A↔B and B↔C are both edges, A↔C is automatically in the same component even if no rule directly matched A and C.

The `genai_agentic_incidents` 2.0.0 bug #2 was greedy pairwise merging: `merge(A, B)`, then `merge(B, C)`, but the index of canonical IDs was not refreshed, so when the next pass looked up A it found B's old canonical and missed the transitive link to C.

### Step 5: Refresh indices after every merge pass

If your dedup runs in passes (e.g. you build candidate pairs from a blocking key, then refine), rebuild any in-memory index (canonical-id map, blocking-key index, similarity cache) at the top of each pass. Stale indices were the `genai_agentic_incidents` 2.0.0 bug #1.

### Step 6: Emit auditable diff

Every dedup run produces three buckets:

- `merged`: pairs / components that auto-collapsed, with the rule and confidence that triggered each
- `borderline`: pairs above a "review at all" floor but below `review_threshold` — these go to a human
- `untouched`: every record that had no edges; these survive as their own component

The diff is the audit trail. Without it, the question "why did A and B merge?" three months from now has no answer.

## Outputs

A dedup report containing:

1. **Rule table** — Rule number · Match expression · Confidence · Records matched
2. **Component summary** — Total input records · Components after collapse · Average component size · Largest component
3. **Diff JSON** — `{merged: [{component_id, records, rules_fired}], borderline: [{record_a, record_b, rule, score}], untouched: [record_ids]}`
4. **Manual review queue** — records in the `borderline` bucket with one row per pair and the rule + score
5. **Reproducibility footer** — input row count, output component count, rule versions, random seed if any fuzzy step is stochastic

## Failure modes

- **Stale-index bug** — merging without refreshing the canonical-id index between passes; an A↔B merge updates the index, but the next pass still sees B's pre-merge identity. Caught by: Step 5 (refresh-index requirement).
- **Greedy transitive collapse failure** — merging pairwise and trusting the chain to close; A↔B and B↔C merge but A↔C is never checked. Caught by: Step 4 (union-find on the full graph).
- **ID-format mismatch** — same incident appears under `AIID-N` and `AIID-N-OECD`; the rules never fire because the strings differ. Caught by: Step 2 (normalize before matching).
- **Silent over-merge** — low-confidence fuzzy rules promoted directly to merge. Caught by: `review_threshold` and the explicit `borderline` bucket.
- **No audit trail** — three months later, no one can answer "why did A and B merge?" Caught by: Step 6 (diff JSON with rule + confidence per merge).

## References

- `reference/dedup-rule-template.md` — the ordered-rules template with confidence column
- `reference/transitive-collapse-pitfall.md` — worked example of greedy pairwise vs union-find on the same input
- [Christen 2012 *Data Matching*](https://link.springer.com/book/10.1007/978-3-642-31164-2) — canonical text on record linkage and dedup discipline

## Examples

### Example 1: Multi-source incident corpus (happy-path)

Input: "I have 12,000 records merged from AIID, OECD AIM, and AIAAIC. Each source uses its own ID format. After ingest I see duplicates. How should I dedupe?"

Output: Skill specifies (a) Step 1 ordered rules — CVE ID > canonical URL > DOI > fuzzy title within ±365 days; (b) Step 2 ID normalization — strip `-OECD` and `-AIAAIC` suffixes from AIID-derived IDs; (c) Step 4 union-find connected-components closure, not greedy pairwise; (d) Step 5 index refresh between passes; (e) Step 6 borderline review queue. Emits a per-rule confidence table.

### Example 2: Transitive miss (edge-case)

Input: "We merged record A with B, then B with C, but A and C are still flagged as duplicates afterward. Why?"

Output: Skill identifies this as the transitive-collapse failure pattern. Explains greedy pairwise merging without index-refresh: `merge(A, B)` updates B's canonical to A, but if the next merge sees record C and looks up B by its old identity, it misses that B is now A. Recommends rebuilding the duplicate graph fresh and running union-find on all edges at once. Cites stale-index as the secondary failure if a pass-based pipeline is required.

### Example 3: Primary-key dedup (anti-trigger)

Input: "I have a customers table with a primary key customer_id. Dedupe it."

Output: Skill explicitly refuses the multi-key fuzzy workflow. Recommends `SELECT DISTINCT customer_id, ... FROM customers` or pandas `df.drop_duplicates(subset=['customer_id'])`. Explains that the multi-key + connected-components workflow is for cases where no single trusted ID exists across the input rows.

## See also

- `workflow/validating-temporal-fields` — pairs with this skill when the corpus contains event dates that need their own validation pass
- `workflow/auditing-data-quality` — run this first; quality issues like null IDs invalidate dedup rules
- `workflow/auditing-source-provenance` — record where each row came from so the dedup diff is replayable

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored from `genai_agentic_incidents` CHANGELOG.md 2.0.0 incident report (three documented dedup bugs)
