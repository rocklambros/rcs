---
name: pre-registering-eval-study
description: >
  Locks the hypothesis, falsification criteria, stopping rules, and power
  justification of an empirical evaluation BEFORE any data is collected or
  observed. Use when designing an LLM eval, an A/B experiment, a clinical or
  observational study, an ML model comparison, or any decision that will rest
  on a test statistic. Produces a one-page pre-registration document committed
  to a versioned location prior to the first run, so that HARKing
  (hypothesizing after results are known), p-hacking, optional-stopping, and
  outcome-switching cannot quietly inflate the false-positive rate. Refuses to
  pre-register vague hypotheses ("model A is better"), open-ended stopping
  rules ("until results stabilize"), or post-hoc rationalizations of data
  already observed.
version: 0.1.0
status: shipped
track: workflow
audience: [data-scientist, ml-engineer, security-eng, stats-student, instructor]
evidence:
  - llm-safety-alignment-study
  - DU-MSDSAI-4441-Final
  - incident-rank-validation
last-updated: 2026-05-23
---

# Pre-registering an Eval Study

## When to use

Trigger this skill when the user requests or implies one of:

- Designing an LLM eval, jailbreak-judge study, A/B test, clinical-style study, or model comparison whose conclusion will be reported as "significant" or "we picked X"
- Phrases like "before we run this", "lock in the design", "pre-register", "commit to the analysis plan", "what's the right sample size?"
- Stakes high enough that a false positive (or a false negative) would be costly: deployment go/no-go, paper submission, regulatory filing, security claim
- Repeated-comparison settings where peeking would balloon Type-I error (sequential A/B, interim looks, multi-arm bandits framed as confirmatory)

## When NOT to use

Hand off to a different skill or proceed without pre-registration when:

- The work is genuinely exploratory (EDA) and the user is not going to claim "significant" — pure pattern-finding to generate hypotheses for a later confirmatory study is its own legitimate mode; use a data-exploration pattern instead
- The user wants help running a pre-registered design that is already locked — recommend an execution skill, not this one
- The decision has no inferential test attached (e.g., a UX preview where the team just wants to look)
- Throwaway prototypes whose results will not be published or used to gate a downstream decision

## Quick start

User says: *"We want to evaluate whether Claude Sonnet 4.6 is safer than Claude Haiku 4.5 on our jailbreak corpus. About 500 prompts. How do we set this up?"*

Skill response: produces a filled-in pre-registration with (1) primary hypothesis stated as a one-sentence directional claim with an operationalized outcome; (2) the statistical test selected and the effect-size threshold that would count as meaningful; (3) a stopping rule fixed in advance (here: all 500 prompts scored, no peeking); (4) a power calculation showing 500 prompts is or is not adequate to detect the minimum-effect-of-interest at the chosen α; (5) the falsification criterion — what numeric result would let the team say "no, Sonnet is not safer"; (6) the commit hash + path where the pre-registration lives.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| study_kind | "llm-eval" \| "ab-test" \| "clinical" \| "model-comparison" \| "observational" | yes | — | Selects the appropriate template section. |
| primary_outcome | string | yes | — | One operationalized metric (e.g., "jailbreak success rate per 100 prompts"). Vague outcomes ("safety") get bounced. |
| effect_threshold | number + units | yes | — | The minimum effect the user wants to detect; drives the power calc. |
| alpha | float | no | 0.05 | Type-I error rate. |
| stopping_rule | "fixed-n" \| "group-sequential-with-spending" \| "bayesian-posterior-threshold" | yes | — | No "until results stabilize" allowed. |
| commit_location | path | yes | — | Where the pre-registration markdown lives; must be committed before data observation. |

## Workflow

Copy this checklist into the response and check off each item before any data is observed:

```
Pre-registration progress:
- [ ] Primary hypothesis stated as one directional, falsifiable sentence
- [ ] Primary outcome operationalized (metric + unit + measurement procedure)
- [ ] Statistical test selected and justified by data characteristics
- [ ] Minimum effect of interest fixed with units
- [ ] Power calculation showing planned n detects the effect at chosen α
- [ ] Stopping rule fixed in advance (no "until results stabilize")
- [ ] Falsification criterion stated (what result would refute the hypothesis)
- [ ] Multiplicity correction chosen if > 1 outcome (Bonferroni, Holm, FDR)
- [ ] Pre-registration document committed to versioned location BEFORE data observation
- [ ] Commit hash recorded in any subsequent analysis report
```

### Step 1 — Hypothesis

One sentence, directional, falsifiable. "Model A produces fewer jailbreak successes than Model B on the company corpus." NOT "Model A is better."

### Step 2 — Outcome operationalization

Name the metric, its units, and the measurement procedure. Jailbreak success = judge model returns `unsafe: true`. Two independent judges; Cohen's κ reported alongside.

### Step 3 — Test + assumption gate

Pick the test using the `ml-datasci/selecting-statistical-test` decision tree. Name the assumption check that gates the choice (e.g., "Shapiro-Wilk on the difference scores; Wilcoxon if p < 0.05").

### Step 4 — Effect threshold + power

The minimum effect of interest comes from the user (domain knowledge), not from the data. Once fixed, run a power analysis: at α and chosen test, what sample size achieves ≥ 0.8 power to detect that effect? If the planned n is below the requirement, the design is underpowered — say so before collecting data.

### Step 5 — Stopping rule

Choose ONE:

- **Fixed-n**: data collection stops at the pre-planned sample size. No early peeks.
- **Group-sequential with alpha-spending**: pre-planned interim analyses; alpha allocated per look (Pocock / O'Brien-Fleming / Lan-DeMets). Document the spending function.
- **Bayesian posterior threshold**: stop when the posterior probability of the hypothesis crosses a pre-specified threshold. Document the prior, the threshold, and the maximum-n cap.

"Until results stabilize" is not a stopping rule. Reject and ask the user to pick one of the three above.

### Step 6 — Falsification

State the specific numeric result that would let the user say "no, the hypothesis is wrong." If no such result exists, the hypothesis is not falsifiable; rewrite it.

### Step 7 — Commit BEFORE observation

Write the pre-registration to a versioned location (git repo, OSF, AsPredicted, the company's pre-reg registry). Record the commit hash. Any analysis report that references this study must cite the commit hash; any deviation from the pre-registered plan must be flagged as an exploratory secondary analysis, not as the primary result.

## Outputs

A single markdown document with these sections in order:

1. **Study identifier** — slug + commit hash + author + date
2. **Primary hypothesis** — one directional sentence
3. **Primary outcome** — metric, units, measurement procedure
4. **Statistical test** — chosen test + the gating assumption check
5. **Effect threshold + power** — minimum effect of interest + sample size + computed power
6. **Stopping rule** — fixed-n / sequential / Bayesian, fully specified
7. **Falsification criterion** — the result that would refute the hypothesis
8. **Multiplicity plan** — if > 1 outcome, the correction method
9. **Deviations log** — empty at pre-registration; populated post-hoc if the plan changed

The output is committed BEFORE data observation; the commit hash is the artifact's identity.

## Failure modes

Known pitfalls in pre-registration and how this skill catches them:

- **Vague hypothesis** ("model A is better"). Caught by: the directional + falsifiable requirement in Step 1; refuse to proceed without a one-sentence operational claim.
- **HARKing** (hypothesizing after results are known). Caught by: the "commit BEFORE observation" rule and the requirement to record the commit hash in the analysis report.
- **Optional stopping** ("we'll stop when it's significant"). Caught by: the "until results stabilize" rejection and the three-choice menu in Step 5.
- **Underpowered design hidden by post-hoc power**. Caught by: the power calc happens BEFORE data collection and is recorded in Step 4; post-hoc power computed on the observed effect is explicitly disallowed.
- **Outcome switching** (the primary outcome quietly becomes whatever was significant). Caught by: the primary outcome is locked in Step 2; any change is logged as a deviation in Step 9 and demotes the analysis to exploratory.
- **Multiple-comparisons leak** (10 outcomes, no correction). Caught by: Step 8 requires a correction plan when k > 1.

## References

- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — eval-first authoring discipline
- [Nosek et al. 2018, *The preregistration revolution* (PNAS)](https://www.pnas.org/doi/10.1073/pnas.1708274114) — origin of modern pre-registration practice
- [Wagenmakers et al. 2012, *An agenda for purely confirmatory research*](https://journals.sagepub.com/doi/10.1177/1745691612463078) — confirmatory vs exploratory distinction
- [Center for Open Science pre-registration templates](https://osf.io/zab38/) — field-specific templates worth adapting

## Examples

### Example 1: LLM jailbreak study (happy-path)

Input: *"Evaluate whether Claude Sonnet 4.6 is safer than Claude Haiku 4.5 on our jailbreak corpus of 500 prompts."*

Output: a pre-registration document with primary hypothesis ("Sonnet 4.6 produces fewer judged-unsafe completions than Haiku 4.5 on the 500-prompt corpus"); operationalized outcome ("unsafe rate = count of judge-model-`unsafe:true` per 100 prompts; two independent judges; Cohen's κ reported"); test (McNemar's paired binary, both models on the same prompts); minimum effect of interest (5 percentage-point absolute reduction); power calc (n = 500 gives power 0.84 at α = 0.05 for a 5pp effect on a baseline rate of 12% — adequate); fixed-n stopping rule; falsification (Sonnet unsafe-rate ≥ Haiku unsafe-rate minus 1pp). Committed to repo path with hash recorded.

### Example 2: Anti-trigger (pure EDA)

Input: *"I just got 50K rows of customer churn data. What patterns are in there?"*

Output: skill declines to engage. Explains EDA does not need pre-registration because no confirmatory claim is being made. Notes that any specific hypothesis the user wants to confirm AFTER finding it in this data must be tested on a FRESH dataset (HARKing protection); the EDA itself can be done freely.

## See also

- `workflow/running-adversarial-premortem` — the retrospective failure-mode analysis; pre-registration is the prospective counterpart
- `ml-datasci/selecting-statistical-test` — the decision tree for Step 3's test choice
- `ml-datasci/checking-test-assumptions` — runs the assumption gate cited in Step 3
- `ml-datasci/running-power-analysis` (planned v2-batch-4) — deep dive on the power calc in Step 4
- `workflow/writing-successor-primers` — pairs well after pre-registration to hand off the locked design

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 under PRAGMATIC discipline as part of v2-batch-3 (research-discipline cluster)
