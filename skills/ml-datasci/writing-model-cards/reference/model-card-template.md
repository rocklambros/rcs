# Model card template (Mitchell 2019 + AIBOM)

Copy this template and fill every section. Vague placeholders ("TBD", "may have biases", "should be used responsibly") are not acceptable for a production model card.

---

# Model card: `<model-name-vX.Y.Z>`

## 1. Model details

- **Name**: `<model-name>`
- **Version**: `<SemVer>`
- **Architecture**: `<gradient-boosted trees | fine-tuned BERT | ResNet-50 | ...>`
- **Training framework + version**: `<LightGBM 4.5.0 | PyTorch 2.4.1 + HuggingFace transformers 4.42.0 | ...>`
- **Trained on**: `<YYYY-MM-DD>` (training run completion date)
- **Pretrained backbone** (if fine-tune): `<model_id + revision_hash + license>`
- **Maintainer**: `<team-alias@org>`
- **Last reviewed**: `<YYYY-MM-DD>`
- **Next review**: `<YYYY-MM-DD>`
- **License**: `<license + commercial-use status>`

## 2. Intended use

**In-scope use cases:**

- `<concrete use case 1>`
- `<concrete use case 2>`

**Out-of-scope use cases:**

- `<explicit out-of-scope use 1>`
- `<explicit out-of-scope use 2>`
- (e.g. "Used as the sole basis for criminal investigation"; "Used outside the trained currency / amount / language range"; "Used in clinical decision support without a clinician in the loop")

**Primary intended users:**

- `<who consumes this model's outputs>` (e.g. "Fraud-detection backend at decision time"; "Triage queue prioritization assistant for medical reviewers")

## 3. Factors

Dimensions affecting model performance:

- `<demographic factor>` (if measured + legally permissible)
- `<geographic factor>` (country / region / locale)
- `<temporal factor>` (model trained on data window; behavior on newer traffic)
- `<device / channel factor>`
- `<language / script factor>`

Each factor named here MUST appear with disaggregated metrics in section 7.

## 4. Metrics

**Aggregate metrics + 95% CIs (bootstrap n = 1000+):**

| Metric | Value | 95% CI |
|---|---|---|
| `<metric_1>` | `<value>` | `[<lo>, <hi>]` |
| `<metric_2>` | `<value>` | `[<lo>, <hi>]` |

**Threshold (if classification):** `<value>` (chosen per `ml-datasci/tuning-classification-threshold` using `<selector>` with `<parameter>`)

## 5. Evaluation data

- **Source**: `<dataset name + URL + version>`
- **Collection window**: `<start_date>` to `<end_date>`
- **License**: `<license>`
- **n_samples**: `<count>`
- **Subgroup composition**: `<{subgroup_factor: distribution}>`
- **Known biases / limitations**: `<concrete biases — selection, missing groups, temporal drift indicators>`
- **Exclusion criteria**: `<what was filtered out and why>`
- **Hash (canonical evaluation set)**: `<SHA-256>`

## 6. Training data

- **Source**: `<dataset name + URL + version>`
- **Collection window**: `<start_date>` to `<end_date>`
- **License**: `<license>`
- **n_samples**: `<count>`
- **Subgroup composition**: `<{subgroup_factor: distribution}>`
- **Known biases / limitations**: `<concrete biases — selection, missing groups, temporal drift indicators>`
- **Exclusion criteria**: `<what was filtered out and why>`
- **Hash (canonical training set)**: `<SHA-256>`

## 7. Quantitative analyses

Per-subgroup metrics + 95% CIs across the factors in section 3:

| Factor | Subgroup | n | Metric | Value | 95% CI |
|---|---|---|---|---|---|
| `<factor>` | `<subgroup_value>` | `<n>` | `<metric>` | `<value>` | `[<lo>, <hi>]` |
| ... |

**Fairness gap analysis:** for each factor, the worst-vs-best disparity in the primary metric. Flag any gap exceeding `<pre-registered threshold>`.

**Leakage firewall status:** `<pass | conditional | fail>` per `ml-datasci/enforcing-leakage-firewall`. If conditional or fail, the gaps reported above may reflect leakage and not true model behavior — block deployment until firewall passes.

## 8. Ethical considerations, caveats, and recommendations

**Named harms:**

- `<harm 1 — concrete, deployment-specific — e.g. "False positive blocks a legitimate transaction → customer harm + churn risk">`
- `<harm 2 — concrete, deployment-specific — e.g. "False negative misses fraud → institutional financial loss + downstream customer harm">`
- `<harm 3 — disparity — e.g. "Demographic disparity in either rate → discrimination, regulatory liability, civil-rights harm">`

**Mitigations for each named harm:**

| Harm | Mitigation |
|---|---|
| `<harm 1>` | `<mitigation — concrete>` |
| ... |

**Residual risks (not mitigated):**

- `<risk + monitoring plan>`

**Out-of-distribution behavior:** `<known behavior on inputs outside the trained distribution — graceful degradation, refusal, escalation, etc.>`

**Recommendations for downstream users:**

- `<concrete recommendation>` (e.g. "Pair with a human-in-the-loop reviewer for borderline scores in the [0.4, 0.6] range")

## 9. AIBOM addendum (AI supply-chain traceability)

**Direct dependencies:**

| Component | Name | Version | Source URL | Hash | License |
|---|---|---|---|---|---|
| Framework | `<LightGBM>` | `<4.5.0>` | `<URL>` | `<sha256>` | `<MIT>` |
| Pretrained backbone | `<bert-base-uncased>` | `<revision_hash>` | `<HF URL>` | `<sha256>` | `<Apache-2.0>` |
| Embedding model | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |
| Vocabulary / lookup | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

**Training-data manifest hash**: `<SHA-256>`
**Model artifact hash**: `<SHA-256>`
**Build environment**:
- Container image: `<image:tag@sha256:...>`
- Python: `<3.13.0>`
- OS: `<distro + version>`

## 10. Sign-off

- **Maintainer**: `<name + alias>`
- **Reviewed by**: `<reviewer + role + date>`
- **Approved for deployment context**: `<production | staging | research-only | open-weights>`
- **Change log**: `<link to commit history or changelog file>`
- **Next review date**: `<YYYY-MM-DD>`
- **Incident-response contact**: `<oncall alias + escalation path>`
