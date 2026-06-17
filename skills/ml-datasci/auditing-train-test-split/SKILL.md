---
name: auditing-train-test-split
description: >
  Audits a train / test / validation split for leakage, stratification,
  group-aware violations, and temporal-order violations. Use when the user
  creates a train/test split, when classifier accuracy looks suspiciously
  high, when the same ID could appear in both train and test, when
  time-series data is split randomly instead of by date, or when group-aware
  data (multiple rows per patient / user / customer) is split row-wise.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer]
evidence:
  - DU-MSDSAI-4432-Final
  - TRACT
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Auditing a Train/Test Split

## When to use

Trigger this skill when the user asks for or implies one of:

- "Audit my train/test split" or "did I split this correctly?"
- Just used `train_test_split(...)`, `KFold(...)`, or `StratifiedKFold(...)` and wants validation
- Classifier accuracy / AUC looks suspiciously high (≥ 0.99 on a non-trivial problem; near-perfect generalization on the first try)
- Data has a "group" column (patient_id, user_id, customer_id, session_id) and was split at the row level
- Data is a time series (sales, sensor readings, daily counts) and was split randomly
- Imputation, normalization, or feature engineering was done BEFORE the split
- Phrases like "is there leakage?", "why is my AUC so high?", "should I stratify?", "is this group-aware?"

## When NOT to use

Skip this skill and hand off when:

- The user is doing **unsupervised** learning (k-means, hierarchical, GMM) — there is no held-out test set in the supervised sense; validation is by cluster stability (bootstrap silhouette, gap statistic, ARI under perturbation)
- The user is using **bootstrap / cross-validation** that already accounts for leakage at the resampling layer (e.g., grouped CV, blocked time-series CV) and is asking a different question
- The user is doing **Bayesian** model evaluation (PSIS-LOO, WAIC) — different validation framework
- The user is asking about hyperparameter tuning leakage between dev and test specifically — narrower question; mention but do not run full split audit

## Quick start

User says: "I'm building a classifier on hospital readmission. Each row is one visit; some patients have multiple visits. I used `train_test_split(X, y, test_size=0.2, random_state=42)`. Audit it."

Skill response: walks the four-check audit (leakage / stratification / group-awareness / temporal), flags **group-leakage** (same patient_id can land in both train and test), recommends `GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42).split(X, y, groups=patient_id)`, and explains why row-level random split overestimates generalization for visit-level data.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| split_method | string | yes | — | The exact splitter the user used (e.g., `train_test_split`, `KFold`, `StratifiedKFold`, `TimeSeriesSplit`). |
| data_shape | "tabular-iid" \| "tabular-grouped" \| "time-series" \| "panel" \| "text" \| "image" | yes | — | Structure of the data. Drives which split is appropriate. |
| target_distribution | "balanced" \| "imbalanced" \| "regression" | no | — | If classification, balance status drives the stratification recommendation. |
| group_column | string or null | required if data_shape is tabular-grouped or panel | — | The column identifying the group (patient_id, user_id, etc.). |
| time_column | string or null | required if data_shape is time-series or panel | — | The column identifying the time index. |
| preprocessing_order | string | no | — | Did the user fit imputation / normalization on the **full** dataset before splitting? If so, that's leakage. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check items off as each check completes:

```
Split-audit progress:
- [ ] Check 1: Leakage — same ID in train+test? feature derived from target? preprocessing fit on full data?
- [ ] Check 2: Stratification — for imbalanced classification, was stratify=y used?
- [ ] Check 3: Group-awareness — multiple rows per group → GroupShuffleSplit / GroupKFold?
- [ ] Check 4: Temporal order — time-series data → split by date, not random?
- [ ] Verdict: which check(s) failed; corrected split recommendation
```

### Check 1: Leakage

Three flavors of leakage to look for:

1. **Identifier leakage** — the same group (patient_id, user_id) has rows in both train and test. Generalization estimate becomes "can the model recognize this specific patient?" instead of "can it predict for a new patient?"
2. **Target leakage** — a feature in X is derived from or computed using the target y. Classic examples: a "patient_outcome_severity_score" that was assigned after the outcome was known; a "claim_was_fraudulent_flag" that's a downstream label propagation.
3. **Preprocessing leakage** — imputation mean / median, standardization mean+std, or any other statistic fit on the FULL dataset before the train/test split. The test set has informed the imputation / scaling.

**Rule for preprocessing:** fit on TRAIN, transform on TEST. Use sklearn `Pipeline` or `ColumnTransformer` inside cross-validation to make this automatic.

### Check 2: Stratification

For classification with an **imbalanced** target (e.g., 5% positive class), a random split can produce a test set with 2% positives, distorting metrics. Use `stratify=y` in `train_test_split` or `StratifiedKFold` to preserve the class proportion.

- Multi-class: stratify on the multi-class label.
- Multi-label: use `MultilabelStratifiedKFold` (from `iterative-stratification`).
- Regression: stratify on a **binned** version of y (deciles) if the distribution is highly skewed.

### Check 3: Group-awareness

If multiple rows share a group (patient with multiple visits, user with multiple sessions, customer with multiple orders), row-level random splits leak the group between train and test. The model can "recognize the patient" instead of generalizing to a new patient.

Use:

- `GroupShuffleSplit` for a single random group-aware split
- `GroupKFold` for grouped cross-validation
- `StratifiedGroupKFold` (sklearn ≥ 1.0) for stratified + grouped

If groups also have time order (e.g., visits per patient over time), consider `GroupTimeSeriesSplit` (manual; sklearn doesn't ship one).

### Check 4: Temporal order

For time-series data — daily sales, sensor readings, weekly counts, anything time-indexed — random splits LEAK future information into the training set. The model "predicts" the past from the future, which is not the deployment condition.

Use:

- `TimeSeriesSplit` (expanding window) — sklearn built-in
- Walk-forward / rolling-origin evaluation — fit on `[0, t]`, predict `[t+1, t+h]`, slide
- Manual date-based slice — train on `< 2025-01-01`, test on `>= 2025-01-01`

**LOFO discipline** (leave-one-source-out) — for crosswalking / multi-source learning, holding out one **source** at a time prevents the model from memorizing source-specific quirks (TRACT-style validation; CIS-ENISA-NIST hub-firewall pattern).

### Verdict

State explicitly:

1. Which check(s) failed
2. The corrected splitter call (the exact code line)
3. What the corrected generalization estimate is likely to look like (typically, accuracy / AUC will DROP — that's the leakage being removed, not a bug)

## Outputs

A short markdown response with:

1. **Audit summary table** — Check · Verdict · Evidence
2. **Failures highlighted** — the specific leakage / stratification / group / temporal issue
3. **Corrected splitter code** — exact line(s) the user should swap in
4. **Expected impact** — typically, "your reported accuracy will drop by X–Y points; that drop is the leakage being removed"
5. **Reporting checklist** — what to put in the methods section (splitter, stratification, group column, time cutoff)

## Failure modes

- **Reporting near-perfect accuracy without auditing** — AUC = 0.999 on a non-trivial problem is almost always leakage, not a great model. Caught by: Check 1 (target leakage) + Check 3 (group leakage) explicitly look for the most common causes.
- **Group-leakage on visit-level data** — most common in healthcare ML. Caught by: Check 3 forces the group_column question.
- **Random split on time-series** — most common in forecasting + IoT. Caught by: Check 4 makes the data_shape question gate the splitter choice.
- **Preprocessing leakage** — fitting `StandardScaler` on the full dataset before `train_test_split`. Caught by: Check 1.3 asks the preprocessing-order question explicitly.
- **Stratification omission** — random split on a 5% positive-class dataset produces a test set with random class proportions. Caught by: Check 2 requires the target_distribution question.
- **Hyperparameter tuning leakage** — selecting hyperparameters on the **test** set instead of a separate dev set. Mentioned but not in scope for the primary 4-check audit; flagged in the verdict for the user to pursue separately.

## References

- [`reference/split-cookbook.md`](reference/split-cookbook.md) — per-data-shape recommended splitter with code (tabular-iid / tabular-grouped / time-series / panel / text / image)
- [sklearn cross-validation API](https://scikit-learn.org/stable/modules/cross_validation.html) — splitter reference
- [Kapoor & Narayanan, *Leakage and the reproducibility crisis in ML-based science* (2022)](https://reproducible.cs.princeton.edu/) — taxonomy of ML leakage failures

## Examples

### Example 1: Group-leakage on visit-level data (happy-path)

Input: "I'm building a classifier on hospital readmission. Each row is one visit; some patients have multiple visits. I used `train_test_split(X, y, test_size=0.2, random_state=42)`. Audit it."

Output:

| Check | Verdict | Evidence |
|---|---|---|
| 1. Leakage | **FAIL** (group-leakage) | Same patient can appear in both train and test because the split is row-level |
| 2. Stratification | Not assessed (depends on readmission balance) | — |
| 3. Group-awareness | **FAIL** | Visit-level data needs patient-level grouping |
| 4. Temporal order | Not assessed (no time column mentioned) | — |

Corrected splitter:

```python
from sklearn.model_selection import GroupShuffleSplit
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=patient_id))
```

Expected impact: reported accuracy / AUC will drop, often substantially (visit-level leakage typically inflates accuracy by 5–20 points for visit-clustered features). The drop is the leakage being removed.

### Example 2: Random split on time-series (edge-case)

Input: "I'm forecasting demand from 5 years of weekly sales. I used `train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)`. Audit it."

Output:

| Check | Verdict | Evidence |
|---|---|---|
| 1. Leakage | **FAIL** (temporal leakage) | `shuffle=True` mixes future weeks into the training set |
| 4. Temporal order | **FAIL** | Time-series data MUST split by date |

Corrected splitter:

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    # fit on train_idx, score on test_idx (test is always future of train)
    ...
```

Or for a single train/test cutoff:

```python
cutoff_date = "2024-01-01"
train = df[df["date"] < cutoff_date]
test = df[df["date"] >= cutoff_date]
```

Expected impact: forecasting accuracy will drop, often significantly (random splits give the model "free" future information). The drop is the leakage being removed; the new number is the realistic deployment estimate.

### Example 3: Unsupervised clustering (anti-trigger)

Input: "I'm running k-means clustering on customer segments. Audit my train/test split."

Output: K-means is unsupervised. There is no labeled target, so train/test split is not the right validation paradigm. The skill explains that:

1. The audit does NOT criticize the absence of a train/test split
2. The appropriate validation is **cluster stability** — bootstrap silhouette, gap statistic, ARI under data perturbation, or held-out within-cluster cohesion
3. Train/test split is a supervised-learning concept; for unsupervised, the relevant validity check is whether the cluster structure is robust to resampling or to small perturbations of the data

Hands off to cluster-stability validation methodology.

## See also

- `ml-datasci/evaluating-binary-classifiers` — once the split is clean, evaluate properly (paired McNemar, bootstrap CI on AUC, calibration)
- `ml-datasci/auditing-data-quality` — data-side checks (duplicates, missingness, schema) that often co-occur with leakage
- `ml-datasci/deduplicating-records` — for dedup-before-split, an upstream concern (Batch 4)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
