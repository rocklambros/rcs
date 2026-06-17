---
name: evaluating-ood-detection
description: >
  Evaluates an out-of-distribution (OOD) detector on a held-out in-distribution set
  plus one or more curated OOD sets, using AUROC, AUPR-out, FPR-at-95-TPR, and
  near-OOD vs far-OOD stratification. Walks a method selection (max-softmax-probability,
  energy score, Mahalanobis distance, KNN distance, ODIN) and a calibration step.
  Use when deploying a classifier into an open-world setting where novel-class inputs
  arrive, when a safety reviewer requires "the model should know what it doesn't
  know", or when the model has a documented rejection / abstain pathway. Refuses to
  evaluate OOD detection in a closed-world setting where every test input is
  guaranteed in-distribution, and refuses to compare OOD detectors using only in-
  distribution accuracy.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer, ai-security]
evidence:
  - llm-toxicity-visual-analysis
  - multiturn-injection-detection
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Evaluating OOD Detection

## When to use

Trigger this skill when:

- A classifier is being deployed into an open-world setting where novel-class or distribution-shifted inputs will arrive
- A safety / risk reviewer requires the model to "know what it doesn't know"
- The model has a documented rejection or abstain pathway (e.g., "if OOD score > τ, route to human review")
- Comparing two OOD detectors (e.g., max-softmax-probability vs energy score) on the same backbone
- A regulator requires uncertainty quantification for high-risk decisions (EU AI Act high-risk, FDA SaMD, autonomous-vehicle perception)
- The user reports the deployed model is "confidently wrong" on novel inputs and wants to add a rejection layer

## When NOT to use

Skip and hand off when:

- The deployment is closed-world: every test input is guaranteed to belong to a training class (e.g., a card-game state classifier with 52 cards, no novel cards possible). OOD is not a meaningful concept here.
- The user wants to detect adversarial perturbations (FGSM/PGD/etc.) on in-distribution inputs — use `running-adversarial-perturbation-suite` (planned); OOD methods sometimes catch adversarial inputs but are not designed for it
- The user wants distribution-drift monitoring on production data over time — use `monitoring-data-drift`; OOD detection is per-input, drift monitoring is per-cohort over time
- The model is a generative model (LLM, diffusion); OOD detection on generative outputs is a different problem class (perplexity-based, likelihood-based)

## Quick start

User says: "I'm shipping a 10-class image classifier. Some inputs in production will be outside the 10 classes. Help me add OOD detection."

Skill response: walks (1) method selection — for a softmax classifier with no architectural change wanted, start with energy score (better than max-softmax-probability per Liu et al. 2020); if architectural change is OK, Mahalanobis on penultimate features is stronger; (2) OOD set construction — need at least one near-OOD set (same domain, novel class) and one far-OOD set (different domain entirely); (3) metrics — AUROC, AUPR-out, FPR-at-95-TPR; (4) threshold selection — pick τ to hit a target FPR or TPR depending on whether false-rejection or false-acceptance is more costly. Refuses to ship without near-OOD evaluation; far-OOD-only is too easy.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| model | trained classifier | yes | — | The in-distribution classifier; supplies softmax/logits/features. |
| id_test | array | yes | — | Held-out in-distribution test set with labels. |
| ood_near | list of arrays | yes | — | At least one near-OOD set (same domain, novel class). Required, not optional. |
| ood_far | list of arrays | no | — | Far-OOD set (different domain). If supplied, evaluated separately from near-OOD. |
| method | "msp" \| "energy" \| "mahalanobis" \| "knn" \| "odin" | yes | "energy" | OOD scoring method. |
| target_tpr | float | no | 0.95 | TPR (in-distribution recall) the threshold is calibrated to hit; used for FPR-at-95-TPR reporting. |
| n_bootstrap | int | no | 1000 | Bootstrap samples for AUROC CI. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

```
OOD detection evaluation progress:
- [ ] Step 1: Confirm open-world setting (refuse with hand-off if closed-world)
- [ ] Step 2: Pick OOD scoring method (msp / energy / mahalanobis / knn / odin)
- [ ] Step 3: Construct OOD sets — REQUIRE at least one near-OOD set; far-OOD optional
- [ ] Step 4: Compute scores on id_test, ood_near, ood_far separately
- [ ] Step 5: Compute AUROC, AUPR-out, FPR-at-95-TPR per OOD set
- [ ] Step 6: Bootstrap 95% CIs on each metric
- [ ] Step 7: Pick threshold τ for deployment based on cost trade-off (false-reject vs false-accept)
- [ ] Step 8: Report — metrics per OOD set, threshold + expected operating point, in-distribution accuracy unchanged check
```

### Step 1: Confirm open-world

If the user can enumerate every possible test input and every input maps to a training class, the deployment is closed-world. OOD detection has no value; hand off to general classification evaluation.

### Step 2: Pick method

| Method | Backbone change | Compute cost | Strength |
|---|---|---|---|
| MSP (max softmax probability) | None | Free | Baseline; weak |
| Energy score | None | Free | Better than MSP (Liu et al. 2020); easy retrofit |
| Mahalanobis (on penultimate features) | None at train; cov matrix at deploy | Moderate | Strong on near-OOD; needs class-conditional cov |
| KNN distance | None at train; index at deploy | High at inference | Strong on near-OOD; non-parametric |
| ODIN | Temperature scaling + input perturbation | Moderate | Strong but requires hyperparameter tuning per OOD set (avoid hyperparameter overfitting) |
| Outlier exposure / energy-bound training | YES | Moderate (re-train) | Strongest but needs labeled OOD samples at train time |

Default: energy score for retrofit, Mahalanobis for stronger evaluation when feature extraction is feasible.

### Step 3: Construct OOD sets

- **Near-OOD** (REQUIRED): same domain as training, novel class. Example: train on 10 ImageNet classes, near-OOD = 10 other ImageNet classes. Hard to detect; the realistic deployment threat.
- **Far-OOD** (optional): different domain entirely. Example: train on ImageNet, far-OOD = CIFAR. Easy to detect; not informative on its own.
- A detector that aces far-OOD but fails near-OOD is shipping a false sense of safety.

### Step 4: Score

- id_test scores S_in
- ood_near scores S_near
- ood_far scores S_far (if applicable)

Higher score = more in-distribution (convention; flip if your method outputs OOD-ness directly).

### Step 5: Metrics

- **AUROC**: P(S_in > S_ood); want > 0.85 for serious deployment
- **AUPR-out**: precision/recall for the OOD class; report when OOD is the minority
- **FPR at TPR=0.95**: at the threshold τ where 95% of in-distribution inputs are accepted, what fraction of OOD inputs are falsely accepted? Want < 0.10 for serious deployment; > 0.50 means the detector is near-useless at high TPR

Report each metric separately for near-OOD and far-OOD. Do not aggregate.

### Step 6: Bootstrap CIs

Resample id_test + ood set with replacement n_bootstrap times; recompute metric; report 2.5/97.5 percentiles.

### Step 7: Threshold selection

Pick τ based on the deployment cost trade-off:

- If false-reject (rejecting a true in-distribution input) is expensive (e.g., medical triage where rejection delays care) → high TPR, accept higher FPR
- If false-accept (accepting an OOD input as in-distribution) is expensive (e.g., autonomous-vehicle perception where a novel obstacle must trigger fallback) → low FPR, accept lower TPR
- Document the cost trade-off and the chosen operating point

### Step 8: Report

- Per-OOD-set metric table with CIs
- ROC curve overlay (id vs near-OOD, id vs far-OOD)
- Chosen threshold + expected (TPR, FPR) at that threshold
- In-distribution accuracy unchanged check — adding OOD detection must not degrade closed-world accuracy

## Outputs

A markdown report with:

1. **Detector identity** — method, backbone, OOD sets used
2. **Metric table** per OOD set (near, far): AUROC, AUPR-out, FPR@95TPR, with 95% CIs
3. **ROC curves** (id vs near, id vs far)
4. **Chosen threshold** + operating point + cost rationale
5. **Sanity check** — in-distribution accuracy unchanged with detection enabled
6. **Limitations** — explicit note on what classes of OOD were NOT tested; if only synthetic OOD was used, flag that real-world OOD distribution may differ

## Failure modes

- **Far-OOD-only evaluation** — testing only on a different-domain OOD set, getting AUROC 0.99, declaring victory. The near-OOD threat is the real one. Caught by: Step 3 requires near-OOD.
- **Method-overfitting to OOD set** — ODIN's hyperparameters tuned on the same OOD set used for evaluation (classic leakage). Caught by: split OOD into a tuning set and a test set, or use defaults.
- **MSP baseline trap** — using MSP as the only method; weak and well-known to fail on confident-incorrect outputs. Default to energy score.
- **Bootstrap-on-OOD only** — bootstrapping only the in-distribution side; ignores OOD sample variance. Caught by: Step 6 resamples both sides.
- **In-distribution accuracy drift** — adding a softmax temperature change for ODIN and forgetting it also affects normal predictions. Caught by: Step 8 unchanged-accuracy check.
- **Threshold drift in production** — picking τ on the held-out set and never recalibrating as deployment population shifts. Recommend `monitoring-data-drift` for runtime monitoring.
- **Calling drift "OOD"** — gradual covariate shift on in-distribution classes is drift, not OOD. Different remediation (retraining vs rejection). Caught by: Step 1 framing.

## References

- `reference/method-selection-table.md` — backbone-change / compute / strength per method
- `reference/near-vs-far-ood.md` — what counts as near-OOD vs far-OOD with worked examples
- [Hendrycks & Gimpel 2017 — A Baseline for Detecting Misclassified and OOD Examples (MSP)](https://arxiv.org/abs/1610.02136)
- [Liu et al. 2020 — Energy-based OOD Detection](https://arxiv.org/abs/2010.03759)
- [Lee et al. 2018 — Mahalanobis-distance-based OOD](https://arxiv.org/abs/1807.03888)
- [OpenOOD benchmark](https://github.com/Jingkang50/OpenOOD)

## Examples

### Example 1: 10-class ImageNet subset, near + far OOD (happy-path)

Input: ResNet-50 trained on 10 ImageNet classes. Near-OOD = 10 other ImageNet classes. Far-OOD = CIFAR-100 resized.

Output: Method = energy score (chosen for retrofit). id_test n=2000, ood_near n=2000, ood_far n=2000. Energy AUROC near-OOD: 0.82 [0.80, 0.84]. AUROC far-OOD: 0.99 [0.985, 0.995]. FPR@95TPR near-OOD: 0.38 — meaning at 95% in-distribution recall, 38% of near-OOD inputs are falsely accepted. Recommendation: 0.82 near-OOD AUROC is moderate; if the cost trade-off favors low false-accept, lower the TPR target (say 0.80) to drop FPR to ~0.15; alternatively, switch to Mahalanobis-on-features for likely improvement on near-OOD. In-distribution accuracy unchanged at 91.4%. Report explicitly flags that real-world novel classes may not match the near-OOD distribution used here.

### Example 2: ODIN with hyperparameters tuned on test OOD (edge-case)

Input: User trained ODIN; chose temperature + input perturbation by maximizing AUROC on the same OOD set they now want to evaluate on.

Output: Skill flags hyperparameter leakage. AUROC on the tuning-equals-test set is optimistically biased. Recommends: (a) split the OOD set into ODIN-tune and ODIN-test halves, retune on the tune half, evaluate on test half; OR (b) use defaults T=1000, perturbation 0.0014 from the ODIN paper; OR (c) switch to a method without OOD-set hyperparameters (energy, Mahalanobis with class-conditional cov). Report the leakage-corrected AUROC alongside the original number.

### Example 3: Closed-world tabular classifier (anti-trigger)

Input: "I have a 5-class tabular fraud classifier deployed on a fixed schema. Help me add OOD detection."

Output: Skill asks if the deployment is genuinely open-world (novel schemas, novel fraud types, schema drift?). If user confirms the schema is fixed and every record maps to a known class (perhaps with an "unknown" class trained in), recommends NOT adding an OOD layer — recommends instead: (a) training a 6th "unknown" class if rejection is a real outcome, OR (b) adding a confidence-threshold abstain mechanism for low-margin predictions, OR (c) data-drift monitoring (`monitoring-data-drift`) for population shift. Hand-off rather than forcing OOD methods that assume open-world novelty.

## See also

- `ml-datasci/monitoring-data-drift` — for population-shift detection over time (not per-input)
- `ml-datasci/monitoring-prediction-drift` — for output-distribution monitoring
- `ml-datasci/auditing-deep-learning-overfit` — for diagnosing why in-distribution accuracy is poor (different problem)
- `ml-datasci/tuning-classification-threshold` — for cost-aware threshold choice
- `ml-datasci/building-conformal-prediction-set` — for distribution-free uncertainty (planned, complementary)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
