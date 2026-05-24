---
name: monitoring-data-drift
description: >
  Builds a per-feature data-drift monitor for a deployed ML model — population
  stability index (PSI) and Kolmogorov-Smirnov for continuous features,
  chi-squared / Jensen-Shannon for categorical features, with a documented
  reference window, alerting thresholds calibrated against baseline noise, and
  attribution to the top drifting features. Triggers whenever a production
  model has been live long enough to accumulate at least one reference window
  of inference traffic, whenever the user suspects upstream data has shifted,
  whenever feature ranges look different from training, or whenever model
  performance erodes without a known cause and the drift hypothesis must be
  tested before retraining. Refuses to set fixed alert thresholds without a
  baseline-noise calibration and refuses to engage on pre-deployment systems
  where no inference traffic exists yet.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - devops
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - genai_agentic_incidents
last-updated: 2026-05-23
---

# Monitoring Data Drift

## When to use

Trigger this skill when:

- A production ML model has been deployed long enough to accumulate at least one full reference window of live inference traffic (typically 2-4 weeks for a daily-cohort model, or 1-3 days for a high-throughput model)
- The user reports model performance erosion ("our AUC dropped from 0.84 to 0.71 over six months") and the drift hypothesis must be tested before retraining
- A pipeline upstream of the model has changed (new data source merged, feature engineering rewrite, schema migration, vendor swap) and the team wants to confirm the input distribution did not silently shift
- Feature ranges in live traffic look different from training ranges (categoricals with new levels, continuous features at the tails)
- The user asks for "drift detection", "PSI monitor", "feature stability", "distribution shift", "data quality monitor for prod"
- A regulator, auditor, or model-card commitment requires periodic drift attestation

## When NOT to use

Skip this skill and hand off when:

- The model has not been deployed yet — drift monitoring requires live inference traffic vs. a reference distribution; use `ml-datasci/auditing-train-test-split` and `ml-datasci/auditing-data-quality` for pre-deployment audits
- The concern is prediction-side drift (calibration erosion, score-shift, per-segment AUC drop) not input-side drift — use `ml-datasci/monitoring-prediction-drift`
- The concern is concept drift where the label distribution itself moved (not just features) — drift on `y` is a different problem; flag for label-delay-aware analysis
- The system is batch-only with monthly retraining where the retraining cadence already serves the same purpose
- The model is one-shot / experimental / not in production — drift monitoring overhead exceeds value
- Embedding drift in a RAG pipeline (the embedding-space side) → use `ml-datasci/auditing-embedding-drift` (planned)

## Quick start

User: *"Our credit-risk model has been in production for six months. AUC just dropped from 0.83 to 0.74 over the last quarter. Help me set up drift monitoring to find the cause."*

Response: define a reference window (the training data or the first 30 days post-deploy, whichever is stable and labeled). For each feature, compute PSI (continuous, binned to 10 deciles) or Jensen-Shannon (categorical) between reference and the current 14-day window. Calibrate the alert threshold against the baseline noise floor (the PSI of one reference subwindow vs. another — never alert below the noise floor). Rank features by drift magnitude. The top 3-5 are the attribution candidates for the AUC erosion.

```python
import numpy as np

def population_stability_index(reference, current, bins=10):
    # Bin on reference quantiles so empty bins do not crash the log
    edges = np.quantile(reference, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    ref_p = (ref_counts + 1) / (ref_counts.sum() + bins)  # Laplace smoothing
    cur_p = (cur_counts + 1) / (cur_counts.sum() + bins)
    return float(np.sum((cur_p - ref_p) * np.log(cur_p / ref_p)))
```

See `reference/drift-metrics.md` for the metric-per-feature-type decision table, `reference/threshold-calibration.md` for the baseline-noise calibration recipe, and `reference/alerting-template.md` for the alert payload schema.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `reference_window` | DataFrame / parquet path / SQL query | yes | — | The baseline distribution. Typically the model's training set OR the first stable post-deploy window (≥ N samples; see threshold-calibration.md for N rule). |
| `current_window` | DataFrame / parquet path / SQL query | yes | — | Live inference traffic for the comparison window. |
| `feature_schema` | dict / YAML | yes | — | Per-feature `name`, `type` (continuous / ordinal / categorical / boolean), and optionally `expected_range` and `expected_levels`. Drives metric choice. |
| `window_length` | string (e.g., "14d") | no | `"14d"` | Length of the rolling current window. Shorter windows surface drift faster but produce more noise. |
| `cohort_dim` | column name | no | none | Optional cohort split (region, product line, channel). Per-cohort drift often reveals which slice moved. |
| `noise_floor_subwindows` | integer | no | 6 | Number of reference subwindows used to estimate baseline PSI noise. Alert threshold = max(0.1, p95 of noise distribution + safety margin). |
| `cooldown_hours` | integer | no | 24 | Minimum hours between repeat alerts on the same feature. Prevents alert-storms during sustained drift. |

## Workflow

```
Data-drift monitoring progress:
- [ ] 0. Confirm scope: at least one labeled reference window exists; model is live; goal documented
- [ ] 1. Define reference window: pick training set OR first stable post-deploy slice; record provenance + window dates
- [ ] 2. Per-feature metric selection: continuous → PSI + KS; ordinal → PSI; categorical → Jensen-Shannon or chi-squared; boolean → proportion delta
- [ ] 3. Baseline-noise calibration: compute the chosen metric between K subwindows of the reference; record p50, p95, p99 noise floors per feature
- [ ] 4. Compute drift metric on the current window vs. reference; per feature and per cohort if cohort_dim given
- [ ] 5. Threshold check: alert only when current-vs-reference exceeds max(industry-band, p95 baseline noise + safety margin)
- [ ] 6. Attribution: rank features by drift; identify top 3-5; categorize as range shift / mean shift / new-level / missingness spike
- [ ] 7. Root-cause hypothesis: instrumentation bug? Upstream schema change? Real population shift? List candidates with the diagnostic to confirm each
- [ ] 8. Alert payload: feature, metric, value, baseline noise, threshold, attribution category, suggested next step
- [ ] 9. Cooldown: dedupe alerts within cooldown_hours; promote sustained drift to incident
```

### Step 2: Metric selection per feature type

| Feature type | Primary metric | Secondary | Why |
|---|---|---|---|
| Continuous (e.g., income, latency) | PSI (10-decile binning on reference quantiles) | KS test on full distribution | PSI maps cleanly to industry bands; KS catches shape changes PSI misses |
| Ordinal (e.g., star rating, education level) | PSI | — | Treat as continuous-equivalent on the ordinal scale |
| Categorical (e.g., country, product code) | Jensen-Shannon divergence | Chi-squared if low cardinality | JS handles new-level introduction without infinite KL |
| Boolean | Proportion delta + binomial CI | — | Simple, interpretable |
| High-cardinality text / IDs | Frequency of "new level not seen in reference" + cardinality delta | — | PSI / JS are noise-dominated on long-tail categoricals |
| Datetime | Out-of-range count + cadence shift (events / day) | — | See `workflow/validating-temporal-fields` for the future-date class |

### Step 3: Baseline-noise calibration (the step most monitors skip)

**Industry-default bands** (PSI < 0.1 stable, 0.1-0.25 minor, > 0.25 major) are starting points, not thresholds. They were calibrated against credit-risk feature distributions in the 1990s. For high-variance features (e.g., session counts, ad impressions) the natural week-over-week PSI in the reference window may already be 0.15 — alerting at 0.1 produces continuous false alarms.

Calibration recipe:

1. Slice the reference window into `noise_floor_subwindows` equal-length subwindows
2. For each pair (or each subwindow vs. the full reference), compute the chosen metric
3. Record the p50 / p95 / p99 across pairs; this is the per-feature noise floor
4. Set the alert threshold to `max(industry_band, p95 + safety_margin)` where safety_margin is small (1.5x of p95 - p50) to avoid noise-dominated alerts

Document the noise floor per feature in `reference_window_baseline.json`. Re-calibrate when the reference window itself rotates.

### Step 6: Attribution categories

When a feature breaches threshold, categorize:

- **Range shift** — `min` / `max` / quantiles moved (e.g., income p99 went from $250K to $480K). Often a new geography or product cohort.
- **Mean shift** — center moved, shape similar. Often a real population change or a unit / scale change upstream.
- **Variance shift** — spread changed without center change. Common in measurement-instrument swaps.
- **New levels** (categorical) — values that did not exist in reference. Usually upstream pipeline change or actual new content.
- **Missingness spike** — null rate went from 0.1% to 8%. Almost always an instrumentation bug, not real drift.
- **Cardinality shift** — categorical feature suddenly has 10x distinct values. Often free-text leaking into a categorical column.

### Step 7: Root-cause hypotheses

Always enumerate at least three candidates before concluding "the world changed":

1. **Instrumentation bug** — schema change, new column rename, default-value bug, vendor library update. Diagnostic: diff the feature-extraction code commit log against the drift onset date.
2. **Upstream data-source change** — new geography enrolled, marketing campaign shifted cohort mix, a partner data feed swapped formats. Diagnostic: per-cohort drift (with `cohort_dim`); if drift concentrates in one cohort, the world likely changed for that cohort, not for the feature itself.
3. **Real population drift** — actual shift in customer behavior, regulatory change, macroeconomic factor. Diagnostic: per-cohort drift is broadly spread; external indicators confirm.

Refuse to recommend retraining as the first action — retraining a model on contaminated upstream data hard-codes the bug.

## Outputs

A markdown report with:

1. **Window provenance** — reference window dates + size, current window dates + size, feature schema fingerprint
2. **Per-feature drift table** — feature · type · metric · value · baseline-noise p95 · threshold · status (stable / minor / major) · attribution category
3. **Top 3-5 drifters** — with values, attribution, and the diagnostic question for each
4. **Cohort breakdown** (if `cohort_dim` given) — per cohort × feature heatmap
5. **Root-cause hypotheses** — at least three candidates with the next diagnostic per hypothesis
6. **Recommendations** — ordered: (a) confirm-or-rule-out instrumentation bug; (b) confirm-or-rule-out cohort-mix shift; (c) only then consider retraining

## Failure modes

Known anti-patterns and how this skill catches them:

- **Fixed PSI threshold at 0.1 without baseline noise calibration** — caught by mandatory step 3 (per-feature noise floor); the alert threshold is the larger of the industry band and the empirical p95 noise floor
- **Alerting on individual high-variance features without cohort decomposition** — caught by step 6 cohort breakdown; sudden drift often concentrates in one cohort
- **Concluding "the world changed" before ruling out instrumentation bugs** — caught by step 7 forcing three hypotheses with diagnostics in priority order (instrumentation → cohort → real drift)
- **Recommending retraining as the first response** — caught by step 7 explicit refusal; retraining on contaminated data hard-codes upstream bugs
- **PSI / KL division-by-zero on empty bins** — caught by step 2 implementation using Laplace smoothing (+1 / +bins to numerator / denominator) and binning on reference quantiles to ensure no empty reference bin
- **New categorical levels causing infinite KL** — caught by metric selection in step 2 (Jensen-Shannon, not KL, for categoricals; JS is bounded)
- **Comparing windows of unequal size without normalization** — caught by step 4 using probability vectors (counts / total), not raw counts
- **Alert-storm during sustained drift** — caught by step 9 cooldown_hours dedupe; sustained drift becomes one incident, not 100 alerts
- **No reference-window rotation policy** — the reference will eventually drift from the live distribution by design (concept drift); document a re-baseline cadence (typically quarterly) and re-calibrate noise floors when rotating

## References

- `reference/drift-metrics.md` — metric-per-feature-type decision table with formulas
- `reference/threshold-calibration.md` — baseline-noise calibration recipe with worked example
- `reference/alerting-template.md` — JSON alert payload schema for downstream paging systems
- [Population Stability Index, *Credit Scorecards*, Siddiqi 2017](https://www.wiley.com/en-us/Intelligent+Credit+Scoring%3A+Building+and+Implementing+Better+Credit+Risk+Scorecards%2C+2nd+Edition-p-9781119279150) — origin of the PSI bands
- [Continuous Adaptation for Machine Learning Systems, Klaise et al., Seldon 2020](https://arxiv.org/abs/2007.06299) — practitioner-facing drift framework
- [NannyML documentation](https://nannyml.readthedocs.io/) — open-source drift library; the PSI / KS / JS choices here align with NannyML defaults

## Examples

### Example 1: Post-deployment drift audit on a credit-risk model (happy-path)

Input: *"Our credit-risk model has been in production for 6 months. AUC dropped from 0.83 to 0.74 over the last quarter. Drift monitoring isn't set up yet — help me find the cause."*

Output: Skill walks the 9-step workflow. Selects PSI (continuous features), JS (categoricals). Calibrates per-feature noise floor against 6 subwindows of the first stable 30 days post-deploy. Computes drift over the most recent 14-day current window. Surfaces top drifters: `applicant_income` PSI = 0.41 (major, attribution = range shift), `employment_tenure_months` PSI = 0.22 (minor), `loan_purpose` JS = 0.18 with one new level "auto-refi" never seen in reference. Names the three root-cause hypotheses with diagnostics. Recommends: (a) confirm `applicant_income` extraction code unchanged since deploy, (b) check whether a new marketing channel introduced higher-income applicants, (c) hold off on retraining until (a) and (b) are answered.

### Example 2: Expected seasonal drift (edge-case)

Input: *"Our retail-demand model has been in prod for 18 months. PSI on `weekly_units_sold` just spiked to 0.31. The alert is firing. Is this real drift?"*

Output: Skill asks what time of year the spike occurred relative to the reference window. Retail demand has known weekly / monthly / annual seasonality; if the reference window is one calendar quarter and the current window is the next quarter spanning a holiday season, a 0.31 PSI is the expected baseline. Recommends: (a) re-calibrate the noise floor using year-over-year same-period subwindows (not adjacent subwindows), (b) annotate the seasonality cycle in `reference_window_baseline.json`, (c) suppress the alert OR re-baseline on a seasonally-matched reference. Does NOT recommend retraining or rolling back. Names the failure mode (using sequential subwindows to calibrate a seasonally-varying feature).

### Example 3: Pre-deployment system (anti-trigger)

Input: *"We're about to deploy a new fraud-detection model next week. Help me set up drift monitoring for it now."*

Output: Skill identifies this as a pre-deployment system. Explains that drift monitoring requires live inference traffic to compare against a reference distribution — there is no current window to monitor yet. Hands off the pre-deployment audits: `ml-datasci/auditing-train-test-split` (for leakage / temporal-order checks before deploy) and `ml-datasci/auditing-data-quality` (for input-data sanity). Recommends the team return to this skill once 2-4 weeks of live inference traffic has accumulated. Provides a minimum-viable pre-deployment checklist: (a) decide what the reference window will be, (b) instrument feature logging from day one, (c) pre-stage the drift-monitor code so it can run on day 30 without re-engineering.

## See also

- `ml-datasci/monitoring-prediction-drift` — sibling for the prediction-side (calibration / score / per-segment AUC erosion)
- `ml-datasci/auditing-inference-latency-budget` — sibling for the latency-side production monitoring
- `ml-datasci/auditing-train-test-split` — the pre-deployment counterpart (catches leakage before drift monitoring is even possible)
- `ml-datasci/auditing-data-quality` — input-side sanity checks; drift monitoring assumes the inputs are well-formed
- `workflow/validating-temporal-fields` — datetime-specific drift sanity (future-dated rows / max-year-fallback)
- `ml-datasci/auditing-embedding-drift` (planned) — embedding-space drift for RAG / retrieval systems

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-2, skill 1) via PRAGMATIC discipline
