---
name: enforcing-leakage-firewall
description: >
  Defends a supervised pipeline against four leakage classes ordinary
  train-test-split audits miss: (1) LOFO sweep that surfaces a feature whose
  removal collapses test performance (target-encoding / post-event signature);
  (2) hub-firewall isolation for crosswalk / multi-source data where one "hub"
  source connects others and its representation leaks to held-out sources;
  (3) group-aware splitting (GroupKFold, GroupShuffleSplit, leave-one-group-out)
  so multi-row-per-entity data (patient visits, user sessions, customer orders)
  does not put the same entity in train and test; (4) no-row-in-two-splits
  invariant via row-hash check after split. Triggers when fitting on
  multi-source data, when test metrics seem suspiciously high, when the dataset
  has group structure, or after any join / merge step. Skips clean IID
  single-source data with one row per entity.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
evidence:
  - ai-security-framework-crosswalk
  - TRACT
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
last-updated: 2026-05-23
---

# Enforcing Leakage Firewall

## When to use

Trigger this skill when:

- The dataset is assembled from multiple sources (crosswalk, integration, merge of registries) and a model will be evaluated for cross-source generalization
- The data has natural group structure: multiple visits per patient, multiple sessions per user, multiple orders per customer, multiple measurements per device
- A held-out test metric looks suspiciously high (test ROC-AUC > 0.95 on a hard problem, test accuracy > 0.99 on imbalanced data, train/test gap is near zero on a noisy domain) — a leakage smell
- After any `join`, `merge`, `concat`, or `groupby` step that touches feature columns
- The model is being deployed to make predictions on a held-out source / population / time period that does NOT exist in the training data
- Keywords: leakage, leak, group-aware, GroupKFold, LOFO, leave-one-feature-out, hub source, crosswalk, multi-source, patient ID, user ID

## When NOT to use

Skip this skill and hand off when:

- The dataset is genuinely clean IID single-source with one row per entity, simple features, and a standard random train/test/val split → use `ml-datasci/auditing-train-test-split` for the standard leakage checks (overlap on ID, target-derived features, leak via global preprocessing fit on full dataset)
- The data is time series → temporal leakage is the dominant concern; use `ml-datasci/auditing-train-test-split` (it covers temporal split discipline) — temporal leakage is in scope of that sibling skill
- The user wants a model-architecture choice (deep vs simple) → use `ml-datasci/running-chollet-ratio-check` (for text) or `ml-datasci/building-baseline-models` (for tabular)
- The request is pure pedagogy on what leakage means without a real pipeline — explain the concept and do not force the workflow

## Quick start

User: "I built a classifier on a crosswalk dataset that pulls from NIST, MITRE, OWASP, and ENISA framework controls. Train ROC-AUC 0.94, test ROC-AUC 0.91. Should I trust it?"

Response: this is a multi-source crosswalk — the standard leakage firewall applies. Run all four checks (LOFO, hub-firewall, group-aware split if any control_id repeats across sources, no-row-in-two-splits via hash dedup). The 0.91 test AUC is suspect until those checks pass. NIST is the dominant "hub" source in most crosswalks, so leave-NIST-out cross-validation is the load-bearing diagnostic.

```python
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
import numpy as np
import hashlib

# Group-aware: source is the group; LOFO over sources tests cross-source generalization
logo = LeaveOneGroupOut()
for train_idx, test_idx in logo.split(X, y, groups=source_labels):
    held_out_source = source_labels[test_idx][0]
    model.fit(X[train_idx], y[train_idx])
    auc_holdout = roc_auc_score(y[test_idx], model.predict_proba(X[test_idx])[:, 1])
    print(f"holdout={held_out_source}: AUC={auc_holdout:.3f}")
```

See `reference/leakage-firewall-checklist.md` for the full four-check workflow.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `X` | DataFrame or array | yes | — | Feature matrix. Must include any group / source / entity ID columns referenced by `group_col` and `source_col`. |
| `y` | array-like | yes | — | Target labels. |
| `group_col` | str | conditional | — | Required when the dataset has multi-row-per-entity structure. Column name holding `patient_id`, `user_id`, `customer_id`, etc. |
| `source_col` | str | conditional | — | Required when the dataset is multi-source (crosswalk, merged registries). Column name holding `source`, `framework`, `vendor`, etc. |
| `hub_sources` | list of str | conditional | — | Sources that act as connecting hubs (NIST in security-control crosswalks; ICD-10 in medical-code mappings). Triggers the hub-firewall check. |
| `lofo_features` | list of str | no | all numeric features | Features to test with leave-one-feature-out. Defaults to all numeric features; for large feature sets, pre-filter via mutual information to the top 20-50. |
| `lofo_collapse_threshold` | float | no | `0.20` | Drop in test AUC (or chosen metric) when a single feature is removed that triggers a leakage flag. Default 0.20 = 20% relative drop. |
| `cv_folds` | int | no | `5` | Cross-validation folds for group-aware splits. |

## Workflow

```
Leakage firewall progress:
- [ ] 0. Sanity check — confirm group / source / hub columns exist and are populated
- [ ] 1. No-row-in-two-splits invariant — hash every (X, y) row before split; verify zero hash collisions across train/val/test
- [ ] 2. Group-aware split if group_col present — GroupKFold or GroupShuffleSplit so same entity does not appear in train and test
- [ ] 3. LOFO sweep — for each feature, remove it, refit, measure test-metric drop; flag any feature whose removal exceeds lofo_collapse_threshold
- [ ] 4. Hub-firewall — if hub_sources provided, run leave-one-source-out CV with the hub source explicitly held out; compare hub-out test metric to all-source test metric
- [ ] 5. Cross-source LOFO — leave-one-source-out CV to measure cross-source generalization vs in-source generalization
- [ ] 6. Report block — per-check pass/fail with evidence (metric drop, hash collision count, hub-out AUC vs all-source AUC)
```

### Step 1: No-row-in-two-splits invariant

After computing the split indices, hash each row of `X` (concatenate column values, SHA-256) and verify that the hash sets across train / val / test are disjoint. Hash collision under a strong hash means the same exact row appears in two splits. Cause: a duplicate row that survived deduplication, or an incomplete `train_test_split` after a `concat` step.

```python
def hash_row(row): return hashlib.sha256(str(tuple(row)).encode()).hexdigest()

train_hashes = set(X_train.apply(hash_row, axis=1))
test_hashes = set(X_test.apply(hash_row, axis=1))
assert train_hashes.isdisjoint(test_hashes), f"{len(train_hashes & test_hashes)} rows leaked"
```

### Step 2: Group-aware split

When `group_col` is provided, replace `train_test_split` with `GroupShuffleSplit` or `GroupKFold` keyed on the group column. The invariant: any unique `group_id` value appears in either train OR test, never both. Common groups: `patient_id`, `user_id`, `customer_id`, `device_id`, `session_id`, `case_id`.

### Step 3: LOFO sweep

For each candidate feature `f` in `lofo_features`:

1. Train model on all features
2. Train model on all features EXCEPT `f`
3. Compute test metric (ROC-AUC, F1, RMSE, etc.) for each
4. Compute `drop = metric_full - metric_without_f`

Any `drop > lofo_collapse_threshold * metric_full` is a leakage flag. Inspect the feature:

- Is it derived from the target (e.g. `severity_score_at_outcome`)?
- Is it post-event (e.g. `was_admitted_within_30_days`)?
- Is it a unique-ID column the model can memorize?
- Is it an aggregated statistic computed on the full dataset before split?

### Step 4: Hub-firewall

When the dataset is a crosswalk / merge of multiple sources and one source acts as a hub (NIST in security-framework crosswalks; ICD-10 in medical-code mappings; English in multi-language NLP), run `LeaveOneGroupOut` keyed on `source_col` with the hub explicitly in the held-out fold. Compare:

- `auc_all_source_random_split` — naive random-split test AUC
- `auc_hub_held_out` — test AUC when the hub source is the held-out fold

Large gap (`auc_random > auc_hub_out + 0.10`) signals that the model was relying on the hub source's signal to generalize to the others — and will fail when deployed to a source not seen in training.

### Step 5: Cross-source LOFO

Beyond the hub, run leave-one-source-out for every source. Report per-source held-out metric. Sources with large drops are the ones the model cannot generalize to. The minimum across sources is the deployment-realistic worst-case.

### Step 6: Report block

For each check: pass / fail with the evidence (metric value, drop magnitude, hash collision count, hub-out AUC).

## Outputs

A markdown report with this structure:

1. **No-row-in-two-splits verdict** — hash collision count (must be 0); cause analysis if > 0
2. **Group-aware split verdict** — group column used, max group-overlap across splits (must be 0)
3. **LOFO sweep results** — per-feature drop sorted descending; flagged features with cause analysis
4. **Hub-firewall verdict** — all-source AUC, hub-held-out AUC, gap, verdict
5. **Cross-source LOFO** — per-source held-out metric table; worst-case named
6. **Overall verdict** — pass (all four checks clear) / conditional pass (some checks pass with caveats) / fail (one or more checks failed; deployment blocked)

## Failure modes

Known anti-patterns and how this skill catches them:

- **Same patient in train AND test** — caught by step 2 group-aware split + step 1 hash invariant.
- **Target-encoded feature leaking the target** — caught by step 3 LOFO; removing the offending feature collapses test AUC by 30%+.
- **Aggregated statistic fit on full dataset before split** — caught by step 1 hash invariant (identical aggregated values across splits) + step 3 LOFO when the aggregate is the leak channel.
- **Cross-source crosswalk evaluated only with random split** — caught by step 4 hub-firewall + step 5 cross-source LOFO.
- **Duplicate rows surviving deduplication** — caught by step 1 hash invariant.
- **Group column ignored because the rate of per-group rows is "low"** — caught by `When to use` triggers; even 2-row-per-entity data violates the invariant.
- **Model showing 0.99 test accuracy treated as "good"** — caught by the trigger criteria (suspicious metric → run all four checks before trusting).

## References

- `reference/leakage-firewall-checklist.md` — copy-paste implementation of all four checks
- [scikit-learn group-aware splitters](https://scikit-learn.org/stable/modules/cross_validation.html#group-cv-iterators) — GroupKFold, GroupShuffleSplit, LeaveOneGroupOut definitions
- [Kapoor and Narayanan 2023 *Leakage and the reproducibility crisis in machine-learning-based science*](https://doi.org/10.1016/j.patter.2023.100804) — survey of leakage classes across 17 fields
- [Lones 2024 *How to avoid machine learning pitfalls: a guide for academic researchers*](https://arxiv.org/abs/2108.02497) — common leakage and evaluation pitfalls

## Examples

### Example 1: Security framework crosswalk (happy-path)

Input: "Multi-source crosswalk over NIST CSF + MITRE ATT&CK + OWASP Top 10 + ENISA AI Threat Landscape — 8,000 control / threat pairs after dedup. Predict 'related vs not related' from text embeddings. Train ROC-AUC 0.94, random-split test ROC-AUC 0.91. Audit for leakage."

Output: Skill runs all four checks. (1) No-row hash invariant: pass (zero collisions). (2) Group-aware split: groups = control_id within each source — flags 240 control_ids that appear in BOTH NIST and ISO 27001 mappings; recommends GroupKFold by canonical_control_id. (3) LOFO: flags the `cosine_similarity_to_nist_anchor` feature whose removal drops AUC from 0.91 → 0.62 — leakage signature. (4) Hub-firewall: leave-NIST-out AUC = 0.71 vs random-split 0.91 = gap of 0.20 → fail; model is leaning on NIST as the hub. Verdict: model fails the firewall on three of four checks; deployment to a non-NIST-anchored source will collapse.

### Example 2: Subtle hub leakage (edge-case)

Input: "I'm training a recommender on customer purchase histories. 50,000 customers, 1.2M purchase events. Random row-split: test recall@10 = 0.42. Looks reasonable. Should I deploy?"

Output: Skill flags the group structure immediately — `customer_id` repeats across the 1.2M rows; random row-split puts the same customer in train and test. Runs GroupShuffleSplit by `customer_id`: test recall@10 drops to 0.18. The 0.42 random-split number was leakage via customer-history overlap. Recommends GroupKFold for the production-realistic metric and reports the 0.18 as the deployment-realistic number. Suggests considering temporal split (train on early purchases, test on later) if the recommender will see returning customers in production — the GroupKFold answer is for the cold-start customer scenario.

### Example 3: Clean IID single-source (anti-trigger)

Input: "I have a tabular dataset of housing prices — 20,000 rows, one row per house, 30 numeric/categorical features. I'm using train_test_split with random_state=42 and stratify=None. Do I need the leakage firewall?"

Output: Skill identifies this as clean IID single-source with one row per entity. The four checks here add no value — there is no group structure (one row per house), no multi-source structure (single dataset), no LOFO leakage candidate (standard features), and the no-row-in-two-splits invariant is trivially satisfied by `train_test_split`. Hands off to `ml-datasci/auditing-train-test-split` for the standard checks (stratification on the target if classification, leakage via global preprocessing fit on full data, target-derived features). Does NOT force the four-check firewall workflow.

## See also

- `ml-datasci/auditing-train-test-split` — the standard single-source train/test/val leakage audit; this skill is the multi-source / grouped-data extension
- `ml-datasci/evaluating-binary-classifiers` — apply AFTER the leakage firewall passes; evaluating on a leaky split inflates every metric
- `ml-datasci/evaluating-multiclass-classifiers` — same, for multi-class
- `ml-datasci/building-baseline-models` — required pre-step; a Dummy classifier under the same group-aware split tells you what "above chance" looks like in the firewall regime
- `ml-datasci/comparing-models-fairly` — required when comparing two models head-to-head; both must clear the firewall before comparison

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-2, skill 1) via PRAGMATIC discipline
