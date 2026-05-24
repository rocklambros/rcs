# Baseline-noise calibration for drift thresholds

The industry-default PSI bands (< 0.1 stable, 0.1-0.25 minor, > 0.25 major) are starting points calibrated on credit-risk features in the 1990s. They are wrong for many production features today. Calibrating the alert threshold against the **empirical baseline noise** of the reference window prevents both false-alarm storms and silent misses.

## When the industry default fails

- **Naturally high-variance features**: session counts, ad impressions, request latency. Week-over-week PSI within the reference window may be 0.15 with no semantic drift. Alerting at 0.1 fires continuously.
- **Strongly seasonal features**: retail demand, holiday traffic, weekday-vs-weekend cohort mix. Same-period-prior-year PSI is the right baseline; adjacent-week PSI is meaningless.
- **Sparse-event features**: low-frequency categoricals where a single rare event swings the metric. Use rolling windows long enough to reach a stable signal.
- **Low-variance regulatory features** (state, country, regulated_industry_flag): adjacent-window PSI is near zero; even 0.05 is suspicious. Tightening the threshold here catches real drift the industry bands miss.

## Calibration recipe

1. **Pick K reference subwindows** (default K = 6). Choose them to span the same kinds of variation the production window will span: if the production window is 14 days, use 14-day subwindows. If the feature is seasonal, use same-season subwindows from prior cycles.
2. **Compute the chosen drift metric** (PSI / JS / KS) between each pair of subwindows OR between each subwindow and the full reference. Pairwise gives `K * (K-1) / 2` data points; against-full gives `K`.
3. **Record per feature**: p50, p95, p99 of the noise distribution.
4. **Set the alert threshold** to `max(industry_band_minor, p95 + safety_margin)` where `safety_margin = 1.5 * (p95 - p50)`. Major threshold to `max(industry_band_major, p99 + safety_margin)`.
5. **Persist** the per-feature noise floor in `reference_window_baseline.json` so monitoring code reads it instead of hard-coding 0.1 / 0.25.

## Worked example

Reference: 60 days of post-deploy inference data on a retail-pricing model. Feature: `weekly_units_sold`.

- K = 6 subwindows, each 10 days
- Pairwise PSI distribution: p50 = 0.04, p95 = 0.18, p99 = 0.26
- Industry-default minor threshold (0.1) is below p50 — would have fired on every subwindow

Calibrated thresholds:

- Minor: max(0.1, 0.18 + 1.5 * 0.14) = max(0.1, 0.39) = **0.39**
- Major: max(0.25, 0.26 + 1.5 * 0.14) = max(0.25, 0.47) = **0.47**

For comparison, on the same model the feature `customer_age_bracket` has p50 = 0.005, p95 = 0.02, p99 = 0.04. Calibrated thresholds:

- Minor: max(0.1, 0.02 + 1.5 * 0.015) = max(0.1, 0.043) = **0.1** (industry band dominates)
- Major: max(0.25, 0.04 + 1.5 * 0.015) = max(0.25, 0.063) = **0.25**

So the same monitor uses 0.39 / 0.47 for one feature and 0.1 / 0.25 for another. This is the point — the threshold belongs to the feature, not the framework.

## Re-calibration cadence

The reference window itself drifts from live distribution by design (this is concept drift; it is real, it is normal, and the model deserves periodic re-baselining). Suggested cadence:

- **Re-calibrate the noise floor** when the reference window is rotated (typically quarterly for stable systems, monthly for fast-moving systems).
- **Annotate** the calibration date in `reference_window_baseline.json`. Stale calibration is invisible — surface it in the daily monitor's banner.

## Anti-patterns

- **Calibrating against adjacent windows when the feature is seasonal.** Use same-season prior cycles instead, or document that the feature is non-seasonal.
- **Calibrating on a 14-day reference that is already drifting.** The reference must be a stable epoch. If the team only has 14 days of post-deploy data, defer monitoring or use the training set with the caveat that training-to-production gap is itself part of the noise.
- **Hard-coding the calibration result in code.** The result lives in a config file (`reference_window_baseline.json`) so re-baselining does not require a code change.
- **Sharing one calibration across cohorts when cohort distributions differ.** Per-cohort noise floors are cheap; share-one only when cohorts genuinely have the same noise behavior.
