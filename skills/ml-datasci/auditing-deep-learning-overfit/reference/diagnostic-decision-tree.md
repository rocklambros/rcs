# Overfit diagnostic decision tree

```
Start
  │
  ▼
Q1: Is train loss low (near floor) AND val loss higher than train?
  │
  ├── NO (train loss still high) ─► UNDERFIT
  │                                    Recommend: more capacity, longer training, better optimization
  │                                    Do NOT add regularization
  │
  └── YES
        │
        ▼
      Q2: Is val loss RISING across recent epochs (not just plateau)?
        │
        ├── NO (val flat at minimum) ─► PLATEAU / converged
        │                                    Recommend: lower LR / re-evaluate stopping criterion
        │
        └── YES
              │
              ▼
            Q3: Do train and val come from the same distribution?
            Check: class balance, feature stats, augmentation regime, time period, source
              │
              ├── NO (shift detected) ─► SHIFT (possibly + overfit)
              │                            Recommend: match distributions, domain-adaptation,
              │                            stratified val sampling, OR reweight loss
              │                            Regularization will NOT fix this
              │
              └── YES (no shift)
                    │
                    ▼
                  Q4: Sample 50 mis-classified val examples — how many are mislabeled?
                    │
                    ├── ≥ 5% mislabeled ─► LABEL NOISE (possibly + overfit)
                    │                          Recommend: clean val labels FIRST
                    │                          The "irreducible" val loss is partly noise floor
                    │
                    └── < 5% mislabeled
                          │
                          ▼
                        Q5: Is weight norm rising across epochs?
                          │
                          ├── YES ─► CLASSIC OVERFIT (parameter-magnitude memorization)
                          │            Remediation: early stop → augment → weight decay → dropout → less capacity → more data
                          │
                          └── NO  ─► CLASSIC OVERFIT (representational, not magnitude)
                                       Remediation: early stop → augment → dropout → less capacity → more data
                                       Weight decay less targeted here
```

## Notes on each branch

- **Underfit** is often misdiagnosed as overfit because val > train. The deciding question is whether train loss has actually reached the floor.
- **Plateau** is not overfit either; the model has converged. Recommend a lower LR or accept the current val loss as the model's capability.
- **Shift** is the most-frequently-missed cause of "overfit"-looking gaps. Always check class balance and feature stats.
- **Label noise** can floor the val loss at a non-zero value. Without cleaning, the val curve will look "stuck" no matter what regularization is added.
- **Classic overfit** can be parameter-magnitude (weight norm grows) or representational (weight norm flat but model has memorized in a different sense). The remediation differs slightly.
