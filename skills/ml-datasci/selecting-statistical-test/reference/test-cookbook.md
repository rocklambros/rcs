# Per-test cookbook

One short card per test. Use as a lookup after the decision tree in `decision-tree.md` points you to a test.

Each card: **assumptions**, **when to use**, **effect size to pair with**, **common gotcha**.

## One-sample t-test

- **Assumptions:** Normality of the sample, independent observations
- **When to use:** one continuous sample, compared against a known constant μ₀
- **Effect size:** Cohen's d = (x̄ − μ₀) / s
- **Gotcha:** small n + non-Normal → use Wilcoxon signed-rank against median instead

## Paired t-test

- **Assumptions:** Normality of the **differences** (NOT of either column individually), independent pairs
- **When to use:** before/after, matched-pair, within-subject continuous
- **Effect size:** Cohen's dz = mean(diff) / sd(diff); also report Hedges' gz for small n
- **Gotcha:** people Shapiro-test the raw before and after columns; what matters is the differences

## Pooled (Student) two-sample t-test

- **Assumptions:** Normality per group, **equal variance** (Levene p ≥ 0.05), independent samples
- **When to use:** two independent continuous samples with confirmed equal variance
- **Effect size:** Cohen's d (pooled SD)
- **Gotcha:** Levene's test failure is common; default to Welch's instead of pooled if unsure

## Welch's t-test

- **Assumptions:** Normality per group, **does NOT assume equal variance**, independent samples
- **When to use:** two independent continuous samples; safer default than pooled t when variances are unequal or unknown
- **Effect size:** Cohen's d (unpooled, with Welch dof)
- **Gotcha:** the dof is non-integer (Satterthwaite); report it to 1 decimal place

## Wilcoxon signed-rank

- **Assumptions:** continuous OR ordinal differences, symmetric distribution of differences (relaxed for paired-comparison interpretation)
- **When to use:** paired continuous when Normality of differences fails, or paired ordinal
- **Effect size:** matched-pair rank-biserial correlation r = (W⁺ − W⁻) / (W⁺ + W⁻)
- **Gotcha:** Wilcoxon is paired; do not confuse with Wilcoxon rank-sum (= Mann-Whitney U), which is the independent-samples version

## Mann-Whitney U (Wilcoxon rank-sum)

- **Assumptions:** independent samples; SAME shape distributions if interpreting as difference in medians
- **When to use:** two independent continuous or ordinal samples when Normality fails
- **Effect size:** rank-biserial correlation r = 1 − 2U / (n₁ × n₂); or Cliff's δ
- **Gotcha:** rejection of H₀ does not mean "medians differ" unless the distributions have the same shape; interpret as "stochastic dominance" otherwise

## Sign test

- **Assumptions:** very few; only that the sign of the difference is well-defined
- **When to use:** one-sample or paired, very small n, distribution highly skewed, or interest in median only
- **Effect size:** proportion of positive differences (with exact CI)
- **Gotcha:** the sign test is less powerful than Wilcoxon when Wilcoxon's symmetry assumption holds; prefer Wilcoxon if it does

## Chi-squared test of independence

- **Assumptions:** independent observations, **all expected cell counts ≥ 5** (for 2x2; for larger tables, no more than 20% of cells below 5)
- **When to use:** k×j categorical contingency table
- **Effect size:** Cramer's V; for 2x2, the odds ratio or phi coefficient
- **Gotcha:** the chi-squared statistic compares **observed vs expected**; if any expected count drops below 5, switch to Fisher exact (2x2) or Fisher-Freeman-Halton (larger)

## Fisher's exact test

- **Assumptions:** marginal totals are fixed (which is technically rare in practice but the test is robust to this)
- **When to use:** 2x2 with at least one expected cell < 5
- **Effect size:** odds ratio (with exact CI)
- **Gotcha:** for larger-than-2x2 sparse tables, use Fisher-Freeman-Halton or Monte-Carlo p-value; the basic `fisher.test` in R / SciPy is 2x2 only by default

## McNemar's test

- **Assumptions:** paired binary, n_discordant ≥ 25 (for the χ² approximation); use exact mid-p for smaller
- **When to use:** before/after binary, matched-pair binary, classifier-vs-classifier comparison on the same test set
- **Effect size:** odds ratio of discordant pairs, or Cohen's g for paired proportions
- **Gotcha:** only the **discordant** cells (b and c) drive the test; the concordant cells (a and d) are ignored. People wrongly include all four

## Cochran's Q

- **Assumptions:** repeated binary, same subjects across k ≥ 3 timepoints / conditions
- **When to use:** k ≥ 3 paired-binary comparisons (McNemar's multi-timepoint extension)
- **Effect size:** report per-pair McNemar odds ratios as post-hoc
- **Gotcha:** post-hoc pairwise McNemars need Bonferroni or Holm correction across the (k choose 2) comparisons

## One-way ANOVA

- **Assumptions:** Normality per group, equal variance (Levene), independent samples
- **When to use:** 3+ independent continuous groups
- **Effect size:** eta-squared (η²) or omega-squared (ω²) for less bias
- **Gotcha:** a significant F doesn't tell you WHICH groups differ; run Tukey HSD or Dunnett post-hoc

## Kruskal-Wallis

- **Assumptions:** independent samples, ordinal or continuous
- **When to use:** 3+ independent groups when ANOVA assumptions fail
- **Effect size:** epsilon-squared (ε²)
- **Gotcha:** post-hoc is Dunn's test (or Conover-Iman), NOT pairwise Mann-Whitney without correction

## Friedman test

- **Assumptions:** repeated measures, ordinal or continuous, 3+ conditions
- **When to use:** non-parametric alternative to repeated-measures ANOVA
- **Effect size:** Kendall's W
- **Gotcha:** post-hoc is Nemenyi or pairwise Wilcoxon with Bonferroni

## Repeated-measures ANOVA

- **Assumptions:** Normality of residuals, **sphericity** (Mauchly's test)
- **When to use:** 3+ within-subject continuous timepoints
- **Effect size:** partial eta-squared (η²ₚ)
- **Gotcha:** sphericity is the assumption people forget; if Mauchly p < 0.05, apply Greenhouse-Geisser or Huynh-Feldt correction to the dof
