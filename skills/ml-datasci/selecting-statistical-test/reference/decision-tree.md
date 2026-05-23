# Decision tree for statistical test selection

Full text version of the test-selection decision tree. This file is bundled reference; the SKILL.md links here from `## References`.

The four inputs that drive the entire tree:

1. **Design** — paired, independent, one-sample, or repeated-measures
2. **Scale** — continuous, ordinal, binary, or nominal
3. **Sample size** — per group
4. **Gating assumption check** — Normality (Shapiro / Anderson-Darling), equal variance (Levene), or expected counts (chi-squared cell rule)

## Step-by-step walk

```
1. Confirm design
   ├── paired (within-subject) ────→ go to (2P)
   ├── independent (between-subject) → go to (2I)
   ├── one-sample (vs constant) ───→ go to (2O)
   └── repeated-measures (3+ times) → go to (2R)

2P. Paired, confirm scale
    ├── continuous ─→ Normality of differences?
    │   ├── pass (Shapiro p ≥ 0.05) → paired t-test
    │   └── fail (Shapiro p < 0.05) → Wilcoxon signed-rank
    ├── ordinal ─→ Wilcoxon signed-rank
    └── binary ─→ McNemar
        ├── n ≥ 25 → McNemar with continuity correction
        └── n < 25 → McNemar exact (mid-p)

2I. Independent, confirm scale
    ├── continuous ─→ Normality per group?
    │   ├── both pass → equal variance (Levene)?
    │   │   ├── pass (Levene p ≥ 0.05) → pooled (Student) t-test
    │   │   └── fail (Levene p < 0.05) → Welch's t-test
    │   └── at least one fails → Mann-Whitney U
    ├── ordinal ─→ Mann-Whitney U
    └── binary / 2x2 categorical ─→ expected counts?
        ├── min expected ≥ 5 → chi-squared test of independence
        └── min expected < 5 → Fisher's exact test

2O. One-sample, confirm scale
    ├── continuous ─→ Normality?
    │   ├── pass → one-sample t-test (vs known μ)
    │   └── fail → Wilcoxon signed-rank (vs known median) OR Sign test
    ├── binary (proportion) ─→
    │   ├── n × p ≥ 10 AND n × (1−p) ≥ 10 → normal-approx z-test
    │   └── otherwise → exact binomial
    └── nominal k-level ─→ chi-squared goodness-of-fit (expected counts ≥ 5)

2R. Repeated-measures (3+ within-subject), confirm scale
    ├── continuous ─→ Normality of residuals?
    │   ├── pass → repeated-measures ANOVA
    │   │       (check sphericity via Mauchly; if violated → Greenhouse-Geisser correction)
    │   └── fail → Friedman test
    ├── ordinal ─→ Friedman test
    └── binary ─→ Cochran's Q

3-plus-groups independent (between-subject)
    ├── continuous ─→ Normality per group + homoscedasticity (Levene)?
    │   ├── both pass → one-way ANOVA + Tukey HSD post-hoc
    │   └── either fails → Kruskal-Wallis + Dunn or Conover post-hoc
    ├── ordinal ─→ Kruskal-Wallis
    └── categorical k×j ─→ chi-squared
        ├── all expected ≥ 5 → standard chi-squared
        └── sparse cells → Fisher-Freeman-Halton exact OR Monte-Carlo p-value
```

## Worked branches

### Branch 2P-continuous-fail

User has before/after Y for n = 18 subjects. Shapiro on `after − before` → p = 0.003.

- Design: paired
- Scale: continuous
- n: 18 (small)
- Gating check: Normality of differences → **fail**
- Recommendation: **Wilcoxon signed-rank**
- Why: paired + continuous + non-Normal → the parametric paired t-test assumption is violated
- Effect size to pair with: matched-pair rank-biserial correlation, or Hedges' g if the user wants a parametric reference

### Branch 2I-continuous-unequal-variance

User has independent Y for two groups, both Shapiro pass. Levene p = 0.02.

- Design: independent
- Scale: continuous
- Gating check: Normality (pass) + Levene (fail → unequal variance)
- Recommendation: **Welch's t-test**
- Why: variances are unequal; pooled (Student) t-test would inflate Type I rate
- Effect size to pair with: Hedges' g with Welch correction, or Cohen's d (unpooled)

### Branch 2I-categorical-sparse

User has a 2x2 table with marginals giving min expected count = 3.67.

- Design: independent
- Scale: binary
- Gating check: minimum expected count < 5
- Recommendation: **Fisher's exact test**
- Why: chi-squared approximation requires all expected counts ≥ 5
- Effect size to pair with: odds ratio (with exact CI) or risk difference

### Branch 2P-binary-large-n

User has paired binary outcomes for n = 80 subjects (e.g., before-after diagnostic test).

- Design: paired
- Scale: binary
- Gating check: n ≥ 25
- Recommendation: **McNemar with continuity correction**
- Why: the discordant-pair count is large enough for the asymptotic chi-squared approximation
- Effect size to pair with: McNemar odds ratio, or Cohen's g (paired proportions)

### Branch 2R-binary

User has yes/no outcomes for the same n = 50 subjects across 4 timepoints.

- Design: repeated-measures
- Scale: binary
- Recommendation: **Cochran's Q**
- Why: Cochran's Q is the multi-timepoint extension of McNemar
- Post-hoc if Q is significant: pairwise McNemar with Bonferroni correction across the (k choose 2) comparisons

## Tests this tree does NOT cover

- Survival analysis (Kaplan-Meier, log-rank, Cox PH) — different framework (time-to-event with censoring)
- Bayesian analogues (BEST, JZS Bayes factor) — different paradigm
- Permutation / randomization tests — minimal assumptions, distinct decision logic
- Mixed-effects models / GLMM — for nested data with random effects
- Multivariate tests (Hotelling's T², MANOVA) — multi-outcome
- Time-series tests (Ljung-Box, ADF) — temporal-dependence-aware

If the user's design fits one of those, hand off to a domain-specific reference.
