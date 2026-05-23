---
name: running-hyperparameter-sweep
description: >
  Designs and runs a disciplined hyperparameter sweep with Optuna or Ray Tune:
  defines a search space, picks a sampler (TPE / random / grid) and pruner
  (median / Hyperband / ASHA), splits the compute budget between sweep and
  final retrain, enforces seed stratification (≥ 3 seeds per candidate before
  declaring a winner) and a tuning-vs-test firewall so the held-out test set is
  never seen during search. Use when the user is about to call .fit() with
  default hyperparameters on a non-trivial model, when manual single-config
  tuning has stalled, when a sweep result looks suspiciously close to the
  defaults, or when planning compute for an expensive training run. Refuses to
  engage on tiny one-shot models where defaults are fine and on cases where no
  validation set exists.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - stats-student
evidence:
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Running Hyperparameter Sweep

## When to use

Trigger this skill when the user asks for or implies one of:

- "How do I tune hyperparameters for `<model>`?"
- "I'm getting 0.78 accuracy with defaults — can tuning help?"
- "I have 100 GPU-hours; how should I spend them on tuning vs final training?"
- "Optuna study setup", "Ray Tune setup", "Bayesian hyperparameter optimization"
- "Should I do grid search, random search, or Bayesian?"
- The user has tried tweaking 2–3 hyperparameters by hand and is asking for a more systematic approach
- Sweep results look weird (best trial ≈ defaults, or best trial wildly different per re-run) — indicates either flat landscape or bad seed strategy
- Need to budget compute across multiple candidate configs before kicking off the final training run

This skill pairs with `ml-datasci/scaffolding-pytorch-training-loop` (the trainable each trial wraps) and `ml-datasci/auditing-train-test-split` (the firewall that the sweep must respect).

## When NOT to use

Skip this skill and hand off or do nothing when:

- The model is sklearn `LogisticRegression` on a 1k-row tabular set — defaults are usually fine and the variance from CV is larger than any tuning gain
- No validation set exists — sweeping against the test set leaks; sweeping against the training set overfits the search. Hand off to `ml-datasci/auditing-train-test-split` first
- Compute budget is < ~10 full training runs — a sweep can't differentiate noise from signal at that scale; run defaults plus a small manual variation
- The user wants to tune the loss function or model architecture — that's neural architecture search (NAS), a different skill class
- Production constraints fix a hyperparameter (e.g., `batch_size = 1` for online inference) — the search space is degenerate
- This is a homework problem where the rubric expects grid search of a small space — follow the rubric, not the optimal strategy

## Quick start

User says: "I have a PyTorch image classifier. I want to tune learning rate, weight decay, and batch size. Budget is 64 GPU-hours."

Skill response (in order):

1. **Validate the firewall**: confirm a held-out test set exists and the sweep will use a separate validation set (never the test). Sweep on train→val; report final once on test. Cross-reference `ml-datasci/auditing-train-test-split`.
2. **Define the search space** in [`reference/optuna-example.py`](reference/optuna-example.py): `lr ~ loguniform(1e-5, 1e-1)`, `weight_decay ~ loguniform(1e-6, 1e-2)`, `batch_size ~ categorical([64, 128, 256, 512])`
3. **Pick sampler**: TPE (default Optuna) for low-d continuous spaces (~3–10 dims). Random for higher-d or as a sanity check. Grid only if the rubric demands it.
4. **Pick pruner**: ASHA (`SuccessiveHalvingPruner`) for expensive training — kills bad trials early. Median pruner is simpler and almost as good. Hyperband if user wants a textbook answer.
5. **Budget split**: spend ~60% on the sweep (e.g., 40 GPU-hours for ~50–80 trials with pruning), reserve 40% (24 GPU-hours) for the final retrain at the best config with ≥ 3 fresh seeds.
6. **Seed-stratify candidates**: before declaring a winner, retrain the top-3 configs with seeds {42, 1337, 2026} each. If the rank order changes across seeds, the gap is noise; report the seed-mean ± seed-SD per config.
7. **Set the failure-mode alarms**: if the best trial is the first trial sampled → sampler hasn't converged, budget was too small. If the best trial sits on a boundary of the search space → expand the range and re-sweep.
8. **Final test eval**: load best config, train on train+val with the best hyperparameters, evaluate once on test. Report this as the headline number — NOT the best validation score from the sweep.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| framework | "optuna" \| "ray-tune" \| "sklearn-search" | yes | — | Drives the API surface. Optuna for most cases; Ray Tune for distributed; sklearn `GridSearchCV` / `HalvingRandomSearchCV` for sklearn-native flows |
| n_trials | int | no | 50 | Number of sweep trials. < 20 trials = essentially random sampling; 50–200 is the productive zone for TPE on 3–10 dims |
| sampler | "tpe" \| "random" \| "cmaes" \| "grid" | no | "tpe" | Optuna sampler. TPE for low-d Bayesian; random as sanity baseline; CMA-ES for tightly continuous spaces; grid only when required |
| pruner | "asha" \| "median" \| "hyperband" \| "none" | no | "asha" | Trial-pruning policy. ASHA preferred for expensive training; "none" only when each trial is cheap |
| budget_split | float in [0, 1] | no | 0.6 | Fraction of total compute spent on the sweep (vs the final-retrain budget) |
| n_final_seeds | int | no | 3 | Number of fresh seeds for the final retrain of the best config |
| search_space | dict | yes | — | Per-hyperparameter distribution (loguniform / uniform / int / categorical) + bounds |
| validation_split | "predefined" \| "cv-k" | no | "predefined" | Use a held-out val set or k-fold CV inside each trial |
| direction | "maximize" \| "minimize" | yes | — | Optimization direction for the trial metric (accuracy / F1 → max; loss / RMSE → min) |
| timeout_seconds | int \| None | no | None | Wall-clock cap; trials beyond this are stopped |

## Workflow

Copy this checklist into the response and check off each item as it lands:

```
Hyperparameter-sweep progress:
- [ ] Step 1: Confirm train / val / test firewall — sweep on val only, test is locked
- [ ] Step 2: Define search space with explicit distributions and bounds
- [ ] Step 3: Pick sampler (TPE / random / CMA-ES / grid) and justify
- [ ] Step 4: Pick pruner (ASHA / median / Hyperband / none) and justify
- [ ] Step 5: Split budget: sweep_budget = budget_split × total; retrain_budget = (1 - budget_split) × total
- [ ] Step 6: Run the sweep with the chosen sampler + pruner + n_trials
- [ ] Step 7: Take top-K configs (K=3 default) and retrain each with n_final_seeds fresh seeds
- [ ] Step 8: Pick the winner by seed-mean (with seed-SD reported); flag if seed-SD > between-config gap
- [ ] Step 9: Sanity-check: best trial NOT trial #0; best params NOT on search-space boundary
- [ ] Step 10: Retrain winner on train+val with the locked test set; report test metric ONCE
```

### Step 1: Firewall

The test set is locked until step 10. The sweep sees only train + val. If the user has no val set, hand off to `ml-datasci/auditing-train-test-split` to create one (group-aware, temporally-aware, stratified as appropriate).

### Step 2: Search space distribution choices

| Hyperparameter | Right distribution | Why |
|---|---|---|
| Learning rate | log-uniform | Effect scales multiplicatively; 1e-4 → 1e-3 matters as much as 1e-3 → 1e-2 |
| Weight decay / L2 | log-uniform | Same reason |
| Dropout | uniform on [0, 0.5] | Linear in effective regularization on that range |
| Batch size | categorical on powers of 2 | Hardware-aligned; non-power-of-2 wastes GPU |
| Hidden units | log-uniform int OR categorical on powers of 2 | Capacity scales multiplicatively |
| Number of layers | int uniform | Discrete |
| Optimizer | categorical (AdamW / SGD / RMSprop) | Discrete |

### Step 3: Sampler

- **TPE** (Tree-structured Parzen Estimator) — Optuna default. Good for ≤ 10 dimensions, mixed continuous/categorical, moderate trial count (50–500).
- **Random** — sanity baseline. Always run random with the same budget once; if TPE ≈ random, the landscape is flat and tuning isn't the bottleneck.
- **CMA-ES** — strictly continuous, tight Gaussian neighborhoods; good for fine-tuning around a known-good point.
- **Grid** — only when the rubric demands or the space is genuinely small (< 25 points). Grid is wasteful in high dimensions.

### Step 4: Pruner

- **ASHA** (`SuccessiveHalvingPruner`) — promote the top 1/η trials after each rung, kill the rest. Default η = 3. Best for expensive training.
- **Median** — at each step, prune any trial below the running median of completed trials. Simpler, almost as good.
- **Hyperband** — runs ASHA at multiple bracket sizes. Textbook answer; more compute overhead than ASHA alone.
- **none** — no pruning. Use only when each trial is cheap (< 1 minute).

### Step 5: Budget split

Reserve compute for the final retrain. Default split: 60% sweep / 40% retrain. The retrain is where the seed-stratified comparison happens — under-budgeting it means a single-seed winner that may not generalize.

### Step 7 — Step 8: Seed stratification

Single-seed winners are noise. The minimum discipline:

1. Take top-K=3 configs from the sweep ranked by val metric
2. Retrain each with seeds {42, 1337, 2026} (or 3 fresh seeds of the user's choice)
3. Report `metric_mean ± metric_std` per config
4. Pick winner by mean; flag prominently if the std overlaps the mean gap between configs

If the top-3 rank order changes across seeds, the configs are statistically indistinguishable. Report this honestly; pick the simplest config among the indistinguishable set.

### Step 9: Failure-mode alarms

- **Best trial is trial #0** — sampler hasn't converged. Increase `n_trials` or check for a search-space bug.
- **Best params sit on boundary** — `lr = 1e-1` when upper bound is `1e-1` → the optimum is OUTSIDE the search space. Expand and re-sweep.
- **Best trial ≈ defaults** — either the landscape is flat (tuning doesn't matter), or the sweep is mis-configured (wrong metric direction, bad CV split). Run random-sampling baseline; if it matches TPE, the landscape really is flat.
- **Best trial val_metric >> test_metric** — sweep overfit the val set. Reserve a second val fold or use nested CV.

### Step 10: Final test eval — ONCE

After picking the winner: retrain on `train ∪ val` (more data than sweep trials saw), evaluate once on `test`. Report this number. Do NOT iterate on the test metric — that's the moment the firewall breaks.

## Outputs

A short markdown report:

1. **Search-space table** — each hyperparameter, distribution, bounds, sampled best value
2. **Sweep results plot** — trial number × metric, with pruned trials marked
3. **Top-K config table** — top 3 by val metric, with seed-mean ± seed-SD across `n_final_seeds`
4. **Winner declaration** — best config + the seed-mean gap to second place, flagged if not statistically separable
5. **Final test metric** — one number, computed once on the locked test set
6. **Compute accounting** — sweep_budget_used / sweep_budget_planned, retrain_budget_used / retrain_budget_planned

## Failure modes

- **Test-set leakage via sweep** — sweep on test instead of val → reported "best" is over-fit; real generalization is worse. Caught by: Step 1 firewall check + Step 10 single-shot test eval.
- **Single-seed winner** — best trial wins by 0.001 over second-best; on a different seed the rank flips. Caught by: Step 7 mandates `n_final_seeds ≥ 3` and Step 8 reports seed-SD.
- **Best on boundary** — search space too narrow; the real optimum is outside. Caught by: Step 9 alarm; expand range and re-sweep.
- **Wrong direction** — `direction="minimize"` on accuracy or `"maximize"` on loss → the best trial is the worst model. Caught by: `direction` argument is required (no default); explicit choice forces the user to think about it.
- **Pruner with too-aggressive η** — ASHA with η = 10 kills 90% of trials at each rung → only initial fast-starters survive, but slow-starters that would have won later are killed. Caught by: default η = 3 in the pruner config; do not raise η without justification.
- **Pruning trials in a noisy-metric scenario** — early-epoch validation metrics are noisy; ASHA prunes based on noise. Caught by: recommend `min_resource ≥ 5 epochs` (don't prune in the first few epochs) for any task with high per-epoch variance.
- **Categorical sampled as continuous** — `lr ~ uniform(1e-5, 1e-1)` instead of `loguniform` → sampler concentrates on the high end of the range; the true optimum at `1e-4` is starved. Caught by: Step 2 distribution table; log-uniform for any multiplicative hyperparameter.
- **Budget exhausted on sweep, no retrain** — `budget_split = 1.0` → no retrain budget → reported winner has been seen by exactly one seed. Caught by: `budget_split` default 0.6; warn loudly if user sets > 0.8.

## References

- [`reference/optuna-example.py`](reference/optuna-example.py) — copy-paste Optuna study with TPE + ASHA + seed-stratified final retrain
- [`reference/sweep-design-cheatsheet.md`](reference/sweep-design-cheatsheet.md) — sampler vs pruner choice matrix, budget split heuristics, boundary-alarm checklist
- [Optuna docs](https://optuna.readthedocs.io/) — official sampler / pruner reference
- [Ray Tune docs](https://docs.ray.io/en/latest/tune/index.html) — distributed alternative when the sweep needs > 1 node
- [Successive Halving Algorithm paper](https://arxiv.org/abs/1502.07943) — origin of ASHA / Hyperband
- `ml-datasci/auditing-train-test-split` — the firewall the sweep must respect
- `ml-datasci/scaffolding-pytorch-training-loop` — the trainable each trial wraps

## Examples

### Example 1: Image classifier, 3 hyperparameters, 64 GPU-hour budget (happy-path)

Input: "I have a PyTorch image classifier. I want to tune learning rate, weight decay, and batch size. I have 64 GPU-hours total."

Output: Confirm train/val/test split exists with test locked. Define `lr ~ loguniform(1e-5, 1e-1)`, `weight_decay ~ loguniform(1e-6, 1e-2)`, `batch_size ~ categorical([64, 128, 256, 512])`. Use TPE + ASHA. Budget split: 40 GPU-hours / ~60 trials with pruning for sweep, 24 GPU-hours for 3-seed retrain of top-3 configs (i.e., 9 retrains, ~2.7 GPU-hours each). After sweep, take top 3 by val metric, retrain each with seeds {42, 1337, 2026}, report seed-mean ± SD, declare winner, retrain on train ∪ val with the winning config + final seed, evaluate on locked test set once. Report sweep config + winner + test metric.

### Example 2: Best trial is the first one sampled (edge-case)

Input: "I ran an Optuna study with 30 trials. The best trial is trial #0. Is that result valid?"

Output: No — trial #0 is the TPE sampler's initial random sample, before TPE has any history to learn from. If trial #0 wins, TPE never improved on random; the sweep either had too few trials (TPE needs ~25 trials of history before its proposals beat random), or the landscape is flat (tuning isn't the bottleneck), or there's a search-space bug (e.g., wrong direction, the "good" region is the user's default and TPE keeps proposing further from it). Diagnose by: (1) re-running with a random sampler on the same budget — if random matches TPE, landscape is flat and tuning doesn't help; (2) checking metric direction; (3) inspecting the metric history (was the metric monotonically getting worse? probably wrong direction). Do NOT ship the trial-0 config as the winner without explicitly verifying defaults are equivalent on the val set.

### Example 3: Sklearn LogReg on a 1k-row tabular set (anti-trigger)

Input: "I'm fitting sklearn LogisticRegression on a 1,000-row tabular classification dataset (40 features, 60/40 class split). Should I run a hyperparameter sweep on C, penalty, and solver?"

Output: Probably not worth it. For LogReg at this scale: defaults (`C=1.0`, L2 penalty, lbfgs solver) are near-optimal in the vast majority of cases. CV variance on a 1,000-row dataset is typically larger than the tuning gain — sweeping 50 configs with 5-fold CV uses 250 fits, and the winner-vs-defaults gap will be smaller than the seed-to-seed CV noise. Recommendation: skip the formal sweep. Run defaults plus 2–3 manual variations (`C ∈ {0.1, 1.0, 10.0}`, `penalty ∈ {l1, l2}`). If a structural data issue is suspected, audit the data first (hand off to `ml-datasci/auditing-train-test-split` for split integrity + `building-baseline-models` for the chance baseline). Reserve a real sweep for the case where the model is genuinely expensive (deep learning, gradient boosting on 100k+ rows) or where defaults are obviously failing.

## See also

- `ml-datasci/scaffolding-pytorch-training-loop` — the trainable each Optuna / Ray trial wraps; seed-stratified retrain uses the same loop
- `ml-datasci/auditing-train-test-split` — required prerequisite (the sweep firewall depends on a correct split)
- `ml-datasci/building-baseline-models` — run the baseline ladder BEFORE the sweep; if defaults beat baselines by a wide margin, tuning probably doesn't move the needle
- `workflow/enforcing-seed-hygiene` — seed call discipline for the per-trial trainables and the final-retrain seeds

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
