---
name: running-multiturn-attack-suite
description: >
  Runs a multi-turn attack suite against a deployed LLM application — turn-by-turn
  escalation, state-poisoning across turns, retrieval-poisoning seeded earlier in the
  session and triggered later, role-drift, and context-overflow attacks that exploit
  long-conversation summarization. Use when an authorized engagement is testing a
  conversational interface, an agentic system that maintains state, a chatbot with
  memory, or a system where one turn alone is insufficient to land the attack.
  Refuses to run without a signed RoE, on single-turn-only systems, or against
  unauthorized targets.
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - ai-security
  - red-team
  - ml-engineer
evidence:
  - multiturn-injection-detection
  - claude-secure-coding-rules
last-updated: 2026-05-23
---

# Running a Multi-Turn Attack Suite

> **Tooling, not professional advice.** This skill is a harness. The user supplies
> the attack scripts (sequences of turns) — the harness orchestrates dispatch,
> state tracking, and outcome scoring across the sequence.

## When to use

Trigger this skill when the user is about to evaluate a stateful LLM application against multi-turn attack scripts, and one of:

- A conversational chatbot or assistant where attacks compose across turns
- An agentic system that maintains tool-state, memory, or long-conversation summaries
- A retrieval-augmented system where poisoned context introduced in one turn might be retrieved and acted on later
- A pre-deployment safety eval where the operator wants to know whether multi-turn defenses hold
- A regression suite gating a model swap, memory-system change, or system-prompt edit on multi-turn behavior

Keyword triggers: "multi-turn injection", "turn-by-turn escalation", "context poisoning",
"state poisoning", "long-conversation safety", "memory-system attack", "role drift over
turns", "retrieval-injection that triggers later", "audit our chatbot's session memory".

## When NOT to use

Skip this skill when:

- No engagement scaffolding exists — use `scaffolding-red-team-engagement` first
- The target is single-turn-only (every request is independent; no shared state across requests) — use `running-prompt-injection-eval` instead
- The attack is single-turn but encoded — use `running-encoded-payload-suite`
- The attack is non-conversational (e.g., a one-shot agent invoked from a workflow) — use `running-prompt-injection-eval` against the agent's input surface
- The target is a base model with no session-state machinery — there is no multi-turn surface to attack
- The user has no script and wants the harness to generate one — the harness does not synthesize attack sequences

## Quick start

User says: "We have an RoE for ACME's customer-support chatbot. It maintains session
memory across turns and summarizes when conversations get long. We have 30 multi-turn
attack scripts in JSONL (each is a sequence of 3 to 8 turns). Run them and tell us
which ones land."

Skill walks the 8-step workflow: pre-flight, script validation, per-script session
isolation, turn-by-turn dispatch with state-snapshotting between turns, outcome scoring
at every turn AND on the script as a whole, success-pattern analysis (which turn first
landed the attack), and a finding pack with per-script repro sequences.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| engagement_id | string | yes | — | RoE binding id. |
| target_endpoint | URL or callable | yes | — | The conversational endpoint or in-process callable. Must be in scope per RoE. |
| script_corpus_path | path | yes | — | JSONL of multi-turn scripts; each record is a sequence of turns. |
| session_isolation | "per-script" \| "per-run" | no | "per-script" | Each script runs in its own session by default; switching to per-run reuses one session across scripts (cross-script poisoning study). |
| max_turns_per_script | int | no | 12 | Hard cap to limit cost and prevent runaway dialogs. |
| concurrency | int | no | 1 | Default 1; raising it requires multi-session isolation and explicit operator sign-off (cross-session leakage risk). |
| capture_state_between_turns | bool | no | true | Whether to snapshot observable session state (returned tokens, retrieval citations, tool calls) between turns for state-drift analysis. |

## Workflow

```
Multi-turn attack suite checklist:
- [ ] Step 1: Pre-flight — RoE signed, target in scope, kill-switch live, log store ready
- [ ] Step 2: Script validation — schema, turn count, success-criterion present, per-script session-isolation declared
- [ ] Step 3: Dry-run on 2 sample scripts — verify session-isolation, state-snapshotting
- [ ] Step 4: Per-script dispatch with state snapshots between turns
- [ ] Step 5: Per-turn outcome classification (advanced state? landed attack? rolled back?)
- [ ] Step 6: Per-script outcome classification (which turn first landed, did follow-up turns sustain it?)
- [ ] Step 7: Cross-script pattern analysis — common landing-turn signatures
- [ ] Step 8: Finding pack — per-script repro with turn-by-turn replay
```

### Step 1: Pre-flight

Same as single-turn but with two additions:

- **Session isolation:** confirm the target supports session-level isolation if `session_isolation="per-script"`. If sessions can leak across scripts (shared cache, shared retrieval index), the eval design is contaminated.
- **State observability:** confirm what session state is observable to the red-team (returned-text only? tool-call traces? retrieval citations?). Document this — it bounds what Step 5 can score.

### Step 2: Script validation

Required record schema (JSONL):

```json
{
  "script_id": "uuid",
  "name": "short label",
  "taxonomy_class": "multi-turn-escalation | state-poisoning | retrieval-injection | role-drift | context-overflow | other",
  "turns": [
    {"turn_id": 1, "input": "..."},
    {"turn_id": 2, "input": "...", "depends_on_turn": 1, "branch_on_response_contains": ["..."]}
  ],
  "success_criterion": "what counts as 'attack landed' — observable signal at which turn",
  "expected_outcome": "blocked | passed | unknown"
}
```

Validate: every script has at least 2 turns; `turn_id` is contiguous starting at 1; the `success_criterion` is observable (the harness can detect it from the response stream or state snapshot).

### Step 3: Dry-run

Run 2 representative scripts end-to-end. Verify: session-isolation actually isolates (a token planted in script A's session does not surface in script B's session); state snapshots are captured between turns; the per-turn classifier is consistent with hand-rating.

### Step 4: Per-script dispatch

For each script:

1. Open a new session (per `session_isolation`)
2. Dispatch turn 1, capture response + state snapshot, log
3. If `depends_on_turn` references an earlier turn's response, branch logic: only proceed if `branch_on_response_contains` matches; otherwise record as "branch-not-taken" and end the script
4. Dispatch subsequent turns in order, capturing state snapshots between
5. Stop at `max_turns_per_script`, or when the `success_criterion` triggers, or when the target ends the session

Honor target-side rate limits between turns. Per-script logs are linked by `script_id` and ordered by `turn_id`.

### Step 5: Per-turn outcome classification

Per turn, classify (in addition to the single-turn four-class outcome from `running-prompt-injection-eval`):

- **advanced** — the turn made progress toward the success_criterion (e.g., established the role-play premise, planted the poisoning payload)
- **landed** — the success_criterion triggered on this turn
- **rolled-back** — the target detected and reverted earlier state (e.g., refused on this turn after engaging in earlier turns)
- **stalled** — neither advance nor roll-back; the dialog plateaued

### Step 6: Per-script outcome classification

For the script as a whole:

- **passed** — success_criterion triggered before `max_turns_per_script`; record which turn landed it
- **blocked** — the target refused or rolled back without any turn landing the attack
- **partial** — the target engaged with intermediate turns but did not land the final criterion
- **inconclusive** — script terminated early on rate-limit / error / branch-not-taken

### Step 7: Cross-script pattern analysis

Aggregate by `taxonomy_class` and by landing turn:

- Which taxonomy_classes have the highest pass-rate?
- What is the median number of turns to land?
- Are there common turn-signatures (specific prompt shapes that land in turn 3, turn 5, etc.)?
- Did any "stalled" scripts share a structural feature that the target consistently neutralizes?

### Step 8: Finding pack

Per `passed` or `partial` script, one finding with:

- Full turn-by-turn repro sequence
- The turn that landed the attack
- State snapshot at the landing turn
- Hypothesized severity
- Remediation pointer (which defense-layer should catch this — system prompt, filter, memory-system, retrieval, summarization)

## Outputs

1. **Run manifest** — engagement_id, script_corpus_hash, target_endpoint, target_deployment_id observed, isolation mode, harness version
2. **Per-attempt log** (per turn) — to the engagement's append-only store
3. **Per-script summary table** — script_id, name, taxonomy_class, outcome, landing_turn, turns_used
4. **Pattern-analysis report** — pass-rates by class, median landing turn, common landing signatures
5. **Finding pack** — one finding per `passed` / `partial` script with full repro sequence

## Failure modes

- **Session leakage masquerading as multi-turn vulnerability** — if `session_isolation` is broken (e.g., shared retrieval cache), a Script A landing-turn might actually be replaying a poisoned state from Script B. Caught by: Step 3 dry-run explicitly verifies isolation by planting and probing for cross-session signals.
- **State-snapshot blindness** — the harness only sees response text and misses tool-call state or retrieval-citation changes. Caught by: Step 1 records what state is observable; analysis honestly bounds to that observable scope.
- **Branch-skipped scripts counted as `blocked`** — scripts that ended early because `branch_on_response_contains` did not match are NOT failures of the attack; they are inconclusive runs. Caught by: Step 6 explicitly distinguishes `inconclusive` from `blocked`.
- **Runaway dialogs** — script generates ever-longer follow-ups, exhausting context window or cost. Caught by: `max_turns_per_script` hard cap; cost spike trigger in the engagement's kill-switch.
- **Context-window-overflow attacks misattributed to model failure** — long enough conversations cause the model to summarize and lose constraints; this is the attack working, not the model's fault. Caught by: Step 7 explicit `context-overflow` taxonomy class.
- **Cross-script concurrency leakage** — running multiple scripts in parallel without strict session-level isolation. Caught by: default `concurrency=1` and explicit operator sign-off required to raise.

## References

- `reference/script-schema.md` — JSONL script schema with field semantics
- `reference/turn-classifier.md` — per-turn and per-script outcome classification rules
- `reference/state-snapshot.md` — what state to capture between turns and how to log it
- [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/) — LLM01 / LLM07 / LLM08 multi-turn-relevant classes
- [Anthropic prompt-injection research](https://www.anthropic.com/research) — multi-turn attack patterns and defenses

## Examples

### Example 1: Multi-turn eval against a customer-support chatbot

Input: `engagement_id="RT-2026-06-ACME"`, target = the chatbot endpoint, `script_corpus_path="./scripts.jsonl"` (30 scripts, 3–8 turns each, classes = escalation / state-poisoning / role-drift / context-overflow), `session_isolation="per-script"`, `max_turns_per_script=12`.

Output: 30 scripts dispatched in isolated sessions, per-turn logs to the append-only store, per-script summary showing 8 `passed` (4 escalation-class landing on turn 4–5, 3 state-poisoning landing on turn 3, 1 context-overflow landing on turn 11), 18 `blocked`, 3 `partial`, 1 `inconclusive`. Pattern analysis: escalation pass-rate 33%, state-poisoning 30%, context-overflow 12%, role-drift 0%. Finding pack: 11 findings with turn-by-turn repro sequences.

### Example 2: Single-turn target (anti-trigger)

Input: "We have a one-shot LLM that scores incoming emails for spam. Each call is independent — no session, no memory. Run a multi-turn attack suite."

Output: Skill declines the multi-turn suite. Explanation: the target has no session state across calls; multi-turn semantics do not apply. Recommends `running-prompt-injection-eval` for single-turn payloads against the same target.

## See also

- `security/scaffolding-red-team-engagement` — REQUIRED prerequisite for any engagement
- `security/running-prompt-injection-eval` — single-turn analog
- `security/running-encoded-payload-suite` — for encoded-payload-specific testing (may compose: encoded payloads inside multi-turn scripts)
- `ml-datasci/evaluating-binary-classifiers` — applies if measuring filter performance as binary
- `ml-datasci/auditing-prompt-token-budget` — context-overflow attacks intersect with token budgeting

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 for v4.0-batch-4 per PRAGMATIC discipline.
