---
name: running-eval-before-after-finetune
description: >
  Runs a paired before/after evaluation comparing a base checkpoint to its
  fine-tuned descendant on a held-out eval set. Picks the paired test per
  metric family: McNemar (with exact/mid-p for small discordant counts) for
  paired-binary classification, paired-t or Wilcoxon signed-rank (auto-
  selected on Shapiro) for paired-continuous metrics like log-likelihood /
  BLEU / ROUGE-L, and Cochran's Q for 3+ checkpoints. Reports effect sizes
  with 95% confidence intervals and attributes change to the fine-tune
  rather than to sampling variance. Use after an SFT or DPO run produces a
  candidate checkpoint and the user wants to certify the fine-tune helped
  with evidence stronger than a single-number metric delta. Refuses to
  certify improvement without a paired baseline-checkpoint comparison on
  the same held-out eval, and flags underpowered evals as inconclusive.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - ml-engineer
  - data-scientist
  - stats-student
  - ai-security
evidence:
  - DU-MSDSAI-4441-Final
  - llm-safety-alignment-study
  - multiturn-injection-detection
last-updated: 2026-05-23
---

# Running a Before / After Fine-Tune Evaluation

## When to use

Trigger this skill when the user has a fine-tuned checkpoint and wants to
know whether it is genuinely better than the base checkpoint it was derived
from, and one of:

- An SFT run just completed and the user wants to gate the model swap on
  evidence of improvement (not just "the loss went down")
- A DPO / KTO / IPO preference-tuning run produced a candidate and the user
  wants to verify safety / helpfulness gains on a held-out eval
- A regression suite is comparing two checkpoint candidates (e.g., two SFT
  recipes) against the same base
- Three or more checkpoints (base, SFT-v1, SFT-v2) need to be compared on
  the same eval set (Cochran's Q for paired binary, or paired-folds
  Friedman for continuous)
- The user reports "my fine-tune got 73% on the eval, the base got 68% —
  ship it" without naming a paired test
- Keywords: "before / after fine-tune", "did the fine-tune help", "compare
  base to fine-tune", "is my SFT better than the base", "paired eval"

## When NOT to use

Skip this skill and hand off when:

- The user has no baseline checkpoint (only the fine-tuned model exists).
  The paired test requires both. Refuse to certify improvement; suggest the
  user evaluate the base on the same eval set first.
- The user wants to compare two independently-trained models (different
  bases, different data), not a base vs its fine-tuned descendant — that is
  `ml-datasci/comparing-models-fairly` (planned); the paired-on-same-base
  assumption does not hold
- The eval set is the training set or overlaps with it — this is the
  leakage failure mode that `ml-datasci/auditing-sft-dataset` Step 5
  catches before training; if it was missed, return there first
- The metric is throughput / latency / cost / GPU memory — those are
  systems benchmarks, not statistical comparisons
- The user wants a single-checkpoint evaluation (no comparison) — use
  `ml-datasci/evaluating-binary-classifiers` (binary), `ml-datasci/evaluating-multiclass-classifiers` (planned), or task-specific eval skills

## Quick start

User says: "I fine-tuned Llama-3.1-8B on a customer-intent classification
task. Base model gets 68% on my 500-row held-out eval; fine-tune gets 73%.
That's a 5-point improvement. Should I ship it?"

Skill walks the 6-step workflow: confirm pairing (both checkpoints scored
on the same eval), pick the test (McNemar for paired binary), compute the
test statistic, compute the effect size (odds ratio with 95% CI) and the
absolute improvement with paired CI, run a power-check (is n=500 enough to
detect a 5-point shift at the observed disagreement rate?), and emit the
certify / do-not-certify decision with explicit reasoning.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `base_predictions_path` | path | yes | — | Per-row predictions / scores from the base checkpoint on the eval set. |
| `finetune_predictions_path` | path | yes | — | Per-row predictions / scores from the fine-tuned checkpoint on the same eval set, in the same row order. |
| `eval_labels_path` | path | yes | — | Ground-truth labels for the eval set. Row-aligned with both prediction files. |
| `metric_family` | "paired-binary" \| "paired-continuous" \| "paired-multi-checkpoint" | yes | — | Drives test selection. `paired-binary` = per-row correct/incorrect on a classification task (McNemar); `paired-continuous` = per-row continuous metric like log-likelihood / BLEU (paired-t or Wilcoxon); `paired-multi-checkpoint` = 3+ checkpoints to compare (Cochran's Q or Friedman). |
| `alpha` | float in (0, 1) | no | `0.05` | Significance level for the paired test. The skill always reports the effect size + CI separately; `alpha` is for the test decision only. |
| `minimum_detectable_effect` | float | no | (auto) | The smallest effect the user cares to detect. Required for the power-check step. If omitted, the skill computes the achieved power at the observed effect and reports it instead. |
| `continuous_subtest` | "auto" \| "paired-t" \| "wilcoxon" | no | `"auto"` | For `paired-continuous`. `auto` runs Shapiro on the per-row differences; uses paired-t if Normal (p > 0.05), Wilcoxon signed-rank otherwise. |
| `mcnemar_correction` | "auto" \| "continuity" \| "exact" \| "mid-p" | no | `"auto"` | For `paired-binary`. `auto` picks `exact` if the discordant count is < 25, `continuity` otherwise. `mid-p` is offered for users who prefer the mid-p convention. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check items off as the audit progresses:

```
Before / after fine-tune eval progress:
- [ ] 0. Pre-flight — same eval set, row-aligned files, both checkpoints scored
- [ ] 1. Pair the per-row outcomes — build the paired record (base_outcome, finetune_outcome) per row
- [ ] 2. Pick the test per metric_family (and assumption check for continuous)
- [ ] 3. Compute the test statistic + p-value
- [ ] 4. Compute the effect size with 95% CI (odds ratio for McNemar / Cohen's dz for paired-t / Cliff's δ paired for Wilcoxon)
- [ ] 5. Power-check — is the eval large enough to detect the minimum_detectable_effect at the observed discordance rate?
- [ ] 6. Certify / do-not-certify with explicit attribution language and residual risks
```

### Step 0: Pre-flight

- Verify both prediction files have the same number of rows as the eval label file
- Verify row alignment by hashing the first 10 input strings from each file and confirming they match (catches the "I evaluated the base on eval-v1 and the fine-tune on eval-v2" silent error)
- Verify both predictions cover every row (no NaN, no missing rows)
- Verify the eval set is held-out per `ml-datasci/auditing-sft-dataset` Step 5 — leakage candidates flagged there must have been remediated, or the eval comparison is invalid
- If `metric_family = paired-multi-checkpoint`, verify the user supplied a third (and beyond) checkpoint's predictions

### Step 1: Pair the per-row outcomes

For `paired-binary`:

- Per row, derive `base_correct ∈ {0, 1}` and `finetune_correct ∈ {0, 1}` from the predictions and labels
- Build the 2x2 contingency table:
  - **a** = base_correct AND finetune_correct (both right)
  - **b** = base_correct AND finetune_wrong (regression on this row)
  - **c** = base_wrong AND finetune_correct (gain on this row)
  - **d** = base_wrong AND finetune_wrong (both wrong)
- The McNemar test operates on **b** and **c** (discordant pairs); **a** and **d** are concordant and do not contribute to the test (this is THE reason McNemar is the right test, not chi-squared on the marginals)

For `paired-continuous`:

- Per row, compute the per-row metric (log-likelihood, BLEU, ROUGE-L, exact-match-F1, etc.) for both checkpoints
- Build the per-row paired differences `d_i = finetune_metric_i - base_metric_i`

For `paired-multi-checkpoint`:

- Build the matrix of per-row outcomes across all checkpoints (rows = eval rows, columns = checkpoints)

### Step 2: Pick the test

- **paired-binary** → McNemar's test on the (b, c) discordant pairs
  - If `b + c < 25` → exact binomial McNemar (also called the exact McNemar / mid-p variant); the chi-squared approximation is unreliable for small discordant counts
  - If `b + c ≥ 25` → continuity-corrected McNemar (chi-squared with Yates)
- **paired-continuous**, `continuous_subtest = "auto"`:
  - Shapiro-Wilk on the per-row differences `d_i`
  - If Shapiro p > 0.05 (and n < ~5000 where Shapiro becomes hypersensitive) → paired-t
  - Otherwise → Wilcoxon signed-rank
- **paired-multi-checkpoint binary** → Cochran's Q
- **paired-multi-checkpoint continuous** → Friedman's test (followed by paired post-hoc Wilcoxon with Holm correction if Friedman is significant)

State the gating assumption check that drove the choice in the report — e.g., "Shapiro p = 0.003 on the per-row differences → using Wilcoxon signed-rank, not paired-t."

### Step 3: Compute the test statistic + p-value

Standard library calls — `statsmodels.stats.contingency_tables.mcnemar`, `scipy.stats.ttest_rel`, `scipy.stats.wilcoxon`, `scipy.stats.cochran`, `scipy.stats.friedmanchisquare`. Report:

- Test name (e.g., "exact McNemar")
- Test statistic
- p-value
- Discordant count or n (whichever is relevant for the test)

### Step 4: Compute the effect size with 95% CI

The p-value alone tells you nothing about magnitude. Required effect-size + CI per test:

- **McNemar (paired-binary 2-checkpoint)** → odds ratio `c / b` with 95% CI (use the exact binomial-proportion CI on the proportion `c / (b + c)` and transform); OR report the absolute accuracy difference `(c - b) / n` with the paired-proportion 95% CI
- **paired-t** → Cohen's `dz = mean(d) / sd(d)` with 95% CI (parametric)
- **Wilcoxon signed-rank** → paired rank-biserial correlation `r = 1 - (2 * W / (n*(n+1)/2))` with bootstrap 95% CI; or Cliff's delta for the paired ordering
- **Cochran's Q / Friedman** → Kendall's W (coefficient of concordance) with bootstrap 95% CI; post-hoc paired effect sizes per pair

Direction sentence: always state which checkpoint is higher. "Fine-tune > base by Δaccuracy = 0.041 [95% CI: 0.012, 0.071]." Never just "the test was significant."

(Cross-reference `ml-datasci/reporting-effect-sizes` for the per-test effect-size selector.)

### Step 5: Power-check

The eval set must be large enough to detect the effect the user cares about, given the observed discordance / variance:

- **paired-binary** → at the observed discordance rate `(b + c) / n`, what is the achievable power to detect a minimum-detectable-effect (MDE) of `minimum_detectable_effect` at `alpha`? Compute via `statsmodels.stats.power.NormalIndPower` adapted for the paired-proportion test, or via simulation.
- **paired-continuous** → at the observed `sd(d)`, what is the achievable power to detect an MDE of `minimum_detectable_effect` at `alpha`? Compute via `statsmodels.stats.power.tt_solve_power(effect_size, n, alpha)`.

If `minimum_detectable_effect` was not supplied, instead report the achieved power at the observed effect size; if achieved power < 0.8, flag the eval as underpowered for this comparison.

### Step 6: Certify / do-not-certify

Final report block:

- **Verdict** — `certified-improvement` / `certified-no-difference` / `certified-regression` / `underpowered-inconclusive`
- **Attribution** — explicit language: "The observed Δ of <value> is attributable to the fine-tune at α = <alpha>, with effect size <ES> [95% CI: <low>, <high>]." OR "The observed Δ of <value> is within sampling variance at α = <alpha>; cannot attribute to the fine-tune."
- **Residual risks** — drift on production traffic that doesn't match the eval, single eval set (no per-segment breakdown), training-eval set drift if the eval was constructed before the fine-tune data was collected, multiple-comparison cost if the user evaluated against several candidate checkpoints (the eval set was reused; apply Holm or Bonferroni)

See `reference/test-selector.md` for a one-page decision-tree summary.

## Outputs

1. **Paired-evaluation report** (markdown) — the 6-step structure above with the verdict block at the end
2. **Per-row paired records** (CSV / JSONL) — for audit: `row_id, label, base_pred, finetune_pred, base_correct, finetune_correct, base_metric, finetune_metric, diff` — so a reviewer can re-run any test independently
3. **Contingency table** (2x2 for paired-binary, or paired-difference distribution plot for paired-continuous) — image asset alongside the report
4. **Power-curve plot** — power vs n at the observed discordance rate / variance; helps the user decide whether to expand the eval before re-running
5. **Eval manifest** — checkpoint IDs, eval set hash, predictions file hashes, library versions, test parameters — reproducibility artifact

## Failure modes

- **Marginal-totals chi-squared instead of McNemar** — caught by Step 2 explicitly naming McNemar for paired-binary and rejecting the marginal-totals chi-squared; the discordant pairs are what carry the paired information
- **Paired-t on non-Normal differences** — caught by Step 2 `continuous_subtest = "auto"` running Shapiro on the per-row differences and switching to Wilcoxon
- **Significant p-value on a tiny effect size (large eval, trivial improvement)** — caught by Step 4 requiring effect size + CI; the report leads with the effect, not the p-value
- **Underpowered eval declared "no significant difference"** — caught by Step 5 power-check; an underpowered "no difference" finding gets `underpowered-inconclusive`, not `certified-no-difference`
- **Different eval sets compared** — caught by Step 0 hash check on the input rows; row-alignment is verified, not assumed
- **Reused eval across many candidate checkpoints (multiple-comparison inflation)** — caught by Step 6 residual-risks block flagging multiple-comparison cost and recommending Holm correction on the family of comparisons
- **Eval contamination from training data** — out of scope for this skill; flagged in `When NOT to use` with the redirect to `auditing-sft-dataset`
- **Single-checkpoint evaluation mislabeled as "before / after"** — caught by `When NOT to use` redirecting to single-checkpoint eval skills

## References

- `reference/test-selector.md` — decision tree from metric_family to test + effect-size pairing
- `reference/power-recipe.md` — paired-proportion and paired-continuous power computation recipes
- [Pembury Smith & Ruxton 2020 *Effective use of the McNemar test*](https://doi.org/10.1007/s00265-020-02916-y) — McNemar with exact / continuity / mid-p variants
- [Dietterich 1998 *Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms*](https://doi.org/10.1162/089976698300017197) — McNemar vs 5x2cv for ML comparison
- [Demšar 2006 *Statistical Comparisons of Classifiers over Multiple Data Sets*](https://www.jmlr.org/papers/v7/demsar06a.html) — Friedman + Nemenyi for multi-checkpoint
- `ml-datasci/reporting-effect-sizes` — the effect-size selection skill this one composes with
- `ml-datasci/checking-test-assumptions` — the assumption-check skill driving the auto-subtest selection in Step 2

## Examples

### Example 1: Customer-intent classifier, paired-binary (happy-path)

Input: `metric_family="paired-binary"`, base on 500-row eval = 68% correct,
fine-tune = 73%. Contingency: a=320 (both right), b=21 (regression),
c=46 (gain), d=113 (both wrong); discordant b+c = 67.

Output: Skill runs continuity-corrected McNemar (b+c ≥ 25): χ² ≈ 8.61,
p ≈ 0.0033. Effect size: Δaccuracy = (c − b) / n = (46 − 21) / 500 =
0.050 [95% CI: 0.014, 0.086] via paired-proportion CI. Direction: fine-tune
> base by 5 percentage points. Power-check at the observed b+c rate of 13.4%
on n=500 has 0.80 power to detect MDE = 0.04 at α=0.05 (matches user's
implied "5 point" threshold). Verdict: `certified-improvement`. Residual
risks: single eval set (no per-intent-class breakdown reported; recommend
follow-up per-class McNemar with Holm correction across the K classes).

### Example 2: Continuous perplexity with non-Normal differences (edge-case)

Input: `metric_family="paired-continuous"`, n=2000 eval rows, per-row
log-likelihood from both checkpoints. `continuous_subtest="auto"`.

Output: Shapiro on the per-row LL differences returns p = 0.0008 → skill
switches to Wilcoxon signed-rank. W test statistic returned, p = 0.041.
Effect size: paired rank-biserial r = 0.18 with bootstrap 95% CI [0.04, 0.31].
Direction: fine-tune log-likelihood > base log-likelihood (positive median
of the per-row differences). Verdict: `certified-improvement (small effect)`.
Skill explicitly notes the Wilcoxon choice was driven by the Shapiro
assumption check; reports BOTH the paired-t result as a sensitivity check
(p = 0.029, dz = 0.05) and notes the qualitative agreement.

### Example 3: Single-checkpoint evaluation (anti-trigger)

Input: User says: "I fine-tuned a model and got 73% on my eval. Evaluate
it." (No base-checkpoint predictions supplied.)

Output: Skill does NOT run the paired test (it has no base predictions to
pair against). Explains that the certify/do-not-certify framing requires a
baseline. Recommends: (1) evaluate the base on the same eval first, then
return for the paired analysis; (2) or use a single-checkpoint eval skill
(`evaluating-binary-classifiers`, etc.) if the user only wants to describe
the fine-tune's standalone performance. Refuses to call 73% "good" or "an
improvement" without the comparison.

## See also

- `ml-datasci/auditing-sft-dataset` — required pre-step; eval must be held out, contamination remediated
- `ml-datasci/reporting-effect-sizes` — required composition; this skill's Step 4 outputs are produced under that skill's discipline
- `ml-datasci/checking-test-assumptions` — drives the Shapiro-based auto-subtest selection in Step 2
- `ml-datasci/selecting-statistical-test` — sibling for the broader test-selection decision tree (this skill is the fine-tune-specific instance)
- `ml-datasci/comparing-models-fairly` (planned) — sibling for comparing two independently-trained models (not paired-on-same-base)
- `ml-datasci/writing-finetune-spec-sheet` — the documentation artifact that this evaluation report should be attached to

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-4, skill 5.4.2) via PRAGMATIC discipline
