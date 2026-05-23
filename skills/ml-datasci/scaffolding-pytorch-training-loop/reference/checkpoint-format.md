# Checkpoint Format

The canonical checkpoint dict written by `save_checkpoint` in [`training-loop.py`](training-loop.py) and consumed by `load_checkpoint`. Restoring less than the full set turns "resume" into "restart from a different initialization."

## Required keys

| Key | Type | Why it matters |
|---|---|---|
| `model` | `state_dict` | Network weights. Necessary but NOT sufficient on its own. |
| `optimizer` | `state_dict` | Adam/AdamW momentum buffers (`exp_avg`, `exp_avg_sq`). Dropping these resets gradient momentum to zero — the next few steps are wildly off-policy and the loss spikes. |
| `scheduler` | `state_dict` or None | The internal step counter and last LR. Dropping these resets the cosine/onecycle schedule to epoch 0 → the LR jumps back up and undoes the late-training annealing. |
| `scaler` | `state_dict` or None | The GradScaler dynamic scale factor. Dropping it on an fp16 run resets to default scale → first few resume steps overflow or underflow until the scaler re-converges. |
| `epoch` | int | Where to resume the outer loop. Resume on `epoch + 1`. |
| `best_metric` | float | Carry forward the early-stop monitor. Resetting this means the early-stop counter restarts and a worse model could be saved as `best.pt`. |
| `rng_python` | tuple | `random.getstate()`. Augmentation pipelines that use Python `random` advance independently of NumPy and torch. |
| `rng_numpy` | tuple | `np.random.get_state()`. Same reason. |
| `rng_torch` | Tensor | `torch.get_rng_state()`. DataLoader shuffling and torch-native augmentation. |
| `rng_torch_cuda` | list[Tensor] or None | `torch.cuda.get_rng_state_all()`. CUDA-side dropout, sampling, augmentation. |

## Atomic write

Preemption SIGTERM can land mid-`torch.save`. Write to `.tmp` then `os.replace` — the rename is atomic on POSIX, so the next resume always reads a complete file (either the old one or the new one, never a half-written one).

```python
tmp = path.with_suffix(path.suffix + ".tmp")
torch.save(state, tmp)
os.replace(tmp, path)
```

`os.replace` is atomic on POSIX (per `man 2 rename` — same-filesystem rename). On Windows the guarantee is weaker; for SLURM clusters, the checkpoint path should be on a POSIX filesystem.

## last.pt vs best.pt

- `last.pt` — written every `save_every` epochs regardless of metric. This is the resume target after preemption.
- `best.pt` — written only when the monitored metric improves. This is the final-eval target.

Don't conflate them. Resuming from `best.pt` works for weights but the surrounding state (epoch counter, early-stop counter) may not match where training actually stopped.

## Inspect a checkpoint

```python
import torch
state = torch.load("checkpoints/last.pt", map_location="cpu")
print(sorted(state.keys()))
# expected: ['best_metric', 'epoch', 'model', 'optimizer', 'rng_numpy',
#            'rng_python', 'rng_torch', 'rng_torch_cuda', 'scaler', 'scheduler']
print(f"epoch: {state['epoch']}, best_metric: {state['best_metric']}")
```

If the printed keys are a subset (e.g., `['model']` only), the checkpoint was written by a weights-only `torch.save(model.state_dict(), path)` flow — resuming from it is restart-with-loaded-weights, not actual resume. Train fresh from epoch 0 going forward with the proper checkpoint format; do not pretend the resume worked.

## Version pin

The reference snippet targets PyTorch 2.4+. On older PyTorch the `autocast(dtype=...)` kwarg and `GradScaler.state_dict()` keys differ; pin `torch>=2.4` in `requirements.lock` and bump deliberately.
