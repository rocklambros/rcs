# Why CPU-pin matters for cross-platform sampler determinism

A fixed seed pins the RNG. It does not pin the order of floating-point reductions.

## The mechanism

Modern BLAS / OpenMP runtimes parallelize reductions (sums, dot products) across CPU threads. The reduction order depends on:

1. Number of threads (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`)
2. Work-stealing scheduler decisions (which thread finishes first)
3. CPU architecture (cache-line size, SIMD width)

Floating-point addition is non-associative: `(a + b) + c ≠ a + (b + c)` in general. Different reduction orders produce different bit-exact results. For most ML training the divergence is in the 6th-7th decimal and irrelevant; for samplers (NUTS, HMC, leapfrog integration) tiny per-step divergences compound across thousands of leapfrog steps and produce visibly different posterior distributions.

## The fix

Set:

```bash
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export JAX_PLATFORM_NAME=cpu  # forces JAX off GPU even if available
```

A single-thread CPU reduction has a fixed order, so the same seed produces the same arithmetic on any platform.

## Cost

Single-threaded sampling is slower (typically 2-8x for NUTS workloads). This is an acceptable trade for reproducibility in research / publication / regulatory contexts. For production inference where reproducibility is not the goal, leave the thread count at the default.

## Provenance

This pattern was discovered during the incident-rank-validation work where identical-seed NUTS runs on a MacBook Pro and an Ubuntu GPU server diverged after ~50 leapfrog steps. CPU-pin closed the gap to bit-exact agreement across the two platforms.

## Related sources of non-determinism not fixed by CPU-pin

- **cuDNN convolution algorithm selection** (PyTorch): set `torch.backends.cudnn.deterministic = True` + `benchmark = False`
- **Atomics on GPU**: some CUDA kernels use atomic adds with nondeterministic ordering; switch to deterministic algorithm variants where available
- **Driver / library version drift**: same seed on the same code with different cuDNN / MKL versions can still diverge; pin those in the environment lockfile

The combined practice — seed hygiene + CPU-pin + library pinning — is what produces bit-exact reproducibility across platforms.
