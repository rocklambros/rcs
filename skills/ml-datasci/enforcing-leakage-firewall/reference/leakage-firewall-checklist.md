# Leakage firewall — four-check implementation

Run all four checks before trusting a held-out metric. Each check has a precondition; if the precondition does not apply (e.g. no group column), the check is automatically pass — record it as N/A in the report.

## Check 1: No-row-in-two-splits invariant

```python
import hashlib
import pandas as pd

def hash_row(row):
    return hashlib.sha256(str(tuple(row.values)).encode()).hexdigest()

def assert_disjoint_splits(X_train, X_val, X_test):
    train_h = set(X_train.apply(hash_row, axis=1))
    val_h = set(X_val.apply(hash_row, axis=1))
    test_h = set(X_test.apply(hash_row, axis=1))
    train_val_leak = len(train_h & val_h)
    train_test_leak = len(train_h & test_h)
    val_test_leak = len(val_h & test_h)
    assert train_val_leak == 0, f"{train_val_leak} rows leak train↔val"
    assert train_test_leak == 0, f"{train_test_leak} rows leak train↔test"
    assert val_test_leak == 0, f"{val_test_leak} rows leak val↔test"
    return {"train_val": 0, "train_test": 0, "val_test": 0}
```

Failure cause: duplicate rows survived dedup; concat-then-split picked the same row twice; a join multiplied rows that should have been collapsed.

## Check 2: Group-aware split

```python
from sklearn.model_selection import GroupShuffleSplit, GroupKFold

def split_group_aware(X, y, groups, test_size=0.2, random_state=42):
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(splitter.split(X, y, groups))
    assert len(set(groups[train_idx]) & set(groups[test_idx])) == 0, "group leak"
    return X.iloc[train_idx], X.iloc[test_idx], y.iloc[train_idx], y.iloc[test_idx]

# For CV:
def cv_group_aware(model, X, y, groups, scoring, n_splits=5):
    cv = GroupKFold(n_splits=n_splits)
    return cross_val_score(model, X, y, groups=groups, cv=cv, scoring=scoring)
```

Common group columns: `patient_id`, `user_id`, `customer_id`, `device_id`, `session_id`, `case_id`, `canonical_control_id`.

## Check 3: LOFO sweep

```python
def lofo_sweep(model_class, X_train, y_train, X_test, y_test, candidate_features,
               scoring_fn, collapse_threshold=0.20):
    """Train with all features, then with each feature removed; record drop."""
    model = model_class().fit(X_train, y_train)
    full_score = scoring_fn(y_test, model.predict_proba(X_test)[:, 1])

    drops = {}
    for feature in candidate_features:
        cols = [c for c in X_train.columns if c != feature]
        model_minus = model_class().fit(X_train[cols], y_train)
        minus_score = scoring_fn(y_test, model_minus.predict_proba(X_test[cols])[:, 1])
        drops[feature] = full_score - minus_score

    flags = {f: d for f, d in drops.items() if d > collapse_threshold * full_score}
    return {"full_score": full_score, "drops": drops, "flagged": flags}
```

For large feature sets, pre-filter via mutual information to the top 20-50 to keep the sweep tractable.

Interpretation of flagged features: target-derived (e.g. `*_at_outcome`, `*_after_event`, `score_using_label`), post-event (a feature only knowable after the prediction time), unique IDs the model memorizes, aggregates fit on full dataset before split.

## Check 4: Hub-firewall + cross-source LOFO

```python
from sklearn.model_selection import LeaveOneGroupOut

def hub_firewall(model_class, X, y, sources, scoring_fn, hub_sources):
    """For each source, hold it out; compare hub-out to random-split."""
    logo = LeaveOneGroupOut()
    results = {}
    for train_idx, test_idx in logo.split(X, y, groups=sources):
        held = sources[test_idx[0]]
        model = model_class().fit(X.iloc[train_idx], y.iloc[train_idx])
        score = scoring_fn(y.iloc[test_idx], model.predict_proba(X.iloc[test_idx])[:, 1])
        results[held] = score

    hub_scores = {s: results[s] for s in hub_sources if s in results}
    non_hub_min = min(s for src, s in results.items() if src not in hub_sources)
    return {"per_source": results, "hub_scores": hub_scores, "non_hub_worst": non_hub_min}
```

Flag if `random_split_score - hub_score > 0.10` (model leans on the hub source).
Flag if `non_hub_worst < 0.5 + small_margin` (chance-level on the worst non-hub source — no generalization).

## Report template

```
Leakage firewall report
=======================
Check 1 (no-row-in-two-splits): <pass | fail (N collisions)>
Check 2 (group-aware split): <pass | N/A | fail (N group overlaps)>
Check 3 (LOFO sweep):
  full score: <metric>
  flagged features: <feature_name (drop = X.XX)>
  ...
Check 4 (hub-firewall):
  random split: <metric>
  per-source held-out: <{source: metric, ...}>
  hub-held-out: <metric>
  gap: <random - hub>
  verdict: <pass | fail>

Overall verdict: <pass | conditional | fail>
Deployment recommendation: <ship | ship-with-caveats | block>
```
