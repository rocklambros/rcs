---
name: enforcing-seed-hygiene
description: >
  Enforces deterministic seed initialization in any Jupyter notebook, Python/R script,
  or ML training pipeline that touches randomness. Use whenever the user is starting
  an ML/DS notebook, writing a training script, or asks why results changed run-to-run.
  Walks the multi-library seed-set pattern (Python random, NumPy, PyTorch, JAX,
  TensorFlow, R), the CPU-pin pattern for NUTS/JAX cross-platform determinism,
  and a pre-commit gate that catches missing seed calls in new files.
version: 0.1.0
status: shipped
track: workflow
audience: [data-scientist, ml-engineer, security-eng, skill-author]
evidence:
  - incident-rank-validation
  - multiturn-injection-detection
  - llm-toxicity-visual-analysis
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - DU-MSDSAI-4432-OptimalClusteringComparison
last-updated: 2026-05-23
---

# Enforcing Seed Hygiene

## When to use

Trigger this skill when the user asks for or implies one of:

- Starting a new Jupyter notebook, Python script, R script, or ML training pipeline that involves randomness (model init, dropout, data shuffle, sampling, augmentation)
- Reporting that "my results changed between runs" or "I cannot reproduce this number"
- Diagnosing why a NUTS / HMC / JAX sampler gives different posteriors on laptop vs. server with the same seed
- Reviewing a notebook before publication / submission / paper attachment where reproducibility is a hard requirement
- Setting up a pre-commit hook for an ML repo to enforce seed discipline going forward

## When NOT to use

Skip this skill and hand off when:

- The user wants a fresh random nonce for cryptographic / security purposes — fixed seeds are wrong; use `secrets.token_bytes()` or `os.urandom()`
- The user is running a Monte Carlo study that legitimately requires fresh seeds per replicate (in that case run-stamp each replicate, but do not pin a fixed seed)
- The work is throwaway exploration that will not be re-run, persisted, or shared
- The user is asking about cryptographic key derivation (different skill: key management)

## Quick start

User says: "I'm starting a new notebook to train a PyTorch CNN on CIFAR-10. Set me up."

Skill response: produces a first-cell seed block that covers Python `random`, NumPy, PyTorch (CPU + CUDA), sets `PYTHONHASHSEED`, names a single integer seed (e.g., 42), and adds an explicit comment naming which downstream nondeterminism sources (cuDNN benchmarking, JAX platform) the user should also pin.

```python
# Seed-hygiene first cell — one call per library the notebook will touch.
import os, random
import numpy as np
import torch

SEED = 42
os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| libraries | list of strings | yes | — | The libraries the notebook / script will touch (e.g., `[numpy, torch, jax, tf, r]`). Drives which seed-set calls to emit. |
| seed_value | integer | no | 42 | The seed value. 42 is conventional; any positive int is fine. |
| platform_pin | "cpu" \| "gpu" \| "any" | no | "any" | If `cpu`, also emits `OMP_NUM_THREADS=1` + `MKL_NUM_THREADS=1` + `JAX_PLATFORM_NAME=cpu` for cross-platform sampler determinism. |
| install_pre_commit | bool | no | false | If true, also generates a `.pre-commit-config.yaml` snippet that fails on new files lacking a seed-set call. |

## Workflow

Copy this checklist into the response and check off items as the setup progresses:

```
Seed-hygiene setup progress:
- [ ] Identify the libraries the notebook will touch (Python random, NumPy, PyTorch, JAX, TensorFlow, R)
- [ ] Emit a single first-cell seed block covering every identified library
- [ ] If sampler / cross-platform reproducibility is required: add CPU-pin env vars
- [ ] If repo-level enforcement is wanted: add pre-commit hook
- [ ] Verify no per-cell seed scatter (np.random.seed(...) inside the model-training cell is an anti-pattern)
```

### Step 1: Identify the library set

Inventory the libraries the notebook or script will import. Common combinations:

- Tabular ML: Python `random` + NumPy + scikit-learn (scikit-learn respects NumPy's RNG)
- Deep learning: + PyTorch or TensorFlow or JAX
- Bayesian / probabilistic programming: + PyMC / NumPyro / Stan (need CPU-pin for cross-platform determinism)
- R analyses: R's `set.seed()` is independent of any Python seeds

### Step 2: Emit the multi-library seed block

See `reference/seed-cookbook.md` for the per-library cookbook. Every notebook gets ONE first-cell block that covers EVERY library it touches. No scattered per-cell `np.random.seed(42)` calls — that pattern is the anti-pattern the pre-commit hook should catch.

### Step 3: CPU-pin (if applicable)

For NUTS / JAX / sampler workloads where determinism must hold across laptop / Linux server / CI:

```bash
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export JAX_PLATFORM_NAME=cpu
```

Or in the notebook's first cell before any imports:

```python
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["JAX_PLATFORM_NAME"] = "cpu"
```

Reason: parallel thread scheduling produces non-bit-exact floating-point reductions across runs. The seed alone is insufficient — the same seed with different thread counts produces different posteriors. See `reference/cpu-pin-rationale.md`.

### Step 4: Pre-commit gate (optional but recommended)

For repo-wide enforcement, add a pre-commit hook that fails on any new `.py` / `.ipynb` / `.R` file lacking a seed-set call. See `reference/seed-cookbook.md` "Pre-commit hook" section for the exact configuration.

## Outputs

A markdown block plus code snippets:

1. **First-cell seed block** — copy-pasteable, covers every named library
2. **Environment pin block** (if `platform_pin != "any"`) — exports or `os.environ` writes
3. **Pre-commit snippet** (if `install_pre_commit: true`) — YAML hook config
4. **Anti-pattern warning** — explicit note that scattered `np.random.seed(...)` calls in later cells violate the discipline

## Failure modes

Known pitfalls in seed hygiene and how this skill catches them:

- **Single-library seed assumption** — calling only `np.random.seed(42)` while PyTorch / JAX / Python `random` go unseeded. Caught by: Step 1 forces explicit library inventory; Step 2 enforces one call per library.
- **Per-cell seed scatter** — repeating `np.random.seed(42)` inside the training cell to "make sure" determinism holds, which masks ordering bugs. Caught by: explicit anti-pattern warning + pre-commit hook configured to flag multiple seed calls in one file.
- **Cross-platform sampler drift** — same seed produces different posteriors on laptop vs. server because parallel thread counts differ. Caught by: Step 3 CPU-pin recommendation for sampler workloads.
- **PYTHONHASHSEED omission** — Python's dict / set iteration order is hash-seeded per process; without `PYTHONHASHSEED=N`, any code path that converts a set to a list (then iterates) is nondeterministic. Caught by: `os.environ["PYTHONHASHSEED"]` in the first-cell block.
- **Fresh-entropy use case mis-applied** — applying seed hygiene to nonce generation, session tokens, or password salts. Caught by: explicit "When NOT to use" anti-trigger; hand off to `secrets` module.

## References

- `reference/seed-cookbook.md` — per-library seed-set calls + pre-commit hook YAML
- `reference/cpu-pin-rationale.md` — why thread-count determines posterior reproducibility for samplers
- [PyTorch reproducibility guide](https://pytorch.org/docs/stable/notes/randomness.html) — upstream guidance on cuDNN flags
- [JAX deterministic behavior](https://jax.readthedocs.io/en/latest/notebooks/Common_Gotchas_in_JAX.html#pseudo-random-numbers) — JAX's explicit-key RNG model

## Examples

### Example 1: New PyTorch CNN notebook (happy-path)

Input: "I'm starting a new notebook to train a PyTorch CNN on CIFAR-10. Set me up."

Output: Skill emits a first-cell block that covers Python `random`, NumPy, PyTorch CPU + CUDA, sets `PYTHONHASHSEED`, and adds the cuDNN `deterministic=True / benchmark=False` flags. Names SEED = 42. Adds an explicit warning that scattered per-cell `np.random.seed(...)` calls inside the training loop would violate the discipline.

### Example 2: NUTS sampler differs between laptop and Linux GPU server (edge-case)

Input: "My NUTS sampler results differ between my laptop and our Linux GPU server. Same seed, same code. Help."

Output: Skill diagnoses the cross-platform sampler drift pattern. Recommends the CPU-pin block (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `JAX_PLATFORM_NAME=cpu`) BEFORE any imports. Explains that seed alone is insufficient because parallel-thread reduction order is non-bit-exact. References `cpu-pin-rationale.md`.

### Example 3: Crypto nonce request (anti-trigger)

Input: "Generate me a random nonce for an API request."

Output: Skill refuses to engage seed-set workflow. Explains that fixed seeds defeat the purpose of a cryptographic nonce. Recommends `secrets.token_bytes(16)` or `os.urandom(16)`. Hands off.

## See also

- `workflow/pinning-reproducible-environments` — pairs naturally; seed hygiene + env pinning together give bit-exact runs
- `workflow/auditing-jupyter-execution-order` — out-of-order cell execution can re-seed silently (planned)
- `ml-datasci/scaffolding-pytorch-training-loop` — bundles seed setup with the broader training-loop scaffold (planned)
- `workflow/auditing-data-quality` — same first-cell discipline pattern, for data audits instead of seeds

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from incident-rank-validation (NUTS CPU-pin), multiturn-injection-detection (set_global_seed(42)), and the DU-MSDSAI-4432-* notebook family
