---
name: writing-model-cards
description: >
  Authors a deployment-ready model card per Mitchell et al. 2019 plus AIBOM
  additions for AI supply-chain traceability: intended and out-of-scope use,
  training and evaluation data provenance with source, license, and collection
  date, metrics with confidence intervals across subgroups, known limitations,
  ethical considerations and harms, license, version, maintainer, and model
  dependencies with versions and hashes. Also emits a CycloneDX AIBOM JSON
  companion and verifies it scores 100% on the genai-security-project
  aibom-generator evaluator, fetching the evaluator's required
  fields dynamically at runtime so the card stays compliant as that repo
  changes. Triggers when a model moves toward production, when a compliance
  review (EU AI Act, NIST AI RMF, ISO/IEC 23894) asks for documentation, when
  an open-weights model is released, when an AIBOM is requested, or when a
  customer, regulator, or auditor requests a model card. Refuses for a research
  prototype not headed for deployment, where the format is overkill.
version: 0.2.0
status: shipped
track: ml-datasci
audience:
  - ml-engineer
  - data-scientist
  - security-eng
  - devops
evidence:
  - llm-safety-alignment-study
  - ai-security-framework-crosswalk
  - multiturn-injection-detection
last-updated: 2026-06-15
---

# Writing Model Cards

## When to use

Trigger this skill when:

- A model is moving from development to production deployment (any customer-facing inference path, any safety-critical decision, any externally observable behavior)
- A compliance review requires model documentation: EU AI Act Article 11 (technical documentation for high-risk AI), NIST AI RMF (Govern + Map), ISO/IEC 23894 (AI risk management), GDPR Article 22 (automated decision-making explanation), HIPAA/HITRUST for clinical AI
- An open-weights model is being released publicly (Hugging Face publish, GitHub release, internal model hub)
- A customer / regulator / auditor requests documentation about a deployed or about-to-be-deployed model
- A model is being included in an AI bill of materials (AIBOM) for supply-chain traceability
- A model handed off across teams (ML team → product team, ML team → SRE / oncall) needs a single document of record
- Keywords: model card, datasheet, AIBOM, intended use, model documentation, EU AI Act, AI RMF, model release

## When NOT to use

Skip this skill and hand off when:

- The model is a research prototype that is explicitly not headed for deployment, customer use, or external release — the model card format is overkill, and harms analysis without a deployment context is speculative (note the model is research-only in the project README instead)
- The model is throwaway exploratory work for a single notebook or paper-replication exercise
- The "documentation" need is implementation-specific (training code, hyperparameter sweep results, ablation tables) → those belong in a separate experiment log, not a model card
- The user wants a generic "AI ethics statement" for the company website rather than a per-model artifact → out of scope; model cards are per-model
- The user wants a data card (dataset documentation) rather than a model card → use Gebru et al. 2018 Datasheets for Datasets format; not in scope of this skill

## Quick start

User: "We're deploying a fraud-detection model to production next week. We need a model card for compliance review. Walk me through it."

Response: produce the eight Mitchell-2019 sections plus the AIBOM addendum: model details, intended use, factors / subgroups, metrics + CIs, evaluation data, training data, quantitative analyses across subgroups, ethical considerations + caveats + recommendations, AIBOM (dependencies + versions + hashes). Each section needs concrete content; placeholder text like "TBD" or "may have biases" fails the card. The fraud-detection context implies specific harms (false-positive blocking legitimate transactions = customer harm; false-negative missing fraud = institutional harm) that must be named.

```markdown
# Model card: fraud-detection-v2.3

## Model details
- Name: fraud-detection-v2.3
- Architecture: gradient-boosted decision tree (LightGBM)
- Trained: 2026-04-15 on 12.4M historical transactions
- ...

## Intended use
- In-scope: scoring real-time credit-card transactions for fraud risk
- Out-of-scope: any other transaction type (ACH, wire, BNPL)
- ...
```

See `reference/model-card-template.md` for the full eight-section + AIBOM template.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `model_name` | str | yes | — | Stable identifier including SemVer (e.g. `fraud-detection-v2.3`). |
| `deployment_context` | str | yes | — | Where this model will run: production / staged / research-internal-only / open-weights-release. Drives the depth of harms analysis. |
| `training_data_provenance` | dict | yes | — | At minimum: `source`, `collection_window`, `license`, `n_samples`, `known_biases`. |
| `evaluation_data_provenance` | dict | yes | — | Same fields as training data, plus `subgroup_columns` for subgroup metric reporting. |
| `metrics_with_ci` | dict | yes | — | `{metric_name: {value, ci_low, ci_high, subgroup_breakdown}}`. CIs must come from bootstrap or analytic — point estimates alone are not enough. |
| `known_limitations` | list of str | yes | — | Concrete limitations the team has observed in the model, not boilerplate. |
| `ethical_considerations` | list of str | yes | — | Specific harms enumerated per deployment context. |
| `dependencies` | list of dict | yes | — | For AIBOM compliance: `{name, version, source_url, hash}` for each direct dependency (framework, pretrained backbone, lookup table). |
| `maintainer_contact` | str | yes | — | Team alias or email for incident-response routing. |

## Workflow

```
Model card progress:
- [ ] 0. Deployment-context check — confirm card is appropriate (production / public release / compliance review); skip if research-only
- [ ] 1. Section 1: Model details (name, architecture, training date, version, maintainer)
- [ ] 2. Section 2: Intended use + out-of-scope use (concrete; reject vague language)
- [ ] 3. Section 3: Factors / subgroups (demographic, geographic, temporal, etc. that affect performance)
- [ ] 4. Section 4: Metrics + 95% CIs per subgroup (not just aggregate; surfaces fairness gaps)
- [ ] 5. Section 5: Evaluation data provenance (source, license, collection window, known biases)
- [ ] 6. Section 6: Training data provenance (same fields)
- [ ] 7. Section 7: Quantitative analyses (subgroup-disaggregated metrics with CIs)
- [ ] 8. Section 8: Ethical considerations, caveats, and recommendations
- [ ] 9. AIBOM addendum: dependencies with versions and hashes
- [ ] 10. Sign-off: maintainer, review date, next-review date
- [ ] 11. AIBOM 100% compliance: emit a CycloneDX AIBOM JSON companion and verify it scores 100% on the live evaluator
```

### Step 11: AIBOM 100% compliance

Every model card ships with a CycloneDX AIBOM JSON companion that scores 100% on the genai-security-project aibom-generator completeness evaluator. The evaluator's required fields change as that public repo evolves, so the requirements are fetched at runtime, never hard-coded. Run the bundled engine as a validator loop (scaffold, fill real values, score, fix gaps, repeat until 100%):

```bash
python3 scripts/aibom_compliance.py requirements              # live required fields + weights
python3 scripts/aibom_compliance.py scaffold model.aibom.json # maximal structure at every live jsonpath
# replace every <FILL:...> with real content from the markdown card above
python3 scripts/aibom_compliance.py score model.aibom.json    # exits 0 only at 100% with no penalty
```

The evaluator measures structural completeness, not truthfulness. A scaffold full of placeholders scores 100 and is worthless. Replace every placeholder with the model's real values before the card is submitted. See `reference/aibom-100-compliance.md` for the scoring model, the dynamic-lookup rationale, and the security note on running the evaluator's scorer.

### Section 2: Intended use + out-of-scope use

Both halves are required. "Intended use" alone is incomplete — the out-of-scope half is the place to name uses the team has explicitly considered and excluded.

- **In-scope** examples: "Score credit-card transactions in USD between $1 and $50,000 for fraud risk at decision time"
- **Out-of-scope** examples: "Used as the sole basis for criminal investigation; applied to non-card transaction types; applied to transactions outside the trained currency / amount range"

Reject vague placeholders: "may have unintended uses", "should be used responsibly".

### Section 3: Factors / subgroups

List the dimensions that affect model performance — demographic (where consented and legally permitted), geographic (region, country), temporal (model trained on 2025-Q1 data, behavior on 2026 traffic), device / channel, language. Each factor named here MUST appear in Section 7 with disaggregated metrics + CIs.

### Section 4: Metrics + 95% CIs

Aggregate metric is the headline; per-subgroup metrics + CIs are what reveal fairness gaps. CIs must come from bootstrap or analytic computation, never point estimates only. Cross-link to `ml-datasci/evaluating-binary-classifiers` or `evaluating-multiclass-classifiers` or `evaluating-regression-models` for the full evaluation report.

### Section 5 + 6: Data provenance

Each dataset (training, evaluation, monitoring) needs: source / vendor, collection window, license, n_samples, known biases (collection-time selection bias, missing groups, temporal drift indicators), exclusion criteria.

### Section 8: Ethical considerations

Name specific harms per deployment context, not generic "may exhibit bias":

- Fraud detection: false positive blocks a legitimate transaction → customer harm; false negative misses fraud → institutional + downstream-customer harm; demographic disparity in either rate → discrimination
- Medical screening: false negative misses disease → patient harm; false positive triggers unnecessary anxiety / cost → patient + system harm
- Hiring: any disparate impact across protected class → legal liability + civil rights harm; "AI screened candidates" framing may displace human review

Tie each named harm to a mitigation (threshold tuning per `ml-datasci/tuning-classification-threshold`, human-in-the-loop review, monitoring dashboard for subgroup drift).

### AIBOM addendum

For AI supply-chain traceability (executive guidance for federal AI procurement; emerging compliance frameworks 2025-2026):

- Direct dependencies: framework (PyTorch / TensorFlow / sklearn) with exact version + install hash; pretrained backbone (model name + hash + license) if fine-tuned; lookup tables / vocabularies (source + version + hash); embedding model (provider + version + dimension)
- Training-data hash: SHA-256 of the canonical training set (or the manifest hash if streaming)
- Model artifact hash: SHA-256 of the serialized model weights
- Build environment: container image hash, Python version, OS

## Outputs

A markdown model card with this structure:

1. **Model details** — name + SemVer + architecture + training date + maintainer
2. **Intended use + out-of-scope use** — concrete, both halves
3. **Factors / subgroups** — the dimensions that affect performance
4. **Metrics + 95% CIs** — aggregate + per-subgroup
5. **Evaluation data** — provenance + collection window + known biases
6. **Training data** — provenance + collection window + known biases
7. **Quantitative analyses** — subgroup-disaggregated metrics
8. **Ethical considerations, caveats, recommendations** — concrete harms + mitigations
9. **AIBOM addendum** — dependencies + versions + hashes + training-data hash + model artifact hash
10. **Sign-off** — maintainer + review date + next review date + change log link
11. **CycloneDX AIBOM JSON companion**: `model.aibom.json`, verified at 100% on the live genai-security-project aibom-generator completeness evaluator

## Failure modes

Known anti-patterns and how this skill catches them:

- **Vague "may have biases" language** — caught by section 8 requirement of concrete deployment-specific harms.
- **No out-of-scope use enumerated** — caught by section 2 requiring both halves.
- **Aggregate-only metrics, no subgroup breakdown** — caught by sections 3 + 4 + 7 requiring subgroup disaggregation with CIs.
- **Training data provenance reduced to "internal data"** — caught by section 6 fields (source, collection window, license, n_samples, known biases).
- **No AIBOM / no dependency versions** — caught by section 9; supply-chain traceability is now table stakes for production AI.
- **"Will update later" placeholders** — caught by step 0 deployment-context check; if the card is for production, all sections are required.
- **Authoring a card for a throwaway research notebook** — caught by `When NOT to use` and step 0.
- **AIBOM JSON below 100% on the evaluator** — caught by step 11; the `score` command exits non-zero and lists every missing field until the AIBOM is complete against the live registry.
- **Hard-coded AIBOM field list that drifts when the evaluator changes** — caught by step 11; the engine clones the public repo at run time and reads the live registry, so it never hard-codes the requirements.

## References

- `reference/model-card-template.md` — the full eight-section + AIBOM template ready to copy-paste-fill
- `reference/aibom-100-compliance.md`: making the AIBOM JSON companion score 100% on the live evaluator, with requirements fetched dynamically
- `scripts/aibom_compliance.py`: runtime engine that fetches live requirements, scaffolds a maximal AIBOM, and scores it with the evaluator's own scorer
- [genai-security-project/aibom-generator](https://github.com/genai-security-project/aibom-generator): the AIBOM completeness evaluator this skill targets
- [Mitchell et al. 2019 *Model Cards for Model Reporting* (FAT* 2019)](https://doi.org/10.1145/3287560.3287596) — original model-card format
- [Gebru et al. 2018 *Datasheets for Datasets*](https://arxiv.org/abs/1803.09010) — sibling format for dataset documentation; cross-link from sections 5 + 6
- [EU AI Act Article 11 — Technical documentation for high-risk AI](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) — compliance reference
- [NIST AI RMF 1.0](https://doi.org/10.6028/NIST.AI.100-1) — Govern + Map functions tie to model-card content
- [NTIA AIBOM workstream](https://www.ntia.gov/programs/ai-accountability) — AI bill of materials guidance

## Examples

### Example 1: Production-bound fraud detector (happy-path)

Input: "We're deploying a fraud-detection model to production next week. Need a model card for compliance review (EU AI Act high-risk classification). Walk me through it."

Output: Skill produces the full eight-section card. Section 2 names in-scope (real-time credit-card scoring, USD, $1-$50K) and out-of-scope (ACH, wire, BNPL, criminal-investigation use). Section 3 names factors: card-issuing country, transaction amount band, merchant category, time-of-day. Section 4 reports aggregate ROC-AUC + PR-AUC with bootstrap 95% CIs, links to `evaluating-binary-classifiers` for the full report. Section 7 disaggregates metrics by the named factors. Section 8 names specific harms (FP blocks legitimate transaction → customer harm; FN misses fraud → loss; demographic disparity in either → discrimination) and pairs each with a mitigation (threshold-per-segment per `tuning-classification-threshold`, manual review queue for borderline scores, daily subgroup-drift dashboard). AIBOM addendum lists LightGBM version + hash, training-data hash, model artifact hash.

### Example 2: Open-weights model release with potential redistribution downstream (edge-case)

Input: "We're open-weights releasing a fine-tuned BERT for medical-document classification. Used internal clinical notes for fine-tuning. What goes in the model card?"

Output: Skill flags the dual concerns. (a) Clinical-note training data: even if open-weights, the data provenance section must address whether the model could memorize / regurgitate PHI (membership-inference + training-data-extraction risk); recommends membership-inference test results in section 7 + an explicit harm note in section 8. (b) Open-weights distribution means downstream fine-tuners + integrators are unknown — out-of-scope use in section 2 must explicitly enumerate clinical-decision use, prescribing, and triage as out-of-scope (the model is a research artifact, not a clinical decision-support system) with a strong recommended-mitigations block. AIBOM addendum is mandatory for a public release.

### Example 3: Throwaway research notebook (anti-trigger)

Input: "I'm reproducing a paper's CNN on CIFAR-10 in a Jupyter notebook for a class assignment. Should I write a model card?"

Output: Skill identifies this as a throwaway research / pedagogy artifact with no deployment context, no customer exposure, no downstream redistribution. The model card format is overkill — harms analysis without a deployment context is speculative; the AIBOM addendum is busywork. Recommends a short README in the notebook directory naming the paper, the version of CIFAR-10 used, the libraries, and the run-environment, instead of a full model card. Notes that if the notebook later becomes the basis for an actual deployment, return to this skill at that point.

## See also

- `ml-datasci/evaluating-binary-classifiers` — produces the metrics + CIs that populate section 4 + 7 of the card for binary classifiers
- `ml-datasci/evaluating-multiclass-classifiers` — same, for multi-class
- `ml-datasci/evaluating-regression-models` — same, for regression
- `ml-datasci/tuning-classification-threshold` — the threshold-selection rationale belongs in section 4 of the card
- `ml-datasci/enforcing-leakage-firewall` — the firewall results belong in section 5 + 6 of the card (training and evaluation data integrity)
- `ml-datasci/auditing-train-test-split` — same; the split discipline goes in section 5 + 6
- `workflow/auditing-source-provenance` — sibling for the underlying dataset; the data-provenance fields here cross-reference its output

## Status & version

- Status: shipped
- Version: 0.2.0
- Last-updated: 2026-06-15
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-2, skill 3) via PRAGMATIC discipline. v0.2.0 adds the AIBOM 100% compliance engine (`scripts/aibom_compliance.py`, `reference/aibom-100-compliance.md`) verified against the live genai-security-project aibom-generator scorer.
