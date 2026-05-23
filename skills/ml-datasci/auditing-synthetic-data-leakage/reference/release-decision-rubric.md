# Release-Decision Rubric

Verdict thresholds for synthetic-data release decisions. Combines Stage 1-2 (duplicate counts), Stage 3-4 (DCR / NNDR), Stage 5 (MIA AUC), and Stage 6 (per-attribute disclosure). All thresholds tighten as the data sensitivity class rises.

## Sensitivity classes

| Class | Examples |
|---|---|
| **PHI** | Protected health information per HIPAA — diagnoses, medication history, genetic data |
| **PII-high** | Direct identifiers — SSN, full name + DOB, biometrics |
| **PII-low** | Pseudo-identifiers — postcode prefix, age band, occupation category |
| **Financial** | Salary, account balance, transaction history, credit score |
| **Customer** | Behavior logs, preferences, location traces |
| **Public** | Already-public-domain benchmarks — no protected membership signal exists |

## Verdict thresholds (per sensitivity class)

### PHI

| Signal | Publish | Publish-with-DP | Restrict-distribution | Withhold |
|---|---|---|---|---|
| Exact duplicates (Stage 1) | 0 | 0 | n/a | ≥ 1 |
| Near duplicates (Stage 2) | 0 | ≤ 5 (with redaction) | ≤ 50 | > 50 |
| DCR median ratio train/holdout (Stage 3) | ≥ 0.98 | 0.92 – 0.98 | 0.85 – 0.92 | < 0.85 |
| NNDR < 0.5 fraction (Stage 4) | ≤ 0.005 | 0.005 – 0.02 | 0.02 – 0.05 | > 0.05 |
| MIA AUC point (Stage 5) | ≤ 0.52 | 0.52 – 0.57 | 0.57 – 0.62 | > 0.62 |
| MIA AUC 95% CI upper bound | ≤ 0.55 | ≤ 0.60 | ≤ 0.65 | > 0.65 |
| Max per-attribute entropy reduction (Stage 6) | ≤ 0.30 | 0.30 – 0.50 | 0.50 – 0.70 | > 0.70 |

The verdict is the **worst** band any signal lands in. A dataset with perfect Stages 1-4 and a Stage 5 MIA AUC of 0.59 is `publish-with-DP`, not `publish`, because Stage 5 alone bumps the verdict.

### PII-high / Financial

Same thresholds as PHI.

### PII-low / Customer

| Signal | Publish | Publish-with-DP | Restrict | Withhold |
|---|---|---|---|---|
| Exact duplicates | 0 | 0 | ≤ 10 | > 10 |
| MIA AUC point | ≤ 0.55 | 0.55 – 0.62 | 0.62 – 0.70 | > 0.70 |
| MIA AUC 95% CI upper | ≤ 0.58 | ≤ 0.65 | ≤ 0.72 | > 0.72 |
| Max per-attribute entropy reduction | ≤ 0.40 | 0.40 – 0.60 | 0.60 – 0.80 | > 0.80 |

### Public

No leakage audit is required for utility purposes — the source data is already accessible. Recommend Stage 1 only (exact duplicate cleanliness check) and skip the rest. Treat any signal as informational, not gating.

## Differential-privacy budget guidance

When verdict is `publish-with-DP`:

| Sensitivity class | Recommended ε per dataset | Notes |
|---|---|---|
| PHI | ε ≤ 1.0 | Match HIPAA Safe Harbor expectations; further restrict in long-tail / rare-disease subsets |
| PII-high / Financial | ε ≤ 1.0 | Same as PHI; tighter (ε ≤ 0.5) if external research partner is untrusted |
| PII-low / Customer | ε ≤ 5.0 | Looser is acceptable; verify utility holds after DP via auditing-synthetic-data-utility |

After re-fitting with DP, re-run this audit. The MIA AUC should drop into the `publish` band; if it does not, ε is too loose for the dataset.

## Reporting template

```markdown
## Privacy verdict

| Stage | Signal | Threshold (PHI) | Observed | Band |
|---|---|---|---|---|
| 1 | Exact duplicates | 0 | {n_exact} | {band} |
| 2 | Near duplicates | 0 | {n_near} | {band} |
| 3 | DCR ratio train/holdout | ≥ 0.98 | {dcr_ratio} | {band} |
| 4 | NNDR < 0.5 fraction | ≤ 0.005 | {nndr_frac} | {band} |
| 5 | MIA AUC point | ≤ 0.52 | {mia_auc} | {band} |
| 5 | MIA AUC 95% CI upper | ≤ 0.55 | {mia_ci_upper} | {band} |
| 6 | Max attribute entropy reduction | ≤ 0.30 | {entropy_red} | {band} |

**Verdict**: {worst_band}

**Remediation** (if not "publish"): {named SDG modification + re-audit requirement}

**Hand-off**: re-run `ml-datasci/auditing-synthetic-data-utility` to verify utility post-DP.
```
