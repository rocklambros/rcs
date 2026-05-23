---
name: scaffolding-pytorch-training-loop
description: >
  Scaffolds a production-grade PyTorch training loop with deterministic seeding,
  mixed-precision (AMP) with grad-scaler, gradient clipping, learning-rate
  scheduling, early stopping on a validation metric, checkpoint save/load with
  full optimizer + scheduler + scaler state, and run telemetry to TensorBoard or
  Weights & Biases. Use when starting a new PyTorch training script for a vision
  / NLP / tabular deep-learning model, when an existing training loop lacks
  resume-from-checkpoint after a preemption / OOM crash, when training cost is
  high enough that AMP and LR-scheduling matter, or when results vary run-to-run
  on the same seed. Refuses to scaffold around sklearn / xgboost / lightgbm
  (those are different ecosystems) and skips on toy MNIST-tier scripts where the
  full machinery is overhead.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - stats-student
evidence:
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - llm-toxicity-visual-analysis
  - incident-rank-validation
last-updated: 2026-05-23
---

# Scaffolding PyTorch Training Loop

## When to use

Trigger this skill when the user asks for or implies one of:

- "I'm starting a new PyTorch training script for `<vision / NLP / tabular DL>`"
- "My training crashed at epoch N and I lost all progress" — needs resume-from-checkpoint
- "Training results differ between runs with the same seed" — needs full determinism (seed + cuDNN flags + dataloader workers)
- "I want to use mixed precision to fit a bigger batch / train faster"
- "How do I add a learning-rate schedule / early stopping / gradient clipping?"
- "I'm preempting on a spot instance / SLURM cluster and need to survive restarts"
- "Set up a training loop with W&B / TensorBoard logging"
- Migrating a notebook-tier `for batch in loader: model(...)` loop to something shippable

This skill pairs with `workflow/enforcing-seed-hygiene` (the seed call multi-library cookbook), `ml-datasci/running-hyperparameter-sweep` (Optuna/Ray over this loop), and `ml-datasci/auditing-deep-learning-overfit` (post-training diagnostics).

## When NOT to use

Skip this skill and hand off or do nothing when:

- The framework is sklearn, xgboost, lightgbm, statsmodels, or any non-PyTorch DL framework (JAX, TensorFlow) — the AMP / scaler / DataLoader machinery is PyTorch-specific
- The model is a 2-minute MNIST script that runs once and is thrown away — the resume / scheduler / scaler scaffolding is overhead
- The user is using PyTorch Lightning, Hugging Face `Trainer`, or fastai — those frameworks ship the loop already; the right move is to learn their callbacks API, not rewrite the loop
- The task is pure inference / serving (different concerns — see `ml-datasci/packaging-model-for-deployment`, planned)
- The user wants distributed training (DDP / FSDP / DeepSpeed) — call out that this skill covers single-process loops and the multi-process patterns add their own scaffolding layer

## Quick start

User says: "I'm starting a ResNet-50 image classifier on CIFAR-100. I want a production training loop — full determinism, AMP, LR schedule, early stop, checkpoint, W&B."

Skill response (in order):

1. **Seed everything first cell**: `set_seed(42)` covering Python / NumPy / PyTorch / cuDNN (cross-reference `workflow/enforcing-seed-hygiene`)
2. **Build the loop skeleton** from [`reference/training-loop.py`](reference/training-loop.py): train_one_epoch + validate + save_checkpoint + load_checkpoint + main
3. **Wire AMP**: `torch.cuda.amp.autocast()` + `GradScaler()` — scaler must be in checkpoint state
4. **Add LR scheduler**: `CosineAnnealingLR(T_max=epochs)` (default) or `OneCycleLR` for short training; scheduler must be in checkpoint state
5. **Gradient clipping**: `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)` after `scaler.unscale_`
6. **Early stopping**: track best validation metric; stop when no improvement for `patience` epochs (default 10)
7. **Checkpoint**: save model + optimizer + scheduler + scaler + epoch + best_metric + RNG states on every `save_every` epochs AND on best-metric improvement
8. **W&B init**: `wandb.init(project=..., config=hparams, resume="allow", id=run_id)` — `resume="allow"` is the key flag for crash recovery
9. **Run**: surface the launch command + how to resume from a checkpoint

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| task | "image-classification" \| "text-classification" \| "regression" \| "segmentation" \| "other" | yes | — | Drives loss choice and metric defaults (accuracy / F1 / RMSE / Dice / user-supplied) |
| seed | int | no | 42 | Reproducibility seed (applied to Python, NumPy, PyTorch CPU + CUDA, cuDNN, DataLoader workers) |
| precision | "fp32" \| "fp16-amp" \| "bf16-amp" | no | "fp16-amp" | AMP path. bf16 preferred on Ampere+; fp16 needs the GradScaler |
| max_epochs | int | yes | — | Hard ceiling; early-stopping may terminate sooner |
| patience | int | no | 10 | Early-stop patience (epochs with no improvement on monitored metric) |
| monitor_metric | str | no | "val_loss" | Metric to monitor for early-stop + best-checkpoint selection |
| monitor_mode | "min" \| "max" | no | "min" | Lower-is-better (loss) vs higher-is-better (accuracy / F1) |
| grad_clip_norm | float \| None | no | 1.0 | `clip_grad_norm_` max_norm; `None` disables clipping |
| scheduler | "cosine" \| "onecycle" \| "step" \| "plateau" \| "none" | no | "cosine" | LR schedule family |
| logger | "wandb" \| "tensorboard" \| "none" | no | "wandb" | Run-telemetry backend |
| ckpt_dir | str (path) | no | "./checkpoints" | Where to write `last.pt` + `best.pt` |
| resume_from | str (path) \| None | no | None | Path to a checkpoint to resume from; `None` = fresh start |
| save_every | int | no | 1 | Save `last.pt` every N epochs (independent of best-checkpoint save) |

## Workflow

Copy this checklist into the response and check off each item as it lands in the user's code:

```
PyTorch training-loop scaffolding progress:
- [ ] Step 1: Seed everything (Python, NumPy, torch CPU+CUDA, cuDNN deterministic, DataLoader workers)
- [ ] Step 2: Build model + loss + optimizer + scheduler + AMP scaler
- [ ] Step 3: Wire train_one_epoch (forward → autocast → loss → scaler.scale.backward → clip → scaler.step → scaler.update)
- [ ] Step 4: Wire validate (no_grad + autocast, return loss + monitored metric)
- [ ] Step 5: Wire save_checkpoint (model + optimizer + scheduler + scaler + epoch + best_metric + RNG)
- [ ] Step 6: Wire load_checkpoint (mirror of save; resumes optimizer/scheduler/scaler/RNG, NOT just weights)
- [ ] Step 7: Wire early stopping on monitor_metric with monitor_mode + patience
- [ ] Step 8: Wire logger (W&B init with resume='allow' + run_id, or TensorBoard SummaryWriter)
- [ ] Step 9: Wire main: parse args → seed → build → load_checkpoint(resume_from) → train_loop → final eval
- [ ] Step 10: Surface launch command + resume command in the README block
```

### Step 1: Determinism

```python
def set_seed(seed: int) -> None:
    import random, os
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False  # mutually exclusive with deterministic
```

DataLoader workers need their own seed via the `worker_init_fn` argument — without it, augmentation pipelines drift across runs. See [`reference/training-loop.py`](reference/training-loop.py) for the full pattern including `generator=torch.Generator().manual_seed(seed)`.

Cross-platform CPU/GPU determinism: pin `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1` if the user reports laptop-vs-server result drift (this is the incident-rank-validation lesson — applies to PyTorch JAX sampler-style work).

### Step 2 — Step 9: Loop skeleton

The full ~150-line skeleton lives in [`reference/training-loop.py`](reference/training-loop.py). Copy it, fill in `build_model()`, `build_dataloaders()`, and `compute_metric()` for the user's task. The skeleton already wires AMP, the scaler, the scheduler, early-stop, the checkpoint round-trip, and W&B `resume="allow"`.

### Step 10: Launch + resume

Surface two commands in the user's README:

```bash
# Fresh start
python train.py --task image-classification --max-epochs 200 --seed 42

# Resume after preemption / crash
python train.py --task image-classification --max-epochs 200 --seed 42 \
    --resume-from checkpoints/last.pt
```

The resume path MUST restore optimizer + scheduler + scaler + epoch + best_metric + RNG state, not just model weights. Loading weights alone gives the wrong LR (scheduler reset), wrong optimizer momentum, and a fresh RNG that re-shuffles data — the run is not actually resumed, it's restarted from a new initialization.

## Outputs

A complete training script (`train.py`) plus:

1. **README block** — launch + resume commands
2. **Hyperparameter block** — every config value pinned (seed, lr, batch_size, weight_decay, epochs, patience, grad_clip_norm)
3. **Checkpoint dir** — `last.pt` (most recent) + `best.pt` (best monitor metric); both contain full restorable state
4. **Run telemetry** — W&B run URL or TensorBoard log dir, with the run_id surfaced so resume can find the same run
5. **Final eval block** — load `best.pt`, run on held-out test set once, log final metrics (separate from per-epoch validation)

## Failure modes

- **Resume restores only model weights** — `model.load_state_dict()` without restoring optimizer / scheduler / scaler / epoch means the LR is reset, momentum is gone, and gradient scale starts fresh. The run resets, it doesn't resume. Caught by: Step 6 mandates the full mirror in `load_checkpoint`.
- **AMP without GradScaler on fp16** — produces silent NaN losses after a few epochs (gradient underflow). Caught by: Step 3 wires `GradScaler` whenever `precision == "fp16-amp"`; bf16 path skips the scaler (bf16 has the fp32 dynamic range so no scaling needed).
- **`cudnn.benchmark = True` with determinism flag** — `benchmark=True` selects algorithms by input shape and breaks determinism. Caught by: Step 1 sets `benchmark = False` after `deterministic = True`; the linter inside the reference snippet rejects setting both true.
- **DataLoader workers re-seed per process** — without `worker_init_fn`, each worker picks up a different RNG and augmentation differs across runs. Caught by: Step 1 reference script wires `worker_init_fn` and a `Generator()` with the user's seed.
- **Best-checkpoint selection on the wrong metric direction** — `monitor_metric = "val_accuracy"` with `monitor_mode = "min"` silently picks the worst model. Caught by: Step 7 requires `monitor_mode` argument; the script asserts mode is in `{"min", "max"}` and fails fast.
- **W&B `resume="must"` vs `"allow"`** — `"must"` errors if the run_id doesn't exist (breaks first launch); `"never"` errors if the run_id DOES exist (breaks resume). Caught by: Step 8 specifies `resume="allow"` (works in both cases) and a stable `run_id` (e.g., a hash of the config + seed).
- **Checkpoint write race on preemption** — script gets SIGTERM mid-save → corrupted `last.pt`. Caught by: reference script writes to `last.pt.tmp` then `os.replace(last.pt.tmp, last.pt)`; the rename is atomic on POSIX.
- **RNG state not in checkpoint** — augmentation order drifts after resume even with the same seed because the global RNG has been advanced. Caught by: `save_checkpoint` includes `torch.get_rng_state()` and `torch.cuda.get_rng_state_all()` plus `random.getstate()` and `np.random.get_state()`.

## References

- [`reference/training-loop.py`](reference/training-loop.py) — copy-paste skeleton: ~150 lines, fully wired (seed + AMP + scheduler + clip + early-stop + atomic-write checkpoint + W&B resume)
- [`reference/checkpoint-format.md`](reference/checkpoint-format.md) — the exact dict keys saved + restored, atomic-write pattern, and a `tools/inspect_checkpoint.py` snippet
- [PyTorch reproducibility docs](https://pytorch.org/docs/stable/notes/randomness.html) — upstream guidance on `cudnn.deterministic` + the cross-CUDA-version caveats
- [W&B resume reference](https://docs.wandb.ai/guides/runs/resuming) — `resume="allow" | "must" | "never"` semantics
- `workflow/enforcing-seed-hygiene` — sibling skill; the first-cell seed pattern + CPU-pin determinism for cross-platform reproducibility

## Examples

### Example 1: Fresh ResNet-50 on CIFAR-100 (happy-path)

Input: "I'm starting a ResNet-50 image classifier on CIFAR-100. Full determinism, AMP, LR schedule, early stop, checkpoint, W&B. Scaffold it."

Output: Produce `train.py` from the reference skeleton with `task="image-classification"`, `precision="fp16-amp"` (or `"bf16-amp"` if Ampere+ available), `scheduler="cosine"` with `T_max = max_epochs`, `patience=10`, `monitor_metric="val_acc"`, `monitor_mode="max"`. Wire `set_seed(42)` + `worker_init_fn`. W&B `resume="allow"` with run_id = `hash(config + seed)`. Surface launch + resume commands. Hand off `compute_metric` to the user to fill in (top-1 accuracy here). Estimated wall time and disk for checkpoints surfaced as guidance.

### Example 2: Resume after SLURM preemption (edge-case)

Input: "My training was at epoch 45 of 200 and the SLURM job got preempted. I have `checkpoints/last.pt`. How do I resume?"

Output: Verify the checkpoint contains the full restorable state (model + optimizer + scheduler + scaler + epoch + best_metric + RNG). If yes: `python train.py --resume-from checkpoints/last.pt --max-epochs 200 --seed 42`. If only weights: explain why this is restart, not resume — the LR schedule will reset to epoch 0 LR, momentum is gone, augmentation order differs. Fix path: open the checkpoint with `torch.load`, inspect `keys()`. If missing optimizer/scheduler/scaler/RNG, recommend losing this resume and re-training from epoch 0 with the proper checkpoint format; future runs will resume correctly. W&B side: `resume="allow"` with the SAME run_id will append to the existing run instead of forking a new one.

### Example 3: Sklearn / xgboost script (anti-trigger)

Input: "I'm training an XGBoost binary classifier on tabular fraud data. Set up a training loop with AMP and a learning-rate scheduler."

Output: This is the wrong scaffolding. XGBoost has no AMP (no GPU tensor autocast), no `GradScaler`, and its "learning rate" (`eta`) is a single hyperparameter, not a per-iteration schedule. The training loop is `xgb.train(...)` or `XGBClassifier.fit(...)` — one call, not a per-epoch Python loop. Recommend: pin a seed (`random_state=42`), use early stopping (`early_stopping_rounds=...`), enable `tree_method="hist"` for speed, and validate via cross-validation or a held-out set. Hand off to `ml-datasci/evaluating-binary-classifiers` for post-training metrics. Skip the PyTorch loop scaffolding entirely.

## See also

- `workflow/enforcing-seed-hygiene` — multi-library seed cookbook + CPU-pin determinism (covers what `set_seed` does in detail)
- `ml-datasci/running-hyperparameter-sweep` — Optuna / Ray Tune wrapped around this loop with seed-stratified trials
- `ml-datasci/auditing-deep-learning-overfit` (planned) — post-training diagnostics: train/val gap, learning curves, weight-norm growth
- `ml-datasci/packaging-model-for-deployment` (planned) — once `best.pt` exists, how to ship it (ONNX / torchscript / signature + smoke test)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
