# OOD method selection table

| Method | Backbone change | Train-time cost | Inference cost | Hyperparameters | Strength on far-OOD | Strength on near-OOD | Best for |
|---|---|---|---|---|---|---|---|
| MSP (max softmax probability) | None | None | Free | None | Moderate | Weak | Baseline only |
| Energy score | None | None | Free | None (or temperature T) | Strong | Moderate | Default retrofit |
| ODIN | None at train; temperature + input perturbation at deploy | None | Moderate (per-input perturbation) | T, ε (sensitive) | Strong | Moderate-strong | When ODIN hyperparams can be tuned on held-out OOD without leakage |
| Mahalanobis (penultimate features) | None at train; class-conditional cov estimation at deploy | None | Moderate (matrix mult per input) | None | Strong | Strong | When penultimate features are accessible |
| KNN distance | None at train; index at deploy | None | High (kNN per input) | k | Strong | Strong | When inference cost is acceptable |
| Outlier exposure | YES (loss term) | Higher train cost (need OOD samples at train) | Free | OE weight | Strongest | Strongest | When labeled OOD samples are available at train time |
| Generative model density | Separate generative model | High | High | Model arch | Variable | Variable | Research / specialized; high engineering cost |

## Defaults

For most teams retrofitting OOD detection to an already-deployed softmax classifier:

1. Try **energy score** first — zero train cost, zero inference overhead, well-documented improvement over MSP
2. If you can extract penultimate features, try **Mahalanobis** — often significantly stronger on near-OOD
3. ODIN is fine but the hyperparameter sensitivity is a footgun; if you tune T and ε on the same OOD set you evaluate on, you have leakage

## Don't

- Don't use MSP and stop. It is well-known to fail in "confidently wrong" cases.
- Don't pick a method by its far-OOD AUROC. The near-OOD case is the realistic deployment threat.
- Don't tune ODIN's hyperparameters on the OOD test set. Use defaults from the paper, or split into tune + test.
