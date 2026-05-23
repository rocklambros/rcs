---
name: recommending-model-tier
description: >
  Recommends which Claude tier — Haiku, Sonnet, or Opus — to route each task in
  a pipeline through, based on reasoning depth required, latency budget,
  per-call cost target, context-window pressure, and whether the task is
  classification / extraction / summarization / planning / coding / agentic /
  multi-step. Returns a per-task tier assignment with a confidence and a
  fallback escalation rule (e.g., 'Haiku first, escalate to Sonnet if the JSON
  schema fails'). Use whenever the user is designing a new LLM pipeline, has
  a single-tier deployment that is too slow or too expensive, asks which Claude
  model fits a specific task, is responding to a benchmark that disagrees with
  their current production tier, or is shipping a multi-stage agent. Refuses
  to engage on locked / single-vendor / single-tier deployments where the
  choice is already made by policy.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer, devops, security-eng]
evidence:
  - mac-harness architecture (subagent same-family cache lineage)
  - multiturn-injection-detection
  - email-spam-classifier-naive-bayes-comparisson-roc
last-updated: 2026-05-23
---

# Recommending Model Tier

## When to use

Trigger this skill when the user asks for or implies one of:

- "Which Claude model should I use for X?" — single-task tier choice
- "My pipeline is too slow / too expensive on Opus — can I move some steps to Sonnet or Haiku?" — multi-stage routing
- "Sonnet gets 92% on this benchmark, Haiku gets 87% — is Haiku good enough?" — cost-vs-quality trade
- Designing a new agentic loop or RAG pipeline that has > 1 LLM call per task
- Setting up subagents in Claude Code where same-family cache lineage matters
- Per-call cost is climbing and the user wants to know whether downgrading a step from Opus to Sonnet (or Sonnet to Haiku) is safe
- Latency P95 is breaching SLO and the user is considering a tier downgrade on the latency-critical step

This skill pairs with `ml-datasci/auditing-prompt-token-budget` (per-token cost depends on tier) and `ml-datasci/evaluating-binary-classifiers` / `ml-datasci/evaluating-regression-models` (the eval that should sit on top of any tier change).

## When NOT to use

Skip this skill and hand off or do nothing when:

- The user's deployment is locked to a single tier by policy / contract / on-prem licensing — the choice is already made; tier recommendation can't change it
- The user is on a non-Anthropic provider — tier names (Haiku / Sonnet / Opus) and their capability bands are Anthropic-specific; OpenAI / Gemini / Bedrock / Vertex have different families and the recommendations here would mislead
- The user is asking about model FINE-TUNING (different question; routes to a planned fine-tuning skill)
- The user wants a benchmark NUMBER for a specific task on a specific model — point them at MMLU / HumanEval / SWE-bench / domain-specific evals directly; this skill is for tier-selection given a task, not for predicting benchmark scores
- The user is in a context where audit-ability or determinism requires the same model for every call (e.g., regulated decisions, reproducible scientific claims) — recommend pinning to one tier and document the choice; don't mix-and-match

## Quick start

User says: "I'm building a 3-stage RAG pipeline: stage 1 classifies the user query into one of 8 intents, stage 2 retrieves and synthesizes from a knowledge base, stage 3 formats the answer. I'm currently using Opus for all 3 stages. Per-call cost is too high. Recommend tier per stage."

Skill response (in order):

1. **Stage 1 (intent classification, 8 classes):** Haiku 4.5. Reasoning depth = low; classification with a small label set is well within Haiku's competence. Latency budget tight (head of pipeline) → Haiku is the right cost/latency point. Fallback: if confidence on the returned class is low (model expresses uncertainty), escalate that call to Sonnet.
2. **Stage 2 (RAG synthesis from retrieved docs):** Sonnet 4.6. Reasoning depth = medium; synthesis across retrieved chunks needs more capacity than Haiku reliably provides, but doesn't require Opus's deep reasoning. Sonnet's cost is ~5× cheaper than Opus for ~95% of the synthesis quality on typical RAG tasks.
3. **Stage 3 (answer formatting, optional polish):** Haiku 4.5. Reformatting + tone adjustment is a Haiku-tier task.
4. **Escalation rule:** if the synthesized answer's faithfulness score (from an evaluator) is below threshold, re-run stage 2 on Opus.
5. **Cost projection:** going Haiku → Sonnet → Haiku versus Opus → Opus → Opus is roughly a 70–85% reduction in per-call input/output cost, depending on token mix.
6. **Same-family cache lineage:** if any stage is a subagent of a Claude Code parent session, choose the same family as the parent to share prompt cache (Opus parent → Opus subagent shares cache; Opus → Sonnet does NOT share cache).

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| task | "classification" \| "extraction" \| "summarization" \| "rag-synthesis" \| "planning" \| "tool-use" \| "code-generation" \| "agentic-loop" \| "judge" \| "rewrite" | yes | — | The category the task falls into. Drives the initial tier-band recommendation. |
| reasoning_depth | "low" \| "medium" \| "high" | yes | — | Low = single-step / pattern-match; medium = synthesis / multi-hop with retrieved context; high = open-ended planning / proof / complex code. |
| latency_budget_ms | int (P95) | no | unspecified | The P95 latency the call must hit. Tight budget (< 1500ms) biases toward Haiku. |
| cost_target | "minimize" \| "balanced" \| "quality-first" | no | "balanced" | Default tilts toward Sonnet; "minimize" toward Haiku-with-escalation; "quality-first" toward Opus. |
| context_window_pressure | "low" \| "medium" \| "high" | no | "low" | High = approaching the model's window; all current Claude 4 models share the 200k window, so this rarely changes the tier but matters for input-token cost. |
| parent_session_model | "claude-haiku-4-5" \| "claude-sonnet-4-6" \| "claude-opus-4-7" \| "none" | no | "none" | If this is a Claude Code subagent, same-family parent shares prompt cache; this can dominate the tier choice. |
| safety_critical | bool | no | false | Safety-critical tasks (decisions affecting users, content moderation, security gates) bias up one tier. |

## Workflow

Copy this checklist into the response and check items off as each step completes:

```
Tier-recommendation progress:
- [ ] Step 1: Decompose the pipeline into discrete tasks (one tier choice per task)
- [ ] Step 2: For each task, classify reasoning depth and latency budget
- [ ] Step 3: Map the (task × reasoning depth) pair to a baseline tier (Haiku / Sonnet / Opus)
- [ ] Step 4: Apply modifiers: safety-critical → up one; same-family cache lineage → match parent; tight latency → down one (if quality permits)
- [ ] Step 5: Define an escalation rule per task (when to retry on the next tier up)
- [ ] Step 6: Project cost and latency for the recommended assignment vs the current (or alternative) assignment
- [ ] Step 7: Recommend the eval that should sit on top of the tier change (the eval set that catches a regression if the downgrade is too aggressive)
```

### Step 1: Decompose the pipeline

A "model tier" recommendation makes no sense for a pipeline as a whole; it only makes sense per-task. Split the pipeline into discrete LLM calls and label each:

- Input format (structured / freeform text / multimodal)
- Output format (structured / freeform / tool call / code)
- Whether downstream code consumes the output as structured data
- Whether the task is on the critical path for user-perceived latency

### Step 2: Reasoning depth + latency budget

| Reasoning depth | Definition | Example tasks |
|---|---|---|
| Low | One-step pattern match; few-shot examples cover most cases | Intent classification with ≤ 10 labels, entity extraction from a sentence, simple format conversion |
| Medium | Multi-hop reasoning over retrieved context; synthesis across 2–5 sources | RAG synthesis, summarizing a 5-page document, multi-step extraction with reasoning |
| High | Open-ended planning, deep code reasoning, novel-problem decomposition, math/proof | Agentic loops with > 5 tool calls, complex code generation with cross-file context, security threat modeling, mathematical reasoning |

Latency budget:

| P95 latency budget | Implication |
|---|---|
| < 1500 ms | Strongly favors Haiku 4.5 |
| 1500–4000 ms | Sonnet 4.6 is the sweet spot |
| > 4000 ms | Opus 4.7 is acceptable; users tolerate the wait for high-reasoning output |
| Streaming (UI typing) | First-token latency matters more than total; all 3 tiers stream similarly fast for first token |

### Step 3: Map task × reasoning to baseline tier

| Task | Low | Medium | High |
|---|---|---|---|
| Classification | Haiku | Sonnet | Sonnet |
| Extraction | Haiku | Sonnet | Sonnet |
| Summarization | Haiku | Sonnet | Sonnet |
| RAG synthesis | Sonnet | Sonnet | Opus |
| Planning | Sonnet | Sonnet | Opus |
| Tool use (single tool) | Haiku | Sonnet | Sonnet |
| Tool use (multi-step agent) | Sonnet | Sonnet | Opus |
| Code generation | Sonnet | Sonnet | Opus |
| Judge / evaluator | Sonnet | Sonnet | Sonnet |
| Rewrite / style change | Haiku | Haiku | Sonnet |

**These are starting points, not commandments.** Apply the modifiers in Step 4.

### Step 4: Apply modifiers

- **Safety-critical** (content moderation, security gate, decisions affecting users): bump up one tier from the baseline
- **Same-family cache lineage** (Claude Code subagent of a parent session): match the parent's tier when feasible — Opus parent + Opus subagent shares prompt cache, Opus + Sonnet does not; cache savings can dominate the per-token cost difference
- **Latency-critical** (P95 < 1500 ms): bump DOWN one tier from the baseline if the eval permits the quality drop
- **Cost-target = minimize**: drop one tier from baseline AND add an escalation rule on the next-tier-up so the bad cases still recover
- **Context-window pressure high**: doesn't change tier (all Claude 4 models have 200k); but does suggest moving stable prefix into a cache_control segment (see `auditing-prompt-token-budget`)
- **Judge / evaluator role for an LLM-as-judge eval**: bias toward Sonnet; using Opus as judge for Opus output creates a same-family bias problem (the judge favors output that "thinks like it does"); use a different family or rotate the judge

### Step 5: Escalation rule per task

Single-tier deployments are brittle. For every task, define when to re-try on the next tier up:

- Structured-output task: escalate on schema validation failure
- Classification with confidence: escalate on `confidence < 0.7` or "unknown" label
- Code generation: escalate on test-failure of generated code
- RAG synthesis: escalate when an evaluator flags low faithfulness
- Agentic loop: escalate when the loop hits N consecutive tool failures or exceeds a turn budget

The escalation rule typically catches 5–15% of calls and recovers most of the quality loss from the downgrade.

### Step 6: Project cost and latency

Per-million-token list prices (approximate; check current docs):

| Tier | Input $/M | Output $/M | Cache-write 1h | Cache-read |
|---|---|---|---|---|
| Haiku 4.5 | $1 | $5 | $2 | $0.10 |
| Sonnet 4.6 | $3 | $15 | $6 | $0.30 |
| Opus 4.7 | $15 | $75 | $30 | $1.50 |

For a 5,000-input + 1,000-output token call:

| Tier | Cost per call |
|---|---|
| Haiku 4.5 | $0.010 |
| Sonnet 4.6 | $0.030 |
| Opus 4.7 | $0.150 |

A 3-stage pipeline going Opus → Opus → Opus = $0.45/call; going Haiku → Sonnet → Haiku = $0.050/call (~90% reduction).

Latency P50 estimates (vary by load; verify against your own deployment):

| Tier | P50 latency (5k in + 1k out) |
|---|---|
| Haiku 4.5 | ~1.0 s |
| Sonnet 4.6 | ~2.5 s |
| Opus 4.7 | ~5.0 s |

### Step 7: Eval recommendation

A tier downgrade without an eval set is a hope, not a decision. Recommend the eval that catches a regression:

- Classification: a holdout test set with per-class precision/recall on the new tier
- RAG synthesis: a golden Q-A set with faithfulness + answer-relevance scored
- Code generation: a regression suite of test cases
- Agentic loop: a scenario-based eval (5–20 scenarios) with task completion as the metric

Run the eval on BOTH tiers (old and proposed); the downgrade is acceptable if the new tier's score is within a pre-specified delta (typical: ≤ 3 percentage-point drop).

## Outputs

A short markdown report:

1. **Pipeline decomposition** — one row per LLM call, with task, reasoning depth, latency budget, output format
2. **Per-task tier recommendation** — Haiku / Sonnet / Opus with one-sentence rationale referencing the Step 3 baseline + Step 4 modifiers
3. **Escalation rules** — per task, the condition that triggers a re-run on the next tier up
4. **Cost projection** — current vs proposed: per-call $, daily $, monthly $
5. **Latency projection** — current vs proposed: per-call P50/P95 (estimated from the per-tier numbers in Step 6)
6. **Eval recommendation** — what to measure, on which holdout set, with what threshold for "acceptable downgrade"
7. **Same-family cache note** — if any task is a Claude Code subagent, the lineage implication of the tier choice

## Failure modes

- **Recommending one tier for the whole pipeline** — treating "which model should I use?" as a single answer when the pipeline has 3+ heterogeneous tasks. Caught by: Step 1 decomposes into per-task tier choices.
- **Downgrading without an escalation rule** — moving Opus → Haiku on a structured-output task and shipping it; the 5–15% of inputs Haiku gets wrong now fail silently. Caught by: Step 5 requires an escalation rule on every downgrade.
- **Downgrading without an eval set** — relying on vibes ("Haiku looked fine on 5 examples I tried"). Caught by: Step 7 requires the eval recommendation and a pre-specified delta threshold.
- **Same-family cache miss when a subagent crosses families** — Claude Code parent on Opus, dispatching a subagent on Sonnet for "cost reasons" — the subagent loses all parent-prompt cache reads. The "savings" are wiped out and then some by cache writes on the colder family. Caught by: Step 4 modifier explicitly checks parent_session_model.
- **Using Opus to judge Opus output** — same-family judge bias; the judge consistently rates Opus output higher than it deserves. Caught by: Step 4 modifier biases judge to Sonnet (or recommends a different family / rotation).
- **Tier-bumping safety-critical tasks the wrong direction** — moving a content-moderation step from Sonnet to Haiku to save cost. False-negatives on moderation are the bad outcome and they get worse on the lower tier. Caught by: Step 4 modifier biases safety-critical tasks UP, not down.
- **Picking tier based on a single benchmark number** — "Sonnet gets 92% on MMLU, Haiku 87%, so Sonnet is best" — ignoring that MMLU is not the task, latency is not on MMLU, cost isn't on MMLU. Caught by: Step 3 baseline maps task category, not benchmark percentage; Step 6 brings in cost; Step 7 requires task-specific eval.

## References

- [`reference/tier-cheat-sheet.md`](reference/tier-cheat-sheet.md) — per-task tier table with cost and latency for quick lookup
- [Anthropic model overview](https://docs.claude.com/en/docs/about-claude/models) — current capability bands, pricing, context windows for Haiku 4.5 / Sonnet 4.6 / Opus 4.7
- mac-harness `mac/ARCHITECTURE.md` — origin of the same-family-cache-lineage principle for Claude Code subagents

## Examples

### Example 1: 3-stage RAG pipeline (happy-path)

Input: "3-stage RAG pipeline: (1) intent classification across 8 intents, (2) RAG synthesis from retrieved docs, (3) answer formatting. Currently all Opus. Per-call cost too high. Recommend tier per stage."

Output:
- **Stage 1** (classification, 8 classes, low reasoning depth): **Haiku 4.5**. Baseline = Haiku per Step 3; latency-critical (head of pipeline). Escalation: if model returns "unknown" or low-confidence, re-run on Sonnet.
- **Stage 2** (RAG synthesis, medium reasoning depth): **Sonnet 4.6**. Baseline = Sonnet; not safety-critical; synthesis quality is the deliverable. Escalation: if downstream faithfulness check (e.g., RAGAS) scores below 0.7, re-run on Opus.
- **Stage 3** (answer formatting, low reasoning depth, rewrite task): **Haiku 4.5**. Baseline = Haiku.
- **Cost projection:** Opus×3 ≈ $0.45/call → Haiku/Sonnet/Haiku ≈ $0.050/call ≈ 89% reduction.
- **Latency P50:** ~15s → ~4.5s (~70% reduction).
- **Eval:** golden Q-A set with intent accuracy (stage 1), faithfulness + answer-relevance (stage 2), format-correctness (stage 3); ≤ 3pp drop is acceptable on each metric.

### Example 2: Benchmark says Sonnet, cost requires Haiku (edge-case)

Input: "I have a new content-moderation classifier. On my internal eval, Sonnet gets 92% accuracy and Haiku gets 88%. My budget only fits Haiku-priced calls. Can I just ship Haiku?"

Output: Not without an escalation rule. Content moderation is safety-critical (Step 4 modifier biases UP one tier), so the baseline pushes back against the downgrade. Ship recommendation: **Haiku as the primary with an escalation rule on low-confidence outputs to Sonnet**. Concretely: ask Haiku to return a confidence (or run a separate confidence head); if confidence < 0.85, re-run on Sonnet. Empirically the escalation typically catches 10–20% of calls and recovers most of the 4-point accuracy gap, at a marginal cost. Also: re-do the eval with the escalation logic in place; the question isn't Haiku vs Sonnet alone, it's Haiku+escalation vs Sonnet alone. Track the escalation rate post-deployment; if it climbs above 30%, the cost case for Haiku is gone.

### Example 3: Single-tier locked deployment (anti-trigger)

Input: "Our company has an enterprise contract that locks us to Sonnet 4.6 only — no other tiers allowed. What model should I use for my new classifier?"

Output: The tier choice is already made by policy; recommending Haiku or Opus would be ignored. The right answer is to use Sonnet (no choice) and put the engineering effort into the levers that DO matter: prompt design, few-shot example curation, structured-output format, escalation-to-human on low-confidence, and prompt caching (see `auditing-prompt-token-budget`). Skill does NOT walk the per-task tier recommendation workflow because the output isn't actionable in this constraint. Confirms the user's locked-tier reality and routes the question to the levers under their control.

## See also

- `ml-datasci/auditing-prompt-token-budget` — once the tier is picked, the next lever is caching on the chosen model
- `ml-datasci/evaluating-binary-classifiers` — the eval that should sit on top of any tier change for a classification task
- `ml-datasci/evaluating-regression-models` — same idea for regression tasks
- `ml-datasci/building-baseline-models` — before tier-shopping, verify the task even needs an LLM; a Dummy / LogReg baseline may already be enough

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
