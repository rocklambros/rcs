# Test selector — paired before/after fine-tune evaluation

This is the one-page decision tree invoked by Step 2 of `running-eval-before-after-finetune`. The skill's body cites it; this file documents the full tree with the gating-assumption-check rules and the paired effect-size pairing per test.

## Decision tree

```
metric_family?
├── paired-binary (one fine-tune vs one base, per-row correct/incorrect)
│     │
│     ├── discordant count b + c < 25?
│     │     ├── yes → exact McNemar (binomial / mid-p)
│     │     │           effect: odds ratio c/b  OR  Δaccuracy = (c-b)/n
│     │     │           with paired-proportion 95% CI
│     │     │
│     │     └── no  → continuity-corrected McNemar (Yates χ²)
│     │                 effect: same as above
│     │
│     └── (chi-squared on marginal totals is WRONG here — discards pairing)
│
├── paired-continuous (one fine-tune vs one base, per-row continuous metric)
│     │
│     ├── continuous_subtest = "auto":
│     │     │
│     │     ├── Shapiro-Wilk on per-row differences d_i = ft_i - base_i
│     │     │   (or Anderson-Darling if n > 5000 where Shapiro becomes hypersensitive)
│     │     │
│     │     ├── Shapiro p > 0.05 → paired-t
│     │     │      effect: Cohen's dz = mean(d) / sd(d)  with parametric 95% CI
│     │     │
│     │     └── Shapiro p ≤ 0.05 → Wilcoxon signed-rank
│     │            effect: paired rank-biserial r = 1 - 2W / (n(n+1)/2)
│     │                    with bootstrap 95% CI (or Cliff's delta paired)
│     │
│     └── (state which test was chosen AND why in the report)
│
└── paired-multi-checkpoint (3+ checkpoints, same eval set)
      │
      ├── binary (per-row correct/incorrect across K checkpoints):
      │     omnibus  → Cochran's Q
      │     post-hoc → pairwise McNemar with Holm correction on the family
      │     omnibus effect → Kendall's W
      │
      └── continuous (per-row continuous metric across K checkpoints):
            omnibus  → Friedman's test
            post-hoc → pairwise Wilcoxon signed-rank with Holm correction
            omnibus effect → Kendall's W
```

## Why these specific tests (briefly)

- **McNemar over marginal chi-squared** — the pairing is the whole point. Marginal chi-squared treats the two columns of (base predictions, fine-tune predictions) as if they came from independent samples, throwing away the per-row pairing information. McNemar uses the discordant pairs only because the concordant pairs (both right, both wrong) carry zero information about which model is better — they would have agreed on a random label too.
- **Exact / continuity / mid-p variants** — the chi-squared approximation in McNemar is unreliable when the discordant count is small. b + c < 25 is the conventional threshold to switch to the exact binomial form. Mid-p is offered for users who prefer the mid-p convention (split the boundary probability).
- **Shapiro-driven paired-t vs Wilcoxon** — paired-t assumes the per-row differences are Normally distributed. For LLM eval metrics (log-likelihood, BLEU, ROUGE-L) the differences are often heavy-tailed; Shapiro catches that and Wilcoxon avoids the assumption violation. For very large n (> 5000), Shapiro becomes hypersensitive and rejects Normality on trivially-non-Normal data — switch to Anderson-Darling or QQ-plot judgment.
- **Cochran's Q for multi-checkpoint binary** — the K-sample paired analog of McNemar. Friedman is the K-sample paired analog of Wilcoxon.

## What this tree does NOT cover

- **5x2 cross-validation t-test** (Dietterich 1998) — for ML model comparison with CV folds; out of scope for this skill (assumes one eval set, not cross-validation). If the user wants 5x2cv, hand off to `ml-datasci/comparing-models-fairly` (planned).
- **Bayesian paired comparison** (BEST: Bayesian Estimation Supersedes the t-Test, Kruschke 2013) — out of scope for v1; future skill.
- **Equivalence testing** (TOST: two one-sided tests, to argue "the fine-tune is at least as good as the base within a margin") — not currently in this skill's flow; if the user explicitly wants equivalence (not superiority), suggest TOST in the residual-risks block.
- **Per-segment breakdown** — the residual-risks block of Step 6 notes that a single eval set without per-segment (per-class, per-difficulty, per-language) breakdown can mask Simpson's-paradox-style regressions; the per-segment workflow is a separate analysis.

## Quick-reference effect-size pairing

| Test | Effect size | CI method |
|---|---|---|
| Exact McNemar | OR = c/b or Δaccuracy = (c-b)/n | paired-proportion exact binomial |
| Continuity McNemar | same | paired-proportion Wilson / Newcombe |
| Paired-t | Cohen's dz | parametric (Hedges & Olkin formula) |
| Wilcoxon signed-rank | paired rank-biserial r OR Cliff's delta paired | bootstrap n_bootstrap ≥ 1000 |
| Cochran's Q | Kendall's W | bootstrap |
| Friedman | Kendall's W | bootstrap |
