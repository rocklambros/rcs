# Drift alert payload schema

Alerts should be machine-readable (downstream paging / ticketing systems) and human-readable (the on-call engineer at 2am needs to act). One JSON payload per alert.

## Schema

```json
{
  "alert_id": "drift-2026-05-23T14:00Z-applicant_income",
  "model_id": "credit-risk-v3",
  "feature": "applicant_income",
  "feature_type": "continuous",
  "metric": "PSI",
  "value": 0.41,
  "baseline_noise_p95": 0.12,
  "threshold_used": 0.30,
  "severity": "major",
  "reference_window": {
    "start": "2026-01-01",
    "end": "2026-01-31",
    "n_rows": 218450,
    "provenance": "first-stable-post-deploy"
  },
  "current_window": {
    "start": "2026-05-09",
    "end": "2026-05-22",
    "n_rows": 94320
  },
  "cohort_split": {
    "by": "marketing_channel",
    "values": {
      "organic": 0.08,
      "paid_search": 0.11,
      "partner_referral": 0.93
    }
  },
  "attribution_category": "range-shift",
  "attribution_detail": "p99 of applicant_income shifted from $250K to $480K; concentrated in partner_referral cohort",
  "root_cause_hypotheses": [
    {
      "hypothesis": "instrumentation-bug",
      "diagnostic": "diff feature-extraction code at deploy_date_2026-05-09; check for unit / scale change",
      "evidence_for": "abrupt onset on 2026-05-09 aligns with a deploy",
      "evidence_against": "delta concentrates in one cohort, not all"
    },
    {
      "hypothesis": "cohort-mix-shift",
      "diagnostic": "check marketing-campaign attribution for partner_referral channel onboarded near 2026-05-09",
      "evidence_for": "drift concentrates in partner_referral cohort",
      "evidence_against": "—"
    },
    {
      "hypothesis": "real-population-shift",
      "diagnostic": "check macroeconomic indicators (housing prices, wage growth) for the period",
      "evidence_for": "—",
      "evidence_against": "concentration in one cohort argues against broad shift"
    }
  ],
  "recommended_next_action": "investigate cohort-mix-shift first (highest evidence); rule out instrumentation second; defer retraining decision until both ruled in/out",
  "cooldown_until": "2026-05-24T14:00Z"
}
```

## Severity mapping

- **stable**: metric below minor threshold — no alert, included in daily roll-up only
- **minor**: metric between minor and major thresholds — page during business hours; ticket
- **major**: metric above major threshold — page immediately; incident review

## Cooldown semantics

`cooldown_until` is set when the alert fires. Repeat alerts on the same (model_id, feature) pair within the cooldown window are suppressed but counted. A sustained drift produces ONE alert at onset; if the drift persists past cooldown, a follow-up "still drifting" alert fires (escalates severity if value increased).

## What NOT to put in the alert

- **The raw histogram data**: stash to object storage, link by URL. Otherwise the alert payload bloats.
- **Recommendations to "retrain the model"**: retraining is a downstream decision after root cause is established. Surface the diagnostic, not the verdict.
- **Mean / std without quantiles**: production drift is usually in the tails; report p50 / p95 / p99 deltas, not just summary statistics.
- **Static severity ladders**: severity follows the calibrated threshold, not a global hard-code.

## Integration points

- **PagerDuty / Opsgenie**: alert_id as dedup key, severity → priority mapping
- **Jira / GitHub issues**: open a ticket on `minor`; auto-link to root_cause_hypotheses
- **Slack**: human-readable summary + link to the full JSON in object storage
- **Datadog / Grafana**: emit the `value` as a gauge metric, the `severity` as a tag

## Audit trail

Persist every alert (fired or suppressed-by-cooldown) to an append-only store. Quarterly drift reviews need the historical record to distinguish "we had one bad week" from "this feature has been drifting for two quarters."
