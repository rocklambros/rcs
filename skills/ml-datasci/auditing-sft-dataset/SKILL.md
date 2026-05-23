---
name: auditing-sft-dataset
description: >
  Audits a supervised fine-tuning (SFT) dataset before training across seven
  dimensions: schema and format validity, chat-template conformance,
  length-distribution sanity, duplicate detection (exact and near-duplicate),
  leakage against the held-out eval set, PII / sensitive-content detection
  with a user-supplied policy, and label-quality spot-check. Use when an SFT
  corpus has been assembled (scraped chats, synthetic demonstrations,
  human-annotated instructions, RLHF preference pairs converted to SFT) and
  the user is about to launch a fine-tune run. Refuses to certify the dataset
  without an explicit eval-set boundary and refuses to silently drop rows
  without a per-rule audit log.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - ml-engineer
  - data-scientist
  - security-eng
  - ai-security
evidence:
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - llm-safety-alignment-study
  - genai_agentic_incidents
last-updated: 2026-05-23
---

# Auditing an SFT Dataset

> **Tooling, not professional advice.** This skill is an audit harness. It
> produces a findings report against rules the operator supplies (PII policy,
> chat template, length budget). It does not bundle a PII catalog, a content-
> moderation taxonomy, or a chat-template registry — those are inputs.

## When to use

Trigger this skill when the user is about to start (or has just assembled the
dataset for) a supervised fine-tune and one of:

- The corpus came from a scrape (subreddit threads, support-ticket exports,
  forum dumps) and may carry PII, duplicates, or off-policy content
- The corpus is a mix of human-written and synthetic demonstrations and may
  carry generation artifacts (template echoes, model self-references)
- A preference-pair dataset (DPO / IPO source) was flattened into SFT format
  and the chat template may not match the target model
- The fine-tune is gated by a regulatory or contractual constraint (HIPAA,
  GDPR, NDA terms) and a documented audit is required before training
- The user mentions: "I have a chat dataset", "scraped conversations",
  "ShareGPT format", "Alpaca-style instructions", "fine-tune dataset",
  "ready to launch SFT"

## When NOT to use

Skip this skill and hand off when:

- The dataset is a published, pre-curated benchmark already audited upstream
  (e.g., a Hugging Face official tokenizer-aligned SFT split, Alpaca-cleaned,
  Dolly-15K, OASST). Respect the upstream audit; spot-check only.
- The dataset is for pre-training / continued pre-training (raw-text corpus,
  not instruction-tuning) — different audit dimensions (deduplication scale,
  language-mix, contamination against eval benchmarks) apply
- The dataset is for RLHF / DPO / KTO and is still in preference-pair format
  — audit the pairs before flattening; use a preference-data audit (planned)
- The user has no held-out eval set defined — first establish the split
  (see `ml-datasci/auditing-train-test-split`), then return for the SFT audit
- The user wants to filter for quality (perplexity, length, instruction
  diversity) as an optimization step — that is curation, not audit; this
  skill validates safety + integrity, not quality optimization

## Quick start

User says: "I have a 120K-row SFT dataset I scraped from a customer-support
forum, plus 2K held-out for eval. It's in ShareGPT format. Target model is
Llama-3.1-8B. Audit it before I launch training."

Skill walks the 7-dimension audit, requires the user to point at the eval
split for leakage checking, requires the user's PII policy (or asks for a
minimum default: emails, phone numbers, full names, account IDs), and
produces a findings report with per-rule pass / fail / row-counts and a
remediation plan. Drops are quarantined to a separate file, never silent.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `train_path` | path | yes | — | Path to the SFT training file (JSONL, Parquet, or HF dataset dir). |
| `eval_path` | path | yes | — | Path to the held-out eval file. Required for leakage detection. Refuse to audit without it. |
| `format` | "sharegpt" \| "alpaca" \| "openai-messages" \| "custom" | yes | — | Dataset schema for chat-template conformance. `custom` requires a `schema_path`. |
| `target_chat_template` | string \| path | yes | — | Either a known template name (`llama-3`, `chatml`, `mistral-v3`) or a path to a Jinja2 template file. The audit checks every row renders cleanly under this template. |
| `pii_policy_path` | path | recommended | — | JSON or YAML listing PII entity types to flag and redaction style. If absent, default policy is `[email, phone, ssn-like, ip-address, credit-card-like]`; flag-only (no redaction). |
| `length_budget` | int | no | `8192` | Max tokens per row under `target_chat_template`'s tokenizer. Rows exceeding are flagged for truncation review. |
| `near_duplicate_threshold` | float in [0,1] | no | `0.85` | MinHash Jaccard threshold for near-duplicate clustering. |
| `leakage_n_gram` | int | no | `13` | Substring n-gram size for exact-substring leakage check against eval. |
| `drop_policy` | "quarantine" \| "report-only" | no | `"quarantine"` | `quarantine` writes failing rows to `quarantine/<rule>.jsonl`; `report-only` keeps the dataset intact and only produces findings. Never silently drops. |
| `sample_for_label_quality` | int | no | `100` | Number of rows to sample for human label-quality review (the audit cannot judge label correctness; it produces the sample). |

## Workflow

Copy this checklist into the response and check items off as the audit progresses:

```
SFT dataset audit progress:
- [ ] 0. Pre-flight — both paths exist, formats parse, target template loads, eval is held-out
- [ ] 1. Schema + format validity — every row parses to the declared format
- [ ] 2. Chat-template conformance — every row renders under the target template without error
- [ ] 3. Length distribution — token-count histogram; flag rows over length_budget
- [ ] 4. Duplicate detection — exact-hash + MinHash near-duplicates
- [ ] 5. Leakage check — substring n-gram overlap between train and eval
- [ ] 6. PII / sensitive content — entity detection per the supplied policy
- [ ] 7. Label-quality sample — N rows pulled for human review (skill produces the sample, does not judge)
- [ ] 8. Findings report + remediation plan + quarantine manifest
```

### Step 0: Pre-flight

- Confirm `train_path` and `eval_path` exist and are different files
- Confirm `format` matches the file structure (load 5 sample rows; verify they parse)
- Confirm `target_chat_template` loads (named template resolves, or Jinja2 file parses)
- Confirm `eval_path` is held out: the audit must not be used to pre-filter eval rows out of train; the leakage check is one-directional (train must not contain eval)
- If `pii_policy_path` is absent, emit a warning and proceed with the default minimum policy

### Step 1: Schema + format validity

For each row, validate against the declared format schema:

- **ShareGPT:** `{"conversations": [{"from": "human|gpt|system", "value": "..."}]}` — alternating roles, no empty values, no orphan turns
- **Alpaca:** `{"instruction": "...", "input": "...", "output": "..."}` — `instruction` and `output` required; `input` may be empty
- **OpenAI messages:** `{"messages": [{"role": "system|user|assistant|tool", "content": "..."}]}` — `role` from the allowed set, no empty `content` (except for tool calls)
- **Custom:** validate against `schema_path` (JSON Schema or Pydantic)

Count parse failures by failure mode. Quarantine failing rows.

### Step 2: Chat-template conformance

Render every row through the target chat template's `apply_chat_template`
function (Hugging Face tokenizer or equivalent). Flag any of:

- Rendering raises an exception
- Rendered output contains literal template tokens that suggest a mismatch
  (e.g., `<|im_start|>` appearing in row content when the target template is
  Llama-3 style)
- Rendered output contains `{{` / `}}` Jinja delimiters (un-substituted)
- Rendered output ends with an assistant role but no assistant content
  (truncated demonstration)
- Rendered output begins with a system message when the target template
  doesn't support system role (or vice versa)

See `reference/chat-template-audit.md` for the full conformance ruleset and
the per-template caveats (Llama-3, ChatML, Mistral-v3, Gemma-2).

### Step 3: Length distribution

Tokenize every rendered row under the target template's tokenizer. Report:

- Distribution: min, p50, p90, p99, max
- Count of rows exceeding `length_budget`
- Count of rows under a minimum (default 16 tokens) — suspiciously short
  rows often indicate parse failures upstream

Flag the long-tail rows for truncation review. Do NOT silently truncate.

### Step 4: Duplicate detection

Two passes:

1. **Exact duplicates:** SHA-256 hash of the rendered text. Cluster identical
   hashes. Report cluster sizes (a cluster of 50 identical rows usually means
   the upstream scrape captured a recurring template).
2. **Near-duplicates:** MinHash + LSH at `near_duplicate_threshold` Jaccard
   over 5-shingles. Cluster near-duplicates. Report cluster size distribution.

Recommend keeping one row per cluster (highest-quality by length / metadata
heuristic) unless the user has a reason to keep duplicates (preserving
distribution skew). Quarantine the rest.

### Step 5: Leakage check

For each row in `eval_path`, slide a `leakage_n_gram`-token window and check
membership in a precomputed set of train n-grams. Any eval row with ≥ 1
overlapping n-gram is flagged as a leakage candidate. Report:

- Count of eval rows with leakage candidates
- Top 10 most-overlapping eval rows with the matching train row IDs
- Recommendation: drop those train rows (NEVER drop the eval rows — that
  pollutes the eval set with selection bias)

A 13-gram is the conventional threshold (used in GPT-3 era contamination
analyses). Adjust if the dataset is short-text (smaller n) or code-heavy
(consider AST-level overlap, out of scope for this skill).

### Step 6: PII / sensitive content

Run entity detection per the supplied policy. Default minimum: emails, phone
numbers, SSN-like 9-digit patterns, IP addresses, credit-card-like 13-19 digit
sequences with Luhn check. Per finding, log:

- Row ID
- Entity type
- Entity span (offset + length, not the value itself in the findings report —
  the value goes to the quarantine file under restricted access)
- Recommended action per policy (redact / quarantine / drop)

If the policy specifies redaction style (e.g., `<EMAIL>`, `[REDACTED:phone]`),
emit a redacted-output companion file alongside quarantine. The skill never
performs irreversible redaction in place.

See `reference/pii-policy-schema.md` for the policy file format.

### Step 7: Label-quality sample

The audit cannot judge whether an assistant's response is correct. Pull a
random sample of `sample_for_label_quality` rows (default 100) into
`label-quality-sample.jsonl` for human review. Include a per-row rubric
template (correctness, helpfulness, format adherence, refusal appropriateness)
that the reviewer fills in. The sample is for the user's reviewer; the skill
does not score it.

### Step 8: Findings report + remediation

Final report sections:

1. **Dataset summary** — rows in train, rows in eval, format, target template
2. **Per-rule findings table** — rule · pass / fail · count · % · severity
3. **Quarantine manifest** — per-rule file path + row count + per-row IDs
4. **Recommended remediation order** — typically: parse failures → leakage →
   PII → near-duplicates → length truncation review → label-quality review
5. **Re-audit gate** — re-run this audit after applying any remediation; the
   audit is not a one-shot certification, it is a re-runnable gate

## Outputs

1. **Findings report** (markdown) — the 5-section structure above
2. **Quarantine directory** — `quarantine/<rule>.jsonl` per failing rule
   (parse-failures, near-duplicates, leakage-candidates, pii-flagged,
   length-over-budget)
3. **Label-quality sample** — `label-quality-sample.jsonl` for human review
4. **Audit manifest** — `audit-manifest.json` with timestamp, tool version,
   input file hashes, rule versions, parameters; reproducibility artifact
5. **Redacted-output companion** (if PII policy specifies redaction) —
   `train-redacted.jsonl` alongside the original (original is preserved)

## Failure modes

- **Silent row drops** — caught by `drop_policy="quarantine"` default; rows
  are moved to quarantine files, never deleted, and the manifest records the
  per-rule count
- **Eval set used as a filter for train** — caught by Step 0: the audit is
  one-directional. Leakage findings recommend dropping TRAIN rows, never
  removing rows from eval. Removing rows from eval would pollute it with
  selection bias.
- **Chat-template mismatch masked by tokenizer not erroring** — caught by
  Step 2 explicit checks for literal template tokens in rendered output and
  un-substituted Jinja delimiters; tokenizers often accept malformed input
  without raising
- **PII catalog assumed to be comprehensive** — caught by treating the policy
  as user-supplied input; the default minimum is explicitly flagged as
  minimum, not sufficient; the report includes a caveat that the audit only
  catches what the policy describes
- **Near-duplicate clustering collapses legitimate near-paraphrases** —
  caught by reporting cluster sizes and surfacing the largest clusters for
  manual review before drop; default threshold 0.85 is conservative
- **Leakage check inflates false positives on common boilerplate** — caught
  by reporting top-overlap eval rows for spot-check; recommend lengthening
  `leakage_n_gram` if the dataset has heavy templated text
- **Label-quality sample treated as the answer** — caught by Step 7's
  explicit framing: the skill produces the sample, the human judges. The
  audit does NOT score correctness.

## References

- `reference/chat-template-audit.md` — per-template conformance ruleset and caveats (Llama-3, ChatML, Mistral-v3, Gemma-2)
- `reference/pii-policy-schema.md` — JSON / YAML schema for the PII policy input file
- [Hugging Face `apply_chat_template` docs](https://huggingface.co/docs/transformers/main/en/chat_templating) — canonical reference for chat templating
- [Brown et al. 2020 *Language Models are Few-Shot Learners*, appendix C](https://arxiv.org/abs/2005.14165) — origin of the 13-gram contamination convention
- [Lee et al. 2022 *Deduplicating Training Data Makes Language Models Better*](https://aclanthology.org/2022.acl-long.577/) — MinHash + LSH deduplication patterns

## Examples

### Example 1: Scraped support-forum corpus, target Llama-3.1-8B (happy-path)

Input: `train_path=./train.jsonl` (120K rows ShareGPT format),
`eval_path=./eval.jsonl` (2K held-out), `format="sharegpt"`,
`target_chat_template="llama-3"`, default PII policy.

Output: Audit produces findings — 412 rows fail parse (ShareGPT
alternating-role violations), 18K rows are near-duplicates clustered
into 6K groups (recommend keeping 1 per cluster → ~15K drops), 47 eval
rows have 13-gram overlaps with 31 train rows (drop those 31 train rows),
903 rows flag for PII (731 emails, 142 phone numbers, 30 IP addresses).
Quarantine files written under `quarantine/`. Label-quality sample of 100
rows produced. Re-audit recommended after remediation.

### Example 2: Synthetic data with template echo (edge-case)

Input: Same audit run on a different corpus produced by self-instruct
generation from GPT-4. Format is ShareGPT, target template is ChatML.

Output: Chat-template conformance finds 8,200 rows where the assistant
content contains literal `<|im_start|>` tokens — the generator was prompted
with ChatML examples and the model echoed the template scaffolding into the
responses. Audit flags this as a content-leak class, NOT a parse failure;
recommend regenerating those rows or stripping the template tokens from
assistant content with a documented post-processor. Leakage check is clean
because synthetic data did not overlap eval.

### Example 3: Pre-curated Alpaca-cleaned subset (anti-trigger)

Input: User asks to audit a 5K-row subset of `yahma/alpaca-cleaned` before
fine-tuning a small model for prototyping.

Output: Skill notes that `alpaca-cleaned` has been audited upstream
(documented in its dataset card). Recommends a spot-check (sample 100 rows,
verify format + length distribution) rather than the full audit. Does NOT
re-run leakage / PII / near-duplicate at full scale; explains the upstream
audit covers those. Hands the user to the lighter spot-check workflow.

## See also

- `ml-datasci/auditing-train-test-split` — required pre-step; without a held-out eval, leakage detection cannot run
- `ml-datasci/running-eval-before-after-finetune` — the post-fine-tune evaluation skill this audit pairs with
- `ml-datasci/writing-finetune-spec-sheet` — the documentation artifact that should cite this audit's manifest
- `security/scrubbing-PII-with-policy` (planned) — deeper PII workflow if the policy is more involved than this skill's audit pass
- `ml-datasci/auditing-data-quality` — sibling for tabular datasets; this skill is the SFT-corpus analogue

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-4, skill 5.4.1) via PRAGMATIC discipline
