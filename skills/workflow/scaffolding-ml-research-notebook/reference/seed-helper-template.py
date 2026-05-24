"""Multi-library seed helper used by scaffolding-ml-research-notebook.

Call set_seed() in cell 1 of every notebook and at the top of every training
script. Idempotent and side-effect-only — covers every RNG that the project's
ml_stack might pull from.

Cross-reference: skills/workflow/enforcing-seed-hygiene/ for the discipline
this helper encodes (including the CPU-pin pattern for NUTS / JAX
cross-platform determinism, which seed-only cannot fix).
"""

from __future__ import annotations

import os
import random


def set_seed(seed: int = 42) -> None:
    """Pin seeds across every supported RNG in this project.

    Coverage (only the libraries actually installed will fire):
      - Python `random`
      - NumPy
      - PyTorch (CPU + CUDA + cuDNN deterministic)
      - JAX (via PYTHONHASHSEED + jax.random.PRNGKey caller convention)
      - TensorFlow

    Returns None. Safe to call repeatedly.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)

    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass

    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

    try:
        # JAX does not have a process-global seed; callers must pass
        # PRNGKey(seed). We surface the seed as an env var so downstream
        # code can read it consistently.
        os.environ["JAX_DEFAULT_SEED"] = str(seed)
    except Exception:
        pass

    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except ImportError:
        pass
