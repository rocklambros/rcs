# DAG Cheatsheet

Reference for `analyzing-causal-dag`. Pattern-matching guide for the four canonical node roles and the two identification criteria.

## The four node roles

```
Confounder           Mediator             Collider             Instrumental
                                                                  Variable

   age                T                    T   Y                  IV
  /   \               |                     \ /                    |
 v     v              v                      v                     v
 T --> Y              M                      C                     T --> Y
                      |
                      v
                      Y
```

| Role | Structural pattern | Adjust? | Symptom of mis-classification |
|---|---|---|---|
| Confounder | Parent of T, parent of Y, not on causal path from T to Y | YES | Sign flip when added (the path through it was open and biasing T → Y) |
| Mediator | On causal path T → M → Y | NO (for total effect); YES (for direct effect) | Adjusted estimate shrinks; part of the causal effect now hidden |
| Collider | T → C ← Y (or descendant of both) | NO | Adjusting opens a non-causal path; spurious effect appears |
| Instrumental variable | IV → T → Y; IV not connected to Y except through T | NO (use IV-2SLS instead) | Adjusting for it loses the instrument's identifying variation |

## The backdoor criterion

A set Z is a sufficient adjustment set for the causal effect of T on Y if:

1. No node in Z is a descendant of T.
2. Z blocks every "backdoor path" from T to Y — every path that ends with an arrow into T.

A backdoor path is one that ends with `... → T`. Confounders open backdoor paths; the adjustment set closes them.

### Worked example

DAG:
```
age → T → Y
age → Y
severity → T → Y
severity → Y
T → adherence → Y
```

Backdoor paths from T to Y:
- T ← age → Y (open via age)
- T ← severity → Y (open via severity)

Causal paths:
- T → Y (direct)
- T → adherence → Y (indirect via mediator)

Sufficient adjustment set for the TOTAL effect: `{age, severity}`. Adjusting for adherence would block the indirect path.

Sufficient adjustment set for the CONTROLLED DIRECT effect (the part of T → Y that does not go through adherence): `{age, severity, adherence}`. Different estimand, different assumptions.

## The front-door criterion

When backdoor adjustment is impossible (an unmeasured confounder U exists between T and Y), the front-door criterion can sometimes identify the effect via a fully observed mediator M satisfying:

1. M intercepts all directed paths from T to Y (no T → Y direct arrow)
2. No unblocked backdoor path from T to M
3. All backdoor paths from M to Y are blocked by T

Rare in practice. Pearl's classic example: T = smoking, M = tar in lungs, Y = lung cancer.

## Common mistakes

### Adjusting for a post-treatment variable

Symptom: the adjusted estimate is much smaller than the unadjusted estimate.
Cause: the post-treatment variable is a mediator (on the causal path). Blocking it removes part of what the user is trying to measure.
Fix: exclude post-treatment variables unless the explicit estimand is a direct effect.

### Conditioning on a collider

Symptom: two variables that should be independent become correlated within strata of a third variable.
Cause: the third variable is a collider.
Famous case: in a study of athletes, height and basketball-skill may be uncorrelated in the general population but appear NEGATIVELY correlated within the population of professional players (the "collider" is "made it to the pros" — short players need more skill, tall players can compensate for less).
Fix: do not adjust for variables affected by both T and Y, even when they seem like "potential confounders."

### Selection bias

Conditioning on study enrollment is a collider when both T and Y influence enrollment. The classic problem in case-control studies sampling from a hospital population.

### Time-varying treatment with feedback

T at t=1 affects M at t=2 affects T at t=3. Standard DAG adjustment cannot handle this loop within a regression. Use G-methods (G-formula, G-estimation, IPW with time-varying weights). Out of scope for the basic backdoor workflow.

## Assumption stack

Every causal effect estimate from observational data rests on (at minimum):

1. **No unmeasured confounding** — the DAG is complete on the T-Y front, conditional on the measured adjustment set. Unverifiable from data.
2. **Positivity** — every covariate stratum has both T = 0 and T = 1 patients. Empirically checkable.
3. **Consistency / well-defined treatment** — the treatment has a single version with a single causal effect.
4. **Correct functional form** — the regression / matching / IPW model approximates the true conditional expectation. Checkable via diagnostics.
5. **No interference / SUTVA** — one unit's treatment does not affect another unit's outcome.

The user's report MUST state these. Hiding assumptions does not make them go away; it just hides the failure mode.

## Sensitivity analysis

The no-unmeasured-confounding assumption is the most important and the least verifiable. Always pair the point estimate with a sensitivity analysis:

- **E-value** (VanderWeele & Ding, 2017): minimum strength of association an unmeasured confounder would need to have with both T and Y (above and beyond measured confounders) to fully explain away the observed effect. Reported on the risk-ratio scale.
- **Tipping point**: the value at which an unmeasured confounder would flip the sign of the estimate.
- **Rosenbaum bounds** (matching designs): the range of unobserved treatment-assignment odds ratios over which the conclusion holds.

An estimate that tips at E-value = 1.2 is barely defensible. An estimate that holds at E-value = 3.0 is robust to most plausible unmeasured confounding.
