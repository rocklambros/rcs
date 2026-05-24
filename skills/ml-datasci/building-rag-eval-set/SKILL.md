---
name: building-rag-eval-set
description: >
  Builds a golden question-answer evaluation set for a RAG system from a
  domain corpus. Produces three artifacts — a calibration split, a held-out
  test split (never viewed during development), and an adversarial set
  (absent-topic, multi-hop synthesis, distractor-rich). Every Q-A row carries
  source-document IDs and source-text spans so downstream evaluation can
  separately attribute failures to retrieval vs. generation. Forces human
  review on LLM-drafted Q-As before they enter the golden set. Locks the
  final set with a dataset hash and SemVer. Use when starting RAG evaluation
  from scratch in a custom domain (legal, medical, internal product docs)
  where no public benchmark fits, when about to evaluate against ad-hoc
  questions with no source attribution, or when preparing the eval input for
  a chunking-strategy, embedding-drift, or retrieval-quality audit. Refuses
  when an existing benchmark (HotPotQA, MS-MARCO, BEIR, Natural Questions)
  covers the domain, or when the task is generation-only with no retrieval
  step.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [ml-engineer, data-scientist, ai-security, skill-author]
evidence:
  - ai_security_framework_crosswalk
  - multiturn-injection-detection
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Building a RAG Evaluation Set

## When to use

Trigger this skill when the user:

- Is starting RAG evaluation from scratch in a custom domain where no public benchmark fits (internal product docs, proprietary legal corpora, medical records, customer-support transcripts, regulatory filings)
- Is about to run a RAG evaluation against ad-hoc questions invented on the spot, with no source-doc attribution
- Is preparing the eval foundation for a follow-on chunking-strategy, embedding-drift, or retrieval-quality audit (those audits need a held-out QA set as input)
- Has an LLM-generated Q-A list and wants to make it into a real eval set (LLM-generated Q-A is the starting candidate, not the finished product — human review is required)
- Needs a separate held-out / test split so the eval set is not silently leaked into development
- Asks "how do I separate retrieval failures from generation failures in my RAG evaluation" — the answer requires source-span attribution in every Q-A row, which is what this skill produces
- Is rebuilding an eval set because the prior one was contaminated (every dev cycle inadvertently saw it) or undocumented (no schema, no versioning)

## When NOT to use

Skip and hand off when:

- An existing public benchmark covers the domain — HotPotQA for multi-hop, MS-MARCO for passage retrieval, BEIR for cross-domain, KILT for knowledge-intensive tasks, Natural Questions for open-domain QA. Recommend benchmark selection instead of building from scratch.
- The user wants generation-only LLM evaluation with no retrieval step (use `workflow/scaffolding-llm-eval-harness` — that scaffold handles the broader LLM-eval shape; this skill is specifically the QA-with-source-spans variant)
- The user is evaluating a classifier (binary or multiclass) — use `evaluating-binary-classifiers` / `evaluating-multiclass-classifiers`
- The user has a tiny corpus (< 50 documents) where the "eval set" is just the corpus and the questions are toy demos — no formal eval set is warranted at that scale
- The user wants embedding-model evaluation independent of retrieval (use `selecting-embedding-model`)
- The user already has an eval set with source-span attribution and just wants to add scenarios — that is an extension job, not a build job; this skill is for greenfield construction

## Quick start

User: *"I'm building RAG over our internal HR policy documents. About 800 policy PDFs. We have no eval set; right now we test by asking ad-hoc questions in a chat window. Build me a proper eval set."*

Skill walks the 7-step workflow: (1) define coverage (difficulty bands, question types, domain slices), (2) draft Q-A candidates (human-authored where possible; LLM-drafted as candidates needing review), (3) attach source-doc IDs and source-text spans to every candidate, (4) human-review every Q-A (mark difficulty, flag ambiguity, validate ground-truth), (5) split into calibration + held-out test + adversarial, (6) lock the set with a dataset hash and version file, (7) document the schema and the build process so the set can be extended later without contaminating the held-out split.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| corpus | path to dir or list[document] | yes | — | Source corpus the RAG retrieves over. Used both to draft Q-As and to attribute source spans. |
| target_size | int | no | 100 | Total number of Q-A pairs in the final golden set (calibration + held-out + adversarial combined). |
| split_fractions | {calibration: float, held_out: float, adversarial: float} | no | {0.30, 0.40, 0.30} | Fractions of `target_size` going to each split. Adversarial is held separately from held-out test. |
| difficulty_bands | list[string] | no | ["easy", "medium", "hard"] | Bands to stratify across. Each band must contain ≥ 10 questions to be statistically meaningful. |
| question_kinds | list[string] | no | ["factoid", "multi-hop", "synthesis", "absent-topic"] | Question types the set must include. Stratify within each split. |
| llm_draft_model | string | no | null | If set, use this LLM (with revision pin) to DRAFT candidate Q-As. ALL drafts go through step-4 human review before entering the set. |
| reviewers | list[string] | yes | — | Identifiers (name, email, or role tag) of the humans who will review Q-As. At least one. |
| version | string | no | "0.1.0" | SemVer for this eval set. Bumped MAJOR on schema change, MINOR on Q-A additions, PATCH on metadata edits. |

## Workflow

Copy this checklist into the response and check off each step as the eval set lands:

```
Build progress:
- [ ] 1. Define coverage matrix: difficulty bands × question kinds × domain slices
- [ ] 2. Draft Q-A candidates (human-authored preferred; LLM-drafted allowed but only as candidates)
- [ ] 3. Attach source_doc_id + source_span to every candidate (no candidate enters review without attribution)
- [ ] 4. Human review: every Q-A gets reviewed_by + reviewed_at + difficulty + ambiguity_flag + ground_truth_verified
- [ ] 5. Split into calibration + held-out test + adversarial (stratified by difficulty × kind)
- [ ] 6. Lock with dataset_hash (sha256 of canonical-serialized golden.jsonl) + version file
- [ ] 7. Document schema + build process + extension rules in README so future additions don't contaminate the held-out split
```

### Step 1 — Coverage matrix

Build a target table BEFORE drafting any Q-As. Example for a 100-Q-A set with default splits:

| Slice | Easy factoid | Easy multi-hop | Medium factoid | Medium multi-hop | Medium synthesis | Hard multi-hop | Hard synthesis | Absent-topic |
|---|---|---|---|---|---|---|---|---|
| Calibration (30) | 6 | 3 | 6 | 3 | 3 | 3 | 3 | 3 |
| Held-out test (40) | 8 | 4 | 8 | 4 | 4 | 4 | 4 | 4 |
| Adversarial (30) | 0 | 0 | 0 | 0 | 0 | 8 | 8 | 14 |

Stratification matters because end-to-end metrics are dominated by whichever slice has the most rows. Without stratification, you can't see "RAG fails on hard multi-hop questions" because they're 5% of the set and the easy factoids pull the headline number up.

### Step 2 — Draft Q-A candidates

Two paths:

| Path | When | Quality posture |
|---|---|---|
| Human-authored | Domain experts available; small target_size (≤ 100) | Highest quality; expensive |
| LLM-drafted candidates | Larger sets; domain experts review-only | LLM gets ~70% of the way; human review fixes the rest |

If using LLM-drafted: pass the LLM (with revision pin) the corpus chunks and ask for Q-As that meet specific coverage cells (e.g., "draft 5 hard multi-hop questions about employee leave policy that require synthesizing across two specific policy documents"). Save the prompts used. Save which corpus chunks were shown. Never let LLM-drafted Q-As enter the golden set without step-4 human review.

### Step 3 — Source attribution

EVERY Q-A row must include:

```json
{
  "id": "qa-0042",
  "query": "How many weeks of parental leave is a full-time employee entitled to after 1 year of service?",
  "answer": "12 weeks",
  "source_doc_id": "POL-HR-2024-LEAVE",
  "source_spans": [
    {"start_char": 1842, "end_char": 1996, "text": "Full-time employees with at least 12 months of continuous service are entitled to 12 weeks of paid parental leave..."}
  ],
  "difficulty": "easy",
  "kind": "factoid"
}
```

Why source spans matter: without them, a failed evaluation cannot distinguish "the retriever didn't find the right document" from "the retriever found the right document but the generator answered wrong." That separation is the whole point of running a RAG eval; without it, you are running a black-box LLM eval.

A Q-A whose answer cannot be attributed to a specific source span in a specific corpus document is either a synthesis question (legitimate; mark `kind=synthesis` and attach ALL the contributing spans) or an out-of-corpus question (legitimate ONLY in the adversarial set with `kind=absent-topic`).

### Step 4 — Human review

Every Q-A — including human-authored ones, not just LLM-drafted — gets a review pass that captures:

| Field | Meaning |
|---|---|
| `reviewed_by` | Reviewer identifier (matches one of the `reviewers` input list) |
| `reviewed_at` | ISO timestamp of review |
| `difficulty` | Band assignment (validates step-1 stratification) |
| `ambiguity_flag` | bool — query is ambiguous; multiple defensible answers exist |
| `ground_truth_verified` | bool — reviewer confirmed the answer text matches the source span |
| `notes` | Free-text reviewer notes (e.g., "answer depends on date range; flagged for revisit") |

A Q-A with `ground_truth_verified=false` does NOT enter the golden set. A Q-A with `ambiguity_flag=true` can enter the calibration split but should not enter the held-out test (ambiguous queries make threshold tuning unreliable).

### Step 5 — Splits

Stratified sampling within each (difficulty × kind) cell:

- **Calibration (30%)**: visible during development; use for threshold tuning, prompt iteration, retrieval debugging
- **Held-out test (40%)**: NEVER opened during development; used only for end-of-cycle evaluation. If a developer accidentally looks at a held-out item, that item is BURNED — move it to calibration and draft a replacement.
- **Adversarial (30%)**: hard multi-hop, hard synthesis, absent-topic. Used for stress testing. Failures here are expected and informative, not blocking.

Stratification means: if the calibration split has 6 easy-factoid rows, the held-out split has 8 (in the 30/40 ratio), and the adversarial split has 0 (adversarial is all-hard by design).

### Step 6 — Lock with dataset hash + version

Final artifacts:

```
eval-set/
  golden.jsonl              # union of all three splits, with split label per row
  calibration.jsonl         # split-1 only
  held-out.jsonl            # split-2 only (commit but DO NOT VIEW during dev)
  adversarial.jsonl         # split-3 only
  dataset_hash.txt          # sha256 of canonical-serialized golden.jsonl
  VERSION                   # e.g., "0.1.0"
  schema.json               # JSON Schema for one Q-A row
  README.md                 # build process, schema, extension rules
```

Canonical serialization for the hash: sorted keys, LF newlines, no trailing whitespace, UTF-8. Any change to the golden set must bump the version AND the hash. The hash goes into every downstream evaluation's result rows (same five-field contract as `scaffolding-llm-eval-harness`) so a result.jsonl can be traced to the exact eval set version it was scored against.

### Step 7 — Document

The README must answer:

- How were Q-As drafted (human, LLM, both)?
- Which LLM and prompt drafted any LLM-drafted Q-As (with revision pin)?
- Who reviewed (matched to the `reviewers` input)?
- What is the coverage matrix (the table from step 1)?
- What are the split rules?
- What is the rule for adding a Q-A later (PATCH/MINOR/MAJOR semantics)?
- What is the rule for FIXING a Q-A whose ground truth was wrong (correct it, bump PATCH, recompute hash)?
- Who can VIEW the held-out split (typically: nobody during dev; results are reported by a CI runner or a designated evaluator who does not write retrieval/generation code)?

Without this README, a future maintainer will silently violate the held-out discipline and the eval set will lose its meaning.

## Outputs

A populated `eval-set/` directory as described in step 6, plus:

- A coverage-matrix table (the actual one used; may differ from the step-1 target if drafting fell short in some cells)
- A reviewer-attribution table (per reviewer: how many Q-As they reviewed, when, average ambiguity-flag rate as a sanity check on reviewer calibration)
- A printed "what's next" pointer:

```
Done. Next:
  - Wire calibration.jsonl into your dev loop
  - DO NOT view held-out.jsonl until you are ready to evaluate
  - Pass dataset_hash.txt to evaluating-rag-retrieval / auditing-chunking-strategy / etc.
  - When you add a Q-A: edit golden.jsonl, bump VERSION, recompute dataset_hash, document in README
```

## Failure modes

Known pitfalls and how this skill catches them:

- **LLM-drafted Q-As enter the golden set without review** — produces a noisy eval set that punishes the retrieval/generation system for the LLM-drafter's mistakes, not real failures. Caught by step 4 requiring `ground_truth_verified=true` for every row before it enters the set.
- **No source-span attribution** — makes it impossible to separate retrieval failures from generation failures, defeats the purpose of a RAG-specific eval. Caught by step 3 requiring source spans on every non-adversarial Q-A and explicit handling for synthesis / absent-topic.
- **Held-out split silently viewed during development** — silently contaminates the eval; future "we beat the held-out test" claims are meaningless. Caught by step 5 + step 7 README rule: any viewed held-out item is BURNED and replaced.
- **No version + hash** — two evaluations on the "same eval set" weeks apart compare different sets; results are not run-over-run comparable. Caught by step 6 dataset_hash + VERSION in every result row.
- **No stratification** — overall numbers hide the hard-question failure mode. Caught by step 1 forcing a coverage matrix and step 5 stratified sampling.
- **Wrong skill engaged for an existing benchmark** — re-building HotPotQA from scratch wastes weeks. Caught by "When NOT to use" recommending benchmark selection instead.
- **Wrong skill engaged for generation-only eval** — wastes effort on source-span attribution that won't be used. Caught by "When NOT to use" handoff to `scaffolding-llm-eval-harness`.

## References

- `reference/qa-row-schema.json` — JSON Schema for one Q-A row
- `reference/adversarial-templates.md` — templates for absent-topic, distractor-rich, multi-hop synthesis adversarial questions
- `reference/review-protocol.md` — the human-review protocol (per-row fields, reviewer-calibration sanity checks)
- [BEIR benchmark suite](https://github.com/beir-cellar/beir) — for benchmark-selection alternatives before building from scratch
- [Anthropic eval-set guidance](https://docs.claude.com/en/docs/test-and-evaluate/develop-tests) — third-party reference on building task-specific evals

## Examples

### Example 1: Internal HR policy RAG (happy-path)

Input: *"I'm building RAG over our internal HR policy documents. About 800 policy PDFs. We have no eval set right now; we test by asking ad-hoc questions in a chat window. Build me a proper eval set with about 100 Q-A pairs. We have two domain experts who can review."*

Output: Skill walks all 7 steps. Coverage matrix targets 30 calibration + 40 held-out + 30 adversarial, stratified across difficulty × kind. Drafts candidates via LLM (with revision pin) showing it relevant policy chunks, asking for cells specified in the matrix. Every candidate gets source_doc_id + source_spans. Routes all 100 candidates through the two domain experts for review (the reviewer-attribution table flags if one expert is reviewing 90% and the other 10% — calibration concern). Produces `golden.jsonl` + 3 split files + `dataset_hash.txt` + `VERSION=0.1.0` + `schema.json` + a README that documents the LLM prompt used, reviewer names, coverage matrix, and rules for adding Q-As later. Notes that the held-out file must not be opened until end-of-dev-cycle evaluation.

### Example 2: Existing benchmark covers the domain (anti-trigger)

Input: *"I want to evaluate my multi-hop QA system. Build me an eval set."*

Output: Skill declines. Explains that multi-hop QA has established public benchmarks — HotPotQA and 2WikiMultiHopQA being the most common. Recommends starting with one of those benchmarks instead of building from scratch. Notes that building a custom multi-hop eval set is justified only if the user's domain is truly out-of-scope for HotPotQA (e.g., proprietary domain-specific multi-hop) — and in that case, the user should be explicit about WHY HotPotQA doesn't fit before this skill proceeds.

### Example 3: Generation-only eval, no retrieval (anti-trigger)

Input: *"I want to evaluate three prompts for summarizing customer support tickets. There is no retrieval step — we pass the full ticket to the model. Build me an eval set."*

Output: Skill declines because the task is generation-only — there is no retrieval to evaluate, so source-span attribution provides no signal. Hands off to `workflow/scaffolding-llm-eval-harness`, which is the right scaffold for generation-only multi-prompt evals (five-field result-row contract: model_id, dataset_hash, prompt_version, judge_model, result_row). Notes that if a retrieval step is ADDED later, the user can come back here.

## See also

- `ml-datasci/evaluating-rag-retrieval` — the downstream evaluation skill that consumes the eval set this skill produces
- `ml-datasci/auditing-chunking-strategy` — needs the held-out QA set with source spans as input
- `ml-datasci/auditing-embedding-drift` — needs an eval set to quantify whether drift is actually hurting retrieval
- `workflow/scaffolding-llm-eval-harness` — sibling for generation-only evals with the five-field contract
- `ml-datasci/selecting-embedding-model` — orthogonal axis; uses the same eval set
- `ml-datasci/comparing-models-fairly` — paired-test discipline on top of evaluation results from the eval set this skill produces

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
