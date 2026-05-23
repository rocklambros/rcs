---
name: running-power-analysis
description: >
  Runs a prospective (a-priori) power analysis to determine the sample size, the
  minimum detectable effect (MDE), or the achievable power for a planned
  statistical test BEFORE the study runs — pairing the choice of test, the
  expected effect size (from pilot, prior literature, or a smallest-effect-of-
  interest), and the α / β trade-off. Refuses to compute post-hoc / observed-
  power on a completed study (which is mathematically a deterministic function
  of the p-value and adds no information). Use whenever the user is designing
  an experiment, asks how many subjects are required, is writing a grant or
  pre-registration, has a non-significant result and is tempted to argue from
  observed power, or is justifying an MDE.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer, stats-student, instructor]
evidence:
  - DU-MSDSAI-4441-Final
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Running a Power Analysis

## When to use

Trigger this skill when the user asks for or implies one of:

- "How many subjects / observations do I need?" for a planned study
- A grant, pre-registration, or IRB protocol that requires a power / sample-size justification
- Choosing between two designs (within-subject vs between-subject; paired vs independent) and wanting the smaller-n option
- Reporting a non-significant result and being asked "but what was the power?" (this is the post-hoc-power anti-trigger; see below — the skill engages but refuses to interpret observed power)
- Defining a smallest-effect-of-interest (SESOI) or minimum detectable effect (MDE) for an a-priori plan
- Phrases like "power calculation", "sample size justification", "Cohen's tables", "G*Power", "alpha and beta", "MDE"

This skill pairs with `ml-datasci/selecting-statistical-test` (which test) and `ml-datasci/reporting-effect-sizes` (which effect-size metric is the right unit for the power calc).

## When NOT to use

Skip this skill and hand off when:

- The user has already run the test, observed p > 0.05, and wants to compute "observed power" or "post-hoc power" to argue the result is meaningful — observed power is a 1-to-1 monotonic function of the p-value and offers no information beyond the p-value (Hoenig & Heisey 2001). The skill engages with the question but **does NOT compute observed power**; instead it routes to equivalence testing (TOST) or a confidence-interval-based interpretation.
- The user is doing a **Bayesian analysis** — Bayes factor design analysis (BFDA) is the right tool, not frequentist power
- The user is doing **exploratory data analysis** with no hypothesis tests
- The user is doing **adaptive / sequential / Bayesian-adaptive designs** — these use group-sequential boundaries, alpha-spending, or conditional power; refer the user to specialized software (R `gsDesign`, `rpact`)

## Quick start

User says: "I'm planning a two-arm randomized trial comparing a new drug against placebo on blood pressure reduction. The smallest meaningful effect is a 5 mmHg difference. Prior literature suggests SD ≈ 12 mmHg. I want 80% power at α = 0.05. How many per arm?"

Skill response: Cohen's d = 5 / 12 = 0.417 (small-to-medium). For a two-sample t-test with α = 0.05, β = 0.20 (power = 0.80), the per-arm sample size is **n ≈ 92 per group, total N = 184**. Provides the calculation in Python (`statsmodels.stats.power`) and in R (`pwr::pwr.t.test`); names α, β, effect-size, and test family explicitly; flags assumptions (Normal residuals, equal variance) that must hold.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| test | "one-sample-t" \| "paired-t" \| "two-sample-t" \| "anova-oneway" \| "anova-factorial" \| "chi-squared" \| "fisher" \| "mcnemar" \| "correlation" \| "linear-regression" \| "logistic-regression" | yes | — | The planned test that the power analysis is for. |
| solve_for | "n" \| "power" \| "effect_size" | yes | "n" | Which of n / power / effect-size to compute, holding the other two fixed. |
| alpha | float 0–1 | no | 0.05 | Type I error rate. |
| power | float 0–1 | required if `solve_for = "n"` | 0.80 | Desired 1 − β. |
| effect_size | float | required if `solve_for = "n"` or `"power"` | — | The expected or smallest-meaningful effect on the test's natural scale (Cohen's d for t, f for ANOVA, w for chi-squared, r for correlation, OR or log-OR for logistic). |
| n | integer or per-group list | required if `solve_for = "power"` or `"effect_size"` | — | Sample size per group (or total for one-sample / regression). |
| tails | "one" \| "two" | no | "two" | One-sided vs two-sided test; one-sided needs a directional pre-registration justification. |
| sesoi_source | "pilot" \| "prior-literature" \| "domain-judgment" \| "cohen-rule-of-thumb" | required when stating effect-size | — | Provenance for the effect-size assumption; the audit pattern requires this. |

## Workflow

Copy this checklist into the response and check items off as each step completes:

```
Power-analysis progress:
- [ ] Step 1: Identify the planned test and the design (paired / independent / one-sample)
- [ ] Step 2: Decide what to solve for (n / power / effect_size)
- [ ] Step 3: Set α (default 0.05) and either β (default 0.20) or the other fixed quantity
- [ ] Step 4: Determine the effect-size on the test's natural scale + name its provenance (pilot / literature / SESOI / Cohen rule-of-thumb)
- [ ] Step 5: Run the calculation (Python statsmodels / R pwr / G*Power) and report the result
- [ ] Step 6: Sensitivity check — repeat the calc at ± 25% on the effect-size; report how n moves
- [ ] Step 7: Report the assumptions that must hold for the calc to be valid (Normality, equal-variance, etc.)
```

### Step 1: Identify the test and design

The test family determines the natural effect-size scale:

| Test family | Effect-size unit | Symbol |
|---|---|---|
| Two-sample / paired / one-sample t | Cohen's d (paired uses dz) | d, dz |
| ANOVA (one-way / factorial) | Cohen's f | f |
| Chi-squared / Fisher / McNemar | Cohen's w (or odds-ratio) | w, OR |
| Correlation | Pearson r (Fisher z-transform for SE) | r |
| Linear regression | f² for added predictor, or R² for whole model | f², R² |
| Logistic regression | log-odds-ratio | log(OR) |

### Step 2: What to solve for

- **n** is the default question: "how many subjects do I need to detect effect d with power 0.80 at α = 0.05?"
- **power** answers: "given the n I will actually collect, what is the power to detect effect d?" Run BEFORE the study, not after.
- **effect_size** answers: "given fixed n and a target power, what is the smallest effect this study could detect?" This is the **MDE**, a useful design-stage output.

### Step 3: Set α and β (or the other fixed quantity)

Defaults: α = 0.05, power = 0.80 (β = 0.20). Justify deviations:

- α = 0.01 for genome-wide / multiple-testing pre-Bonferroni; for very-high-stakes safety claims
- Power = 0.90 or 0.95 if the study is a primary registration / pivotal trial
- α = 0.10 only with explicit pre-registration justification

### Step 4: Set the effect-size with named provenance

This is the step most studies get wrong. Three legitimate sources:

1. **Pilot data** — compute the observed effect size in the pilot; **inflate the variance estimate** for the final sample (the pilot SE is itself uncertain); a common adjustment is to use the upper 60th–80th percentile of the bootstrapped effect-size distribution
2. **Prior literature** — cite the meta-analytic or single-study effect; **discount for publication bias** if the literature shows funnel-plot asymmetry (typical haircut: 0.5×)
3. **Smallest effect of interest (SESOI)** — choose the *smallest effect that would be substantively meaningful* and design to detect that; this gives a conservative (largest) n and is the most defensible

Cohen's rule-of-thumb (d = 0.2 small, 0.5 medium, 0.8 large; f = 0.10/0.25/0.40; w = 0.10/0.30/0.50; r = 0.10/0.30/0.50) is acceptable **only when there is no domain anchor**; mark explicitly as "rule-of-thumb, no domain anchor" so reviewers can challenge it.

### Step 5: Run the calculation

**Python:**

```python
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower
analysis = TTestIndPower()
n = analysis.solve_power(effect_size=0.417, alpha=0.05, power=0.80, alternative="two-sided")
# n ≈ 91.8 per group
```

**R:**

```r
pwr::pwr.t.test(d = 0.417, sig.level = 0.05, power = 0.80,
                type = "two.sample", alternative = "two.sided")
# n = 91.8 per group
```

Round up to an integer.

### Step 6: Sensitivity check

Repeat the calc with effect size at 0.75× and 1.25× of the planned value; report the corresponding n's. If a 25% miss on the effect-size assumption changes n by > 50%, the study is fragile — recommend either a larger n (conservative) or a pre-specified internal pilot.

### Step 7: Assumptions that must hold

Every power calc has assumptions. Name them:

- t-test power assumes Normal residuals and (for pooled) equal variances. If those fail, the actual power is lower than computed.
- ANOVA power assumes Normality + homoscedasticity within groups.
- Chi-squared power assumes expected counts ≥ 5 in all cells.
- Logistic regression power needs 10–20 events per predictor as a separate rule.

## Outputs

A short markdown report:

1. **Design summary** — test, design (paired / independent), tails, α, target power
2. **Effect-size assumption** — value + provenance (pilot / literature / SESOI / Cohen rule-of-thumb)
3. **Result** — required n (or achievable power, or MDE) with explicit unit
4. **Sensitivity table** — n at 0.75× and 1.25× of the assumed effect-size
5. **Assumptions** — list of distributional / structural assumptions the power calc relies on
6. **Reproducible code** — the exact `statsmodels` or `pwr` call, so reviewers can re-run
7. **Reporting checklist** — what to put in the methods section (α, β, effect-size, provenance, software version)

## Failure modes

- **Post-hoc / observed power on a non-significant result** — using the observed effect-size from the same study to compute "the power we had" and then interpreting low observed power as evidence of an underpowered (but real) effect. This is mathematically a 1-to-1 transform of the p-value (Hoenig & Heisey 2001). Caught by: When-NOT-to-use section blocks it; the skill instead routes to **equivalence testing (TOST)** or CI-based interpretation ("the 95% CI for the difference includes 0 but excludes effects larger than X, so we can rule out effects of clinical significance").
- **Cohen rule-of-thumb without a domain anchor** — picking d = 0.5 because "Cohen says medium" with no substantive justification. Caught by: `sesoi_source` argument is required; "cohen-rule-of-thumb" is allowed but must be declared explicitly so reviewers can challenge it.
- **Pilot-as-truth** — using the raw pilot effect size as the planning effect size, ignoring its own sampling uncertainty (pilot estimates are typically inflated). Caught by: Step 4 instructs to inflate variance or use a percentile of the bootstrap distribution for the planning value.
- **One-sided test without pre-registered direction** — using a one-sided test to lower n. Caught by: `tails = "one"` requires a directional pre-registration justification per the When-to-use trigger.
- **Skipping sensitivity** — reporting a single n with no sensitivity check on the effect-size assumption. Caught by: Step 6 sensitivity is required output.
- **Power for the wrong test** — running a two-sample power calc when the actual analysis is paired or repeated-measures. Caught by: Step 1 enforces the test → effect-size-unit mapping; paired tests use dz, not d.

## References

- [`reference/power-cookbook.md`](reference/power-cookbook.md) — per-test Python (statsmodels) + R (pwr) code snippets with worked examples
- Cohen, *Statistical Power Analysis for the Behavioral Sciences* (1988) — origin of d, f, w, r conventions and rule-of-thumb anchors
- Hoenig & Heisey 2001, *The Abuse of Power: The Pervasive Fallacy of Power Calculations for Data Analysis*, The American Statistician 55(1) — definitive reference for why post-hoc / observed power is uninformative
- Lakens 2017, *Equivalence Tests: A Practical Primer*, Social Psychological and Personality Science — TOST procedure, the right tool for "non-significant result, was the effect really null?"
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — for the workflow-checklist pattern

## Examples

### Example 1: Planned two-group trial (happy-path)

Input: "I'm planning a two-arm randomized trial of a new drug vs placebo on blood pressure reduction. The smallest meaningful effect is a 5 mmHg difference. Prior literature suggests SD ≈ 12 mmHg. I want 80% power at α = 0.05. How many per arm?"

Output: Test = two-sample t (independent). Cohen's d = 5 / 12 = 0.417, provenance = SESOI (smallest meaningful effect anchored in clinical judgment). α = 0.05, power = 0.80, two-sided. Result: **n ≈ 92 per arm, total N = 184**. Sensitivity: at d = 0.31 (effect 25% smaller), n ≈ 163 per arm; at d = 0.52 (25% larger), n ≈ 59 per arm. Code: `statsmodels.stats.power.TTestIndPower().solve_power(effect_size=0.417, alpha=0.05, power=0.80)` and `pwr::pwr.t.test(d=0.417, power=0.80, sig.level=0.05, type="two.sample")`. Assumptions: Normality of BP-change distribution per arm; equal variance (or use Welch and recompute).

### Example 2: Pilot-data planning, with discount (edge-case)

Input: "I ran a pilot with n = 20 and observed Cohen's d = 0.85. I want to run the full study at 80% power. What sample size?"

Output: Pilot d = 0.85 is suspiciously large; n = 20 pilot estimates are wide and typically inflated by the winner's curse. Recommendation: do NOT plan on d = 0.85. Instead (a) compute a 95% bootstrap CI on d from the pilot; (b) use the lower bound (or 25th percentile) as the planning value — e.g., if the lower CI bound is d = 0.40, plan on d = 0.40. At d = 0.40, two-sided α = 0.05, power = 0.80 → **n ≈ 100 per arm**. If the pilot bootstrap lower bound is too uncertain, fall back to a SESOI anchored in domain judgment. Always run a sensitivity check showing n at the lower CI bound, the point estimate, and the upper bound.

### Example 3: Post-hoc / observed power (anti-trigger)

Input: "I ran a two-sample t-test, got t = 1.4, p = 0.18, observed d = 0.32, n = 30 per group. Reviewers asked what my power was. Compute it."

Output: Refuses to report observed / post-hoc power as a meaningful quantity — it is a 1-to-1 transform of the p-value and contains no additional information (Hoenig & Heisey 2001). Instead routes to two alternatives: (1) **Equivalence test (TOST)** — pre-specify an equivalence bound (e.g., d_min = ± 0.3) and run two one-sided tests; reject the null of "effect at least as large as d_min" or fail to do so; (2) **CI-based interpretation** — report the 95% CI on the difference and state which effect sizes the data rules out. Either is informative; observed power is not. The skill cites the Hoenig & Heisey reference and produces the TOST or CI write-up instead.

## See also

- `ml-datasci/selecting-statistical-test` — pick the test first; this skill computes the power for that test
- `ml-datasci/reporting-effect-sizes` — once the study runs, report the achieved effect with CI; this skill plans the study to detect it
- `ml-datasci/checking-test-assumptions` — power calcs assume the test's assumptions hold; verify on pilot or post-collection
- `workflow/pre-registering-eval-study` (planned) — the broader pre-registration workflow this slots into

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
