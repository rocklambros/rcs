# Seed Cookbook — per-library seed-set calls

Every library that touches randomness needs an explicit seed call. Combine the relevant blocks into a single first cell of the notebook.

## Python standard library

```python
import os, random
SEED = 42
os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
```

`PYTHONHASHSEED` must be set BEFORE the Python process starts to affect hash-based ordering across the whole interpreter. Setting it in the first cell pins it for any code launched after the cell via `subprocess` / `multiprocessing`, but for in-process determinism it is too late — for full coverage, also set it as a shell env var when launching the kernel.

## NumPy

```python
import numpy as np
np.random.seed(SEED)
# Preferred (NumPy ≥ 1.17):
rng = np.random.default_rng(SEED)
```

Prefer the `default_rng(SEED)` Generator API over the legacy `np.random.seed(...)` for new code; pass the `rng` instance into downstream functions explicitly rather than relying on the global state.

## PyTorch

```python
import torch
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

`cudnn.benchmark = True` selects the fastest convolution kernel per input shape — that kernel selection is itself nondeterministic. Setting `benchmark = False` plus `deterministic = True` trades throughput for reproducibility.

## JAX

```python
import jax
key = jax.random.PRNGKey(SEED)
# Split keys explicitly for sub-uses:
key, subkey = jax.random.split(key)
```

JAX uses explicit-key RNG (no global state), so the "seed" lives in `key` and must be threaded through the call graph. This is more verbose than NumPy but eliminates the seed-leakage class of bugs.

## TensorFlow

```python
import tensorflow as tf
tf.random.set_seed(SEED)
# For full op-level determinism:
tf.config.experimental.enable_op_determinism()
```

## R

```r
set.seed(42)
```

R's `set.seed` covers base R RNG. Packages with their own RNG (`mc.cores` in parallel, `keras` via TF backend) need their own seeding.

## Pre-commit hook (repo-wide enforcement)

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: seed-hygiene
      name: enforce-seed-hygiene
      entry: bash -c 'for f in "$@"; do grep -lE "(numpy|torch|jax|tensorflow|sklearn)" "$f" >/dev/null || continue; grep -qE "(np\.random\.seed|torch\.manual_seed|jax\.random\.PRNGKey|tf\.random\.set_seed)" "$f" || { echo "seed-hygiene: $f imports an RNG-bearing lib but has no seed call"; exit 1; }; done' --
      language: system
      files: '\.(py|ipynb)$'
```

Customize the import-detection regex for the relevant stack. The hook fails the commit if any file imports a randomness-bearing library without a corresponding seed-set call.
