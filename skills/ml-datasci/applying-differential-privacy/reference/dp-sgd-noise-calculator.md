# DP-SGD Noise-Calculator Recipe

The closed-form formula for noise multiplier σ given (ε, δ, sampling rate q, steps T) does not exist — the RDP accountant is solved iteratively. This is the working recipe.

## Inputs

| Symbol | Name | Typical |
|---|---|---|
| ε | Target privacy budget | 0.5–3.0 for ML |
| δ | Target failure probability | ≤ 1 / (n × poly-log-n); for n = 100K, ≈ 1e-7 |
| q | Sampling rate per step | batch_size / n |
| T | Number of training steps | epochs × (n / batch_size) |
| C | L2 clipping bound | 1.0 after normalization |
| σ | Noise multiplier (the unknown to solve for) | typically 0.5–2.0 |

## Procedure with Opacus (PyTorch)

```python
from opacus.accountants.utils import get_noise_multiplier

sigma = get_noise_multiplier(
    target_epsilon=2.0,        # ε target
    target_delta=1e-7,         # δ target
    sample_rate=256/100_000,   # q
    epochs=30,                 # T = epochs * (n/batch_size) handled internally
    accountant="rdp",          # RDP composition
)
# sigma ≈ 1.1 for these inputs
```

Then in training:

```python
from opacus import PrivacyEngine

privacy_engine = PrivacyEngine()
model, optimizer, train_loader = privacy_engine.make_private(
    module=model,
    optimizer=optimizer,
    data_loader=train_loader,
    noise_multiplier=sigma,
    max_grad_norm=1.0,         # C
)
# Train normally
for epoch in range(epochs):
    for batch in train_loader:
        ...
    eps = privacy_engine.get_epsilon(delta=1e-7)
    print(f"epoch {epoch}: (ε = {eps:.2f}, δ = 1e-7)")
    if eps >= 2.0:
        break
```

## Procedure with TensorFlow Privacy

```python
from tensorflow_privacy.privacy.analysis import compute_dp_sgd_privacy_lib

eps, _ = compute_dp_sgd_privacy_lib.compute_dp_sgd_privacy(
    n=100_000,
    batch_size=256,
    noise_multiplier=1.1,
    epochs=30,
    delta=1e-7,
)
# eps ≈ 2.0 for these inputs (matches the Opacus solve above)
```

Solve in reverse: pick σ candidates iteratively until `compute_dp_sgd_privacy` returns ε ≈ ε_target.

## Procedure with `dp-accounting` (Google's reference)

```python
from dp_accounting import dp_event, rdp

accountant = rdp.RdpAccountant()
event = dp_event.PoissonSampledDpEvent(
    sampling_probability=256/100_000,
    event=dp_event.GaussianDpEvent(noise_multiplier=1.1),
)
accountant.compose(event, count=30 * (100_000 // 256))
eps = accountant.get_epsilon(target_delta=1e-7)
# eps ≈ 2.0
```

## Common errors

- **Forgetting that ε accumulates across epochs** — running training "to convergence" past the budget invalidates the guarantee.
- **Mixing Poisson sampling with deterministic batches** — the RDP accountant assumes Poisson. Opacus's `DPDataLoader` handles this; a vanilla DataLoader does NOT.
- **Setting noise multiplier σ < 0.5** — usually means ε is being overspent; double-check the accountant report.
- **Setting clipping bound C ≫ typical gradient norm** — the clipping never bites and the noise scale is too small relative to the actual gradient signal; effectively no privacy. Set C close to the typical per-example gradient L2.
- **Setting C ≪ typical gradient norm** — all gradient signal is clipped away; loss won't converge. Tune empirically: log per-example gradient L2 over training and pick C near the median.
