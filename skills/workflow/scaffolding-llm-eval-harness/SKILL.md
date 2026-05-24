---
name: scaffolding-llm-eval-harness
description: >
  Scaffolds a structured LLM-evaluation harness from an empty directory. Locks
  in the five fields every comparable eval-run must carry — model_id (with
  revision SHA or API model string), dataset_hash (sha256 of the eval input
  set), prompt_version (semver of the prompt template), judge_model (which model
  graded the output, if any), and results.jsonl (one row per scenario per
  candidate) — and produces the eval-runner skeleton, scenario template,
  per-scenario rubric format, and CI gating hook. Use whenever the user is
  starting a multi-scenario LLM-evaluation pipeline, comparing prompts /
  fine-tunes / model versions across a fixed test set, or asking how to
  structure LLM evals "so the results are actually comparable across runs."
  Refuses for one-shot single-prompt API calls (different concern; just call
  the API) and refuses for ML-classifier evaluation (different skill — use
  evaluating-binary-classifiers / evaluating-multiclass-classifiers).
version: 0.1.0
status: shipped
track: workflow
audience: [ml-engineer, ai-security, data-scientist, skill-author]
evidence:
  - llm-safety-alignment-study
  - multiturn-injection-detection
  - llm-toxicity-visual-analysis
last-updated: 2026-05-23
---

# Scaffolding an LLM-Evaluation Harness

## When to use

Trigger this skill when the user:

- Is starting a structured LLM-evaluation pipeline from an empty or near-empty directory
- Is about to compare two or more prompts, fine-tunes, or model versions on a fixed test set and wants run-over-run comparability
- Has a corpus of evaluation scenarios (jailbreak attempts, RAG questions, summarization inputs, classifier inputs) and asks "how do I structure the harness around them"
- Asks "what fields do I need in my eval result rows so different runs are comparable"
- Is about to roll their own ad-hoc eval script and would benefit from the five-field contract before they start

## When NOT to use

Skip this skill and hand off when:

- The user is making a one-shot single-prompt API call — they just need the API, not a harness
- The user is evaluating a non-LLM classifier (use `ml-datasci/evaluating-binary-classifiers` or `ml-datasci/evaluating-multiclass-classifiers`)
- The user is evaluating a regression model (use `ml-datasci/evaluating-regression-models`)
- The user is evaluating retrieval (use `ml-datasci/evaluating-rag-retrieval`)
- A harness already exists with the five fields in place — the work is adding a scenario, not scaffolding (no scaffold needed)
- The user is auditing fine-tune deltas (use `ml-datasci/running-eval-before-after-finetune` — that is a paired-test discipline, not a harness scaffold)

## Quick start

User: *"I want to evaluate three prompts across 200 jailbreak scenarios and 5 candidate models. Set up the harness."*

Skill walks the 8-step checklist (Workflow below), produces: `pyproject.toml` (pinned `anthropic`, `openai`, `pytest`), `scenarios/` directory with the JSON scenario schema documented in `reference/scenario-schema.json`, `prompts/` directory with versioned prompt files (`prompts/v1.txt`, `prompts/v2.txt`, ...), `eval_runner.py` that emits `results.jsonl` rows carrying all five fields, `judge.py` template if `judge_model` is configured, `Makefile` or `tasks.py` with `make eval` / `make compare`, `.gitignore` (ignores `results-*.jsonl` outputs but commits the scenarios), and `README.md` documenting the five-field contract.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| project_name | string | yes | — | Project slug for the harness directory + pyproject `name`. |
| candidate_models | list[string] | yes | — | Model identifiers for the candidate models being compared. Anthropic API model strings (e.g., `claude-sonnet-4-6`) or Hugging Face revisions (`meta-llama/Llama-3-8b@sha:abc123`). At least one. |
| judge_model | string \| null | no | null | Model identifier for the LLM-judge that grades open-ended outputs. Null means rubric-only / programmatic grading (regex, exact-match, classifier head). |
| scenario_format | "jsonl" \| "json-per-file" | no | "json-per-file" | One file per scenario (easier to diff / review) or one consolidated jsonl. |
| include_ci | bool | no | true | Whether to scaffold `.github/workflows/eval-suite.yml` that runs the harness on PR. |
| prompt_version_init | string | no | "0.1.0" | Starting SemVer for the prompt template. Bumped MAJOR on any contract change, MINOR on any text change that may affect outputs, PATCH on typos / whitespace. |

## Workflow

Copy this checklist into the response and check off each item as the scaffold lands:

```
Scaffold progress:
- [ ] 1. Verify empty target directory
- [ ] 2. Write pyproject.toml with pinned anthropic/openai/pytest deps
- [ ] 3. Create scenarios/ with the documented JSON schema (per reference/scenario-schema.json)
- [ ] 4. Create prompts/v0.1.0.txt (the initial prompt template — version pinned)
- [ ] 5. Write eval_runner.py emitting results.jsonl with the five fields per row
- [ ] 6. Write judge.py template (if judge_model is set) — also emits judge_model into each result row
- [ ] 7. Write Makefile / tasks.py with `eval` (run harness) + `compare` (diff two result jsonls)
- [ ] 8. Write .gitignore (ignore results-*.jsonl; KEEP scenarios/ and prompts/ committed) + README.md (five-field contract documented prominently)
```

### The five-field contract

Every row in `results.jsonl` MUST carry these fields. Without them, two eval runs cannot be compared meaningfully:

| Field | Type | Why it matters |
|---|---|---|
| `model_id` | string | The candidate model under test. Format: `<provider>/<model>@<revision>` (e.g., `anthropic/claude-sonnet-4-6@2026-04-15`). Without a revision pin, the same `model_id` string can refer to two different model weights one month apart. |
| `dataset_hash` | string | sha256 of the canonical-form-serialized scenario set (sorted keys, LF newlines). Detects when "the same eval" silently changed underneath you (a scenario was edited, added, removed). |
| `prompt_version` | string | SemVer of the prompt template used. Lets you ATTRIBUTE a result delta to a prompt change vs. a model change. |
| `judge_model` | string \| null | If LLM-judged, the judge's model_id (same pin format). Same-family bias matters — `judge_model = candidate_model` is suspect. |
| `result_row` | object | The actual scenario_id + completion + rubric scores + timestamp. The other four fields are the FRAME; this is the payload. |

### Step 1 — Verify empty target

Refuse if the directory already has `pyproject.toml`, `eval_runner.py`, `scenarios/`, or git history > 1 commit. Same greenfield discipline as the other two batch-5 scaffolds.

### Step 2 — pyproject.toml

Pin `anthropic~=0.40`, `openai~=1.50` (if cross-provider), `pytest~=8.3`, `jsonschema~=4.23`. Lock the env. See `reference/pyproject-eval-template.toml`.

### Step 3 — scenarios/

JSON files (one per scenario) under `scenarios/`. Each file matches `reference/scenario-schema.json`. The default schema mirrors the RCS eval-protocol (matching `docs/eval-protocol.md`): exactly 3 rubric items per scenario, `query`, `scenario_kind`, `expected_behavior`.

### Step 4 — prompts/

Versioned prompt templates: `prompts/v0.1.0.txt`, then `v0.2.0.txt`, etc. The `prompt_version` in every results row points at one of these. Never edit a published version in place — bump the SemVer and commit the new file.

### Step 5 — eval_runner.py

A skeleton that:

1. Loads scenarios via `scenarios/*.json`
2. Computes `dataset_hash = sha256(canonical_serialize(scenarios))`
3. For each `(candidate_model, scenario)` pair, sends the prompt + scenario.query, captures completion
4. Optionally invokes `judge.py` with `judge_model` to grade rubric items
5. Appends one row per scenario per candidate to `results-<utc-iso>.jsonl` with all five fields

See `reference/eval_runner_template.py`.

### Step 6 — judge.py (if `judge_model` set)

Receives the candidate completion + rubric items + scenario context; returns per-rubric-item pass/fail with a one-sentence rationale. Records `judge_model` into the result row.

Same-family bias warning baked into the template comment: "If `judge_model` shares a model family with any candidate_model, document this in the README — judge bias toward same-family completions is documented in the LLM-as-judge literature."

### Step 7 — Makefile / tasks.py

```makefile
.PHONY: eval compare lint

eval:
	uv run python eval_runner.py --output results-$$(date -u +%Y-%m-%dT%H-%M-%SZ).jsonl

compare:
	uv run python compare.py results-baseline.jsonl results-candidate.jsonl

lint:
	uv run python -m jsonschema -i scenarios/*.json reference/scenario-schema.json
```

### Step 8 — .gitignore + README.md

`.gitignore` ignores `results-*.jsonl` (per-run outputs, not under version control) AND keeps `scenarios/` + `prompts/` committed (the dataset and prompts ARE under version control — that is the whole point of `dataset_hash` and `prompt_version`).

README.md leads with the five-field contract table, then the run workflow.

## Outputs

A populated harness with the following files:

```
<project_name>/
  pyproject.toml
  uv.lock
  .gitignore
  README.md
  Makefile                          (or tasks.py)
  eval_runner.py
  judge.py                          (if judge_model set)
  compare.py
  scenarios/
    01-example.json                 (one stub scenario per scenario_kind)
    02-example.json
    03-example.json
  prompts/
    v0.1.0.txt
  .github/
    workflows/
      eval-suite.yml                (if include_ci)
```

Plus the printed "what's next" pointer:

```
Done. Next:
  uv sync                                       # install deps
  Edit scenarios/*.json to your test set
  Edit prompts/v0.1.0.txt to your template
  make eval                                     # produce first results.jsonl
  make compare                                  # once you have two runs to diff
```

## Failure modes

Known pitfalls and how this skill catches them:

- **Missing model revision in `model_id`** — `claude-sonnet-4-6` without a date pin can silently refer to two different model weights months apart. Caught by the README + result-row schema documenting the `@<revision>` requirement.
- **Silent scenario edits invalidating run comparability** — editing `scenarios/foo.json` between two runs and then comparing them is comparing different evals. Caught by `dataset_hash` (sha256 of canonical scenario serialization) in every result row; comparison tooling refuses to diff rows with mismatched hashes.
- **Prompt edited in place without version bump** — same problem as scenarios, different file. Caught by versioned `prompts/vX.Y.Z.txt` files + README rule "never edit a published version."
- **Same-family judge bias** — if `judge_model` is in the same family as a candidate, the candidate may be scored higher. Caught by the judge.py template comment + README guidance.
- **Wrong skill engaged for a one-shot API call** — would scaffold 11 files for what should be 3 lines of code. Caught by "When NOT to use" handoff.
- **Wrong skill engaged for ML-classifier eval** — would miss confusion matrix / ROC / PR / calibration. Caught by "When NOT to use" handoff to `evaluating-binary-classifiers`.

## References

- `reference/scenario-schema.json` — JSON Schema for scenario files; mirrors `docs/eval-protocol.md`
- `reference/eval_runner_template.py` — the runner skeleton with the five-field result row
- `reference/pyproject-eval-template.toml` — pinned dependencies for the harness
- [Anthropic LLM-as-judge guidance](https://docs.claude.com/en/docs/test-and-evaluate/strengthen-guardrails/classification) — the same-family bias warning
- `../scaffolding-ml-research-notebook/` — sibling for the broader project-scaffold pattern

## Examples

### Example 1: Multi-prompt × multi-model jailbreak eval (happy-path)

Input: *"I want to evaluate three prompts across 200 jailbreak scenarios and 5 candidate models. Set up the harness. Judge model is claude-opus-4-7."*

Output: Skill walks the 8-step checklist. pyproject.toml pins anthropic SDK. scenarios/ stub illustrates the JSON schema. prompts/v0.1.0.txt is the initial template. eval_runner.py iterates candidate_models × scenarios, emits one results row per pair with all five fields (model_id with `@<revision>` pin, dataset_hash, prompt_version="0.1.0", judge_model="anthropic/claude-opus-4-7@<rev>", result_row). README leads with the five-field contract. CI workflow scaffolded. User edits scenarios + prompt, runs `make eval`, gets a comparable baseline.

### Example 2: ML-classifier evaluation (anti-trigger handoff)

Input: *"I want to evaluate my fraud classifier on a test set of 10,000 transactions."*

Output: Skill refuses to scaffold an LLM-eval harness for what is a binary-classifier evaluation. Hands off to `ml-datasci/evaluating-binary-classifiers`: a classifier evaluation needs ROC / PR / calibration / confusion matrix / threshold sweep — not `prompt_version` / `judge_model`.

### Example 3: One-shot API call (anti-trigger)

Input: *"I'm just making one Anthropic API call from a Python script to summarize a document. Scaffold an eval harness."*

Output: Skill declines. Explains that a one-shot single-prompt API call is not an "eval" — it is an inference. Suggests three lines of code calling the SDK directly. Notes that an eval harness becomes useful when the user has multiple scenarios AND multiple candidate prompts/models that need run-over-run comparability.

## See also

- `workflow/scaffolding-ml-research-notebook` — sibling: greenfield for ML/DS research projects
- `workflow/scaffolding-security-research-repo` — sibling: greenfield for security-research projects
- `ml-datasci/evaluating-binary-classifiers` — the right tool for binary classifier evals (not LLM evals)
- `ml-datasci/evaluating-multiclass-classifiers` — the right tool for multi-class classifier evals
- `ml-datasci/evaluating-rag-retrieval` — the right tool for retrieval-eval pipelines
- `ml-datasci/running-eval-before-after-finetune` — paired-test discipline for fine-tune deltas (different concern than scaffolding)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
