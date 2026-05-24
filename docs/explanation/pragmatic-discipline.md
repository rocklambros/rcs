# PRAGMATIC: the eval discipline RCS actually uses

What PRAGMATIC is, why it exists, what it sacrifices, and when to use the full 3-model harness instead.

## The short answer

PRAGMATIC is a fast, in-session eval flow that validates skills against Sonnet only, using Claude Code's own subagent-dispatch mechanism. It has shipped every skill in the RCS catalog (104 as of v7.0.3). The trade is fast iteration over exhaustive model coverage.

The full 3-model harness in `tools/run_evals.py` (Haiku + Sonnet + Opus, requires `ANTHROPIC_API_KEY`) is the aspirational gold standard. It is run on periodic re-validation sweeps and on demand when a regression is suspected.

## Why a separate flow exists

The `tools/run_evals.py` harness was designed first. It makes API calls, costs money, requires a key, runs out-of-session, produces JSON results files, and takes minutes per skill. For a single-skill release that is acceptable overhead. For a batch of 10 skills, each with 3 scenarios across 3 models, it is 90 API calls per release, costing real money and waiting real minutes.

For an author iterating on a skill body, the harness is too slow to be part of the loop. Authors stop using it. Skills ship without evals. The validation discipline degrades.

PRAGMATIC was designed to be fast enough to stay in the loop. It runs in-session, uses subagents the author can already dispatch, costs nothing beyond the session's token usage, and produces results immediately. The author runs evals as part of authoring instead of as a separate step.

## The mechanics

For each of the 3 scenarios in a skill's `evals/` directory:

1. The parent session (the author working in Claude Code) dispatches one general-purpose subagent with `model: sonnet`
2. The subagent is instructed to read the SKILL.md and any bundled reference files, then answer the scenario's `query` as if the skill were loaded in its context
3. The subagent's completion comes back to the parent
4. The parent judges the completion against the scenario's 3 rubric items using intent-matched scoring (not literal phrasing)

Three scenarios × one subagent each = three dispatches per skill. A batch of four skills = twelve dispatches, dispatched in parallel. Wall time: ten to twenty minutes.

## Pass thresholds

Same as the Sonnet column in the 3-model harness:

- happy-path: 3 of 3 rubric items pass
- edge-case: 3 of 3 rubric items pass
- anti-trigger: ≥ 2 of 3 rubric items pass

A skill that meets all three ships at `status: shipped`. A skill that fails any one ships at `status: drafting`, with the failing rubric item noted in the CHANGELOG. Drafting skills are visible in the catalog but not auto-invocable.

## Intent-matched scoring

Sonnet-judging-Sonnet has a same-family bias risk. Strict literal scoring amplifies the risk because the model may use slightly different phrasing than the rubric item names while still meeting the intent.

PRAGMATIC compensates by judging against intent rather than literal phrasing. Example: if a rubric item says "recommends Wilcoxon signed-rank, NOT paired t-test," a completion that says "switches to the rank-based paired test" passes if it is clearly the same recommendation, even though it does not use the word "Wilcoxon." A completion that says "use the paired t-test with caution because the assumptions are violated" fails, because the intent is to switch tests, not to continue with caveats.

The judge documents borderline cases in the CHANGELOG so a future reviewer can see where intent-matched scoring was applied.

## What PRAGMATIC sacrifices

**Smaller-model coverage.** A skill that passes Sonnet may fail Haiku because Haiku skims long bodies, misses nuance, or shortcuts to a fast answer. PRAGMATIC does not catch these failures. The 3-model harness does.

**Same-family bias.** Sonnet judging Sonnet may agree with itself on completions that a different judge would mark wrong. The 3-model harness uses Sonnet as judge but evaluates Haiku and Opus as candidates, which partially mitigates this. The full mitigation (rotating judges) is a v2 protocol change.

**No artifact for downstream re-evaluation.** PRAGMATIC's results live in the session transcript and the CHANGELOG entry. They are not machine-readable JSON files. A reviewer cannot diff results across two PRAGMATIC runs the way they can across two `run_evals.py` runs.

## When PRAGMATIC is appropriate

- Authoring a new skill from scratch (the iteration loop matters)
- Shipping a batch of methodology-only skills where the gap evidence is already in repo history
- Patching an existing skill's body and re-validating only the changed scenarios
- Working without `ANTHROPIC_API_KEY` (open-source contributors without an account)

## When to use the full 3-model harness instead

- Periodic re-validation sweeps (RCS does these on a quarterly cadence when possible)
- Skills targeting safety-critical or regulated-decision contexts where Haiku-tier behavior matters
- Skills where the v0.1 PRAGMATIC release passed but downstream users have reported regressions on smaller models
- Public-release model swaps (when Claude ships a new model version, the catalog gets re-validated against the new revision)

## What "Sonnet-only" means for downstream users

A skill that ships as PRAGMATIC-validated is reliable on Sonnet (the current default model in Claude Code for most workloads). Behavior on Haiku and Opus is not guaranteed but is likely to be similar; the skill format is designed to be model-agnostic, and same-family models share most of their pattern-following discipline.

If you run RCS skills against a non-Anthropic model (a port to GPT, Gemini, or open-weights), no validation flow has tested that path. The skill format is portable in principle; the actual behavior is your problem to evaluate.

## The compromise documented

PRAGMATIC is a deliberate compromise, not an accident. The full 3-model harness is the right discipline; PRAGMATIC is what shipping skills daily requires. Both flows exist; the choice between them is documented per release in the CHANGELOG entry.

The shorthand "PRAGMATIC" appears in every CHANGELOG entry through v7.0.3. When you see it, the skill was validated only against Sonnet, intent-matched scoring, in-session dispatch. When you see "Flow B" or "full 3-model harness," the skill was validated externally with `tools/run_evals.py`.

## Why the discipline is named PRAGMATIC

Because the alternative was to keep promising a 3-model validation in the docs while shipping Sonnet-only in practice. That was the state of the repo through v7.0.0: `docs/eval-protocol.md` claimed 3-model validation, every actual skill shipped with Sonnet-only validation. The doc and the practice diverged silently.

Naming the actual practice and documenting it explicitly is the fix. PRAGMATIC is the actual practice. The 3-model harness is the aspirational flow that runs when convenient. Both are honest about what they cover and what they do not.
