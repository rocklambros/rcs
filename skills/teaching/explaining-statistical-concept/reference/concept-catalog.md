# Concept catalog with tier-by-tier explanations

The canonical concepts the skill covers, with tier-appropriate framings and adjacent-concept bridges.

## P-value

**What it actually is:** the probability of observing data as extreme as (or more extreme than) the observed data, computed under the assumption that the null hypothesis is true.

**Canonical misconception:** "the probability the null hypothesis is true."

**Tier framings:**

| Tier | Framing |
|---|---|
| high-school | "If nothing were really going on, how surprised would we be to see this result? A small p means 'very surprised.'" |
| undergrad-intro | "Probability of seeing this data or stronger IF the null is true. It is a conditional probability on the null world." |
| undergrad-advanced | "Tail-area probability of the test statistic under the null distribution. Sensitive to sample size; a small p with a tiny effect is statistically significant but practically irrelevant." |
| grad | "Tail probability of the observed statistic under H0. Re-derive: it depends on the choice of test statistic and the assumed null DGP; it is NOT a measure of effect size, evidence strength (in a likelihoodist sense), or posterior probability." |
| practitioner | "Conditional probability on no-effect. Use it as one input alongside effect size + CI + practical-significance judgment; never lead with it." |

**Bridges to:** confidence interval (same conditional framing), effect size (the complement to p in a report), power (probability of detecting a true effect at chosen α).

## Confidence interval

**What it actually is:** a procedure for producing intervals from data such that, across repeated experiments, a specified fraction (e.g., 95%) of the intervals contain the true parameter.

**Canonical misconception:** "the true value has a 95% probability of being in this specific interval" (Bayesian credible-interval framing applied to a frequentist CI).

**Tier framings:**

| Tier | Framing |
|---|---|
| high-school | "If we ran this study 100 times, about 95 of the intervals we computed would contain the true value. Any one specific interval either does or does not contain it." |
| undergrad-intro | "Property of the procedure, not the specific interval. The procedure has 95% coverage in repeated sampling." |
| undergrad-advanced | "Frequentist coverage probability. A 95% CI is defined by the inversion of a hypothesis test: all parameter values not rejected at α = 0.05." |
| grad | "Coverage probability of the interval-producing procedure under repeated sampling from the assumed DGP. Distinct from a Bayesian credible interval, which IS a posterior probability on the parameter." |
| practitioner | "An interval that would cover the truth 95% of the time across repeated runs of the procedure. Use it for reporting effect-size uncertainty; do not say 'we are 95% sure the true value is in here.'" |

**Bridges to:** p-value (same conditional framing), Bayesian credible interval (the Bayesian sibling with the intuitive interpretation), bootstrap CI (non-parametric alternative for the same coverage goal).

## Central limit theorem (CLT)

**What it actually is:** for a sample of size n from a distribution with finite variance, the distribution of the sample mean approaches Normal as n grows, regardless of the original distribution's shape.

**Canonical misconception:** "data becomes Normal as sample size grows."

**Tier framings:**

| Tier | Framing |
|---|---|
| high-school | "If you average many random numbers, the average tends to look bell-shaped — even if the individual numbers do not." |
| undergrad-intro | "The sampling distribution of the mean (not the data itself) approaches Normal as n grows. Finite-variance is the catch." |
| undergrad-advanced | "Convergence in distribution of (sqrt(n)(X-bar - μ) / σ) to N(0,1). Rate of convergence depends on the original distribution's skewness / kurtosis." |
| grad | "Lindeberg–Lévy: convergence in distribution to N(0,1) under finite second moments. Extensions: Lindeberg–Feller for triangular arrays, multivariate CLT, martingale CLT." |
| practitioner | "Why t-tests work even when data is not Normal: the test is about the MEAN's distribution, and the mean tends to be Normal-ish at moderate n. Caveat: heavy tails and small n break this." |

**Bridges to:** standard error (the spread of the sampling distribution that the CLT characterizes), bootstrap (an empirical version of the same idea when the analytic CLT does not apply cleanly), t-distribution (the small-n correction when σ is unknown).

## Hypothesis test (in general)

**What it actually is:** a decision procedure that, given data and a specified null hypothesis, returns reject / fail-to-reject at a stated Type I error rate (α).

**Canonical misconception:** "tests prove the alternative."

**Tier framings:** [as above, tier-tabled]

**Bridges to:** p-value (the input to the decision), confidence interval (the inversion), power (the complement Type II error consideration).

## Regression coefficient

**What it actually is:** the estimated change in the response associated with a one-unit change in the predictor, holding other predictors fixed.

**Canonical misconception:** "X causes Y by this amount."

**Tier framings:** [as above]

**Bridges to:** confounding (why "associated" is not "causal"), multicollinearity (why "holding others fixed" can be unstable), causal inference (the formal framework for moving from association to causation).

## Bayes' theorem

**What it actually is:** P(A|B) = P(B|A)P(A)/P(B). A rule for inverting conditional probabilities.

**Canonical misconception:** that the prior is "subjective and arbitrary" (it is subjective, but disciplined choice + sensitivity analysis is its own discipline).

**Tier framings:** [as above]

**Bridges to:** conditional probability (the building block), prior / posterior / likelihood vocabulary (the components), Bayesian credible interval (the inferential output).

## Statistical power

**What it actually is:** probability of correctly rejecting the null when a specified alternative is true; complement of Type II error rate.

**Canonical misconception:** "the test is reliable" (power is conditional on a specified effect size — there is no single "power of a test" without naming the effect).

**Tier framings:** [as above]

**Bridges to:** effect size (the thing power is calibrated for), Type I / Type II errors (the formal framework), sample-size calculation (power's most common practical use).

## Effect size

**What it actually is:** a standardized measure of the magnitude of a phenomenon, separate from the significance of a hypothesis test.

**Canonical misconception:** that p-value alone is sufficient to characterize "how big" the effect is.

**Tier framings:** [as above]

**Bridges to:** confidence interval (effect size + CI is the recommended reporting unit), p-value (what effect size is NOT), Cohen's conventions (a starting point, not a substitute for domain-specific judgment).

## Anti-list — concepts NOT covered by this skill

These are too narrow / too broad / better served by other skills:

- Calculus of derivatives (not a stats concept)
- Specific algorithms (e.g., k-means) — use `ml-datasci/*` skills
- Coding patterns (e.g., how to call `scipy.stats`) — use a programming tutorial
- Research method (e.g., experimental design) — use a research-methods reference
