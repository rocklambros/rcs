---
name: auditing-model-fairness
description: >
  Audits a trained classifier or scoring model for disparate treatment across protected
  attributes (race, sex, age, disability, religion, national origin, sexual orientation,
  or any user-supplied subgroup) using equal-opportunity, demographic-parity,
  calibration-within-group, and intersectional cuts. Use when the model decides
  outcomes for people (hiring, lending, healthcare triage, content moderation, criminal
  justice scoring), when a downstream user asks whether the model is "fair", when a
  regulator requires a disparate-impact analysis, or before deployment of any
  consequential ML system. Refuses to audit without a documented protected-attribute
  list and refuses to declare a model "fair" from a single metric.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer, security-eng, ai-security]
evidence:
  - DU-MSDSAI-4441-Final
  - llm-safety-alignment-study
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Auditing Model Fairness

## When to use

Trigger this skill when:

- The model decides outcomes about people: hiring, lending, healthcare triage, insurance pricing, content moderation, criminal-justice risk scoring, admissions, fraud flagging, or recommendation systems where the recommended item changes life chances
- The user asks "is this model fair?", "are we biased?", "should we deploy this?", "what's our disparate impact?"
- A regulator, internal compliance, or external audit requires a disparate-impact analysis (EU AI Act high-risk, NYC Local Law 144, EEOC four-fifths rule, ECOA)
- Pre-deployment review of any consequential supervised model
- A stakeholder reports a complaint that outcomes differ across a protected group

## When NOT to use

Skip and hand off when:

- No protected attribute is relevant or available (e.g., a server-load classifier with no human subject) — fairness is not a free-floating property; it requires a subject
- The model is descriptive/exploratory and not deciding any outcome (use `evaluating-binary-classifiers` or `evaluating-multiclass-classifiers` for general performance)
- The user supplies only a global accuracy and refuses to share per-group breakdowns — refuse and escalate; a single number cannot answer the question
- Fairness in the policy/values sense (which metric is morally right) — that is a stakeholder decision, not an audit; this skill computes the metrics, the humans pick the trade-off

## Quick start

User says: "We trained a logistic regression to predict loan default. We have race, sex, and age in the dataset. Audit the model for fairness before we ship."

Skill response: requires y_true, y_pred (or y_pred_proba), and the protected-attribute vectors per record. Computes (a) per-group base rate and selection rate, (b) equal-opportunity (TPR) and equalized-odds (TPR + FPR) gaps, (c) demographic-parity gap, (d) calibration-within-group, (e) intersectional cuts for at least the largest 2-way intersections. Reports a per-metric per-group table with 95% bootstrap CIs. Flags any gap > 0.10 absolute or any four-fifths-rule violation as material. Refuses to issue a "fair" or "unfair" verdict — names which metrics pass and which fail and which trade-off the deployer must own.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| y_true | array of {0,1} or class labels | yes | — | Ground-truth outcomes, one per record. |
| y_pred | array, same shape as y_true | yes (one of) | — | Hard predictions. |
| y_pred_proba | array of probabilities | yes (one of) | — | Soft scores, required for calibration check. Pass at least one of y_pred or y_pred_proba. |
| protected_attrs | dict {name: array} | yes | — | One vector per protected attribute (e.g., {"race": [...], "sex": [...]}). Each must align row-wise with y_true. |
| threshold | float | no | 0.5 | Decision threshold for converting y_pred_proba to hard predictions. |
| min_group_size | int | no | 30 | Minimum samples per group to compute a CI; smaller groups get a "low-power" warning instead of a verdict. |
| material_gap | float | no | 0.10 | Absolute gap that triggers a "material" flag on TPR / FPR / selection-rate parity. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off as you go:

```
Fairness audit progress:
- [ ] Step 1: Confirm protected attributes and group sizes (refuse if any group < min_group_size without an explicit override)
- [ ] Step 2: Compute per-group base rate, selection rate, and confusion matrix
- [ ] Step 3: Equal-opportunity (TPR gap) and equalized-odds (TPR + FPR gap)
- [ ] Step 4: Demographic-parity gap (selection-rate gap)
- [ ] Step 5: Calibration-within-group (Brier or reliability bins per group)
- [ ] Step 6: Four-fifths-rule check (selection rate of any group ≥ 0.8 × max group's rate)
- [ ] Step 7: Intersectional cuts (at least the largest 2-way: e.g., race × sex)
- [ ] Step 8: Bootstrap 95% CIs on each gap (n_bootstrap ≥ 1000)
- [ ] Step 9: Report material flags + trade-off statement (no "fair / not fair" verdict)
```

### Step 1: Confirm protected attributes and group sizes

List every protected attribute supplied; for each, report group sizes. If any group has fewer than `min_group_size` records, mark that group as "low power, CI uninformative" and do not issue a per-group verdict for it. Do not silently drop the group; report the limitation.

### Step 2: Per-group base rate, selection rate, confusion matrix

For each group g in each protected attribute:

- Base rate: P(y_true = 1 | group = g)
- Selection rate: P(y_pred = 1 | group = g) at the given threshold
- TP, FP, TN, FN counts (the full confusion matrix per group)

### Step 3: Equal-opportunity and equalized-odds

- Equal-opportunity gap: max TPR - min TPR across groups (TPR = recall on positive class)
- Equalized-odds gap: max(TPR_gap, FPR_gap) — both errors equalized
- A gap > `material_gap` (default 0.10) is flagged as material

### Step 4: Demographic-parity gap

- Demographic-parity gap: max selection rate - min selection rate across groups
- A gap > `material_gap` (default 0.10) is flagged as material
- Note explicitly: demographic parity is incompatible with equal-opportunity when base rates differ across groups (Kleinberg-Mullainathan-Raghavan impossibility); the deployer must pick which to honor

### Step 5: Calibration-within-group

For each group:

- Bin predicted probabilities (10 deciles)
- Within each bin, observed rate vs predicted rate (reliability diagram)
- Brier score per group
- A group whose calibration curve systematically over- or under-predicts is flagged

### Step 6: Four-fifths rule

- For each protected attribute, compute selection_rate(g) / max_g(selection_rate)
- Any group with ratio < 0.8 triggers a four-fifths-rule flag (EEOC disparate-impact threshold)

### Step 7: Intersectional cuts

- For at least the two largest protected attributes, compute group sizes and the metrics above on the 2-way intersection (e.g., Black women, white men, Asian non-binary)
- Disparities often hide at intersections that are masked at the marginal level (Buolamwini & Gebru 2018, Gender Shades)

### Step 8: Bootstrap CIs

For each reported gap, sample with replacement n_bootstrap ≥ 1000 times and report the 2.5th and 97.5th percentile of the gap. A gap whose CI crosses zero is not statistically distinguishable from zero at the given sample size.

### Step 9: Report

Output a structured report (see Outputs). Do NOT declare the model "fair" or "unfair". Name which metrics pass and which fail; name the trade-off the deployer must own (e.g., "equalizing TPR will lower demographic parity because base rates differ").

## Outputs

A markdown report with:

1. **Audit identity** — model name, dataset, threshold, n samples, n groups per attribute
2. **Per-group table** for each protected attribute: Group · n · base rate · selection rate · TPR · FPR · Brier · calibration slope
3. **Gap summary table**: Metric · Gap · 95% CI · Material? · Four-fifths rule?
4. **Intersectional table**: same metrics on at least the largest 2-way intersection
5. **Calibration plots** (one per group) — observed vs predicted reliability
6. **Material findings list** — every metric flagged as material, with the impossibility-theorem trade-off named when relevant
7. **Deployer decision** — explicit list of trade-offs the deployer must pick from (which metric to honor, which threshold to set, whether the largest disparity is acceptable given the use case)

## Failure modes

- **Single-metric declaration** — reporting only demographic parity or only equal opportunity and calling the model "fair". Caught by: required multi-metric table (Step 3 + Step 4 + Step 5).
- **Marginal-only audit** — measuring race and sex separately but never their intersection, missing the worst-off intersectional group. Caught by: Step 7 is required, not optional.
- **Small-group silent drop** — dropping a small group from the report because the CI is wide. Caught by: Step 1 requires explicit low-power flagging, not removal.
- **Verdict overreach** — declaring the model "fair" or "unfair" from the audit. Caught by: Step 9 names trade-offs, the deployer owns the verdict.
- **Threshold gerrymandering** — picking a different threshold per group to equalize a metric without disclosing it; this is itself a fairness decision and must be reported explicitly.
- **Protected-attribute proxies** — auditing on documented protected attributes while a strong proxy (zip code, surname) is in the feature set; flag and recommend `enforcing-leakage-firewall`-style review.

## References

- `reference/metric-definitions.md` — formulas for TPR, FPR, equalized-odds, demographic parity, calibration slope, Brier score
- `reference/impossibility-trade-offs.md` — Kleinberg-Mullainathan-Raghavan + Chouldechova summary
- [Fairlearn library documentation](https://fairlearn.org/)
- [AIF360 library documentation](https://aif360.res.ibm.com/)
- [EEOC Uniform Guidelines on Employee Selection (four-fifths rule)](https://www.eeoc.gov/laws/guidance/uniform-guidelines-employee-selection-procedures)

## Examples

### Example 1: Loan-default model with race + sex (happy-path)

Input: Logistic regression on 5000 loan applications; y_true = default, y_pred_proba scored; protected = {race: [...], sex: [...]}.

Output: Per-group table shows white-male selection rate 0.42, Black-female selection rate 0.18; four-fifths ratio 0.43 (FAIL). TPR gap 0.14 across race (material), FPR gap 0.09 (not material). Calibration slope ~1.0 across all groups (passes). Intersectional Black-female group n=120, all metrics computable. Material findings: four-fifths failure AND material TPR gap. Trade-off: equalizing TPR via lower threshold for Black-female applicants will raise their FPR; alternatively, equalizing selection rates loses some predictive accuracy in the white-male group. Deployer decision named, no skill verdict.

### Example 2: Healthcare triage with all groups < 30 (low-power)

Input: 500-patient cohort, race has 5 groups; smallest group n=18.

Output: Step 1 flags that group as low-power; CI on its TPR will exceed ± 0.20, uninformative. Skill reports metrics for groups n ≥ 30 with full CIs, reports the smallest group's metrics with an explicit "low-power, CI wider than effect of interest" warning. Does NOT drop the group. Recommends recollecting data or stratified sampling before re-audit.

### Example 3: Backend ETL classifier (anti-trigger)

Input: "Audit fairness of our ETL row-malformedness classifier."

Output: Skill identifies no human subject in the prediction (rows are data, not people). Declines the fairness audit. Suggests `evaluating-binary-classifiers` for general performance evaluation. Notes that if downstream effects of misclassification disparately impact users, the fairness question moves to that downstream system.

## See also

- `ml-datasci/evaluating-binary-classifiers` — general performance evaluation; fairness audit sits on top
- `ml-datasci/comparing-models-fairly` — paired comparison of two models; useful when comparing a fairness-mitigated model vs the original
- `ml-datasci/enforcing-leakage-firewall` — catches protected-attribute proxies leaking into the feature set
- `workflow/running-adversarial-premortem` — high-stakes deployment decisions

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
