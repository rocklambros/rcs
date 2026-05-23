# Fine-tune spec sheet — markdown skeleton

Copy this into `MODEL_CARD.md` and replace `<...>` placeholders. The completeness check in Step 8 of `writing-finetune-spec-sheet` validates that no placeholder remains.

---

# Model card: `<model_name>`

**Version:** `<semver>` · **Published:** `<YYYY-MM-DD>` · **Status:** `<draft | published | deprecated>`

## 1. Base checkpoint

- **Org:** `<org, e.g., meta-llama>`
- **Name:** `<model name, e.g., Llama-3.1-8B-Instruct>`
- **Revision (immutable SHA):** `<40-char SHA>` — do NOT use a tag name here; tags move
- **License:** `<SPDX identifier or license name>` — link to text

## 2. Training-data provenance

- **Audit manifest:** [`<relative-path-to-audit-manifest.json>`](<relative-path>)
- **Audit summary:** `<3-5 line description: row counts, per-rule findings, drop-policy, last re-audit date>`
- **Source(s):** `<list of upstream datasets, scrapes, synthetic generators, with versions / fetch dates>`
- **Splits used:** train = `<n>` rows; held-out eval = `<n>` rows; eval-set content hash = `<sha256>`

## 3. Training recipe

| Field | Value |
|---|---|
| Objective | `<sft | dpo | orpo | kto | rlhf | other>` |
| Library + version | `<e.g., trl 0.11.4>` |
| Recipe config | [`<relative-path-to-config.yaml>`](<relative-path>) |
| Training script commit SHA | `<git SHA>` |
| Learning rate | `<value>` |
| Effective batch size | `<value>` |
| Epochs / steps | `<value>` |
| Warmup | `<value>` |
| Weight decay | `<value>` |
| Grad clipping | `<value>` |
| LoRA rank / alpha (if applicable) | `<value>` |
| DPO beta (if applicable) | `<value>` |
| Hardware | `<e.g., 4×A100-80GB, FSDP>` |
| Distributed framework | `<FSDP / DeepSpeed Zero-1/2/3 / single-GPU>` |
| Seeds | `<value>` (per workflow/enforcing-seed-hygiene) |
| Wall-clock time | `<value>` |
| Final training loss | `<value>` |
| Run log | [`<W&B / TensorBoard / log link>`](<link>) |

## 4. Evaluation evidence

- **Paired before/after eval report:** [`<relative-path-to-eval-report.md>`](<relative-path>)
- **Test used:** `<McNemar | paired-t | Wilcoxon | Cochran's Q | Friedman>` (gating assumption check: `<Shapiro p = ... | discordant count = ... | etc.>`)
- **Headline metric delta:** `Δ<metric> = <value> [95% CI: <low>, <high>]`; direction: `<fine-tune > base | base > fine-tune>`
- **Effect size:** `<OR | Cohen's dz | paired r | Cliff's delta paired> = <value> [95% CI: <low>, <high>]`
- **Eval-set hash:** `<sha256>`
- **Per-segment breakdown:** `<linked table or "not available"; if absent under audience="regulated", this is a completeness warning>`
- **Power-check:** achieved power at observed effect = `<value>`; MDE used for sizing = `<value if supplied>`
- **Verdict:** `<certified-improvement | certified-no-difference | certified-regression | underpowered-inconclusive>`

## 5. Limitations + known failure modes

Enumerate at least one entry. Empty list is rejected.

- **Bias:** `<observed disparity per cohort / language / demographic, OR "not evaluated">`
- **Refusal patterns:** `<what the model refuses; what it under-refuses>`
- **Domain boundaries:** `<tasks NOT trained for; expected underperformance domains>`
- **Distributional limits:** `<input length cap, language coverage, modality limits>`
- **Adversarial robustness:** `<from any red-team eval; link to security/running-prompt-injection-eval results if applicable>`
- **Hallucination patterns:** `<task-specific hallucination modes>`
- **Calibration:** `<does confidence track accuracy? Link to calibration plot if available>`
- **Training-data freshness cutoff:** `<date>`

## 6. License reconciliation

- **Base license:** `<SPDX or full name>`
- **Training-data licenses:** `<per-dataset license + chain to upstream>`
- **Weights license:** `<intended publishing license>`
- **Conflicts surfaced:** `<list of conflicts and recommendations, OR "no conflicts identified">`
- **Attribution obligations:** `<list of required attributions, naming clauses (e.g., 'must include "Llama" in derivative name')>`

## 7. Intended use AND out-of-scope use

Both lists required. Out-of-scope is the most actionable section for deployers.

- **Primary use cases:**
  - `<use case 1>`
  - `<use case 2>`
- **Target users:** `<who the model is intended for>`
- **Out-of-scope use cases:**
  - `<use case 1, with reason>`
  - `<use case 2, with reason>`
- **Special deployment caveats:** `<rate limits, content-filter expectations, human-review gates>`

---

## Provenance

- Authored by: `<author>` on `<YYYY-MM-DD>`
- Tooling: `writing-finetune-spec-sheet` (RCS skill, v0.1.0)
- Completeness verdict: `<complete-publishable | complete-with-warnings | incomplete-do-not-publish>`
- Audience: `<public | internal | regulated>`
