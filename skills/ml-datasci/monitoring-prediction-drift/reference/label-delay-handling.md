# Labeling-delay-aware evaluation windows

Labels do not arrive at the same time predictions do. Treating yesterday's predictions as if their labels are observable today silently turns calibration monitoring into garbage. The fix is explicit `labeling_delay_days` accounting in window construction.

## Common labeling delays

| Task | Typical delay | Reason |
|---|---|---|
| 30-day loan default | 30-90 days | Loan must mature past the default definition; collections cycle |
| 90-day customer churn | 90 days | Definition includes "no activity in last 90 days" |
| Click-through prediction | minutes to hours | Click event arrives near-real-time |
| Conversion attribution | 7-30 days | Attribution window standard in marketing |
| Long-term retention | 6-12 months | Annual subscriber cohort |
| Fraud confirmation | 30-180 days | Investigation cycle; chargeback windows can be 120 days |
| Healthcare diagnosis confirmation | 30 days - years | Depends on followup cadence and disease cycle |
| Real-time content moderation | minutes (human review) | Reviewer queue |

The delay is task-defined, not model-defined. Two models predicting the same outcome share the same delay.

## Window construction

Given a prediction made at `t_pred`, its label is observable at `t_label ≈ t_pred + labeling_delay_days`. For an evaluation window `[w_start, w_end]` to be fully labeled, you need:

```
w_end ≤ today() − labeling_delay_days
```

If a 30-day window is needed:

```
w_start = today() − labeling_delay_days − 30
w_end   = today() − labeling_delay_days
```

For a churn model with `labeling_delay_days = 90`, "the last 30 days" you can evaluate are the 30 days ending 90 days ago, not the literal last 30 days.

## Partial-labeling pattern

If some labels arrive faster than others (e.g., default → 30 days, but some loans default at 7 days), maturity is a distribution, not a point. Choices:

1. **Conservative**: use the maximum delay. Loses freshness; gains correctness.
2. **Maturity-aware reweighting**: per-prediction maturity probability `P(label_observable_by(t) | t_pred)`. Weight predictions by maturity. Implementable but adds variance.
3. **Hold the assumption explicit**: in the monitor's banner, state `Assumed labeling delay: 60 days (90th percentile of historical maturation distribution)`. Re-validate the assumption when re-baselining.

Recommend option 1 (conservative) unless reweighting is well-justified.

## Concept-drift-adjacent: changing labeling delay

If a process change (faster collections, new attribution model, regulatory shift) changes the labeling delay itself, the assumption goes stale. Symptoms:

- Recent evaluation windows have systematically more (or fewer) labeled predictions than expected
- Calibration looks fine in old windows and weird in new windows even though the model has not changed

Re-derive `labeling_delay_days` from the recent prediction-to-label timestamp distribution. Document the change in the model-card history.

## Estimation under unknown delay (advanced)

Libraries like NannyML offer Direct Loss Estimation (DLE) and Confidence-based Performance Estimation (CBPE) to estimate performance metrics from predictions alone when labels are unavailable or delayed. These are **estimates**, not measurements:

- Useful for early warning ("there might be a problem")
- Not sufficient for action ("recalibrate the model")
- Always cross-validate the estimator with delayed-but-true labels when they arrive

## Documentation pattern

Every monitor report should open with:

```
Evaluation snapshot — prediction-drift
- Model: credit-risk-v3
- Reference window: 2025-08-01 → 2025-08-31
- Current window: 2026-02-01 → 2026-02-28 (ended 84 days ago, > labeling_delay_days=60)
- Predictions: 142,300 (reference), 168,420 (current)
- Labeled-and-mature: 140,860 (98.9% of reference), 167,012 (99.2% of current)
- Labeling delay assumed: 60 days (p90 of 2024 default-maturation distribution)
```

The "ended N days ago" line is the easy-to-verify check that prevents the most common mistake.
