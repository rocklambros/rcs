# Student vocabulary tiers

The "What it's asking" step in each walkthrough restates the question in the student's vocabulary. Vocabulary must match the student's stage — jargon below the tier confuses, jargon above the tier patronizes.

## Tier definitions

| Tier | Prerequisites assumed | Typical course | Vocabulary ceiling |
|---|---|---|---|
| high-school | Algebra, basic functions, descriptive stats | AP Statistics, intro probability | "spread," "center," "shape" instead of "variance," "mean," "skewness" |
| undergrad-intro | Calc 1, intro stats, basic probability | STAT 101, intro to data analysis | "mean," "variance," "p-value" OK; "homoscedasticity" needs translation |
| undergrad-advanced | Linear algebra, probability theory, regression | Intermediate / advanced stats, ML 101 | "homoscedasticity," "MLE," "bias-variance" OK; "Bayes factor" needs context |
| grad | Measure theory or applied equivalent; research method | Grad-level stats / ML | Most stats jargon OK; introduce niche terms (e.g., "BHHH") with one-line definition |
| practitioner | On-the-job equivalent; varies widely | Working data scientist / engineer | Jargon is OK; CONTEXT matters more (industry conventions, tool-chain assumptions) |

## How to choose the tier

If the user does not specify, default to **undergrad-intro** for stats problems and **undergrad-advanced** for ML problems. Ask if the problem is ambiguous (a grad-level problem written in plain language is common; do not assume tier from problem phrasing alone).

## Common translations (undergrad-intro → high-school)

| Undergrad-intro term | High-school translation |
|---|---|
| Variance | "average squared distance from the mean" |
| Standard deviation | "typical distance from the mean" |
| Skewness | "asymmetry of the distribution" |
| Kurtosis | "fatness of the tails" |
| Central Limit Theorem | "averages of large samples look Normal even when the underlying data does not" |
| p-value | "probability of seeing this result or stronger if nothing were really going on" |
| Type I error | "false alarm — saying 'effect' when there isn't one" |
| Type II error | "missed signal — saying 'no effect' when there is one" |

## Common translations (undergrad-advanced → undergrad-intro)

| Advanced term | Intro translation |
|---|---|
| Homoscedasticity | "the spread of the residuals is roughly constant across the range of predictions" |
| Heteroscedasticity | "the spread of residuals changes systematically — wider for some predictions than others" |
| MLE | "the parameter value that makes the observed data most likely" |
| Bias-variance trade-off | "simple models miss patterns; complex models chase noise" |
| Bayes factor | "ratio of how well two competing hypotheses explain the data" |
| Conjugate prior | "a prior that, when combined with the data's likelihood, produces a posterior of the same shape" |

## Common translations (grad → undergrad-advanced)

| Grad term | Advanced-undergrad translation |
|---|---|
| Asymptotic normality | "as sample size grows, the estimator's distribution approaches a Normal" |
| Consistency | "as sample size grows, the estimator gets arbitrarily close to the true value" |
| Empirical Bayes | "use the data itself to estimate the prior, then proceed Bayesian" |
| Variational inference | "approximate the posterior with a simpler distribution by minimizing a divergence" |

## Anti-patterns

- **Tier collapsing under pressure:** writing a high-school-tier walkthrough but secretly using undergrad jargon "because it's more accurate." Pick a tier and stay in it.
- **Tier over-explanation:** writing a grad-tier walkthrough but defining every term as if for a beginner. Patronizing. Trust the tier.
- **Tier ambiguity:** writing for "anyone" with no tier in mind. The walkthrough lands in the gap between tiers and serves nobody.

## When the problem mixes tiers

Some problems use grad-level setup but ask an undergrad-tier question (e.g., "Given the posterior derived above, compute the credible interval"). The walkthrough's tier matches the question being asked, not the setup. The setup can reference the upstream context without re-explaining it.
