---
name: analyzing-causal-dag
description: >
  Walks a directed acyclic graph (DAG) for an observational causal-inference
  problem and picks the adjustment set that identifies the target causal
  effect. Forces explicit commitment to nodes (treatment, outcome, confounders,
  mediators, colliders, instrumental variables) and edges before any
  estimation runs, then applies the backdoor criterion to nominate an
  adjustment set, screens out colliders and mediators that would bias the
  estimate when conditioned on, and reports the assumptions the resulting
  estimate depends on. Triggers whenever the user proposes an observational
  treatment-effect claim, asks whether a specific covariate should be adjusted
  for, reports a Simpson-paradox-flavored sign flip, or hands over a study
  where confounding is plausible. Refuses to engage on randomized controlled
  trials where the randomization already breaks the confounding paths, and
  refuses to certify an effect estimate when the unverifiable assumptions
  are not stated.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - stats-student
  - instructor
  - ml-engineer
evidence:
  - DU-MSDSAI-4441-Final
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Analyzing Causal DAG

## When to use

Trigger this skill when the user does any of the following:

- Reports an observational effect estimate ("treatment X is associated with outcome Y by beta = ...") and either asks if it is causal or claims it is
- Asks "should I adjust for variable Z?" or "which variables should I include in my regression?"
- Reports a sign flip after adding a control (the textbook Simpson-paradox symptom)
- Hands over a study where measurement bias, confounding, or selection effects are plausible
- Names "DAG", "backdoor criterion", "do-calculus", "front-door", "instrumental variable", "confounder", "mediator", "collider"
- Has plotted observational data and is about to interpret a slope as an intervention effect
- Is writing up an observational study and needs to defend the adjustment-set choice to a reviewer

## When NOT to use

Skip and hand off when:

- The study is a properly-randomized controlled trial (RCT) — randomization breaks the backdoor paths so no DAG adjustment is needed; report the intent-to-treat estimate and move on
- The user only wants a predictive model (e.g., a forecasting score) and explicitly does not need a causal interpretation — point them at standard regression / classification evaluation skills
- This is pure exploratory data analysis with no causal claim attached
- The user wants a full causal-discovery search (learn the DAG from data via PC algorithm / GES / NOTEARS) — that is causal discovery, a different and harder workflow
- The user is computing average treatment effect under positivity violation (treated and untreated groups do not overlap on a key covariate) — no adjustment recovers identifiability there; the workflow fails for a different reason and needs different machinery (instrumental variables, regression discontinuity, etc.)
- The DAG has a known feedback loop (X affects Y affects X within the analysis time window) — naive DAG adjustment does not handle cycles; needs dynamic-treatment / G-methods which are out of scope here

## Quick start

User says: "I have observational data on 4,000 patients. I want to know if drug X causes lower blood pressure Y. Patient age and severity at admission are correlated with both whether the doctor prescribed X and the eventual blood pressure. I also have a measurement of medication adherence taken AFTER prescription. Help me set up the analysis."

Skill response, in order:

1. **Commit the node list** explicitly before drawing edges. Treatment T = drug X (binary). Outcome Y = post-treatment blood pressure (continuous). Candidate variables: age, severity at admission, medication adherence. Be specific about temporal order (admission → prescription → adherence → outcome).
2. **Draw the DAG** with arrows reflecting hypothesized causal direction:
   - age → T (older patients more likely to be prescribed X)
   - age → Y (older patients have higher BP at baseline)
   - severity → T (sicker patients more likely to be prescribed)
   - severity → Y (sicker patients have worse BP outcomes)
   - T → adherence (whether prescribed affects whether adherent)
   - adherence → Y (adherent patients see more effect)
   - T → Y (the causal effect we want to estimate)
3. **Classify each non-treatment, non-outcome node**:
   - age: confounder (parent of both T and Y, not on a causal path from T to Y)
   - severity: confounder (same structural pattern)
   - adherence: **mediator** (on the causal path T → adherence → Y) — DO NOT adjust for it if estimating the total effect; controlling for a mediator blocks part of the causal effect we are trying to measure
4. **Apply the backdoor criterion** to find a sufficient adjustment set: the set must (a) block all backdoor paths from T to Y, (b) contain no descendants of T (no mediators or colliders downstream of T). Adjustment set here: `{age, severity}`. Adherence is excluded as a descendant of T.
5. **Estimate the effect** with the chosen adjustment set: regression `Y ~ T + age + severity`, or matching / IPW / G-computation per preference. The coefficient on T is the adjusted estimate.
6. **State the assumptions the estimate depends on**:
   - No unmeasured confounders affect both T and Y (the structural assumption: the DAG is complete on the T-Y front)
   - Positivity: every covariate stratum has both treated and untreated patients
   - Correct functional form for the regression (linearity or whatever the model assumes)
   - Treatment is well-defined (no version effects)
7. **Sensitivity analysis** for the no-unmeasured-confounders assumption: report the E-value, or bound the bias an unmeasured confounder of plausible strength could induce. A point estimate that flips sign for any plausible unmeasured confounder is fragile.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| treatment | str | yes | — | Name of the treatment / exposure / intervention variable (T) |
| outcome | str | yes | — | Name of the outcome variable (Y) |
| candidate_vars | list[str] | yes | — | All other variables that might enter the DAG (confounders, mediators, colliders, IVs) |
| temporal_order | list[str] | yes | — | Ordered list of variables from earliest to latest in time; required to rule out impossible edges |
| edges | list[tuple[str, str]] | yes | — | Directed edges (cause → effect) the user hypothesizes; must respect temporal order |
| estimand | "ate" \| "att" \| "atc" \| "cate" \| "indirect" \| "direct" | no | "ate" | Which causal estimand is being identified — drives mediator-adjustment policy |
| identification_strategy | "backdoor" \| "front-door" \| "instrumental-variable" | no | "backdoor" | The criterion to use; backdoor is the default; front-door and IV need specific structures |
| estimator | "ols" \| "matching" \| "ipw" \| "g-computation" \| "tmle" \| "iv-2sls" | no | "ols" | Estimation method after the adjustment set is fixed; choice does not change identification |
| sensitivity_method | "e-value" \| "rosenbaum" \| "tipping-point" \| "none" | no | "e-value" | Sensitivity analysis for unmeasured confounding |

## Workflow

Copy this checklist into the response and check off each step as it lands:

```
Causal-DAG progress:
- [ ] Step 1: Commit treatment T, outcome Y, and candidate-variable list explicitly
- [ ] Step 2: Commit temporal order; reject any edge that violates time
- [ ] Step 3: Draw the DAG with directed edges and audience-readable labels
- [ ] Step 4: Classify each non-T/non-Y node: confounder / mediator / collider / IV / descendant
- [ ] Step 5: Apply backdoor criterion to nominate an adjustment set
- [ ] Step 6: Screen the adjustment set — remove descendants of T (mediators, colliders)
- [ ] Step 7: Pick estimator; estimate the effect on the chosen adjustment set
- [ ] Step 8: Run a sensitivity analysis (E-value or equivalent) for unmeasured confounding
- [ ] Step 9: Report the estimate WITH the explicit list of assumptions it relies on
```

### Step 4 — Node classification

| Role | Structural pattern | What to do |
|---|---|---|
| Confounder | Parent of both T and Y, not on a causal path from T to Y | INCLUDE in the adjustment set |
| Mediator | On a causal path T → M → Y | EXCLUDE when estimating total effect; include when estimating direct effect (different estimand) |
| Collider | T → C ← Y (or any descendant of both T and Y) | EXCLUDE; conditioning on a collider OPENS a non-causal path and induces spurious association |
| Instrumental variable | IV → T → Y, no edge IV → Y except through T, no unmeasured confounding between IV and Y | Use for IV estimation; do NOT include in a backdoor adjustment regression |
| Downstream of T (non-mediator) | T → V with no edge V → Y | EXCLUDE; conditioning on it changes nothing for identification but adds variance |
| Downstream of Y | Y → V | NEVER condition on; same collider-style induced association |

### Step 5 — Backdoor criterion

A set Z is a sufficient adjustment set for the causal effect of T on Y if:

1. **No node in Z is a descendant of T** (rules out mediators and downstream colliders)
2. **Z blocks every backdoor path from T to Y** — every path that ends with an arrow into T (e.g., T ← age → Y) must be blocked by some node in Z

The minimum sufficient set is usually the set of direct confounders. Software (`dagitty`, `pyAgrum`, `causaldag`) can enumerate all sufficient sets given a DAG.

### Step 6 — Adjustment-set screening

Watch for these mistakes when conditioning:

- **Adjusting for a mediator** when estimating total effect → underestimates effect (blocks part of the causal path). Symptom: adjusted estimate shrinks substantially after including a post-treatment variable.
- **Adjusting for a collider** → opens a non-causal path; induces spurious correlation. Symptom: previously uncorrelated covariates become correlated within strata; an effect appears where none existed.
- **"Kitchen-sink" regression** (throw every variable in) → high chance of including a mediator or collider; defensible only when every included variable is verifiably a confounder.

### Step 7 — Estimator choice (does not change identification)

| Estimator | When to prefer | Notes |
|---|---|---|
| OLS regression | Continuous outcome, modest covariates, linearity is plausible | Cheapest; widely understood |
| Matching (PSM, Mahalanobis) | Discrete treatment, want a transparent matched comparison | Sensitive to caliper choice; can drop unmatched units |
| Inverse-probability weighting (IPW) | Want to use the full sample, can model the treatment propensity well | Sensitive to extreme weights; truncate or stabilize |
| G-computation | Standard cousin of IPW; model the outcome instead of the treatment | Less sensitive to extreme weights; needs outcome model |
| TMLE | Want doubly-robust estimation with valid inference | More complex; ML-friendly nuisance models |
| 2SLS (instrumental variable) | Have a valid instrument; no backdoor adjustment available | Different identification strategy; produces LATE not ATE |

### Step 8 — Sensitivity analysis

The no-unmeasured-confounders assumption is unverifiable from the data. Report:

- **E-value** (VanderWeele & Ding, 2017): the minimum strength of association (on the risk-ratio scale) that an unmeasured confounder would need to have with BOTH treatment and outcome (above and beyond the measured confounders) to fully explain away the observed effect. Larger E-value = more robust estimate.
- **Tipping-point analysis**: how strong would an unmeasured confounder need to be to flip the sign of the estimate?
- **Rosenbaum bounds** (matching designs): the range of treatment-assignment odds ratios for which the conclusion is robust.

An estimate that tips at E-value = 1.2 is fragile. An estimate that holds at E-value = 3.0 is much more credible.

### Step 9 — Reporting

The report MUST state the adjustment set chosen, the assumptions it rests on, and the sensitivity result. Without these three items, the estimate is a number without provenance.

## Outputs

A short report containing:

1. **DAG diagram** (ASCII, mermaid, or Graphviz) showing nodes and directed edges
2. **Node classification table** — variable, role, included-in-adjustment-set or excluded with reason
3. **Adjustment set** chosen, plus alternative sufficient sets if the user asked
4. **Effect estimate** with confidence interval, computed on the chosen adjustment set with the chosen estimator
5. **Assumptions list** — no unmeasured confounding (per the DAG), positivity, correct functional form, well-defined treatment
6. **Sensitivity analysis result** — E-value or tipping-point, with interpretation
7. **Caveats / flags** — known structural assumptions the user has not verified

## Failure modes

- **Adjusting for a mediator when estimating total effect** — common with post-treatment "adherence" or "compliance" variables. Caught by: Step 4 forces explicit role classification before estimation runs; mediator excluded automatically.
- **Adjusting for a collider** — induces spurious association from previously independent variables; classic example is conditioning on "patient enrolled in study" when both T and Y affect enrollment. Caught by: Step 4 collider role detection; Step 6 screening reminder.
- **Sign flip on adding a control (Simpson's paradox symptom)** — when a confounder is missed, the unadjusted slope tracks the confounder's bias; adding the confounder reveals the true direction. Caught by: Step 3 forces explicit edge commitment; reviewer can spot the missing confounder.
- **Estimating the causal effect of an undefined treatment** — "the effect of obesity on heart disease" is ambiguous because obesity has versions (diet-induced vs metabolic) with different effects. Caught by: Step 6 well-defined-treatment assumption in the report.
- **Confusing association with causation when the DAG is unstated** — running a regression and calling the slope "the effect of T" without checking if the DAG supports identification. Caught by: skill refuses to ship an effect estimate without an explicit DAG and assumption list.
- **Positivity violation** — every covariate stratum must have both treated and untreated; if some strata are 100% treated, the effect there is not identified from data. Caught by: Step 6 assumption list; recommend a positivity diagnostic (e.g., propensity-score distribution overlap).
- **Misuse of an instrumental variable** — IV must satisfy three assumptions (relevance, exclusion, exchangeability); failing any one gives a biased estimate. Caught by: Step 4 IV role classification; refuse to use IV without explicit defense of all three assumptions.
- **Ignoring the unverifiability of structural assumptions** — the DAG itself is an assumption; the data cannot validate it. Caught by: Step 8 sensitivity analysis mandate; Step 9 reporting mandate.

## References

- [`reference/dag-cheatsheet.md`](reference/dag-cheatsheet.md) — confounder / mediator / collider / IV decision rules, the backdoor and front-door criteria, common-mistake patterns
- [`reference/dowhy-example.py`](reference/dowhy-example.py) — DoWhy end-to-end example with a CausalModel, identify, estimate, and refute pipeline
- [Pearl, Glymour, Jewell, "Causal Inference in Statistics: A Primer" (2016)](https://bayes.cs.ucla.edu/PRIMER/) — canonical undergraduate reference
- [Hernán & Robins, "Causal Inference: What If" (2020)](https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/) — graduate reference, freely available
- [VanderWeele & Ding, "Sensitivity Analysis in Observational Research: Introducing the E-Value" (2017)](https://www.acpjournals.org/doi/10.7326/M16-2607) — E-value reference
- [dagitty.net](http://www.dagitty.net/) — interactive DAG editor with backdoor-set enumeration
- `ml-datasci/auditing-train-test-split` — for the data-engineering side of avoiding leakage (orthogonal to causal-identification leakage)
- `ml-datasci/running-bayesian-workflow` — Bayesian causal-inference path when priors on causal effects are available

## Examples

### Example 1: Observational study with confounders and a mediator (happy-path)

Input: "I have observational data on 4,000 patients. I want to know if drug X causes lower blood pressure Y. Patient age and severity at admission are correlated with both whether the doctor prescribed X and the eventual blood pressure. I also have a measurement of medication adherence taken AFTER prescription. Help me set up the analysis."

Output: Commit nodes (T = drug X, Y = post-treatment BP, candidates = age, severity, adherence). Temporal order: admission → age, severity → prescription (T) → adherence → Y. Draw edges (age → T, age → Y, severity → T, severity → Y, T → adherence, adherence → Y, T → Y). Classify: age = confounder, severity = confounder, adherence = mediator (descendant of T). Backdoor adjustment set: `{age, severity}`. EXCLUDE adherence — including it would block part of the causal pathway and shrink the estimated total effect. Fit `Y ~ T + age + severity`; report the coefficient on T as the adjusted total effect. State assumptions: no unmeasured confounders, positivity, correct functional form, well-defined treatment. Compute the E-value; report whether the estimate is robust to plausible unmeasured confounding. If the user instead wanted the DIRECT effect (not through adherence), the adjustment set would be `{age, severity, adherence}` and the estimand would be the controlled direct effect — a different estimand with stricter assumptions.

### Example 2: Sign flip after adding a control (edge-case Simpson-paradox flavor)

Input: "I regressed Y on T and got a positive slope of 0.5. Then I added a control variable C and the slope flipped to -0.3. Which is right?"

Output: Both estimates can be unbiased for different things; one is biased for the causal effect. The flip is a structural signal. Three scenarios cover most cases. First, C is a CONFOUNDER (parent of both T and Y) — then the adjusted estimate (-0.3) is the unbiased causal effect; the unadjusted (+0.5) was confounded by C. Second, C is a COLLIDER (downstream of both T and Y, conditioning on it induces spurious correlation) — then the unadjusted (+0.5) is the right answer; adding C corrupted it. Third, C is a MEDIATOR (T → C → Y) — then the unadjusted (+0.5) is the total effect; the adjusted (-0.3) is the direct effect with the mediator path blocked, which is a different estimand. Decide by drawing the DAG, locating C's role, and committing before the data informs the answer. Reverse-engineering the DAG from which-sign-feels-right is p-hacking. Walk the user through Steps 1–4; the answer falls out of the DAG.

### Example 3: Properly-randomized RCT (anti-trigger)

Input: "I ran a randomized controlled trial. 500 patients assigned randomly to drug X (T=1) or placebo (T=0); outcome Y measured 30 days later. The mean Y in the treated arm is 8.2 lower than in the placebo arm with 95% CI [5.1, 11.3]. Should I be drawing a DAG and adjusting for age and severity?"

Output: No — randomization breaks every backdoor path from T to Y, including paths through age, severity, and any unmeasured confounder. The unadjusted intent-to-treat difference IS the causal effect estimate; the confidence interval is the right inference. Adjusting for baseline covariates in an RCT can tighten precision but does not change the identification — and adjusting for post-randomization variables (adherence, dropout) re-introduces the same risks (mediator bias, collider bias) as in observational work. The DAG-and-adjustment workflow does not apply here; report the ITT difference, the CI, and any pre-specified secondary analyses. If you want to explore mechanism (does the effect run through adherence?), that is a separate mediation analysis with its own assumptions, not a re-do of the primary effect estimate.

## See also

- `ml-datasci/auditing-train-test-split` — leakage in the predictive sense; different from causal identification but worth the cross-check
- `ml-datasci/running-bayesian-workflow` — Bayesian path for causal estimation with informative priors on effects
- `ml-datasci/checking-test-assumptions` — for the frequentist assumption checks on the underlying regression / matching estimator
- `ml-datasci/reporting-effect-sizes` — for the reporting discipline once the causal estimate is in hand
- `ml-datasci/comparing-models-fairly` — when comparing causal effect estimates across competing adjustment sets

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
