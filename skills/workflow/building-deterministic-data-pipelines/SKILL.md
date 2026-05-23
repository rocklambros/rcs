---
name: building-deterministic-data-pipelines
description: >
  Builds data pipelines whose outputs are bit-identical across runs by enforcing
  LF line endings, sorted JSON key order, stable float formatting, content-hash
  snapshotting (SHA-256 of canonicalized output), a `provenance.json` manifest
  (source URL + commit SHA + pull date + adapter version), and a CI drift check
  that re-runs the pipeline and asserts the new artifact hashes match committed
  ones. Use when authoring an ingest / ETL / preprocessing pipeline whose output
  is shared (joined by other pipelines, published, or fed into model training),
  when the user reports run-to-run output diffs that are not from real data
  change, or when audit-grade reproducibility is required (paper supplement,
  regulatory submission, eval harness). Skip for one-shot exploratory scripts.
version: 0.1.0
status: shipped
track: workflow
audience: [data-engineer, data-scientist, ml-engineer, security-eng]
evidence:
  - genai_agentic_incidents
  - TRACT
  - llm-toxicity-visual-analysis
  - rocks-mac-harness-QC.1
last-updated: 2026-05-23
---

# Building deterministic data pipelines

## When to use

Trigger this skill when the user is doing one of these:

- Authoring a new **ingest / ETL / preprocessing pipeline** whose output is shared (joined by other pipelines, fed into model training, published as an open dataset, or relied on by evals)
- Reporting **run-to-run output diffs** in a pipeline they believe should be deterministic ("the file hash changed but the code and the source data did not")
- Producing artifacts that need **audit-grade reproducibility** — paper supplement, regulatory submission (HIPAA, FDA), eval harness, model card supporting evidence
- Joining a project where a teammate said "we cannot reproduce last quarter's numbers" and the suspect is the pipeline's nondeterminism

This skill produces a checklist of invariants the pipeline must satisfy AND a CI drift check that catches violations early.

## When NOT to use

Skip and hand off when:

- The pipeline is a **one-shot exploratory script** — the friction of canonicalization outweighs the benefit at this stage; revisit when the script is about to be reused or shared
- The output is **inherently non-deterministic by design** (sampling Monte Carlo with a documented run-stamp, generating fresh nonces) — see `enforcing-seed-hygiene` for the seed-coverage skill and the legitimate-nondeterminism caveat
- The user wants help with **environment pinning** (Python version, deps, base image) — that is `pinning-reproducible-environments`, not this skill
- The non-determinism complaint is about **model outputs**, not pipeline outputs — that is a model-training reproducibility question; check `enforcing-seed-hygiene` and CPU-pin patterns there

## Quick start

User says: *"I want this pipeline to produce bit-identical output every run."*

Skill response:

1. Inventory the pipeline's output formats (JSON, JSONL, CSV, Parquet, language-native binary, custom).
2. Apply the canonicalization invariants per format (table below).
3. Add a `provenance.json` manifest written alongside every output.
4. Add a CI drift check that re-runs the pipeline and asserts the new output's hash matches the committed one.
5. Commit the artifacts AND their `provenance.json` so reviewers can audit what changed.

| Format | Canonicalization rule |
|---|---|
| JSON | `json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2, separators=(',', ': '))` + LF endings |
| JSONL | One record per line, each record canonicalized as above (no indent for JSONL) |
| CSV | Sorted column order, sorted row order on a stable key, LF endings, no trailing whitespace, quoting rule explicit |
| Parquet | Compression `snappy` (or `none`), sorted column order, row-group size pinned |
| Language-native binary (`.pkl`, `.joblib`, `.npz`) | Avoid for shared artifacts (version-fragile); convert to JSON / Parquet / Arrow IPC for cross-version stability |
| Anything else | Author a canonical-form function and document it in the pipeline's README |

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `output_path` | string | yes | — | The artifact whose determinism is being enforced. May be a single file or a directory; the skill recurses into directories. |
| `format` | enum | no | inferred from extension | One of `json`, `jsonl`, `csv`, `parquet`, `custom`. Inferred from `output_path` extension when not specified. |
| `provenance_required` | bool | no | `true` | Whether to require a sibling `provenance.json` alongside each artifact. Turn off only for transient outputs. |
| `ci_drift_check` | bool | no | `true` | Whether to emit the CI workflow snippet that re-runs the pipeline and diffs hashes. |
| `tolerate` | list | no | `[]` | Field names whose value may change run-to-run (e.g., `pulled_at` timestamp INSIDE the provenance file). The drift check excludes these from the hash. |

## Workflow

Copy this checklist and check items off as you go:

```
Pipeline determinism checklist:
- [ ] Step 1: Output format identified; canonicalization rule chosen from the table
- [ ] Step 2: LF line endings enforced (no CRLF mixed in)
- [ ] Step 3: Sorted output (keys for JSON; column + row order for tabular)
- [ ] Step 4: Stable float formatting (decimal precision pinned; no scientific-vs-decimal drift)
- [ ] Step 5: No floating timestamps inside the data (only inside provenance.json, where they are tolerated)
- [ ] Step 6: provenance.json sibling written: source_url + source_commit_sha + pulled_at + adapter_version + input_hashes
- [ ] Step 7: Content-hash snapshot computed (SHA-256 of canonicalized output) and committed alongside the artifact
- [ ] Step 8: CI drift check added — re-runs the pipeline and asserts new hashes == committed hashes
```

### Step 1 — Identify output format and canonicalization rule

Pick the rule from the table above. If the format is `custom`, author a `canonicalize(obj) -> bytes` function and document it in the pipeline's README; the rest of the workflow assumes a single canonical-form function exists.

### Step 2 — LF line endings

`.gitattributes` should pin LF for all generated artifact extensions:

```
*.json    text eol=lf
*.jsonl   text eol=lf
*.csv     text eol=lf
*.tsv     text eol=lf
```

The pipeline writes with `newline="\n"` (Python) or equivalent and never relies on the OS default.

### Step 3 — Sorted output

- JSON: `sort_keys=True` on `json.dumps`
- JSONL: each line's object is sorted by key; the lines themselves are sorted on a stable record key (e.g., `incident_id`)
- CSV / TSV: column order pinned (alphabetical or a documented business order); rows sorted on a stable composite key
- Parquet: column order pinned; row order pinned on a stable key
- Avoid `set` and `dict` iteration order assumptions in pipeline code; convert to `sorted(...)` before writing

### Step 4 — Stable float formatting

Floats are the silent source of cross-platform diffs. Pin the format:

- For JSON, decide on a precision rule (e.g., `round(x, 6)`) and apply consistently before serialization
- For CSV / TSV, use a format string (`"{:.6f}".format(x)`) instead of `str(x)`
- For Parquet, the column dtype already pins the precision; just confirm the schema is pinned

Float NaN / Inf serialization differs between libraries. Pin one convention (e.g., NaN → `null` in JSON; NaN → empty string in CSV) and apply throughout.

### Step 5 — No floating timestamps inside the data

If the pipeline embeds `"generated_at": "2026-05-23T10:00:00Z"` inside the data payload, every run produces a diff even when the actual records are identical. Move timestamps to `provenance.json` where they belong, and exclude `provenance.json` from the content-hash check (or exclude only the timestamp field via `tolerate`).

### Step 6 — `provenance.json` sibling

Alongside every output artifact, write a `provenance.json`:

```json
{
  "source_url": "https://incidentdatabase.ai/api/v1/incidents",
  "source_commit_sha": "abc1234...",
  "pulled_at": "2026-05-23T10:00:00Z",
  "adapter_version": "0.3.1",
  "input_hashes": {
    "incidents.json": "sha256:..."
  },
  "output_hash": "sha256:...",
  "row_count": 12348
}
```

Commit this file alongside the artifact. Reviewers can answer "what version of which source produced this?" without re-running anything.

### Step 7 — Content-hash snapshot

Compute `sha256(canonicalized_bytes)` for each output artifact and record it in `provenance.json` AND in a top-level `hashes.txt` (one line per artifact, format: `<hash>  <path>`). The hashes file is the artifact reviewers diff against in PR.

### Step 8 — CI drift check

A GitHub Actions job (or equivalent) that:

1. Checks out the repo
2. Runs the pipeline against fixed inputs
3. Canonicalizes the output
4. Recomputes the hashes
5. Asserts the new hashes match `hashes.txt` (excluding `tolerate` fields)
6. Fails if any drift

Cron weekly (or per-PR for pipeline-touching PRs). The drift check is the only invariant that catches "an unrelated dep was bumped and now the floats round differently."

## Outputs

The skill produces:

1. **A canonicalization checklist** the user can apply to the pipeline code (Steps 1–5)
2. **A `provenance.json` schema** with required and optional fields, plus the rationale
3. **A `hashes.txt` format** with one hash per artifact
4. **A CI workflow snippet** (`.github/workflows/drift-check.yml` or equivalent) that runs the drift check on schedule
5. **A diagnosis** when run-to-run drift is reported: which invariant failed (line ending? sort order? float format? embedded timestamp?), with the specific evidence

## Failure modes

- **CRLF leaking in on Windows checkouts.** Even with `core.autocrlf` configured, a teammate cloning on Windows can produce a CRLF-tainted artifact. The `.gitattributes` `text eol=lf` directive is the only reliable fix. Caught by: Step 2 + the drift check, which would flag the hash diff. The skill recommends a pre-commit hook that fails on CRLF in generated artifacts.
- **`dict` iteration relying on Python 3.7+ insertion order without sorting.** Even with insertion-order preservation, two runs that build the dict from different upstream orderings produce different outputs. The skill flags any pipeline code that writes a dict to JSON without `sort_keys=True`. Insertion order is not a substitute for sorting.
- **Float NaN inconsistency.** `json.dumps({"x": float("nan")})` produces `{"x": NaN}` (invalid JSON) by default — `allow_nan=False` raises, `default=str` produces `"nan"`. The skill picks one rule (NaN → null) and enforces it in code review.
- **Provenance file with floating timestamps tripping the drift check.** `pulled_at` legitimately changes every run. The `tolerate` list excludes specific fields from the hash. Without `tolerate`, the drift check fails on its own provenance file. Caught by: the default `tolerate` includes `pulled_at`.
- **Schema drift in source data presenting as code drift.** A source API adds a field; the pipeline's output now contains that field; the drift check fails. The diagnosis is NOT a pipeline bug — it is source drift. The skill recommends naming the source schema version in `provenance.json` so the diagnosis is unambiguous.
- **Treating `sort_keys=True` as sufficient when nested lists are not sorted.** `json.dumps` sorts dict keys but not list elements. If the pipeline emits `{"tags": ["b", "a"]}` from one run and `{"tags": ["a", "b"]}` from another, the hashes differ. Caught by: the canonicalize function explicitly sorts every nested list whose order is not load-bearing.

## References

- `reference/canonicalize.py` — a drop-in `canonicalize(obj) -> bytes` function for JSON / JSONL with the invariants from Steps 3–5 baked in
- `reference/provenance-schema.md` — full `provenance.json` schema with required + optional fields and why each one matters
- `reference/ci-drift-check.yml` — a GitHub Actions workflow snippet for the per-PR + weekly drift check
- [git `gitattributes` documentation](https://git-scm.com/docs/gitattributes) — the `text eol=lf` directive
- RCS `skills/workflow/pinning-reproducible-environments/` — environment pinning is upstream of pipeline determinism; without it, the pipeline can drift on a Python minor-version bump

## Examples

### Example 1: New ingest pipeline with shared output (happy-path)

Input: *"Writing an ingest pipeline that pulls incidents from a public API and writes a normalized JSONL file. Other pipelines join against this file. How to make it deterministic?"*

Output: The skill walks the 8-step checklist for the JSONL case: each record's keys are sorted; the records themselves are sorted on `incident_id`; LF line endings via `.gitattributes`; floats rounded to 6 decimal places consistently; no timestamps in the data (only in `provenance.json`); a sibling `provenance.json` with source URL + source commit SHA (when available) + adapter version + input hashes + output hash + row count; a `hashes.txt` at the top of the artifact directory; a `.github/workflows/drift-check.yml` that runs the pipeline on PR and weekly and asserts the new hashes match committed ones. The skill names that adding the canonical-form function takes ~20 lines of code and that the drift check is the only invariant that catches a silently-bumped pandas minor version changing how floats round.

### Example 2: Run-to-run JSON diff with no code or data change (edge-case)

Input: *"My pipeline writes a JSON file. Code and source data are unchanged, but every run produces a different file hash. Why?"*

Output: The skill walks the diagnosis decision: (1) Are the files byte-identical on the same machine but different across machines? Likely line-ending or float-precision drift. (2) Are the files different on the SAME machine? Look for an embedded `generated_at` timestamp inside the data, or `dict` insertion order that depends on upstream input order. (3) Did Python or pandas minor version change? Then it could be `__repr__` formatting drift (rare, but happens). The skill recommends running `diff <(jq -S . file_run_1.json) <(jq -S . file_run_2.json)` to pinpoint the first divergent key — that usually surfaces the cause within minutes. Then apply Steps 2–5 to fix.

### Example 3: One-shot exploratory script (anti-trigger)

Input: *"Writing a quick script that pulls one CSV from a URL and prints summary stats to stdout. Should the determinism workflow apply?"*

Output: The skill explains that one-shot exploratory scripts pay the friction of canonicalization without earning any benefit — there is no shared output for downstream consumers to depend on, no audit trail, no PR review. Skip the workflow now; revisit if the script is about to be reused, shared with a teammate, or fed into another pipeline. For exploration, the priority is `enforcing-seed-hygiene` (so the seeded RNG calls are deterministic within a single run) and `auditing-data-quality` (so the script's findings are trustworthy), not pipeline-determinism scaffolding.

## See also

- `workflow/pinning-reproducible-environments` — environment pinning is upstream of pipeline determinism; both are needed for end-to-end reproducibility
- `workflow/enforcing-seed-hygiene` — for pipelines that include sampling or RNG steps, ensures the RNG is deterministic
- `workflow/auditing-jupyter-execution-order` — for notebooks that consume the pipeline's output; ensures the notebook's results are reproducible from the deterministic pipeline output
- `workflow/auditing-data-quality` — for the pipeline's input data; without a clean input the deterministic output is bit-identical garbage
- `security/auditing-pinned-dependencies` — for the install commands that produce the pipeline's runtime; floating deps defeat determinism

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
