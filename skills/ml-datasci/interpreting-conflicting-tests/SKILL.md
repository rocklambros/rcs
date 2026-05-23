---
name: interpreting-conflicting-tests
description: >
  Adjudicates between two statistical tests applied to the same data that
  reach opposite conclusions — paired t versus Wilcoxon signed-rank, two-
  sample t versus Mann-Whitney, McNemar versus exact binomial sign, chi-
  squared versus Fisher, parametric ANOVA versus Kruskal-Wallis — by building
  an assumption-status table for both tests, identifying which assumptions
  actually hold, and committing to a single winner with named reasoning.
  Refuses to wave both results around as 'mixed evidence' or to keep
  switching tests until one is significant (p-hacking). Use whenever two
  tests on the same data disagree on the null-hypothesis verdict, the user
  asks which p-value to report, or a reviewer has flagged conflicting
  results in a manuscript.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, stats-student, instructor, ml-engineer]
evidence:
  - DU-MSDSAI-4441-Final
  - llm-safety-alignment-study
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
last-updated: 2026-05-23
---

# Interpreting Conflicting Tests

## When to use

Trigger this skill when the user asks for or implies one of:

- "My paired t-test says p = 0.02 but my Wilcoxon signed-rank says p = 0.18. Which do I report?" — direct conflict between parametric and non-parametric on the same data
- "Chi-squared says significant, Fisher's exact says not significant" — sample-size-driven discrepancy
- "McNemar's says p < 0.05, the exact binomial sign test says p > 0.05" — discreteness / continuity-correction divergence
- Reviewer feedback: "your t-test and Wilcoxon disagree — pick one"
- The user has run BOTH a parametric and non-parametric test "to be safe" and is now confused by mixed results
- Two specifications of the same test (Welch vs pooled t; with vs without continuity correction) disagree
- The user is about to keep running new tests until one is significant — this skill engages with the conflict and refuses the p-hacking path

This skill pairs with `ml-datasci/selecting-statistical-test` (which test you should have committed to before running) and `ml-datasci/checking-test-assumptions` (which assumption check determines the right test).

## When NOT to use

Skip this skill and hand off or do nothing when:

- There is only ONE test result and no conflict — the standard reporting workflow (effect size + CI + direction) applies; route to `ml-datasci/reporting-effect-sizes`
- The "conflict" is between two DIFFERENT samples / studies / time periods (this is a meta-analysis question, not a test-adjudication question)
- The user has ALREADY committed to one test in a pre-registration / protocol and is asking whether to also report the other "for completeness" — they should report the pre-registered test as the primary and the other as exploratory; this skill is for cases without a pre-registration
- The user wants to compute a Bayes factor or run a Bayesian analysis (different skill / workflow)
- The user is doing exploratory data analysis with no formal hypothesis tests

## Quick start

User says: "On 22 paired before/after measurements of reaction time, the paired t-test gives t(21) = 2.6, p = 0.017. Shapiro-Wilk on the differences gives W = 0.86, p = 0.005. Wilcoxon signed-rank gives V = 165, p = 0.11. The two tests disagree. Which do I report?"

Skill response (in order):

1. **Build the assumption-status table:**

   | Test | Key assumption | Test of assumption | Status |
   |---|---|---|---|
   | Paired t | Normality of the differences | Shapiro-Wilk W = 0.86, p = 0.005 | **VIOLATED** |
   | Wilcoxon signed-rank | Symmetry of the differences around the median | (visual / quasi-symmetric is sufficient) | OK by inspection |

2. **The paired t-test's gating assumption (Normality of differences) is violated by Shapiro-Wilk at α = 0.05** with n = 22 (small enough that Shapiro has real power and a real false-positive risk both matter; here the violation is clear with p = 0.005).

3. **Commit to Wilcoxon as the winner.** Report V = 165, p = 0.11; effect size = Cliff's δ or paired rank-biserial r with 95% CI; conclude there is insufficient evidence to reject the null at α = 0.05.

4. **Document the adjudication in the methods section** so reviewers can follow the chain: "We initially planned a paired t-test; Shapiro-Wilk on the difference distribution indicated a Normality violation (W = 0.86, p = 0.005), so the primary analysis switched to Wilcoxon signed-rank."

5. **Refuse to report 'the t-test was significant' as the headline finding** — the t-test's premise is broken; its p-value is unreliable for this sample.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| test_a | name of the first test | yes | — | e.g., "paired-t", "two-sample-t", "chi-squared", "McNemar" |
| test_b | name of the second test | yes | — | The conflicting test; must be a legitimate alternative to test_a on the same data |
| result_a | (statistic, p-value, n) | yes | — | The numeric result from test_a |
| result_b | (statistic, p-value, n) | yes | — | The numeric result from test_b |
| assumption_check_a | dict of (assumption_name, test_used, p_or_verdict) | required | — | The assumption checks that gate test_a (e.g., Shapiro for Normality on a t-test) |
| assumption_check_b | dict of (assumption_name, test_used, p_or_verdict) | required | — | The assumption checks that gate test_b |
| sample_size_pattern | "small-n" \| "moderate-n" \| "large-n" | no | inferred from n | Drives the discreteness / asymptotic-normality argument for some test families |
| pre_registered_test | "test_a" \| "test_b" \| "none" | no | "none" | If a pre-registration commits to one, that test is the primary regardless of conflict (this skill confirms but doesn't override the pre-registration) |

## Workflow

Copy this checklist into the response and check items off as each step completes:

```
Conflict-adjudication progress:
- [ ] Step 1: Confirm both tests legitimately apply to the same data and same null (not a wrong-test mistake)
- [ ] Step 2: Build the assumption-status table — list every gating assumption for each test
- [ ] Step 3: Identify which assumptions are violated, using the assumption-check results
- [ ] Step 4: Apply the adjudication rule: the test whose assumptions hold WINS
- [ ] Step 5: Check for sample-size / discreteness gotchas that flip the answer (small-n exact tests, continuity correction, ties)
- [ ] Step 6: Check for outlier-driven divergence (does removing 1–2 extreme points reconcile the tests?)
- [ ] Step 7: Commit to one winner; report it as primary with effect size + CI
- [ ] Step 8: Document the adjudication in the methods so reviewers can audit the chain
```

### Step 1: Confirm both tests legitimately apply

A "conflict" between a paired t and an independent t isn't a conflict — it's a wrong-test mistake. Verify both tests are valid candidates for the same design:

- Paired t ↔ Wilcoxon signed-rank (both paired; both test the difference distribution)
- Two-sample t ↔ Mann-Whitney U (both independent; both test the location parameter)
- Welch t ↔ pooled t (both two-sample; differ on the equal-variance assumption)
- Chi-squared ↔ Fisher's exact (both 2×2 categorical; differ on the small-expected-count tolerance)
- McNemar ↔ exact binomial sign (both paired binary; differ on the asymptotic vs exact decision)
- ANOVA ↔ Kruskal-Wallis (both 3+ groups independent; parametric vs rank-based)

If the two tests test DIFFERENT nulls (e.g., a t-test on means vs a permutation test on medians), the apparent conflict isn't a conflict — they're answering different questions. Don't adjudicate; report both with their separate interpretations.

### Step 2: Build the assumption-status table

For each test, name the gating assumptions:

| Test | Gating assumptions |
|---|---|
| Paired t | Normality of the differences; independence within differences |
| Two-sample t (pooled) | Normality of each group; equal variance; independence |
| Welch t | Normality of each group; independence (allows unequal variance) |
| One-sample t | Normality; independence |
| Wilcoxon signed-rank | Symmetry of the differences around the median; independence |
| Mann-Whitney U | Both distributions have the same shape (location-shift assumption); independence |
| Chi-squared (2×2) | All expected counts ≥ 5; independent observations |
| Fisher's exact | Independent observations (no expected-count requirement) |
| McNemar | Discordant-pair count ≥ 25 for asymptotic; exact for smaller |
| ANOVA (one-way) | Normality per group; equal variance (homoscedasticity); independence |
| Kruskal-Wallis | Same-shape distributions across groups; independence |

Add a column with the actual assumption-check result (Shapiro p, Levene p, expected-count cells, etc.).

### Step 3: Identify violations

For each row, mark PASS / FAIL / BORDERLINE based on the assumption-check result. The convention:

- Shapiro / Anderson-Darling p < 0.05 → Normality FAIL
- Levene / Brown-Forsythe p < 0.05 → equal-variance FAIL
- Expected counts < 5 in any 2×2 cell → chi-squared FAIL
- Discordant pairs < 25 → McNemar asymptotic borderline → prefer exact
- Sample size < 15 with skewed differences → t's Central Limit Theorem rescue doesn't apply → Normality really matters

### Step 4: The adjudication rule

**The test whose assumptions HOLD wins. The test whose assumptions are VIOLATED loses, regardless of which gave a smaller p-value.**

Concretely:

| Situation | Winner |
|---|---|
| Paired t Normality FAILS, Wilcoxon assumptions hold | Wilcoxon |
| Two-sample t Normality OK, equal-variance FAILS | Welch t (not pooled t, not Mann-Whitney) |
| Chi-squared expected-count < 5, Fisher always valid | Fisher |
| McNemar discordant pairs < 25, exact binomial available | Exact binomial sign |
| Both tests' assumptions hold (rare with conflict) | Pre-registered test wins; if no pre-reg, parametric is more powerful so its result is the better estimator IF the assumption check is convincing |

**Never pick the winner based on which p-value you prefer.** That's p-hacking with extra steps.

### Step 5: Sample-size / discreteness gotchas

Some conflicts are real but arise from discreteness or asymptotic-normality breaking down, not from assumption violations:

- **Wilcoxon with many ties** (e.g., Likert / count data) — the rank-based p-value can be biased; the t-test can be the more accurate test if Normality holds
- **Chi-squared with continuity correction** (Yates) versus without — small samples flip the result; default to Fisher in 2×2
- **McNemar with vs without continuity correction** — for discordant counts in the 10–25 range, the corrected and uncorrected p-values can straddle α = 0.05; use exact binomial
- **Two-sample t with n < 15 and non-Normal data** — CLT rescue does NOT kick in; trust the assumption check, not the t

### Step 6: Outlier-driven divergence

If removing 1–2 extreme points reconciles the tests, the conflict is being driven by outliers. Report:

1. The analysis on the full data (with the conflict)
2. The analysis with outliers removed (note: pre-specify the outlier rule, ideally before seeing the data)
3. Both effect-size estimates with CIs

A robust effect-size estimate (Hodges-Lehmann for median difference, trimmed-mean difference) often resolves the substantive question even when the parametric and non-parametric tests disagree on p.

### Step 7: Commit to a winner

Pick ONE test as the primary analysis. Report it with effect size + 95% CI + direction (see `ml-datasci/reporting-effect-sizes`).

If the winner is the non-parametric test, use the rank-based effect size (Cliff's δ, rank-biserial r, Hodges-Lehmann difference). Don't report Cohen's d as "the" effect size if you've rejected the parametric test.

### Step 8: Document the chain

In the methods section, write the adjudication as a clear chain:

> "We pre-specified [test_a] as the primary analysis. The Shapiro-Wilk test on the difference distribution rejected Normality (W = 0.86, p = 0.005), so the primary analysis switched to [test_b]. The [test_b] result is reported in Table N; the [test_a] result is reported in the supplement for transparency."

If there was no pre-registration, write:

> "Two candidate tests were considered: [test_a] (parametric, assumes Normality) and [test_b] (non-parametric, assumes symmetry). Shapiro-Wilk indicated a Normality violation (W = 0.86, p = 0.005), so [test_b] was selected as the primary analysis. The [test_a] result is reported only to disclose the assumption violation."

## Outputs

A short markdown report:

1. **Conflict header** — the two tests, their p-values, the disagreement (significant vs not)
2. **Assumption-status table** — every gating assumption for both tests, with check results and PASS / FAIL / BORDERLINE
3. **Winner declaration** — which test is the primary, with a one-sentence reason tied to the assumption-status table
4. **Loser disclosure** — the other test's result, kept in the report for transparency, with a one-sentence note on which assumption made it lose
5. **Effect size + 95% CI** — using the appropriate metric for the WINNING test (Cohen's d for parametric, Cliff's δ for non-parametric, OR for categorical)
6. **Outlier / discreteness check** — explicit note on whether the conflict is driven by outliers or ties, with a sensitivity analysis if appropriate
7. **Methods-section snippet** — pre-written paragraph the user can paste into the manuscript

## Failure modes

- **Picking the test with the smaller p-value as the winner** — this is p-hacking with extra steps; the test whose ASSUMPTIONS hold is the right test, not the test that "found" the result. Caught by: Step 4 adjudication rule pins the decision to the assumption-status table, not the p-values.
- **Reporting 'mixed evidence' to dodge the call** — both p-values in the paper with a hand-waved "results were sensitive to test choice" sentence; readers can't act on this. Caught by: Step 7 requires picking ONE primary; the other goes in supplement.
- **Switching tests AFTER seeing the data with no documentation** — running a t, then a Wilcoxon, then a permutation test, then a Bayes factor, and reporting whichever was best — full p-hacking. Caught by: Step 1 requires both tests be legitimate candidates for the same null; Step 8 requires the chain be documented.
- **Forgetting the CLT rescue at large n** — with n > 50 (well-behaved data), the t-test is robust to mild Normality violations; declaring it "broken" because Shapiro p = 0.04 at n = 200 is over-conservative. Caught by: Step 3 violation-call is calibrated to sample size; Step 5 gotcha-list flags this case.
- **Ignoring outlier-driven conflict** — declaring Wilcoxon the winner because Normality "fails" when actually 2 outliers are driving the entire result. Caught by: Step 6 sensitivity analysis on outlier removal.
- **Using parametric effect-size after rejecting the parametric test** — committing to Wilcoxon as primary but reporting Cohen's d in the abstract. Caught by: Step 7 requires the rank-based effect size (Cliff's δ, rank-biserial r, Hodges-Lehmann) for non-parametric winners.
- **Not reporting the loser** — hiding the conflicting test in the file drawer to keep the methods section cleaner. Caught by: Step 4 disclosure requirement; the loser goes in the supplement, not the trash.

## References

- [`reference/adjudication-table.md`](reference/adjudication-table.md) — exhaustive per-test-pair adjudication table with assumption mappings
- Hoenig & Heisey 2001, *The Abuse of Power* — broader context for "the p-value is not the whole story"
- Conover & Iman 1981, *Rank Transformations as a Bridge Between Parametric and Nonparametric Statistics*, The American Statistician — connection between parametric and rank-based tests; useful when explaining the adjudication
- Lumley et al. 2002, *The Importance of the Normality Assumption in Large Public Health Datasets*, Annual Review of Public Health — the CLT-rescue evidence for large n
- `ml-datasci/checking-test-assumptions` (sibling skill) — where the assumption checks originate
- `ml-datasci/selecting-statistical-test` (sibling skill) — what you should have done BEFORE running both tests

## Examples

### Example 1: Paired t significant, Wilcoxon not (happy-path)

Input: "Paired before/after reaction times for 22 subjects. Paired t(21) = 2.6, p = 0.017. Shapiro-Wilk on the differences: W = 0.86, p = 0.005. Wilcoxon signed-rank: V = 165, p = 0.11. Which do I report?"

Output:

Assumption-status table:

| Test | Key assumption | Check | Status |
|---|---|---|---|
| Paired t | Normality of differences | Shapiro p = 0.005 | **FAIL** |
| Wilcoxon | Symmetry of differences | (inspection / sample size) | OK |

**Winner: Wilcoxon signed-rank.** The paired t's Normality assumption is clearly violated (Shapiro p = 0.005 with n = 22, where CLT rescue does not yet kick in). Primary report: V = 165, p = 0.11; rank-biserial r ≈ 0.32 [95% CI tbd], direction = after slightly faster than before but not significant at α = 0.05.

Loser disclosure: the paired t-test's p = 0.017 is reported in the supplement with the note "Normality of differences was rejected by Shapiro-Wilk (W = 0.86, p = 0.005); the t-test result is shown only for transparency."

Sensitivity: if 1 outlier (the largest difference) is removed, both tests give consistent (non-significant) results, suggesting the t's "significance" was outlier-driven.

### Example 2: Outlier-driven conflict (edge-case)

Input: "Two-sample t-test on response latency between two server configs: t(58) = 2.4, p = 0.020. Mann-Whitney U: U = 612, p = 0.18. Levene's test for equal variance: p = 0.92 (OK). Shapiro on group A: p = 0.31 (OK). Shapiro on group B: p = 0.001 (FAIL). I see one observation in group B at 4,800 ms when everything else is 200–600 ms."

Output:

Both tests have assumption issues: t's Normality fails for group B (Shapiro p = 0.001); Mann-Whitney's same-shape assumption is also strained by the outlier. The conflict is being driven by the 4,800 ms outlier, NOT by a clean parametric-vs-non-parametric divergence.

Recommended adjudication:

1. **Inspect the 4,800 ms observation** — is it a measurement error, a timeout, a logging-pipeline bug, or a real long-tail latency event? The decision depends on this. Don't drop without reason.
2. If the outlier is a logging artifact (e.g., a default 5,000 ms timeout that capped a request), exclude it and re-run both tests. They will likely now agree.
3. If the outlier is real (some requests really do take 4,800 ms occasionally), report a **robust comparison**: median difference with Hodges-Lehmann 95% CI, plus a trimmed-mean test (10% trimmed) which is less outlier-sensitive than the raw t.
4. **Do NOT pick the t-test as the winner just because it gave the smaller p-value.** The t's Normality is broken AND the result is driven by 1 observation — that's the worst kind of "significant" finding.

Final commit: **trimmed-mean comparison or Hodges-Lehmann shift estimate as primary**; both t and Mann-Whitney in supplement.

### Example 3: Single test, no conflict (anti-trigger)

Input: "I ran a paired t-test on my data: t(45) = 1.8, p = 0.078. What test should I run next to see if I get a significant result?"

Output: This is the p-hacking failure mode. The skill does NOT recommend running additional tests in the hope that one will be significant.

The right next step is one of:

- **If the assumption check on the paired t was OK** (Shapiro p > 0.05 on the differences, or n large enough for CLT), the t-test is the right test and the result is the result: marginal evidence (p = 0.078) but not significant at α = 0.05. Report the effect size + 95% CI (which will include zero) and let the reader judge.
- **If the assumption check was NOT done**, run Shapiro-Wilk on the differences. If it rejects Normality, switch to Wilcoxon — but ONLY if the assumption fails, not as a fishing expedition.
- **If the underlying question is "did the effect happen at all?"** route to TOST / equivalence testing or a Bayesian estimation of the effect with a credible interval; don't keep frequentist-test-shopping.

Skill explicitly refuses the "run more tests until significant" path and routes to assumption check first, then either commit to the test that's already been run or switch to the equivalence-testing / interval-estimation framing.

## See also

- `ml-datasci/selecting-statistical-test` — the workflow that picks the test BEFORE running it (this skill is the rescue for when that step was skipped)
- `ml-datasci/checking-test-assumptions` — the assumption checks that gate the adjudication here
- `ml-datasci/reporting-effect-sizes` — once the winning test is picked, the effect-size + 95% CI report is the deliverable
- `ml-datasci/running-power-analysis` — if the underlying issue is "I didn't have enough power to resolve this", the next study should be powered for the smallest effect of interest

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
