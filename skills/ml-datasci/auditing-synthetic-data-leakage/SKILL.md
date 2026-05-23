---
name: auditing-synthetic-data-leakage
description: >
  Audits a synthetic dataset (SDG output) for membership-inference and
  record-linkage leakage from the real training set — runs a shadow-model MIA
  attack against the SDG, computes distance-to-closest-record (DCR) and
  nearest-neighbor distance ratio (NNDR) between synth and real-train, flags
  any exact / near-exact duplicates, and produces a release recommendation
  (publish / publish-with-DP / restrict / withhold). Triggers whenever the
  user intends to share, publish, or release synthetic tabular data derived
  from sensitive real data (PHI, PII, financial, customer records). Refuses
  to certify privacy on utility metrics alone, refuses to substitute
  k-anonymity-on-real for MIA-on-SDG, and hands off to
  auditing-synthetic-data-utility when the question is downstream-task
  fidelity rather than re-identification risk.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
  - data-engineer
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - genai_agentic_incidents
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Auditing Synthetic Data Leakage

## When to use

Trigger this skill when:

- A user is about to **share, publish, license, or release** a synthetic dataset derived from sensitive real data (PHI, PII, financial transactions, customer records, employee records)
- The user asks "is my synth data safe to release?", "how do I prove the synth set doesn't leak PII?", "did my generator memorize training rows?", "is this dataset HIPAA-safe / GDPR-safe?"
- A regulator, IRB, DPO, or external partner requires a privacy attestation for an SDG output
- The user is comparing SDG techniques (CTGAN vs DP-CTGAN vs Synthpop) and needs an empirical privacy axis alongside the utility axis
- An SDG was fit on a small minority subgroup (rare disease, high-net-worth customers) and the user needs to verify the synthetic outputs don't expose that subgroup
- Keywords: membership inference, MIA, shadow model, distance-to-closest-record, DCR, nearest-neighbor distance ratio, NNDR, k-anonymity on synth, ε-differential privacy, DP-CTGAN, synth-to-real duplicates

## When NOT to use

Skip this skill and hand off when:

- The question is **downstream-task utility**, not privacy → use `ml-datasci/auditing-synthetic-data-utility`. Utility and privacy are in tension; both audits are required for release decisions.
- The synth data is from a **public source** that was already in the public domain (open benchmarks, scraped public web pages, government open data) — there is no membership signal to protect; this skill's MIA workflow is over-engineered for that case
- The synth data is **text / image / audio** rather than tabular — MIA on text needs perplexity-based attacks; MIA on images needs gradient-based attacks. This skill is tabular-only.
- The real training data was already **k-anonymized / aggregated / DP-perturbed at the source** before the SDG was fit — privacy guarantees stack at the weakest point; auditing the SDG output adds noise to an already-noisy chain. Audit the source instead.
- The user wants **theoretical / formal DP guarantees** (ε, δ accounting) rather than empirical MIA scoring — refer to the DP literature; this skill is empirical-audit, not formal-proof.
- The dataset will **never leave the organization** (internal-only with the same access controls as the real data) — leakage risk = source-data risk; no incremental privacy claim is being made.

## Quick start

User: "I generated 50k synth patient records from a real 50k PHI set using CTGAN. I want to publish the synth set so other researchers can use it without IRB-level access. Is the synth set safe to release?"

Response: walks the 4-stage empirical privacy audit. Stage 1: exact and near-exact duplicate check (synth row byte-identical or within ε of a real row). Stage 2: distance-to-closest-record (DCR) — for each synth row, distance to its nearest real-train neighbor, compared against distance to nearest real-holdout neighbor. Stage 3: nearest-neighbor distance ratio (NNDR) — same neighbors but as a ratio. Stage 4: shadow-model membership-inference attack (MIA) — train shadow generators, build attack classifier that distinguishes "this synth row was generated from real-train" from "this synth row was generated from real-holdout". MIA AUC near 0.5 = no membership signal; AUC ≥ 0.6 = leak.

See `reference/mia-shadow-protocol.md` for the full attack recipe and `reference/release-decision-rubric.md` for the verdict thresholds.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `real_train` | DataFrame | yes | — | The real rows that were used to fit the SDG. The privacy target. |
| `real_holdout` | DataFrame | yes | — | Real rows that were NOT used to fit the SDG. Required as the negative class for MIA scoring. Must come from the same underlying distribution as `real_train` (sample from the same source, then split). |
| `synth` | DataFrame | yes | — | The synthetic dataset to audit. |
| `sdg_handle` | callable or path | recommended | — | A function or saved-model path that can re-fit the SDG on a new dataset. Required for Stage 4 (shadow-model MIA). Without it, the audit is limited to Stages 1-3. |
| `sensitive_columns` | list[str] | recommended | all non-key | Columns whose disclosure is the actual privacy harm (diagnoses, salaries, social-security tails). Drives weighted distance and per-attribute disclosure analysis. |
| `distance_metric` | str | no | "gower" | Gower (mixed-type tabular), euclidean (continuous-only), or hamming (categorical-only). |
| `n_shadow_models` | int | no | `5` | Shadow generators for Stage 4 MIA. More shadows = tighter MIA AUC estimate; cost scales linearly. |
| `n_bootstrap` | int | no | `200` | Bootstrap resamples for 95% CI on MIA AUC and DCR ratio. |
| `epsilon_dup` | float | no | `0.01` | Near-duplicate threshold (fraction of feature-space diameter) for Stage 1. |

## Workflow

Copy this checklist into the response and check items off as each step completes:

```
Synthetic-data leakage audit progress:
- [ ] 0. Pre-flight: real_train and real_holdout disjoint and same distribution; synth schema matches; sensitive_columns named
- [ ] 1. Exact-duplicate check: any synth row byte-identical to a real_train row (a direct re-identification)
- [ ] 2. Near-duplicate check: any synth row within ε of a real_train row in chosen metric (Stage 1 extended)
- [ ] 3. Distance-to-closest-record (DCR): per synth row, distance to nearest real_train neighbor; compare to distance to nearest real_holdout neighbor
- [ ] 4. Nearest-neighbor distance ratio (NNDR): per synth row, ratio of 1st-nearest to 2nd-nearest real_train distance; identical structure to NNDR in image SDG audits
- [ ] 5. Shadow-model MIA: train n_shadow_models SDGs on disjoint real subsets; attack classifier predicts membership from synth row features; AUC = leakage signal
- [ ] 6. Per-attribute disclosure: for each sensitive_column, the per-record disclosure risk (entropy reduction conditional on synth-row attributes)
- [ ] 7. Bootstrap 95% CI on MIA AUC and DCR ratio
- [ ] 8. Verdict: publish / publish-with-DP / restrict-distribution / withhold per `reference/release-decision-rubric.md`
- [ ] 9. Hand-off check: if MIA AUC borderline, recommend re-fitting SDG with differential privacy budget ε (DP-CTGAN, DP-Synthpop) and re-audit
```

### Step 0: Pre-flight

Refuse if:

- `real_train` and `real_holdout` overlap on any ID — MIA scoring requires disjoint sets
- `real_holdout` was drawn from a different population / time period than `real_train` — would confound MIA AUC with distribution shift
- `synth` was generated using `real_holdout` rows in any way — would invalidate the negative class
- `sensitive_columns` is empty — without naming what disclosure means, the audit cannot prioritize findings

### Step 1: Exact-duplicate check

`pd.merge(real_train, synth, how='inner')` on all columns. Any non-empty result is a **direct re-identification** — a synth row is a verbatim copy of a real row. Verdict: withhold unconditionally until the SDG is re-fit. Some SDGs (especially over-fit GANs or noiseless copulas on rare records) produce exact copies; this catches them.

### Step 2: Near-duplicate check

For each synth row, find the nearest real_train row in the chosen distance metric. Flag any synth row whose distance is less than `epsilon_dup * feature_space_diameter`. Near-duplicates allow re-identification under noise tolerance — a synth record that matches a real record on all-but-one feature is a re-identification with high confidence.

### Step 3: Distance-to-closest-record (DCR)

For each synth row, compute:

- `d_train` = distance to nearest neighbor in real_train
- `d_holdout` = distance to nearest neighbor in real_holdout

Report the median ratio `d_train / d_holdout`. If the median ratio < 0.9, synth rows are systematically closer to real_train than to real_holdout — the SDG has memorized training-set neighborhoods. Closer-to-train means re-identification of train members is easier than of holdout members.

### Step 4: Nearest-neighbor distance ratio (NNDR)

For each synth row, find the 1st-nearest and 2nd-nearest neighbors in real_train. NNDR = `d_1st / d_2nd`. NNDR near 0 means the synth row is very close to exactly one real row (a likely memorization). NNDR near 1 means the synth row sits between many similar real rows (a healthy generalization). Report NNDR distribution; flag synth rows with NNDR < 0.5 as memorization-suspect.

### Step 5: Shadow-model MIA

The empirical privacy gold standard for SDG. Recipe:

1. Partition real data into `K` disjoint splits `R_1, ..., R_K`
2. For each `i`, fit a shadow SDG `G_i` on `R_i`; generate `S_i`
3. For each `i`, label rows in `S_i ∪ R_i` with `member = 1` (real rows in `R_i`) or `member = 0` (synth rows in `S_i`); plus rows from real not in `R_i` labeled `member = 0`
4. Train an attack classifier on `(row features → member label)` across all shadows except the target
5. Apply attack to the actual SDG's `synth` set against `real_train`
6. Report attack AUC

MIA AUC interpretation:

- 0.50 ± 0.03 — no membership signal (privacy preserved empirically)
- 0.55 – 0.60 — borderline; consider re-fitting with DP
- ≥ 0.60 — empirical leak; SDG output unsafe for release without DP

### Step 6: Per-attribute disclosure

For each `sensitive_column`, measure how much an attacker holding `(synth_row, public_quasi_identifiers)` can reduce uncertainty about that attribute for a real_train member. Use conditional entropy or Bayesian posterior over the attribute given the quasi-identifiers + synth-row features. Flag any attribute where conditional entropy drops more than 50% from the prior.

### Step 7: Bootstrap 95% CI

Resample synth rows (and shadow-model splits for Stage 5) `n_bootstrap` times. Report 95% CI on MIA AUC and DCR median ratio. CIs spanning [0.50, 0.65] for MIA AUC mean "cannot rule out a leak" even if the point estimate looks fine.

### Step 8: Verdict

Per `reference/release-decision-rubric.md`. The verdict combines duplicate count + DCR + MIA AUC + per-attribute disclosure.

### Step 9: Hand-off

If verdict is `publish-with-DP` or `restrict-distribution`, recommend re-fitting the SDG with a differential-privacy budget (DP-CTGAN, DP-Synthpop, PATE-GAN) and re-running this audit. Note that DP degrades utility; the user must then re-run `auditing-synthetic-data-utility` to verify utility stays acceptable post-DP.

## Outputs

A markdown report:

1. **Audit summary** — real_train n, real_holdout n, synth n, sensitive_columns, distance_metric
2. **Stage 1 / 2: exact and near-duplicate counts** — with example rows redacted (do not echo PII into the report)
3. **Stage 3: DCR distribution** — median, IQR, train-vs-holdout ratio
4. **Stage 4: NNDR distribution** — fraction of synth rows with NNDR < 0.5
5. **Stage 5: MIA AUC** — point + 95% CI per shadow run
6. **Stage 6: per-attribute disclosure** — entropy-reduction percentage per sensitive_column
7. **Verdict** — publish / publish-with-DP / restrict-distribution / withhold with rationale
8. **Remediation** — if not "publish", named SDG modifications and re-audit requirement

## Failure modes

- **Utility-only privacy claim** — "low utility = high privacy". Empirically false. Caught by `When NOT to use` hand-off and the explicit MIA AUC requirement.
- **K-anonymity on synth as a privacy substitute** — k-anonymity on the synth set says nothing about whether real-train members are re-identifiable; it only describes synth-row uniqueness. Caught by the workflow not including k-anon-on-synth and `reference/release-decision-rubric.md` explicitly rejecting it.
- **MIA AUC without confidence interval** — reporting "MIA AUC = 0.54" without a CI lets borderline leaks pass. Caught by Stage 7 bootstrap CI as a required output.
- **No shadow models** — Stage 5 requires an SDG that can be re-fit. Some pre-built synth datasets ship without the generator; in those cases, the audit is limited to Stages 1-3 + reduced confidence. Caught by `sdg_handle` being recommended (not strictly required) and the report noting reduced confidence when missing.
- **Real_holdout from a different distribution** — confounds MIA AUC with covariate shift. Caught by step 0 pre-flight refusing on visible distribution shift.
- **Sensitive columns not specified** — the audit cannot prioritize. Caught by step 0 refusal.
- **PII echoed into the report** — when reporting exact / near duplicates, the report must redact or hash the duplicate rows. Failure mode caught by output format spec (step 1 / 2 outputs are counts + redacted examples, not raw rows).
- **DP-CTGAN with no privacy budget tracking** — DP-CTGAN with `ε = ∞` is non-private; the user must verify the budget. Caught by hand-off recommendation including "verify DP budget ε ≤ documented threshold per dataset class".

## References

- `reference/mia-shadow-protocol.md` — full shadow-model attack recipe with code skeleton
- `reference/release-decision-rubric.md` — verdict thresholds per release-scope and data-class (PHI / PII / financial / general)
- [Shokri, Stronati, Song, Shmatikov 2017 *Membership Inference Attacks against Machine Learning Models*](https://arxiv.org/abs/1610.05820) — original shadow-model MIA paper
- [Carlini, Tramèr, Wallace et al. 2021 *Extracting Training Data from Large Language Models*](https://arxiv.org/abs/2012.07805) — memorization in generative models broadly
- [Stadler, Oprisanu, Troncoso 2022 *Synthetic Data — Anonymisation Groundhog Day*](https://arxiv.org/abs/2011.07018) — empirical critique of synthetic-data privacy claims; explicitly the case for MIA audits over k-anon claims
- [Hyeong, Kim, Cho 2022 *An Empirical Study on the Membership Inference Attack against Tabular Data Synthesis Models*](https://arxiv.org/abs/2208.08114) — DCR + NNDR + MIA tabular benchmark

## Examples

### Example 1: PHI release with shadow-model MIA (happy-path)

Input: "I generated 50k synth patient records from a real 50k PHI set using CTGAN. real_train = 40k, real_holdout = 10k. SDG handle available. Sensitive columns: diagnosis_code, salary_bracket, postcode_outward. I want to publish for external research. Audit privacy."

Output: Skill confirms preflight (disjoint splits, same source, schema match). Stage 1: 0 exact duplicates. Stage 2: 3 near-duplicates flagged (within 0.5% feature-space diameter) — examples hashed and reported. Stage 3: DCR median ratio = 0.96 (synth rows slightly closer to real_train than holdout; borderline). Stage 4: NNDR < 0.5 for 1.8% of synth rows (low memorization). Stage 5: MIA AUC = 0.57 [95% CI: 0.52, 0.62] (borderline leak). Stage 6: diagnosis_code conditional entropy reduces 38% under attack (acceptable); postcode_outward reduces 71% (concerning). **Verdict: publish-with-DP**. Recommends re-fitting with DP-CTGAN at ε = 1.0 and re-running this audit + the utility audit.

### Example 2: Borderline MIA AUC needs CI before decision (edge-case)

Input: "MIA AUC = 0.55. The point estimate looks fine. Can I publish?"

Output: Skill refuses to decide on point estimate alone. Computes 95% CI via bootstrap: [0.49, 0.63]. Explains that CI spanning 0.50 (no signal) to 0.63 (clear leak) means the audit cannot rule out a meaningful leak. Recommends one of: (a) increase n_shadow_models from 5 to 20 to tighten the CI, (b) treat the upper-bound 0.63 as the operative number and verdict accordingly (likely publish-with-DP or restrict-distribution), (c) re-fit with DP and re-audit. Refuses to publish under uncertainty when the dataset class is PHI / PII / financial.

### Example 3: Public benchmark dataset, no privacy signal (anti-trigger)

Input: "I want to release synth versions of the Adult Census Income public benchmark dataset. Should I run a leakage audit?"

Output: Skill explains that Adult Census Income is already public domain; the original real records are not protected and have been in the public ML literature since 1996. There is no membership signal to protect — anyone can re-identify the original rows from the source URL directly. The full MIA audit is over-engineered for this case. Suggests: (a) note in the release that the source is public, (b) optionally run Stage 1 (exact duplicate check) for cleanliness, (c) skip Stages 3-6 (no actionable privacy verdict for a public-source SDG). Hands off to `auditing-synthetic-data-utility` if the user's actual question is whether the synth set is useful as a benchmark.

## See also

- `ml-datasci/auditing-synthetic-data-utility` — the utility sibling; both audits are required for any high-stakes release because utility and privacy trade off
- `ml-datasci/auditing-train-test-split` — the real_train / real_holdout split must be leakage-free; this skill assumes that audit has already been run
- `security/scrubbing-PII-with-policy` (planned) — pre-SDG step to reduce exposure surface; complementary to this audit, not a substitute
- `security/verifying-training-data-erasure` (planned) — DSR-proof workflow for fine-tuned models; this skill is the upstream synth-data analogue
- `workflow/auditing-data-quality` — required pre-step on the real source data; corrupt source → corrupt SDG → corrupt audit

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-5, skill 2) via PRAGMATIC discipline
