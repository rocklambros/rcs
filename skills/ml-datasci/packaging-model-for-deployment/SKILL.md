---
name: packaging-model-for-deployment
description: >
  Packages a trained model for deployment with a versioned artifact, an input/output
  schema, a smoke test, a deterministic preprocessing pipeline, and a deployment
  manifest. Triggers when a notebook-trained model is about to be served behind an
  API, batch job, or scheduled inference; when a teammate asks how to ship a model;
  when the only artifact is a bare pickle in a notebook directory; or when the user
  is choosing between joblib, ONNX, TorchScript, or a framework-native serialization
  format. Refuses to certify a model as deploy-ready without a captured input/output
  schema and a smoke test that round-trips through the saved artifact.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - devops
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - email-spam-classifier-naive-bayes-comparisson-roc
last-updated: 2026-05-23
---

# Packaging Model for Deployment

## When to use

Trigger this skill when:

- The user has a trained model in a notebook and now wants to "deploy", "serve", "ship", "put it behind an API", or "hand it to the platform team"
- The current artifact is a bare `model.pkl` / `model.joblib` with no manifest, no schema, no smoke test, and no recorded preprocessing
- The user is choosing between joblib, ONNX, TorchScript, SavedModel, or a framework-native format and wants to know which one fits their stack
- A platform / SRE team is asking the model team for "what we need to know to run this": signature, schema, expected latency, dependencies, sample inputs
- Keywords: deploy, serve, package, pickle, joblib, ONNX, TorchScript, manifest, FastAPI, BentoML, smoke test, schema

## When NOT to use

Skip this skill and hand off when:

- The user is still iterating in a notebook with no near-term deployment intent — packaging now is premature; revisit at hand-off time
- The model is a one-off batch report generator with no API surface and no scheduled re-run — a saved CSV of predictions is the deliverable, not a packaged model
- The user wants production rollout strategy (canary, A/B, shadow traffic) — that is `ml-datasci/building-canary-rollout`; package the model first, then route
- The user wants a rollback runbook — that is `ml-datasci/building-rollback-plan`; package first, then plan reversal
- The artifact is an LLM behind an API — use the LLM provider's deployment path, not joblib / ONNX serialization

## Quick start

User: "I trained a `RandomForestClassifier` in a notebook on customer-churn data. How do I deploy it behind a FastAPI endpoint?"

Response: A 5-artifact package — versioned model file, input schema, output schema, manifest, smoke test — all under one `artifacts/<model-name>/<semver>/` directory, plus a minimal FastAPI handler that loads the artifact and validates against the schema on every request.

```python
# build_artifact.py — runs once at training time
import joblib
import json
from pathlib import Path
from datetime import datetime

VERSION = "0.1.0"
out = Path(f"artifacts/churn-rf/{VERSION}")
out.mkdir(parents=True, exist_ok=True)

# 1. Save the fitted pipeline (preprocessing + model in ONE object)
joblib.dump(pipeline, out / "model.joblib", compress=3)

# 2. Input schema (Pydantic-compatible JSON Schema)
input_schema = {
    "type": "object",
    "required": ["tenure_months", "monthly_charges", "contract_type"],
    "properties": {
        "tenure_months": {"type": "integer", "minimum": 0, "maximum": 240},
        "monthly_charges": {"type": "number", "minimum": 0.0},
        "contract_type": {"type": "string", "enum": ["month-to-month", "one-year", "two-year"]},
    },
}
(out / "input_schema.json").write_text(json.dumps(input_schema, indent=2))

# 3. Output schema
output_schema = {
    "type": "object",
    "required": ["churn_proba", "model_version"],
    "properties": {
        "churn_proba": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "model_version": {"type": "string"},
    },
}
(out / "output_schema.json").write_text(json.dumps(output_schema, indent=2))

# 4. Manifest — every reviewer reads this first
manifest = {
    "model_name": "churn-rf",
    "version": VERSION,
    "framework": "sklearn",
    "framework_version": "1.5.2",
    "python_version": "3.13",
    "trained_at": datetime.utcnow().isoformat() + "Z",
    "training_data_hash": "sha256:<content-hash-of-train.parquet>",
    "metric": {"name": "roc_auc", "value": 0.872, "ci_95": [0.864, 0.881]},
    "expected_latency_ms_p99": 8,
    "dependencies_lock": "uv.lock",
    "seed": 42,
}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2))

# 5. Smoke test — golden inputs + expected outputs (with tolerance)
smoke = [
    {"input": {"tenure_months": 1, "monthly_charges": 95.0, "contract_type": "month-to-month"},
     "expected_proba": 0.78, "tol": 0.02},
    {"input": {"tenure_months": 60, "monthly_charges": 65.0, "contract_type": "two-year"},
     "expected_proba": 0.04, "tol": 0.02},
]
(out / "smoke.json").write_text(json.dumps(smoke, indent=2))
```

The FastAPI handler then loads `model.joblib`, validates each request against `input_schema.json`, and serves `output_schema.json`-shaped responses. The smoke test is re-run in CI on every image build before the artifact is promoted.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `model_name` | str | yes | — | Short slug used in the artifact path and the manifest. |
| `version` | str (SemVer) | yes | — | Bump per re-train. `0.1.0` → `0.2.0` for breaking schema; `0.1.0` → `0.1.1` for retrain on same schema. |
| `framework` | str | yes | — | `sklearn` \| `xgboost` \| `lightgbm` \| `torch` \| `tensorflow` \| `onnx`. Drives the serialization choice. |
| `pipeline` | object | yes | — | The FITTED preprocessing + model object. Never save bare model + ad-hoc preprocessing code; package the pipeline. |
| `input_schema`, `output_schema` | JSON Schema dict | yes | — | Validated on every inference request. Reject malformed inputs at the boundary, not deep in the model. |
| `smoke_cases` | list of `{input, expected, tol}` | yes | — | Golden inputs + expected outputs + per-case tolerance. ≥ 3 cases covering happy + boundary inputs. |
| `serialization` | "joblib" \| "onnx" \| "torchscript" \| "savedmodel" | no | framework-default | Use ONNX or TorchScript when the runtime is not Python or when the framework / version pin would be a deployment risk. |

## Workflow

Copy this checklist into the response:

```
Packaging progress:
- [ ] 0. Confirm deployment target (API / batch / streaming) and runtime (Python / JVM / browser / mobile)
- [ ] 1. Pin the training environment (uv lock / poetry lock / requirements.lock)
- [ ] 2. Wrap preprocessing + model in a single fitted pipeline object (no ad-hoc preprocessing in the handler)
- [ ] 3. Serialize the pipeline (joblib / ONNX / TorchScript / SavedModel) and record the chosen format in the manifest
- [ ] 4. Capture the input schema (JSON Schema) — names, types, ranges, enums, required fields
- [ ] 5. Capture the output schema — include `model_version` in every response
- [ ] 6. Write the manifest.json — name, version, framework, framework version, Python version, trained_at, training data hash, headline metric + 95% CI, expected p99 latency, seed
- [ ] 7. Write the smoke test — ≥ 3 cases (typical input + boundary input + null-handling input) with expected output + tolerance
- [ ] 8. Verify the smoke test passes against the JUST-saved artifact (load it from disk, do not use the in-memory model)
- [ ] 9. CI hook: run the smoke test on every image build; fail the build if any case misses tolerance
```

### Step 1: Pin the training environment

Save `uv.lock` (or `poetry.lock` / `requirements.lock`) alongside the artifact. Pin the Python version explicitly (`.python-version` or `requires-python` in pyproject). A reproducibility gap between the training environment and the serving environment is the most common cause of "the model works in the notebook but fails in production." Cross-reference `workflow/pinning-reproducible-environments` for the full ecosystem-by-ecosystem pattern.

### Step 2: Single fitted pipeline object

Wrap preprocessing AND the model in one `sklearn.pipeline.Pipeline` (or framework analogue). The deployment handler must never re-implement preprocessing in Python — that is the most common source of training-serving skew. If the pipeline contains a `ColumnTransformer`, the column order at inference time must match the training column order; record the expected column list in the input schema.

### Step 3: Choose the serialization format

| Stack / runtime | Format | Notes |
|---|---|---|
| Python serving, sklearn / xgboost / lightgbm | `joblib` (or `pickle` via joblib) | Pin sklearn version in the manifest; joblib is not version-portable. |
| Python serving, PyTorch | `torch.save(state_dict)` + model code in repo, or `TorchScript` (`torch.jit.save`) | TorchScript when the serving code must not import training code. |
| Python serving, TensorFlow / Keras | `SavedModel` (TF) or `.keras` (Keras) | SavedModel for serving via TF Serving. |
| Non-Python serving (Go, JVM, browser, mobile) | `ONNX` (`onnxruntime`) | Convert with `skl2onnx` / `torch.onnx.export` / `tf2onnx`. Validate the ONNX output matches the original on the smoke set. |
| Edge / mobile | `TFLite` / `CoreML` | Quantize only after the smoke set passes at full precision. |

The serialization choice goes in the manifest under `framework`/`serialization`.

### Step 4: Input schema

JSON Schema (draft-07 or later). Required fields, types, ranges, enums, and an optional `additionalProperties: false` to reject unknown fields. Pydantic models are an acceptable internal form, but emit JSON Schema for the manifest so non-Python consumers can validate.

### Step 5: Output schema

The response must always include `model_version` so downstream logs can tie a prediction to a specific artifact. Include the predicted score plus, where relevant, a confidence band or rationale field. Do not return raw numpy arrays.

### Step 6: Manifest

`manifest.json` lives next to the artifact. Minimum fields: `model_name`, `version`, `framework`, `framework_version`, `python_version`, `trained_at` (ISO 8601 UTC), `training_data_hash` (content hash of the training data — not the path), `metric` (name + value + 95% CI), `expected_latency_ms_p99`, `seed`, `dependencies_lock` (lockfile name).

### Step 7 & 8: Smoke test

Three minimum cases:

1. **Typical** — a representative row from the training distribution. Expected output is the model's prediction at training time (recorded as a JSON value with a tolerance).
2. **Boundary** — values at the edge of the input schema (min / max ranges, rare enum value, an unusual combination). Verifies the pipeline does not crash on plausible-but-extreme inputs.
3. **Null-handling** — a row with a missing field (where the schema allows missing) and a row with a field at a sentinel value. Verifies the preprocessing imputers behave deterministically.

The CI gate loads the saved artifact from disk (NOT the in-memory training object), runs all cases, and fails the build if any case misses its tolerance.

### Step 9: CI hook

The package's smoke test runs on every container image build. A passing smoke test is a precondition for promotion to staging or production. Promotion gates (canary rollout, rollback plan) are downstream skills.

## Outputs

A directory at `artifacts/<model_name>/<version>/` containing:

- `model.joblib` (or `.onnx` / `.pt` / `saved_model/`) — the serialized fitted pipeline
- `input_schema.json` — JSON Schema for inference requests
- `output_schema.json` — JSON Schema for inference responses (must include `model_version`)
- `manifest.json` — name, version, framework, framework version, Python version, trained_at, training data hash, metric + 95% CI, expected p99 latency, seed, lockfile name
- `smoke.json` — list of `{input, expected_output, tolerance}` cases (≥ 3)
- `uv.lock` (or equivalent) — pinned dependency graph
- `README.md` — one-page handoff: what this model is, how to load it, how to run the smoke test

## Failure modes

- **Training-serving skew** — preprocessing is re-implemented in the handler instead of being baked into the fitted pipeline. Caught by step 2 (single pipeline object) and step 8 (smoke test against the on-disk artifact, not the in-memory model).
- **Silent column-order drift** — `ColumnTransformer` was fit on columns `[A, B, C]` but the handler sends `[B, A, C]`. Caught by the input schema's column-order specification + a smoke case that exercises a representative row.
- **Framework version drift** — joblib model trained on sklearn 1.5.2 loaded under sklearn 1.7.0 silently returns different predictions. Caught by `framework_version` in the manifest + the smoke test in CI.
- **No reproducibility** — no lockfile pinned alongside the artifact. Caught by step 1 (lockfile required as part of the package).
- **Schema-less response** — the response is a raw float or numpy array, downstream consumers parse it inconsistently. Caught by step 5 (output schema required, includes `model_version`).
- **"Works in the notebook"** — the smoke test was run against the in-memory training object, not the saved artifact. Caught by step 8 (smoke test MUST load from disk).

## References

- [scikit-learn Model persistence](https://scikit-learn.org/stable/model_persistence.html) — joblib vs pickle vs ONNX trade-offs and version compatibility
- [PyTorch — Saving and loading models](https://pytorch.org/tutorials/beginner/saving_loading_models.html) — state_dict vs TorchScript
- [ONNX Runtime — Tutorials](https://onnxruntime.ai/docs/tutorials/) — converting sklearn / PyTorch / TF to ONNX
- [JSON Schema Specification](https://json-schema.org/specification.html) — input/output schema authoring
- `workflow/pinning-reproducible-environments` — the lockfile + Python-version pinning that step 1 requires
- `ml-datasci/auditing-train-test-split` — required pre-step; the metric in the manifest must come from a leakage-clean split

## Examples

### Example 1: sklearn → FastAPI (happy-path)

Input: "I trained a `RandomForestClassifier` for churn prediction in a notebook. How do I deploy it behind a FastAPI endpoint?"

Output: Skill produces the `artifacts/churn-rf/0.1.0/` layout — fitted Pipeline saved via joblib, JSON Schema for input + output, manifest with framework version + training data hash + metric + 95% CI + seed, smoke test with ≥ 3 cases (typical, boundary, null-handling), and a CI gate that re-runs the smoke test on every image build before promotion. Names training-serving skew as the main risk and shows how the Pipeline + schema together close it.

### Example 2: Custom preprocessing across boundaries (edge-case)

Input: "My model has custom feature engineering — TF-IDF on a text column, target encoding on two categoricals, log-transform on a count column — done in separate notebook cells. The model is XGBoost. How do I package it?"

Output: Skill insists the entire feature pipeline be wrapped in a single fitted `sklearn.pipeline.Pipeline` (or `ColumnTransformer`) before serialization. For target encoding specifically, the encoder must be fit on training fold targets only (leakage hazard, cross-reference `ml-datasci/auditing-train-test-split`). The packaged artifact then includes the full pipeline; the FastAPI handler never re-implements feature engineering. The smoke test must include at least one case with a rare categorical value to verify target-encoding fallback behavior.

### Example 3: Notebook-only experiment (anti-trigger)

Input: "I'm exploring whether random forests outperform logistic regression on this dataset. Do I need to package the model?"

Output: Skill does NOT engage the deployment workflow. Explains that packaging is a hand-off discipline, premature during exploration. Suggests revisiting once a model is chosen for deployment. Recommends `ml-datasci/building-baseline-models` and `ml-datasci/evaluating-binary-classifiers` for the comparison itself.

## See also

- `ml-datasci/building-canary-rollout` — next step after packaging: routing a small slice of production traffic to the new artifact with per-cohort metrics and an auto-rollback trigger
- `ml-datasci/building-rollback-plan` — the reversal plan that a packaged artifact + versioned manifest makes possible
- `workflow/pinning-reproducible-environments` — the lockfile + Python-version pinning required as part of the package
- `ml-datasci/auditing-train-test-split` — the metric in the manifest must come from a leakage-clean split
- `ml-datasci/evaluating-binary-classifiers` / `ml-datasci/evaluating-regression-models` — the metric + CI that goes into the manifest

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-1, skill 5.1.1) via PRAGMATIC discipline
