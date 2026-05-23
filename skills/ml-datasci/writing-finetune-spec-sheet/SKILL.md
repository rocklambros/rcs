---
name: writing-finetune-spec-sheet
description: >
  Produces a fine-tune spec sheet that documents the seven categories an
  external reviewer needs to evaluate a fine-tuned model: base-checkpoint
  identity (org + name + revision SHA), training-data provenance and audit
  manifest, training recipe (objective, hyperparameters, hardware, seeds,
  durations), evaluation evidence (paired before/after results with effect
  sizes and CIs, per-segment breakdowns, eval-set hash), known limitations
  and failure modes, license stack across the base and the data and the
  resulting weights, and intended use plus out-of-scope use. Use when a
  fine-tune is about to be published (Hugging Face model card, internal
  registry, regulatory submission) or handed to a downstream team. Refuses
  to publish a "throwaway personal scratch" fine-tune with a public-style
  spec sheet — that audience does not need it.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - ml-engineer
  - data-scientist
  - security-eng
  - ai-security
evidence:
  - llm-safety-alignment-study
  - claude-secure-coding-rules
  - genai_agentic_incidents
last-updated: 2026-05-23
---

# Writing a Fine-Tune Spec Sheet

> **Documentation discipline, not a regulatory certification.** This skill
> produces the artifact downstream reviewers, model-risk teams, and
> deploying engineers need to make an informed decision. It does not
> substitute for whatever formal model-risk-management process the
> deploying organization runs (and it does not bundle any regulatory
> taxonomy — those are inputs).

## When to use

Trigger this skill when a fine-tune is about to leave the training team and
reach an external audience, and one of:

- Publishing the model on Hugging Face / an internal model registry — the
  registry requires a model card; this skill builds it with completeness
  enforced
- Handing off to a deploying team (SRE, product, downstream ML team) — the
  downstream team needs the spec sheet to integrate without re-deriving the
  training details
- Submitting the model for an internal model-risk review, security review,
  or compliance audit — the reviewer needs every category populated and
  every claim cited to evidence
- Releasing externally with a license obligation — the licenses of the
  base, the training data, and the resulting weights must be reconciled
  and stated; missing this is a common publish blocker
- Producing a spec sheet alongside a regulated deployment (EU AI Act
  high-risk obligations, finance / healthcare governance) where the
  documentation discipline is itself a control
- Keywords: "model card", "fine-tune documentation", "publish my fine-tune",
  "model spec sheet", "what do I need to write up for my fine-tune"

## When NOT to use

Skip this skill and hand off when:

- The fine-tune is a personal-scratch experiment that will never leave the
  author's machine — the spec-sheet overhead is not justified; a short
  README or notebook is sufficient
- The fine-tune is mid-iteration and the author is still experimenting —
  the spec sheet documents a deliverable; intermediate experiments are
  notebook territory
- The task is to write a model card for a model the user did NOT train
  (e.g., wrapping an existing HF model) — different artifact (a deployment
  spec, not a fine-tune spec); use a deployment-doc skill (planned)
- The task is to write a general "AI policy" for an organization rather
  than for a specific model — out of scope; see
  `security/scaffolding-ai-policy-doc` (planned)
- The task is to certify the fine-tune's safety / fairness / robustness
  rather than to document it — the spec sheet *records* what evaluations
  were run; the actual evaluations live in
  `ml-datasci/running-eval-before-after-finetune`,
  `ml-datasci/auditing-model-fairness` (planned), etc.

## Quick start

User says: "I fine-tuned Llama-3.1-8B-Instruct with DPO on 12K preference
pairs we collected from our internal support team. We're going to publish
it on our internal model registry next week. Help me write the spec sheet."

Skill walks the 7-category template, asks the user to supply the artifacts
each category needs (base SHA, data audit manifest, training run log, eval
report, license info for base + data, intended-use statement), refuses to
emit empty sections, and produces a single-file markdown spec sheet plus a
machine-readable companion (JSON) that the registry can index.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `model_name` | string | yes | — | The published name of the fine-tuned model. |
| `base_checkpoint` | object | yes | — | `{org, name, revision_sha, license}`. The base model the fine-tune started from. The `revision_sha` is the immutable identifier (Git commit / HF revision); a tag name alone is not sufficient. |
| `training_data_manifest` | path | yes | — | Path to the data audit manifest from `ml-datasci/auditing-sft-dataset` (or equivalent). Establishes provenance and what was audited. |
| `training_recipe` | object | yes | — | `{objective: "sft"|"dpo"|"orpo"|"kto"|"rlhf"|other, library, hyperparameters, hardware, seeds, wall_time, train_loss_final}`. |
| `eval_report_path` | path | recommended | — | Path to the paired before/after eval report from `ml-datasci/running-eval-before-after-finetune`. If absent, the spec sheet emits a prominent warning and the eval section becomes a stub. |
| `limitations` | list[string] | yes | — | Known failure modes, refusal patterns, domain boundaries, distributional limits. Empty list is not accepted — the user must enumerate at least the trivial limitations or explicitly write "no known limitations identified (caution warranted)". |
| `licenses` | object | yes | — | `{base_license, training_data_licenses: [...], weights_license}`. The skill checks for known incompatibilities (e.g., non-commercial base + commercial use of derivatives) and surfaces conflicts. |
| `intended_use` | object | yes | — | `{primary_use_cases: [...], out_of_scope_use_cases: [...], target_users}`. Both lists are required; "out of scope" carries equal weight to "primary". |
| `audience` | "public" \| "internal" \| "regulated" | no | `"internal"` | Drives the strictness of the empty-section check. `regulated` enforces every category populated with cited evidence; `internal` allows brief stubs with explicit "not applicable" justifications; `public` enforces enough completeness for an outside reader. |

## Workflow

Copy this checklist into the response and check items off as the spec sheet is built:

```
Fine-tune spec sheet checklist:
- [ ] 1. Base checkpoint — org + name + revision_sha (immutable) + license
- [ ] 2. Training-data provenance — link to audit manifest + summary of audit findings
- [ ] 3. Training recipe — objective + lib + key hyperparameters + hardware + seed + wall time
- [ ] 4. Evaluation evidence — paired before/after with effect sizes + CIs + per-segment breakdown + eval-set hash
- [ ] 5. Limitations + known failure modes — at least one entry; bias / refusal / domain boundaries / distributional limits
- [ ] 6. License reconciliation — base + data + weights; surface conflicts explicitly
- [ ] 7. Intended use AND out-of-scope use — both lists; out-of-scope is required, not optional
- [ ] 8. Emit markdown spec sheet + JSON companion + completeness verdict
```

### Step 1: Base checkpoint

Required fields (refuse to proceed without all four):

- `org` — the publishing organization (e.g., `meta-llama`)
- `name` — the model name (e.g., `Llama-3.1-8B-Instruct`)
- `revision_sha` — the immutable revision identifier. A tag name (e.g., `main`) is NOT acceptable; tags move. The revision_sha is the Hugging Face commit SHA, the Git commit SHA, or the internal model registry's content-addressable hash.
- `license` — the base model's license text or SPDX identifier

If the user gives a tag-name only, the skill asks for the SHA and refuses to proceed until supplied. This is the single highest-value field for reproducibility — without it, every other field is uncertain about what was fine-tuned.

### Step 2: Training-data provenance

Required: a link to the data audit manifest (from `ml-datasci/auditing-sft-dataset` or equivalent) and a 3-5 line summary of audit findings:

- Row counts (train + eval, post-remediation)
- Per-rule findings counts (parse failures, near-duplicates, leakage, PII)
- Drop-policy applied (quarantine vs report-only)
- Re-audit status (last re-run date)

If no audit manifest exists, the skill emits a high-severity warning and recommends running the audit first. For `audience="regulated"`, this is a blocking issue, not a warning.

### Step 3: Training recipe

Required fields:

- `objective` — `sft` / `dpo` / `orpo` / `kto` / `rlhf` / etc.
- `library` and `version` — `trl 0.11.4`, `axolotl 0.4.1`, `torchtune 0.3.0`, etc.
- `hyperparameters` — at minimum: learning rate, batch size (effective), epochs / steps, warmup, weight decay, gradient clipping, LoRA rank / alpha if applicable, DPO beta if applicable
- `hardware` — GPU type and count, training framework (FSDP / DeepSpeed Zero stage)
- `seeds` — the random seed used (per `workflow/enforcing-seed-hygiene` discipline)
- `wall_time` — total wall-clock training time
- `train_loss_final` — final training loss (not the headline metric, but useful for sanity-check comparisons across recipes)

Optional but recommended: link to the W&B / TensorBoard run, link to the recipe config file (YAML / JSON), link to the training script commit SHA.

### Step 4: Evaluation evidence

Required: a link to the paired before/after evaluation report from
`ml-datasci/running-eval-before-after-finetune` (or equivalent paired
evaluation). The spec sheet itself includes a summary block:

- **Test used** — McNemar / paired-t / Wilcoxon / Cochran / Friedman (with the gating assumption check)
- **Headline metric delta** — `Δ = <value> [95% CI: <low>, <high>]`, direction stated
- **Effect size** — odds ratio / Cohen's dz / paired r / Cliff's delta paired
- **Eval set hash** — content-addressable hash of the eval file (so a future reader can verify they have the same eval)
- **Per-segment breakdown** — if available, per-class / per-difficulty / per-language Δ with CIs
- **Power-check result** — achieved power at the observed effect; flag underpowered findings as underpowered, not as "no difference"
- **Verdict** — `certified-improvement` / `certified-no-difference` / `certified-regression` / `underpowered-inconclusive` (from the eval report's Step 6)

If no eval report exists, this section becomes a stub with a high-severity warning. For `audience="regulated"` this is a blocking issue.

### Step 5: Limitations + known failure modes

The spec sheet requires at least one entry. Categories to consider (the skill asks the user about each):

- **Bias** — observed disparities across demographics / cohorts / languages in the eval
- **Refusal patterns** — what the model refuses; what it under-refuses
- **Domain boundaries** — what tasks the fine-tune was NOT trained for and likely underperforms on
- **Distributional limits** — input length, language, modality limits
- **Adversarial robustness** — known prompt-injection / jailbreak susceptibility (from any red-team eval, e.g., `security/running-prompt-injection-eval`)
- **Hallucination patterns** — task-specific hallucination modes
- **Calibration** — does the model's confidence track its accuracy?
- **Training-data drift** — what was the freshness cutoff of training data?

An empty `limitations: []` list is rejected. If the user genuinely believes there are no known limitations, the spec sheet records this explicitly with a "caution warranted" framing — silence is not acceptable.

### Step 6: License reconciliation

The spec sheet lists three license categories and surfaces conflicts:

- **base_license** — e.g., Llama Community License, Apache-2.0, MIT
- **training_data_licenses** — each dataset and its license; for derived datasets, the upstream license chain
- **weights_license** — the license the user intends to publish the fine-tuned weights under

Known conflict patterns the skill flags:

- Non-commercial base license → commercial use of derivatives is restricted
- Llama Community License → naming and attribution obligations (must include "Llama" in derivative name, share-alike clauses)
- Share-alike training data (CC-BY-SA, GPL) → propagates to derivative weights
- Proprietary / NDA training data → restricts publication of weights externally
- Mixed-license training data → most-restrictive license dominates

Conflicts are surfaced explicitly with a recommendation, not silently. If `audience="public"` and a conflict exists, the spec sheet emits a `publish-blocker` flag.

### Step 7: Intended use AND out-of-scope use

Both lists are required. The out-of-scope list is NOT a courtesy section; it is the single most actionable guidance for deploying teams and downstream users:

- **Primary use cases** — the tasks this fine-tune was trained for
- **Out-of-scope use cases** — tasks the model should NOT be deployed for, with reasons (out of training distribution, demographic harm risk, regulatory restriction, missing safety eval)
- **Target users** — the audience for whom the model is intended (engineers integrating into a chatbot, end-users of a specific product, internal analysts, etc.)

An empty `out_of_scope_use_cases: []` is rejected. The skill asks at least: "Is this fine-tune appropriate for medical advice? Legal advice? Financial advice? Use against minors? Use in adversarial / red-team contexts? Cross-language deployment to languages outside the training mix?" Common out-of-scope clauses live in `reference/intended-use-prompts.md` as a checklist.

### Step 8: Emit + completeness verdict

Outputs:

- `MODEL_CARD.md` — the human-readable spec sheet
- `model-card.json` — machine-readable companion for registry indexing
- **Completeness verdict** — `complete-publishable` / `complete-with-warnings` / `incomplete-do-not-publish`

For `audience="regulated"`, any high-severity warning (missing audit manifest, missing eval report, license conflict, empty out-of-scope) → `incomplete-do-not-publish`.

For `audience="public"`, missing fields produce warnings but not blockers; the user can publish with a "completeness disclosed" footer.

## Outputs

1. **`MODEL_CARD.md`** — single-file markdown spec sheet with the 7 sections
2. **`model-card.json`** — machine-readable companion; keys mirror the section structure
3. **`completeness-report.md`** — per-section verdict + the overall verdict + remediation list for missing or incomplete sections
4. **Embedded provenance links** — relative paths to the data audit manifest, the eval report, the training recipe config, and any per-segment breakdown reports

## Failure modes

- **Base revision_sha given as a tag (e.g., `main`)** — caught by Step 1's explicit refusal to accept a tag; SHA is required because tags move
- **Empty `limitations` list** — caught by Step 5's rejection; silence on limitations is not allowed
- **Empty `out_of_scope_use_cases`** — caught by Step 7's rejection; the out-of-scope list is the most actionable section
- **License conflict silently published** — caught by Step 6's conflict surfacing; publish-blocker for `audience="public"`
- **No data audit manifest** — caught by Step 2's high-severity warning; blocking for `audience="regulated"`
- **No paired eval report** — caught by Step 4's high-severity warning; blocking for `audience="regulated"`. The spec sheet does NOT accept a single-number metric ("the fine-tune got 73%") as eval evidence; the paired comparison is required.
- **Spec sheet written for a personal scratch experiment that should not have one** — caught by `When NOT to use` redirecting to a notebook README; the spec sheet is for deliverables, not experiments
- **Spec sheet treated as the safety certification** — caught by the opening framing: the spec sheet documents what was done; the safety / fairness / robustness certifications are separate processes whose results the spec sheet records

## References

- `reference/spec-sheet-template.md` — the full markdown skeleton with placeholders for every field
- `reference/intended-use-prompts.md` — checklist of common out-of-scope use-cases to consider per deployment domain
- [Mitchell et al. 2019 *Model Cards for Model Reporting*, FAT*](https://arxiv.org/abs/1810.03993) — the canonical model card paper
- [Hugging Face Model Card Guidebook](https://huggingface.co/docs/hub/model-card-guidebook) — practical model-card template
- [EU AI Act — Article 13 Transparency](https://artificialintelligenceact.eu/article/13/) — regulatory framing for high-risk model documentation (catalog NOT bundled with this skill; cited for context)
- `ml-datasci/auditing-sft-dataset` — the audit manifest this spec sheet links to in Step 2
- `ml-datasci/running-eval-before-after-finetune` — the eval report this spec sheet links to in Step 4

## Examples

### Example 1: Internal DPO fine-tune ready for registry (happy-path)

Input: `model_name="acme-support-dpo-v1"`,
`base_checkpoint={org: "meta-llama", name: "Llama-3.1-8B-Instruct", revision_sha: "<40-char SHA>", license: "Llama-3.1 Community License"}`,
`training_data_manifest="./audit-manifest.json"` (12K preference pairs,
audit produced by `auditing-sft-dataset`),
`training_recipe={objective: "dpo", library: "trl 0.11.4", hyperparameters: {lr: 5e-7, batch_size_effective: 32, beta: 0.1, epochs: 1}, hardware: "4×A100-80GB FSDP", seeds: 42, wall_time: "6h"}`,
`eval_report_path="./eval-report.md"` (paired McNemar from
`running-eval-before-after-finetune`, certified-improvement Δ=0.04
[95% CI: 0.01, 0.07]),
`limitations=["bias toward English-only", "refusal rate higher than base on adversarial inputs (intended)", "no eval on cross-lingual support tickets"]`,
`licenses={base_license: "Llama-3.1", training_data_licenses: ["internal proprietary"], weights_license: "internal proprietary"}`,
`intended_use={primary_use_cases: ["customer-support agent ranking helpful vs unhelpful responses"], out_of_scope_use_cases: ["medical advice", "legal advice", "financial advice", "use against minors"], target_users: ["ACME internal customer-support team"]}`,
`audience="internal"`.

Output: `MODEL_CARD.md` produced with all 7 sections populated;
`completeness-report.md` returns `complete-publishable`; `model-card.json`
companion emitted; the eval section quotes the paired McNemar result with
its effect size + CI; the limitations section enumerates 3 items; the
out-of-scope list is non-empty; license stack is consistent (internal
proprietary all the way).

### Example 2: Tag-only base + missing eval (edge-case)

Input: User supplies `base_checkpoint={org: "meta-llama", name: "Llama-3.1-8B", revision_sha: "main"}` and no `eval_report_path`. `audience="regulated"`.

Output: Skill refuses to proceed on the base_checkpoint — `main` is a
moving tag, not an immutable revision; asks for the SHA. Once SHA is
supplied, Step 4 still has no eval report → emits high-severity warning;
because `audience="regulated"`, this is a blocking issue. Completeness
verdict: `incomplete-do-not-publish`. Remediation list specifies: (1)
supply the eval report (run `running-eval-before-after-finetune` first if
not done), (2) supply the audit manifest if not yet linked.

### Example 3: Personal scratch experiment (anti-trigger)

Input: User says: "I fine-tuned a tiny model on my laptop for a weekend
project I'm just exploring. Should I write a spec sheet?"

Output: Skill does NOT walk the full spec-sheet workflow. Explains that
the spec sheet is for deliverables (publication, hand-off, regulated
deployment) and that a personal scratch experiment doesn't carry the
audience that needs it. Suggests a short README with three sections (what
I tried, what I observed, what I'd do next) instead. Offers to return to
the full workflow if the user later decides to publish.

## See also

- `ml-datasci/auditing-sft-dataset` — produces the data audit manifest cited in Step 2
- `ml-datasci/running-eval-before-after-finetune` — produces the eval report cited in Step 4
- `ml-datasci/writing-model-cards` — sibling for any-model documentation (this skill is the fine-tune-specific instance)
- `ml-datasci/reporting-effect-sizes` — the discipline behind the effect-size + CI requirement in Step 4
- `workflow/enforcing-seed-hygiene` — the discipline behind the seed reporting in Step 3
- `security/scaffolding-ai-policy-doc` (planned) — organizational AI policy (not model-specific); this skill is one model's spec sheet, not a policy

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-4, skill 5.4.3) via PRAGMATIC discipline
