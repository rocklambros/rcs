# Sweep Design Cheatsheet

Reference matrix for picking sampler / pruner / budget split / alarm thresholds without re-deriving from first principles every time.

## Sampler choice

| Situation | Sampler | Why |
|---|---|---|
| 3–10 dim mixed continuous + categorical, 50–500 trial budget | TPE | Default Optuna; Bayesian, robust |
| Want a sanity baseline against any other method | Random | Always run once; if your fancy sampler ≈ random, the landscape is flat |
| Strictly continuous, fine-tuning around a known-good point | CMA-ES | Tight Gaussian neighborhoods, good local refinement |
| ≤ 25 grid points total AND the rubric demands grid | Grid | Otherwise wasteful in high dimensions |
| > 10 dimensions | Don't sweep — feature-select or freeze most | Curse of dimensionality wrecks sample efficiency |

## Pruner choice

| Situation | Pruner | Why |
|---|---|---|
| Each trial is expensive (> 30 min training) | ASHA (SuccessiveHalving) | Kill bad trials early; default η = 3, min_resource = 5 epochs |
| Each trial is cheap (< 1 min) | none | Pruning overhead exceeds savings |
| Want a textbook answer; willing to spend the compute | Hyperband | ASHA at multiple bracket sizes; more robust to bracket choice |
| Metric is very noisy early in training | Median pruner with min_resource ≥ 10 | Avoid pruning on early-epoch noise |

## Budget split heuristic

Total compute = sweep + retrain. Default split: 60% sweep / 40% retrain.

| If... | Then... |
|---|---|
| Highly expensive single trial, only 10–20 trials affordable | 80% sweep / 20% retrain — but accept that the result is noisy and re-sweep next quarter |
| Cheap trials, can afford 200+ | 50% sweep / 50% retrain — invest in seed stratification |
| Already have good baseline numbers and trust them | 40% sweep / 60% retrain — most budget goes to picking among similar configs |

## Distribution choice per hyperparameter

| Hyperparameter | Distribution | Sample bounds |
|---|---|---|
| Learning rate | `loguniform` | (1e-5, 1e-1) for SGD / AdamW |
| Weight decay / L2 | `loguniform` | (1e-6, 1e-2) |
| Dropout | `uniform` | [0, 0.5] |
| Momentum (SGD) | `uniform` | [0.8, 0.99] |
| Beta1 (Adam) | `uniform` | [0.85, 0.99] |
| Beta2 (Adam) | `uniform` | [0.99, 0.9999] |
| Batch size | `categorical` powers of 2 | [16, 32, 64, 128, 256, 512] |
| Hidden units | `categorical` powers of 2 OR `loguniform-int` | [64, 4096] |
| Number of layers | `int` uniform | [2, 12] (for typical CNNs / transformers) |
| Label smoothing | `uniform` | [0.0, 0.2] |
| Optimizer | `categorical` | {adamw, sgd, rmsprop} |
| Scheduler | `categorical` | {cosine, onecycle, step, plateau} |

## Alarm thresholds

| Alarm | Threshold | Meaning |
|---|---|---|
| Best trial is trial #0 | trial.number == 0 | TPE never improved on initial random — too few trials OR landscape is flat OR direction is wrong |
| Best param near boundary | `abs(val - bound) / bound < 0.1` (log scale) OR within 5% of bound (linear) | Real optimum is outside the search space; expand and re-sweep |
| Top-K configs not separable | `gap_to_runner_up < max(top_k_stds)` | Winner is noise; pick the simpler config |
| Pruned > 80% of trials | `n_pruned / n_trials > 0.8` | ASHA η too aggressive (default η=3); reduce to η=2 if budget allows |
| Sweep val_metric >> test_metric | Test < sweep best by > 1 SD of CV variance | Sweep overfit the val set; need nested CV or a second val fold |

## When to skip the sweep entirely

- Sklearn-default-friendly models on small data (logreg, naive bayes, k-NN) — defaults are near-optimal, CV variance > tuning gain
- < 10 full trials affordable — sweep can't differentiate noise from signal
- No validation set exists — fix the split first (`ml-datasci/auditing-train-test-split`)
- The hyperparameter being tuned is fixed by production constraints
- The expected gain is < the seed-to-seed variance you've already measured

## Tooling notes

- **Optuna 4.x** — default for single-machine sweeps. Storage in `optuna.create_study(storage="sqlite:///sweep.db")` for resume / parallelism on one machine.
- **Ray Tune** — multi-node, multi-GPU. Use when one trial fits on one GPU but you have a fleet.
- **Sklearn `HalvingRandomSearchCV`** — sklearn-native, integrates with `cross_validate`. Lower ceiling than Optuna but lower setup cost.
- **`wandb.sweep`** — friendly UI, integrates with W&B logs. Same algorithms internally (random / grid / Bayesian) but a wrapper, not a primary engine.
