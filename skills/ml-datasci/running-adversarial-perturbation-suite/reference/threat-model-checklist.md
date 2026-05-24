# Threat-Model Declaration Checklist

A robustness number without a threat model is unfalsifiable marketing. Fill every field before any attack runs.

## Required fields

| Field | Example | Notes |
|---|---|---|
| Norm | `Linf` | One of: `Linf`, `L2`, `L0`. State which. |
| Epsilon (value) | `0.0314` | Numeric value in the same units as the input. |
| Epsilon (units) | `[0,1]-scaled pixel intensity (= 8/255)` | The units MUST be stated. `ε = 0.03` alone is not a threat model. |
| Attacker access | `white-box` | One of: `white-box` (full model + weights + gradients), `gray-box` (architecture + outputs, no weights), `black-box` (query-only outputs), `decision-only` (predicted label only). |
| Goal | `untargeted` | `untargeted` (any misclassification) or `targeted` (force a specific class). If targeted, name the target class or targeting strategy (e.g., least-likely class, next-most-likely, fixed class). |
| Attack family | `FGSM, PGD-20, AutoAttack-standard` | Explicit list of attacks. |
| Sample subset | `1000 stratified test samples, seed 42` | Which subset of the held-out test set was attacked. NOT training data. |
| Clean accuracy on subset | `94.1%` | Measured on the SAME subset to be attacked. Use as the denominator. |
| Model eval mode | `model.training == False asserted` | Required for BatchNorm / Dropout determinism. |

## Common epsilon conventions

Vision (image classification):

- `Linf, epsilon = 8/255 = 0.0314` (CIFAR-10 / ImageNet weak adversary) — the most common benchmark
- `Linf, epsilon = 4/255 = 0.0157` (stricter)
- `Linf, epsilon = 16/255 = 0.0627` (looser; perturbation visually noticeable)
- `L2, epsilon = 0.5` (CIFAR-10) / `L2, epsilon = 3.0` (ImageNet)

Tabular (always domain-dependent):

- Continuous features standardized to N(0,1) → `Linf, epsilon = 0.1` means 0.1 SD per feature
- Money-denominated features: epsilon stated in the natural unit (e.g., `Linf, epsilon = $50`)
- One-hot categoricals: must use feasibility constraints (no continuous ε meaningful)

## Common errors

- Stating `ε = 8` instead of `ε = 8/255` — off by factor of 255, makes the model look infinitely robust
- Comparing robust accuracy across papers with different ε without normalizing
- Reporting Linf-PGD robust accuracy and calling it "robust" — say nothing about L2 or L0 attacks
- Reporting white-box robust accuracy and calling it the worst case — adaptive attacks against the specific model can be stronger
