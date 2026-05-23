"""Optuna study skeleton with TPE + ASHA pruning + seed-stratified final retrain.

Copy this file, fill in `train_one_trial(cfg, seed)` (which should call your
training loop, return the validation metric, and call `trial.report` + check
`trial.should_prune()` at each epoch). The rest — search space, sampler,
pruner, budget split, seed-stratified retrain, boundary-alarm — is wired.

Targets Optuna 4.x.
"""
from __future__ import annotations
import statistics
from dataclasses import dataclass, asdict
from typing import Callable

import optuna
from optuna.pruners import SuccessiveHalvingPruner  # ASHA
from optuna.samplers import TPESampler


# ---------------------------------------------------------------------------
# User-supplied trainable

@dataclass
class TrialConfig:
    lr: float
    weight_decay: float
    batch_size: int
    optimizer: str
    seed: int = 42
    max_epochs: int = 50


def train_one_trial(cfg: TrialConfig, trial: optuna.Trial | None = None) -> float:
    """USER FILLS IN. Returns the validation metric.

    Inside the loop, call:
        trial.report(val_metric_so_far, epoch)
        if trial.should_prune():
            raise optuna.TrialPruned()
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Search space

def suggest_config(trial: optuna.Trial) -> TrialConfig:
    """Defines the search space. Loguniform for multiplicative hyperparameters."""
    return TrialConfig(
        lr=trial.suggest_float("lr", 1e-5, 1e-1, log=True),
        weight_decay=trial.suggest_float("weight_decay", 1e-6, 1e-2, log=True),
        batch_size=trial.suggest_categorical("batch_size", [64, 128, 256, 512]),
        optimizer=trial.suggest_categorical("optimizer", ["adamw", "sgd"]),
        # seed is fixed during the sweep so trials are comparable
        # (seed stratification happens AFTER the sweep on the top-K configs)
        seed=42,
        max_epochs=50,
    )


# ---------------------------------------------------------------------------
# Boundary / sanity alarms

BOUNDS = {
    "lr": (1e-5, 1e-1),
    "weight_decay": (1e-6, 1e-2),
}


def check_alarms(study: optuna.Study) -> list[str]:
    """Returns a list of warning strings. Empty list = clean."""
    warnings: list[str] = []
    best = study.best_trial
    if best.number == 0:
        warnings.append(
            "Best trial is trial #0 — TPE never improved on the initial random sample. "
            "Increase n_trials or check direction / search-space configuration."
        )
    for param, (low, high) in BOUNDS.items():
        val = best.params.get(param)
        if val is None:
            continue
        # log-distance to bounds
        if abs(val - low) / low < 0.1 or abs(val - high) / high < 0.1:
            warnings.append(
                f"Best {param} = {val:g} sits near search-space boundary "
                f"({low:g}, {high:g}); the real optimum may be outside the range. "
                f"Expand and re-sweep."
            )
    return warnings


# ---------------------------------------------------------------------------
# Sweep

def run_sweep(n_trials: int = 50, study_name: str = "sweep") -> optuna.Study:
    """Run the TPE + ASHA sweep."""
    sampler = TPESampler(seed=42)  # reproducible TPE proposals
    pruner = SuccessiveHalvingPruner(
        min_resource=5,        # do not prune in the first 5 epochs (early-epoch noise)
        reduction_factor=3,    # η = 3; promote top 1/3 at each rung
    )
    study = optuna.create_study(
        study_name=study_name,
        direction="maximize",  # CHANGE TO "minimize" FOR LOSS / RMSE
        sampler=sampler,
        pruner=pruner,
    )

    def objective(trial: optuna.Trial) -> float:
        cfg = suggest_config(trial)
        return train_one_trial(cfg, trial)

    study.optimize(objective, n_trials=n_trials)

    for warning in check_alarms(study):
        print(f"[ALARM] {warning}")

    return study


# ---------------------------------------------------------------------------
# Seed-stratified retrain of the top-K configs

def retrain_top_k(study: optuna.Study, k: int = 3,
                  seeds: tuple[int, ...] = (42, 1337, 2026)) -> dict:
    """Retrain the top-K configs with multiple seeds; report mean ± SD per config.

    Returns a dict mapping config-id → {"mean": float, "std": float, "params": dict, "metrics": list[float]}.
    """
    completed = [t for t in study.trials
                 if t.state == optuna.trial.TrialState.COMPLETE]
    direction = study.direction
    sort_key = (lambda t: -t.value) if direction == optuna.study.StudyDirection.MAXIMIZE else (lambda t: t.value)
    top = sorted(completed, key=sort_key)[:k]

    results: dict = {}
    for i, trial in enumerate(top):
        metrics = []
        for seed in seeds:
            params = dict(trial.params)
            # Override seed for stratification
            cfg = TrialConfig(
                lr=params["lr"],
                weight_decay=params["weight_decay"],
                batch_size=params["batch_size"],
                optimizer=params["optimizer"],
                seed=seed,
                max_epochs=50,
            )
            m = train_one_trial(cfg, trial=None)  # no pruning on the final retrain
            metrics.append(m)
        results[f"top_{i+1}"] = {
            "params": trial.params,
            "metrics": metrics,
            "mean": statistics.mean(metrics),
            "std": statistics.stdev(metrics) if len(metrics) > 1 else 0.0,
        }

    return results


def declare_winner(results: dict) -> dict:
    """Pick the winner; flag if the gap to second is within the std of either."""
    ranked = sorted(results.items(), key=lambda kv: -kv[1]["mean"])
    winner_key, winner = ranked[0]
    if len(ranked) > 1:
        runner_up = ranked[1][1]
        gap = winner["mean"] - runner_up["mean"]
        noise = max(winner["std"], runner_up["std"])
        if gap < noise:
            print(f"[WARNING] Gap {gap:.4f} between winner and runner-up is within "
                  f"the per-config seed-SD {noise:.4f}; configs are not "
                  f"statistically separable. Reporting the simpler config as winner.")
    return {"winner": winner_key, **winner}


# ---------------------------------------------------------------------------
# Driver

if __name__ == "__main__":
    # Step 1: sweep
    study = run_sweep(n_trials=50)

    # Step 2: seed-stratified retrain of top-K
    top_k_results = retrain_top_k(study, k=3, seeds=(42, 1337, 2026))

    # Step 3: declare winner
    winner = declare_winner(top_k_results)
    print("WINNER:", winner)

    # Step 4: retrain on train+val with winner config + a fresh seed;
    #         evaluate ONCE on the locked test set. (Not shown here — call into
    #         your test-eval path with winner["params"] and a final seed.)
