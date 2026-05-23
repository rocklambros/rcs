---
name: auditing-synthetic-data-utility
description: >
  Audits a synthetic dataset (SDG output) for downstream-task utility against
  the real source data via the TSTR / TRTS / TRTR triangle — Train on Synthetic,
  Test on Real vs Train on Real, Test on Real vs Train on Real, Test on Synthetic.
  Reports per-metric utility ratio (synth / real), per-marginal KS / Wasserstein
  distance, pairwise-correlation Frobenius gap, and a downstream-task fidelity
  verdict (use-as-real / use-with-caveats / reject). Triggers whenever the user
  has generated tabular synthetic data via SDV / CTGAN / TVAE / Synthpop / Gretel
  / Mostly AI / private-DP-synth and is about to train or evaluate a model on it.
  Refuses to certify utility without a held-out REAL test set, refuses to lead
  with marginal-only fidelity (which masks correlation collapse), and hands off
  to auditing-synthetic-data-leakage when the question is privacy rather than
  utility.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
  - data-engineer
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - genai_agentic_incidents
last-updated: 2026-05-23
---

# Auditing Synthetic Data Utility

## When to use

Trigger this skill when:

- A synthetic dataset has been generated via SDV, CTGAN, TVAE, Synthpop, Gretel, Mostly AI, private DP-synth, copula sampler, or any tabular SDG and the user is about to train, evaluate, share, or publish a model fit on it
- The user asks "is this synthetic data good enough?", "can I use synthetic data instead of real?", "how do I know my SDG worked?", or "should I trust this synth data for benchmarking?"
- A synthetic-data pipeline produces metrics-on-synth-only and the user wants to know whether those metrics will hold on real data
- The user reports that a model trained on synth performs differently than a model trained on real and needs a structured diagnosis
- Keywords: TSTR, TRTS, TRTR, train-on-synthetic test-on-real, utility ratio, marginal fidelity, correlation collapse, downstream-task fidelity, SDV, CTGAN, TVAE, Synthpop, Gretel, Mostly AI

## When NOT to use

Skip this skill and hand off when:

- The question is **privacy / re-identification risk**, not utility → use `ml-datasci/auditing-synthetic-data-leakage` (membership-inference attacks, k-anonymity-on-synth, record linkage). Utility and privacy are in tension and need separate audits.
- The synthetic data is **text / image / audio**, not tabular → this skill is tabular-only. Text SDG (back-translation, paraphrase, LLM-generated) needs perplexity / BLEU / human eval; image SDG (GAN, diffusion) needs FID / IS / human eval. Different metric families.
- There is **no held-out REAL test set** — refuse to certify utility. Recommend the user partition real data into real-train / real-test BEFORE generating synth (so synth is fit on real-train, evaluated against real-test).
- The user wants **dataset augmentation** (real + synth combined for training, not synth-only) — that is a different audit family; mention it as a downstream option after this skill establishes the utility floor.
- The synthetic data is for **pure schema / format testing** (does my pipeline accept the columns), not statistical fidelity — Faker output is fine and doesn't need this skill.

## Quick start

User: "I generated 50k synthetic patient records with CTGAN from a real 50k-record dataset. I want to share the synth set with a research partner instead of the real one. Is the synth set good enough for them to fit a readmission classifier?"

Response: walks the TSTR / TRTS / TRTR triangle. Splits real into real-train (used to fit the SDG) and real-test (held back). Trains the downstream classifier four ways and reports the utility ratios:

```
                  Test on REAL       Test on SYNTH
Train on REAL     TRTR (baseline)    TRTS (sanity)
Train on SYNTH    TSTR (the answer)  TSTS (over-fit risk)
```

The headline metric is `TSTR_metric / TRTR_metric` — if synth-trained classifier scores 0.78 ROC-AUC on real-test and real-trained scores 0.82, utility ratio is 0.95 (acceptable for most non-clinical use). Below 0.85 = use-with-caveats; below 0.70 = reject. Plus per-marginal KS distance and pairwise-correlation Frobenius gap to localize where the SDG failed.

See `reference/tstr-trts-protocol.md` for the full split + train + score recipe.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `real_data` | DataFrame | yes | — | The real source dataset. MUST be partitioned by the skill (or the user) into `real_train` (used to fit the SDG) and `real_test` (held-out evaluation). Skill refuses if `real_test` is empty or overlaps `real_train` IDs. |
| `synth_data` | DataFrame | yes | — | The synthetic dataset to audit. Same schema (column names + dtypes) as `real_data`. Skill refuses on schema mismatch. |
| `target_column` | str | yes | — | The column the downstream classifier / regressor predicts. Drives the TSTR / TRTR scoring. |
| `task_type` | "classification" \| "regression" | yes | — | Determines the downstream metric — ROC-AUC + F1 + accuracy for classification, RMSE + MAE + R² for regression. |
| `downstream_model` | str | no | "logistic+rf" | Comma-separated list of models to fit. Defaults to a logistic / linear baseline + a RandomForest. Skill recommends fitting at least 2 model families because TSTR can favor different families differently. |
| `n_bootstrap` | int | no | `200` | Bootstrap resamples on `real_test` for 95% CI on the utility ratio. |
| `marginal_test` | "ks" \| "wasserstein" \| "both" | no | "both" | Per-column distributional fidelity test for continuous features. KS is scale-invariant; Wasserstein is in feature units. |
| `correlation_method` | "pearson" \| "spearman" | no | "spearman" | Correlation type for the pairwise-correlation Frobenius gap. Spearman is robust to monotonic transformations. |

## Workflow

Copy this checklist into the response and check items off as each step completes:

```
Synthetic-data utility audit progress:
- [ ] 0. Pre-flight: schema match, real_test held out, no ID overlap, no row identity (real row == synth row)
- [ ] 1. Marginal fidelity per column (KS / Wasserstein) — flag columns with bad marginals
- [ ] 2. Pairwise-correlation Frobenius gap (Spearman on real_train vs Spearman on synth)
- [ ] 3. TRTR baseline: train downstream model on real_train, score on real_test
- [ ] 4. TSTR (the answer): train on synth, score on real_test
- [ ] 5. TRTS sanity: train on real_train, score on synth — should be ≈ TRTR (else synth distribution is off)
- [ ] 6. Utility ratio: TSTR_metric / TRTR_metric per model family + per metric
- [ ] 7. Bootstrap 95% CI on the utility ratio (resample real_test, hold real_train / synth fixed)
- [ ] 8. Verdict: use-as-real (ratio ≥ 0.95) / use-with-caveats (0.85-0.95) / reject (< 0.85)
- [ ] 9. Diagnose: if reject, attribute failure to marginal collapse OR correlation collapse OR rare-class loss
```

### Step 0: Pre-flight

Refuse if:

- `real_test` is missing or empty — without it, TSTR cannot be computed and "utility" is a faith statement
- Any ID in `real_train` also appears in `real_test` — would inflate TRTR baseline; recompute splits
- Any synth row is byte-identical to a real row (`pd.merge(real, synth, how='inner')` returns rows) — would invalidate both utility and privacy claims (also a leakage flag; hand off to `auditing-synthetic-data-leakage`)
- Synth schema differs from real schema (column names, dtypes) — fix or abort

### Step 1: Marginal fidelity per column

For each continuous column, run KS and Wasserstein on `real_train[col]` vs `synth[col]`. For each categorical column, compute total-variation distance between class frequencies. Flag columns where KS p < 0.01 (with Bonferroni correction for n_columns) or where total-variation distance > 0.05.

Marginal fidelity is **necessary but not sufficient** — a SDG that preserves every marginal can still collapse joint structure. Step 2 catches that.

### Step 2: Pairwise-correlation Frobenius gap

Compute Spearman correlation matrix on `real_train` and on `synth`. Report `||C_real - C_synth||_F / ||C_real||_F` (relative Frobenius norm of the difference). Gap > 0.20 → joint structure is degraded; the SDG is preserving marginals but losing correlations (classic CTGAN failure mode on highly-correlated tabular data).

### Step 3: TRTR baseline

Fit `downstream_model(s)` on `real_train`, score on `real_test`. This is the upper bound — synth-trained models cannot beat this in expectation. Record per-model metric (ROC-AUC for classification, RMSE for regression).

### Step 4: TSTR (the answer)

Fit `downstream_model(s)` on `synth` (size-matched to `real_train`), score on `real_test`. This is the utility number that matters: "if I trained on synth and deployed against the real world, what score would I get?"

### Step 5: TRTS sanity

Fit on `real_train`, score on `synth`. If TRTS ≫ TRTR, the synth distribution is easier than real (over-smoothed); if TRTS ≪ TRTR, synth is harder (over-noised). Either signals SDG miscalibration before drawing utility conclusions.

### Step 6: Utility ratio

`utility_ratio = TSTR_metric / TRTR_metric` per model family. For classification with ROC-AUC, normalize against the chance floor: `(TSTR_auc - 0.5) / (TRTR_auc - 0.5)` to avoid inflating ratios near chance.

### Step 7: Bootstrap 95% CI

Resample `real_test` with replacement `n_bootstrap` times. Recompute TSTR and TRTR per resample. Report 95% CI of the utility ratio. CIs > [0.85, 1.05] are normal; CIs spanning [0.50, 0.95] mean the point estimate is unreliable.

### Step 8: Verdict

| Utility ratio (point + 95% CI lower bound) | Verdict |
|---|---|
| Point ≥ 0.95 AND CI lower ≥ 0.90 | Use as real |
| Point in [0.85, 0.95) OR CI lower in [0.80, 0.90) | Use with caveats — name them |
| Point < 0.85 OR CI lower < 0.80 | Reject — diagnose per step 9 |

### Step 9: Diagnose failure

If verdict is reject or with-caveats, attribute the failure:

- **Marginal collapse** (step 1 flags many columns) — SDG is failing at the per-column level; try a different generator family
- **Correlation collapse** (step 2 Frobenius gap > 0.20) — SDG preserves marginals but not joint; CTGAN often does this on > 20 correlated features
- **Rare-class loss** — check per-class recall in TSTR vs TRTR; SDGs often under-sample minority classes
- **Over-smoothing** (TRTS ≫ TRTR) — synth is too easy; increase generator capacity or noise
- **Train-set memorization** (TSTS ≫ TSTR) — generator copied real_train; this is also a privacy red flag (hand off to `auditing-synthetic-data-leakage`)

## Outputs

A markdown report:

1. **Dataset summary** — real n, synth n, schema match status, real_train / real_test split sizes
2. **Marginal fidelity table** — per-column KS / Wasserstein / TV-distance with pass/fail
3. **Correlation gap** — Spearman matrix Frobenius gap (real_train vs synth) with verdict
4. **TRTR / TSTR / TRTS / TSTS table** — per model family, per metric
5. **Utility ratio table** — point + 95% CI per model + per metric
6. **Verdict** — use-as-real / use-with-caveats / reject with rationale
7. **Failure attribution** — if reject or with-caveats, named failure mode and remediation suggestion
8. **Residual risks** — sample-size caveats, privacy-not-audited disclaimer, hand-off to `auditing-synthetic-data-leakage`

## Failure modes

- **Audit-on-synth-only** — many users compute marginal fidelity on synth, see good numbers, and ship. Marginal fidelity ≠ utility. Caught by step 2 correlation gap + step 4 TSTR being the lead metric.
- **TSTR with no real test** — using synth as the test set inflates utility (TSTS ≈ 1.0 always when generator and test share the same distribution). Caught by step 0 refusal.
- **TRTR computed on the same rows used to fit the SDG** — leakage; SDG saw real_train, then we train on real_train and test on real_test. If real_test was held out from SDG fitting, TRTR is honest. If not, TRTR is inflated. Caught by step 0 ID-overlap check.
- **Single-model TSTR** — TSTR with one model family hides family-specific failures. CTGAN-generated data often favors trees over linear models, or vice versa. Caught by `downstream_model` default = "logistic+rf" (at least two families).
- **Bare point estimate of utility ratio** — 0.87 sounds the same as 0.92, but their 95% CIs can overlap. Caught by step 7 bootstrap CI.
- **Privacy claim slipped in** — "low utility means high privacy." False. Privacy is a separate audit. Caught by `When NOT to use` hand-off and step 9 train-set-memorization being a privacy flag explicitly.
- **Verdict pushed up by averaging across model families** — average utility ratio of 0.92 across logistic (0.99) + RF (0.85) hides that RF fails on synth. Caught by per-model reporting.

## References

- `reference/tstr-trts-protocol.md` — full split + train + score recipe with code skeleton
- `reference/utility-ratio-thresholds.md` — verdict thresholds per task type (classification / regression / survival) with calibration notes
- [Jordon, Yoon, van der Schaar 2018 *Measuring the quality of synthetic data for use in competitions*](https://arxiv.org/abs/1806.11345) — original TSTR / TRTS framing
- [Xu, Skoularidou, Cuesta-Infante, Veeramachaneni 2019 *Modeling tabular data using conditional GAN*](https://arxiv.org/abs/1907.00503) — CTGAN paper; documents correlation-collapse failure modes
- [SDV docs: evaluation guide](https://docs.sdv.dev/sdv/single-table-data/evaluation) — Synthetic Data Vault's recommended utility metrics

## Examples

### Example 1: CTGAN synth for tabular classification (happy-path)

Input: "I have 50k real patient records. I fit CTGAN on 40k of them, held out 10k. I generated 40k synth. Target is readmission (binary). Audit utility for a downstream RF + logistic regression."

Output: Skill confirms `real_train = 40k`, `real_test = 10k`, no ID overlap. Step 1: 28 / 30 columns pass marginal fidelity. Step 2: Spearman Frobenius gap = 0.18 (borderline — flag). Step 3: TRTR ROC-AUC = 0.82 (RF) / 0.79 (logistic). Step 4: TSTR ROC-AUC = 0.76 (RF) / 0.75 (logistic). Step 6: utility ratios 0.93 / 0.95. Step 7: bootstrap CI [0.88, 0.97]. Verdict: **use with caveats** — name the borderline correlation gap and the slight RF underperformance vs logistic; recommend the research partner re-audit on their downstream task.

### Example 2: SDG preserves marginals, collapses correlations (edge-case)

Input: "My synth data passes every marginal test (all KS p > 0.5). But the downstream classifier (RF) gets 0.61 ROC-AUC on real test vs 0.84 trained on real. Why?"

Output: Skill computes Spearman Frobenius gap = 0.42 (severe correlation collapse). Step 9 attributes failure to **correlation collapse**: SDG preserves per-column distributions but not pairwise structure. Recommends switching from a marginal-only generator (e.g. independent per-column sampler) to a joint generator (CTGAN with mode-specific normalization, or TVAE, or copula-based SDV with measured pairwise structure). Refuses to certify utility (utility ratio 0.73 / 0.86 well below threshold). Notes that "marginals look perfect" is the textbook signal of correlation collapse, not a sign the audit is wrong.

### Example 3: No real test set provided (anti-trigger)

Input: "I generated 100k synth records and I want to train a classifier and report utility. I don't have a held-out real set — the real data was used to fit the generator."

Output: Skill refuses to certify utility. Explains: TSTR requires real_test, and real_test must not overlap with the rows used to fit the SDG. Recommends the user partition the original real data into real_train (used to fit SDG) and real_test (held back from SDG fitting), then re-run the audit. If the SDG was already fit on the full real set, the user must either (a) collect a fresh real test set, or (b) accept that no utility certification is possible — only marginal / correlation fidelity, which is necessary but not sufficient. Does NOT default to TSTS-only (train on synth, test on synth), which would always pass and is meaningless.

## See also

- `ml-datasci/auditing-synthetic-data-leakage` — the privacy / membership-inference sibling; required when synth is shared externally
- `ml-datasci/auditing-train-test-split` — required pre-step; the real_train / real_test split must be leakage-free before this skill's audit means anything
- `ml-datasci/building-baseline-models` — the TRTR baseline in step 3 should include a Dummy classifier as well as logistic + RF
- `ml-datasci/evaluating-binary-classifiers` — for downstream-task scoring when `task_type = classification`
- `ml-datasci/evaluating-regression-models` — for downstream-task scoring when `task_type = regression`
- `workflow/auditing-data-quality` — required pre-step on the REAL source data; an SDG trained on a corrupt real set produces corrupt synth

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-5, skill 1) via PRAGMATIC discipline
