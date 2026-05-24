# Gotcha catalog by topic

Cataloged failure modes that have been observed across grading histories. Use the catalog to source the "Gotcha" line for each walkthrough step. Do NOT invent gotchas; only use observed ones.

## Paired vs. independent

- Coding a two-sample t-test when the data is paired ("two columns" mistaken for "two groups")
- Coding a paired test when the groups are independent (matched but not paired by subject)
- Running Shapiro on the before column AND the after column for a paired test (should be on the differences)
- Forgetting the paired test reduces dimensionality (n is the number of pairs, not the total observations)

## Normality assumption (parametric tests)

- Skipping the Normality check entirely and reporting a parametric p
- Running Shapiro at n > 5000 where the test rejects on trivial deviation (use QQ-plot instead)
- Running Shapiro at n < 10 where the test is severely underpowered (use QQ-plot judgment + theoretical justification)
- Treating "p > 0.05 on Shapiro" as "data IS Normal" rather than "we fail to reject Normality"
- Forgetting Normality of the differences (paired) vs. Normality of residuals (regression) vs. Normality per group (two-sample) — three different objects

## Equal variance (Levene / two-sample t)

- Defaulting to pooled t without checking Levene; should use Welch's t when variances are unequal
- Running Levene but ignoring the result and proceeding with pooled t anyway
- Assuming equal variance from "the boxplots look similar"

## Multiple comparison

- Reporting many uncorrected p-values and treating each as independent
- Applying Bonferroni when Holm-Bonferroni would be appropriate (and more powerful)
- Forgetting that multiple comparisons applies across the family of related tests, not within a single test
- Cherry-picking the "significant" subset after running 20 tests without correction (garden of forking paths)

## Chi-squared expected counts

- Running chi-squared on a 2x2 table where one or more expected counts < 5; should use Fisher's exact test
- Computing expected counts incorrectly (row total × column total / grand total)
- Treating chi-squared p as the effect size (it isn't; effect size is Cramér's V or the odds ratio)

## Effect size

- Reporting p without effect size (the single most common stats write-up failure)
- Reporting effect size without 95% CI (point estimate without uncertainty)
- Reporting effect size without direction ("groups differ" without naming which is higher)
- Reporting Cohen's d on non-Normal data (should use Cliff's δ for non-parametric)
- Using unpaired Cohen's d formulas on paired data (use Cohen's dz for paired)

## Linear regression

- Reporting R² alone (without RMSE / MAE in target units)
- Reporting R² on training data without cross-validated or held-out R²
- Forgetting to check residuals vs. fitted (heteroscedasticity)
- Forgetting to check QQ-plot of residuals (Normality of residuals)
- Forgetting Cook's D for influential observations
- Including features highly correlated with the target by construction (data leakage)

## Cross-validation

- k-fold cross-validation on time-series data (use TimeSeriesSplit / walk-forward instead)
- Cross-validation on row-level random splits when grouped data is present (use GroupKFold)
- Fitting the preprocessor (imputation / scaling) on the full dataset before splitting (leakage)
- Reporting only the mean CV metric without the std across folds

## Train / test split

- Same patient / user / group ID in both train and test (group leakage)
- Random split on time-series data (temporal leakage)
- Stratification missing when classes are imbalanced
- Using the test set for model selection (model-selection leakage; should use a validation set)

## Hypothesis-test family confusion

- Running parametric and non-parametric tests, reporting whichever is "significant" (p-hacking)
- Switching tests after seeing the data
- Mixing up null and alternative in the conclusion sentence
- Mixing up one-sided and two-sided p-values

## DP / algorithms (programming-track)

- Subproblem definition is incorrect (e.g., "ending at i" instead of "first i prefix") and the recurrence breaks
- Base case forgotten (zero-length prefix, empty set, leaf node)
- Off-by-one in the table dimensions
- Forgetting traceback when the problem asks for the subsequence, not just the length
- O(nm) space when O(min(n, m)) is reachable via rolling-array

## Bayesian inference

- Updating with the wrong likelihood for the data type
- Treating the posterior mean as the answer without reporting the credible interval
- Forgetting that the prior matters; reporting "the answer" as if there is one
- Confusing the posterior predictive with the posterior over parameters

## Probability fundamentals

- Confusing P(A|B) with P(B|A) (base-rate / prosecutor's fallacy)
- Adding probabilities of non-disjoint events
- Treating the variance of a sum as the sum of variances when the variables are correlated
- Treating the expectation of a product as the product of expectations when the variables are correlated

## ML / deep learning

- Reporting test accuracy without baseline comparison
- Reporting accuracy on imbalanced data (use PR-AUC, per-class recall instead)
- Forgetting to set random seeds (irreproducible results)
- Forgetting to set the model to `.eval()` mode (PyTorch) before evaluating (BatchNorm / Dropout still active)

## Adding to the catalog

A gotcha enters this catalog only after being observed in:

- An instructor's grading history (preferred), OR
- A published catalog of common misuses (Cohen, ESL, etc.), OR
- A cross-cohort survey showing ≥ 10% of students made the error

Do NOT add gotchas based on "this sounds like something a student might do." Hypothetical gotchas dilute the catalog and train students to defend against errors that do not happen.
