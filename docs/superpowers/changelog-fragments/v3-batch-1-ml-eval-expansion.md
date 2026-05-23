### v3-batch-1: ML eval expansion — 2026-05-23

Skills shipped:
- `ml-datasci/evaluating-multiclass-classifiers` v0.1.0 — full multi-class evaluation report (per-class P/R/F1 + macro/weighted/micro with cost-model justification + K x K confusion in counts and row-normalized + top-k + one-vs-rest ROC/PR + log loss + Cohen's kappa + bootstrap CIs + confusion-pair audit); refuses bare overall accuracy under imbalance and hands off to evaluating-binary-classifiers on 2-class tasks (Σ 16, status: shipped)
- `ml-datasci/tuning-classification-threshold` v0.1.0 — five-selector threshold-selection library (F-beta, TPR-at-fixed-FPR, precision-at-fixed-recall, cost-weighted, Youden's J) with enforced validation-pick / held-out-test-report separation and mandatory calibration check; refuses default 0.5 and refuses to pick the threshold on the test set (Σ 16, status: shipped)
- `ml-datasci/running-chollet-ratio-check` v0.1.0 — Chollet samples-per-word ratio decision rule for text / sequence classification model-family selection (BoW vs small RNN/CNN vs Transformer) with domain-pretraining adjustment, per-class minimum sanity check, and mandatory BoW baseline comparison regardless of recommendation; refuses to apply the ratio to non-sequence data (Σ 16, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 9 dispatches (3 scenarios × 3 skills); all scored 3/3 against intent. Full 3-model (Haiku / Sonnet / Opus) validation deferred to a future re-run.

Notes: No deviations or calibration corrections. All three skills retained `status: shipped` after eval validation.
