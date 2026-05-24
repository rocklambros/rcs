# Adversarial-Robustness Report Template

```markdown
# Adversarial Robustness Report — <model name> @ <commit / version>

## Threat model

- **Norm:** Linf
- **Epsilon:** 8/255 ≈ 0.0314 ([0,1]-scaled pixel intensity)
- **Attacker access:** white-box (model weights + gradients)
- **Goal:** untargeted (any misclassification counts)
- **Attacks:** FGSM, PGD-20, AutoAttack-standard
- **Sample subset:** 1000 stratified test samples (seed = 42)
- **Model eval mode:** `model.training == False` (asserted)

## Clean accuracy on attacked subset

- 94.1% (mean across 1000 samples, denominator for all robust-accuracy numbers below)

## Per-attack robust accuracy

| Attack | Hyperparameters | Robust accuracy | Attack success rate | Wall-clock | 95% bootstrap CI |
|---|---|---|---|---|---|
| FGSM | one step, ε = 8/255 | 31.2% | 67.0% | 3 s | [28.5, 33.9] |
| PGD-20 | 20 iter, α = ε/4, random start | 12.4% | 86.8% | 41 s | [10.4, 14.7] |
| AutoAttack-standard | APGD-CE + APGD-DLR + FAB + Square | 9.8% | 89.5% | 11 min | [7.9, 11.9] |

## Attack-strength monotone check

PASS — `AutoAttack (9.8) ≤ PGD-20 (12.4) ≤ FGSM (31.2)`. Stronger attacks find more adversarial examples, as expected. No gradient-masking signature detected.

## Saved adversarial examples

- 32 examples per attack saved under `examples/<attack>/`
- Visual inspection: perturbations are imperceptible to the human eye at ε = 8/255 (consistent with the literature)

## Tabular feasibility filter

Not applicable (vision model).

## Caveats — what this report does NOT measure

- **Different ε:** numbers do not generalize to ε = 4/255 (likely lower robustness) or ε = 16/255 (likely lower still). Re-run for any new budget.
- **Different norm:** L-infinity robustness does not imply L2 or L0 robustness. Different attack families operate in different metric spaces.
- **Adaptive attacks:** a defender-specific adaptive attack designed against this exact model's architecture and training may achieve lower robust accuracy. The AutoAttack number is an upper bound on robust accuracy under the standard attack family, not a worst-case bound.
- **Certified robustness:** this report is empirical, not certified. Randomized smoothing + interval-bound propagation produce certified numbers, typically much lower than empirical.
- **Distribution shift:** robustness numbers are conditional on the test set's data distribution. Out-of-distribution inputs (e.g., new lighting conditions, new camera) may be more brittle.

## Recommendation

The model is **not robust** at ε = 8/255 under L-infinity (AutoAttack robust accuracy = 9.8%). If deployment requires robustness to this budget, options include:

1. Adversarial training (Madry et al. 2018) — typically reduces clean accuracy by 5-15 points but raises robust accuracy substantially
2. Randomized smoothing for certified robustness (Cohen et al. 2019)
3. Defensive distillation, input preprocessing — historically less effective; verify against AutoAttack before relying on them
```
