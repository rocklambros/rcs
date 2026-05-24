# Common misconceptions to address head-on

Per-concept catalog of student intuitions the explanation must NAME and CORRECT explicitly. Glossing over these lets the learner reconcile the new explanation against the wrong intuition and pick the wrong intuition.

Primary source for many of these: Greenland et al., *Statistical Tests, P Values, Confidence Intervals, and Power: A Guide to Misinterpretations* (Eur J Epidemiology 2016) — a 25-item catalog of canonical misinterpretations.

## P-value misconceptions

1. **"It is the probability the null is true."** Most common. Address by naming the conditional: p is conditioned on the null, not the other way around.
2. **"It is the probability our result is due to chance."** Conflates "due to chance" with "extreme under chance." Address by name.
3. **"A small p means a large effect."** Conflates significance with magnitude. Address by noting p is sensitive to n.
4. **"A non-significant result means there is no effect."** Absence of evidence vs. evidence of absence. Address with power framing.
5. **"p < 0.05 means the result is 'real' or 'true.'"** Replace "real" with "unlikely under the null at chosen α." Address by name.

## Confidence interval misconceptions

6. **"95% probability the true value is in this specific interval."** Bayesian-flavored applied to frequentist. Address by name; restate as procedure-level coverage.
7. **"A wider interval means more uncertainty about WHAT THE TRUE VALUE IS."** Subtly wrong; a wider interval means more uncertainty about the procedure's estimate. The true value is fixed.
8. **"If the interval includes 0, the effect is zero."** Conflates "fails to exclude" with "is." Address; estimate may be nonzero even when CI includes 0.
9. **"95% of the data falls within the CI."** Confuses CI for the parameter with a prediction interval for new observations. Address; these are different objects.

## Central limit theorem misconceptions

10. **"Data becomes Normal as n grows."** It does not; the SAMPLING DISTRIBUTION OF THE MEAN does. Address by name.
11. **"CLT applies even when variance is infinite."** It does not; finite variance is required. Address (less common, but trips up grad students reading old papers).
12. **"With large n, the t-test is exact."** It is asymptotic, not exact; for heavy-tailed data, the convergence is slow.

## Hypothesis test misconceptions

13. **"The test proves the alternative."** Tests provide evidence; do not prove. Address by name.
14. **"Failing to reject means accepting the null."** Failure to reject is not acceptance. Address by name.
15. **"p < α is the same as 'the effect is meaningful.'"** Statistical significance vs. practical significance. Address with effect-size framing.

## Regression coefficient misconceptions

16. **"X causes Y by this amount."** Association, not causation, without a causal-inference framework. Address by name.
17. **"Holding other variables fixed' is a real-world operation."** It is an estimation technique; not always physically possible. Address; note that "fixed" is a conditional estimate, not a counterfactual.
18. **"A coefficient near zero means no effect."** The coefficient near zero with a wide CI means we do not know the effect. Address with CI framing.
19. **"Standardized coefficients are comparable across studies."** Only within the same scale and feature engineering. Address; standardization depends on the SD of the features in the sample.

## Bayes' theorem misconceptions

20. **"The prior is arbitrary so the posterior is arbitrary."** The prior is subjective but disciplined; sensitivity analysis tests robustness. Address by name.
21. **"Bayesian methods are immune to assumptions."** They have different assumptions (prior choice, likelihood specification), not no assumptions. Address.
22. **"The posterior probability is the true probability."** It is conditioned on the prior, the data, and the model. Address.

## Statistical power misconceptions

23. **"This test has 80% power."** Power is conditional on a specified effect size; no single number characterizes a test's power. Address by name.
24. **"Increasing α increases power but does not affect Type I rate."** It affects both. Address.
25. **"Underpowered studies that find significance are reliable."** Winner's curse: in underpowered studies, significant findings tend to over-estimate the true effect. Address.

## Effect size misconceptions

26. **"Cohen's d > 0.8 means a large, important effect."** Cohen's conventions are starting points; domain matters. Address.
27. **"Effect sizes are interpretable without the underlying SD."** They are standardized; a Cohen's d of 0.5 in one population can be a different practical magnitude in another. Address.
28. **"Reporting only the effect size (no p, no CI) is enough."** Effect size needs uncertainty quantification (CI). Address; effect size alone is a point estimate.

## Probability fundamentals (prerequisites — may surface in explanations)

29. **"P(A and B) = P(A) + P(B)."** Confuses union with intersection. Trips up early-tier students.
30. **"P(A | B) = P(B | A)."** Prosecutor's fallacy / base-rate neglect. Trips up most learners at first exposure.
31. **"Independent events cannot happen together."** Independence is a probability statement, not a possibility statement. Address.

## How to use this catalog

Before authoring the explanation, look up the concept's misconceptions. Pick the one most likely to be active for the learner's tier (or use the `addressed_misconception` argument if the user specified one). The explanation's targeted-explanation step (step 3 of the Socratic structure) MUST name that misconception by surface form before stating the correct version.
