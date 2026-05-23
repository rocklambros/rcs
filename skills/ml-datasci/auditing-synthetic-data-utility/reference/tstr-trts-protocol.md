# TSTR / TRTS / TRTR / TSTS Protocol

The four-cell utility evaluation matrix for synthetic tabular data. Each cell trains a downstream model on one source and tests on another.

|                  | Test on REAL       | Test on SYNTH      |
|------------------|--------------------|--------------------|
| **Train on REAL**  | TRTR (baseline)   | TRTS (sanity)      |
| **Train on SYNTH** | TSTR (the answer) | TSTS (over-fit risk) |

## Reading the cells

- **TRTR** — what your model would score in production today, no SDG involved. Upper bound on TSTR in expectation.
- **TSTR** — the synth-data utility number that decides downstream-task fidelity. The headline answer.
- **TRTS** — diagnostic. If TRTS ≫ TRTR, synth is over-smoothed (easier than real); if TRTS ≪ TRTR, synth is over-noised. Either signals SDG miscalibration.
- **TSTS** — train and test on synth. Always optimistic; meaningless as a utility claim. Useful only as a regression check across SDG runs.

## Required splits

Before fitting the SDG:

```python
real_train, real_test = train_test_split(real, test_size=0.2, stratify=real[target_col], random_state=42)
```

The SDG sees `real_train` only. `real_test` is the privileged held-out set that drives both TRTR and TSTR.

If the SDG was already fit on the full real set, partition retrospectively but acknowledge the leakage risk (TRTR will be inflated because the SDG indirectly saw real_test through its training).

## Recipe

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import numpy as np

X_real_train, y_real_train = real_train.drop(columns=[target]), real_train[target]
X_real_test,  y_real_test  = real_test.drop(columns=[target]),  real_test[target]
X_synth,      y_synth      = synth.drop(columns=[target]),      synth[target]

models = {"logistic": LogisticRegression(max_iter=1000), "rf": RandomForestClassifier(n_estimators=200)}
results = {}

for name, model in models.items():
    # TRTR
    m = clone(model).fit(X_real_train, y_real_train)
    trtr = roc_auc_score(y_real_test, m.predict_proba(X_real_test)[:, 1])
    # TSTR
    m = clone(model).fit(X_synth, y_synth)
    tstr = roc_auc_score(y_real_test, m.predict_proba(X_real_test)[:, 1])
    # TRTS
    m = clone(model).fit(X_real_train, y_real_train)
    trts = roc_auc_score(y_synth, m.predict_proba(X_synth)[:, 1])
    # TSTS
    m = clone(model).fit(X_synth, y_synth)
    tsts = roc_auc_score(y_synth, m.predict_proba(X_synth)[:, 1])
    results[name] = dict(trtr=trtr, tstr=tstr, trts=trts, tsts=tsts)
```

## Bootstrap 95% CI on the utility ratio

Resample `real_test` (with replacement) `n_bootstrap` times. Hold `real_train` and `synth` fixed. Recompute TSTR and TRTR per resample; record `tstr / trtr`. Report the 2.5th and 97.5th percentiles.

For ROC-AUC, normalize against chance: `ratio = (tstr - 0.5) / (trtr - 0.5)` to avoid inflated ratios near chance.

## Multiple model families

Run at least two model families (linear + tree). Reasons:

- CTGAN-generated data often favors trees over logistic regression because mode-specific normalization preserves multi-modal feature distributions
- TVAE-generated data often favors linear models because of smoother latent space
- A single-family TSTR can hide family-specific failure; reporting both prevents over-confident certification

## When to use which task metric

| Task type | TRTR / TSTR metric | Notes |
|---|---|---|
| Binary classification | ROC-AUC | Normalize against 0.5 chance floor |
| Multi-class classification | Macro-F1 | Lead with macro if every class matters; weighted if traffic-mix matters |
| Regression | RMSE in target units | Report ratio as `TRTR_rmse / TSTR_rmse` (inverted; higher is better synth) |
| Survival / time-to-event | C-index | Same direction as ROC-AUC; normalize against 0.5 |
