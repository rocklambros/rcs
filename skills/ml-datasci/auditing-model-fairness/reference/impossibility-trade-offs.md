# Fairness impossibility trade-offs

When base rates differ across protected groups (which is almost always true in real data, even when the underlying construct doesn't differ), it is mathematically impossible to satisfy all common fairness criteria simultaneously. This page summarizes the named trade-offs the deployer must own.

## Kleinberg-Mullainathan-Raghavan (KMR) 2017

For a calibrated classifier whose predictions differ in average score across groups (i.e., base rates differ), these three properties cannot all hold:

1. **Calibration within groups** — within each group, p̂ matches the actual rate
2. **Balance for the positive class** — among true positives, average score is equal across groups (equivalent to equal TPR)
3. **Balance for the negative class** — among true negatives, average score is equal across groups (equivalent to equal FPR)

In trivial cases (perfect classifier, equal base rates), all three can hold. In all real cases, pick at most two.

## Chouldechova 2017

For groups with different base rates, these cannot both hold:

- Predictive parity (equal precision across groups)
- Equalized odds (equal FPR and FNR across groups)

Made famous by the ProPublica / COMPAS recidivism debate: Northpointe argued the model satisfied predictive parity; ProPublica showed it violated equal FPR. Both were correct; the theorem says they cannot both be satisfied when base rates differ.

## Demographic parity vs equal opportunity

When base rates differ across groups, equalizing selection rates (demographic parity) requires either:

- Lowering the threshold for the lower-base-rate group (raising their FPR)
- Raising the threshold for the higher-base-rate group (lowering their TPR)

Equalizing TPR (equal opportunity) does NOT generally equalize selection rates; the group with the higher base rate will still be selected more often.

## What this means for the audit report

The audit reports the gap on each metric. It does NOT declare one metric is the right one to honor. That choice belongs to:

- The legal/regulatory regime (EEOC four-fifths rule defaults to selection-rate parity; EU AI Act high-risk leaves more room)
- The harm asymmetry of the use case (false-negative-heavy for medical diagnosis; false-positive-heavy for criminal risk scoring)
- The stakeholder consultation (the affected population's preference often diverges from the developer's intuition)

A well-formed deployer decision names which metric is being prioritized, which is being traded against, and the documented rationale. The audit's job is to make that trade-off explicit, not to hide it inside a single "fairness score".

## Aggregation pitfalls

- **Marginal-only audit hides intersectional disparities.** Buolamwini & Gebru (2018) showed face-recognition systems with ~95% accuracy on white men and ~65% on Black women, but only ~80% disparity at the marginal level on race and ~85% on sex. The intersectional cut surfaced the harm.
- **A single "average" disparity across many groups can mask one severely-harmed group.** Always report per-group, not just aggregates.
- **CI width grows as 1/√n; small groups have wide CIs.** Report the limitation, do not drop the group.
