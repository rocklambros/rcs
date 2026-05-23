# Shadow-Model Membership Inference Attack (MIA) for Tabular SDG

The empirical privacy gold standard for synthetic tabular data. Adapted from Shokri et al. 2017 (originally on classifiers) for SDG outputs per Hyeong et al. 2022.

## Threat model

Adversary holds:
- A row `x` (a candidate real-train member)
- Black-box access to the released synth set `S`
- Optional auxiliary knowledge: schema, marginal distributions, sample from the same population

Adversary asks: "was `x` in the SDG's training set?"

If MIA AUC ≫ 0.5, the synth set carries a membership signal — an attacker can probabilistically identify training members. For PHI / PII / financial data, this is a HIPAA / GDPR violation surface.

## Shadow model recipe

Setup:

- Real data partitioned into `K` disjoint, equal-size splits `R_1, ..., R_K` (default `K = 5`)
- One held-out `R_test` (disjoint from all `R_i`) for attack-classifier scoring

Per-shadow procedure:

```python
for i in 1..K:
    # Fit shadow generator on R_i
    G_i = sdg_handle.refit(R_i)
    # Generate shadow synth from G_i
    S_i = G_i.sample(n=len(R_i))
    # Build per-shadow attack dataset
    # member = 1 for rows in R_i (the SDG saw them)
    # member = 0 for rows in R_test (the SDG did not see them, same distribution)
    train_attack_dataset.extend(
        rows=R_i, member=1, synth_features=summarize(S_i, row)
    )
    train_attack_dataset.extend(
        rows=R_test_subsample, member=0, synth_features=summarize(S_i, row)
    )
```

`summarize(S, row)` is a feature extractor — distance to nearest synth row, count of synth rows within ε, density of synth in row's neighborhood, etc.

Train attack classifier:

```python
attack_clf = RandomForestClassifier(n_estimators=200).fit(
    X=train_attack_dataset.synth_features,
    y=train_attack_dataset.member
)
```

Apply to the real SDG:

```python
# For each candidate (a real_train row + a real_holdout row):
synth_features_train = summarize(synth, real_train_row)
synth_features_holdout = summarize(synth, real_holdout_row)
score_train   = attack_clf.predict_proba(synth_features_train)[1]
score_holdout = attack_clf.predict_proba(synth_features_holdout)[1]
# MIA AUC: how well does score separate train members from holdout?
mia_auc = roc_auc_score(
    y_true=[1] * n_train + [0] * n_holdout,
    y_score=np.concatenate([scores_train, scores_holdout])
)
```

## MIA AUC interpretation

| MIA AUC + 95% CI | Reading |
|---|---|
| AUC ≈ 0.50, CI ⊆ [0.45, 0.55] | No empirical membership signal |
| AUC in [0.55, 0.60], CI lower ≤ 0.52 | Borderline; CI dominated by noise; tighten with more shadows |
| AUC in [0.55, 0.60], CI lower > 0.52 | Borderline-leak; consider DP re-fit before publishing under sensitive-data class |
| AUC ≥ 0.60 | Clear empirical leak; do not release without DP guarantees |
| AUC ≥ 0.70 | Severe; SDG has memorized; reject and re-fit |

## Cost notes

Shadow MIA cost = `K × (SDG fit + SDG sample + attack feature extraction)`. For `K = 5` and a CTGAN on 50k rows, expect ~1-3 hours on CPU. Reduce `K` to 3 for quick first-pass screening; increase to 10-20 for tight CI on publish decisions.

## Feature extractor choices

`summarize(synth, row)` candidates, in increasing cost / power:

1. **Distance to nearest synth row** — cheapest; misses neighborhood effects
2. **Count of synth rows within ε** — captures local density
3. **Average of k-nearest synth rows in each feature** — captures conditional structure
4. **Kernel density estimate at the row** — captures smooth structure but expensive
5. **Conditional likelihood under a non-parametric synth model** — most powerful; expensive

Start with (1) and (2) for any audit; add (3) for borderline cases.

## Alternatives when SDG handle is unavailable

If the SDG cannot be re-fit (e.g. pre-built synth dataset shipped without the generator):

- Stage 1 (exact duplicates) + Stage 2 (near duplicates) + Stage 3 (DCR) + Stage 4 (NNDR) remain available
- Stage 5 shadow MIA is unavailable; verdict is upper-bounded by the conservative reading of Stages 1-4
- Report the missing-MIA fact in the verdict and reduce confidence accordingly
