# Per-data-shape split cookbook

One card per data shape. Use this after the SKILL.md decision tree identifies the data shape.

## Tabular IID (independent rows; classification or regression)

**Recommended splitter:**

```python
from sklearn.model_selection import train_test_split

# Classification
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y,        # for classification, especially imbalanced
)

# Regression with skewed target
import pandas as pd
y_bin = pd.qcut(y, q=10, duplicates="drop")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y_bin
)
```

**For cross-validation:**

```python
from sklearn.model_selection import StratifiedKFold, KFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)   # classification
kf = KFold(n_splits=5, shuffle=True, random_state=42)              # regression
```

**Common pitfalls:**

- Forgetting `stratify=y` on imbalanced data
- Using `train_test_split` when rows are NOT IID (e.g., grouped, time-indexed)

## Tabular grouped (multiple rows per group: patient, user, customer, session)

**Recommended splitter:**

```python
from sklearn.model_selection import GroupShuffleSplit, GroupKFold

# Single random split
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=patient_id))

# Cross-validation
gkf = GroupKFold(n_splits=5)
for train_idx, test_idx in gkf.split(X, y, groups=patient_id):
    ...
```

**For stratified + grouped (sklearn ≥ 1.0):**

```python
from sklearn.model_selection import StratifiedGroupKFold
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, test_idx in sgkf.split(X, y, groups=patient_id):
    ...
```

**Common pitfalls:**

- Splitting at the row level when the unit of generalization is the group (most common in healthcare ML)
- Using `KFold` or `StratifiedKFold` without `groups=`
- Forgetting that `GroupKFold` does NOT shuffle by default

## Time-series (single series, time-indexed)

**Recommended splitter:**

```python
from sklearn.model_selection import TimeSeriesSplit

# Expanding window (default)
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    ...   # test is always the future of train

# With gap to prevent label leakage at the boundary
tscv = TimeSeriesSplit(n_splits=5, gap=7)   # 7-step gap between train and test
```

**Manual single-cutoff split:**

```python
cutoff = "2024-01-01"
train = df[df["date"] < cutoff]
test = df[df["date"] >= cutoff]
```

**Walk-forward / rolling-origin:**

```python
window_size = 365
horizon = 7
for start in range(0, len(df) - window_size - horizon, horizon):
    train = df.iloc[start : start + window_size]
    test = df.iloc[start + window_size : start + window_size + horizon]
    ...
```

**Common pitfalls:**

- `shuffle=True` in `train_test_split` on time-series data (leaks future into train)
- Building lag features AFTER the split — must be built carefully to avoid using future values for past targets
- Forgetting the `gap` parameter when the target has a forward-looking dependency (e.g., predicting next-week churn)

## Panel data (grouped AND time-indexed, e.g., per-patient per-visit over time)

**Recommended splitter:** no built-in sklearn class; combine group-awareness with temporal ordering.

```python
import pandas as pd

# Sort by time within each group
df = df.sort_values(["patient_id", "visit_date"])

# Last-visit-out per patient
def last_visit_holdout(df, group_col="patient_id"):
    grouped = df.groupby(group_col)
    test_idx = grouped.tail(1).index
    train_idx = df.index.difference(test_idx)
    return df.loc[train_idx], df.loc[test_idx]

# Or: global date cutoff that also respects group time order
cutoff = "2024-01-01"
train = df[df["visit_date"] < cutoff]
test = df[df["visit_date"] >= cutoff]
```

**Common pitfalls:**

- Treating panel data as IID (worst case: leaks both group AND time)
- Treating panel data as pure time-series (ignores within-patient autocorrelation)

## Text (document classification, NER, etc.)

**Recommended splitter:** start with grouped (by document) if multiple rows per document.

```python
from sklearn.model_selection import GroupShuffleSplit

# If rows are sentences and a document has multiple sentences
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=document_id))
```

**For LLM-era eval sets:** also de-duplicate against any pretraining corpus (or use a hold-out set known to be post-cutoff).

**Common pitfalls:**

- Splitting sentences when the unit of generalization is the document
- Near-duplicate documents across train/test (paraphrases, translations) — run minhash or embedding-based dedup first
- Test-set contamination by pretraining data (LLM era)

## Image (classification, detection, segmentation)

**Recommended splitter:** group by source (subject, session, camera) if applicable.

```python
from sklearn.model_selection import GroupShuffleSplit

# E.g., multiple images per subject in a face dataset
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=subject_id))
```

**Common pitfalls:**

- Splitting frames when the unit is the video (most common in surveillance / endoscopy)
- Augmenting BEFORE splitting (augmented copies leak between train and test)
- Splitting by image when subjects appear in multiple images

## Multi-source / crosswalking (TRACT-style; one source per crosswalk node)

**Recommended splitter:** leave-one-source-out (LOFO) cross-validation.

```python
import numpy as np

sources = df["source"].unique()
for held_out_source in sources:
    train = df[df["source"] != held_out_source]
    test = df[df["source"] == held_out_source]
    ...   # fit on train, score on test (one whole source held out)
```

**Hub-firewall:** when one source acts as a "hub" connecting others (e.g., NIST 800-53 in a CIS-ENISA-NIST crosswalk), exclude that source from the training representation when scoring on a non-hub held-out source. Prevents the model from learning hub-specific phrasing and propagating it as universal.

**Common pitfalls:**

- Standard k-fold across sources (model memorizes source-specific quirks)
- Including the hub when validating on a connected leaf
- Reporting in-source accuracy as if it were generalization

## Summary table

| Data shape | Splitter | Key argument |
|---|---|---|
| Tabular IID, balanced | `train_test_split` | `random_state` |
| Tabular IID, imbalanced | `train_test_split` | `stratify=y` |
| Tabular grouped | `GroupShuffleSplit` / `GroupKFold` | `groups=...` |
| Tabular grouped + imbalanced | `StratifiedGroupKFold` | `groups=...` |
| Time-series | `TimeSeriesSplit` | `n_splits=5`, optionally `gap=` |
| Panel (group + time) | manual (last-visit-out or date cutoff) | `group_col`, `time_col` |
| Text (multi-row per doc) | `GroupShuffleSplit` | `groups=document_id` |
| Image (multi-image per subject) | `GroupShuffleSplit` | `groups=subject_id` |
| Multi-source crosswalk | LOFO (manual) | iterate over sources |
