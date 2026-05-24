---
name: applying-differential-privacy
description: >
  Applies differential privacy (DP) to a machine-learning training run or analytic
  query workload — chooses ε / δ budget tied to the threat model, picks the right
  mechanism (Gaussian / Laplace / RDP-accounted DP-SGD), sets the noise scale to
  match the budget given the L2 sensitivity, and tracks composition across multiple
  queries or training steps using RDP (Rényi Differential Privacy) or moments
  accountant. Use when training an ML model on records with formal privacy
  requirements (HIPAA, GDPR, sensitive customer data), when releasing analytics on
  small-population data where re-identification is the risk, when a regulator or
  legal team asks for a formal privacy guarantee, or when ad-hoc anonymization
  (column dropping, hashing, k-anonymity) has been requested but is insufficient
  for the threat model. Refuses to apply DP when k-anonymity / pseudonymization
  is sufficient for the actual threat or when ε is set high enough to provide
  no meaningful guarantee.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
  - ai-security
  - privacy-engineer
evidence:
  - genai_agentic_incidents
  - ai-security-framework-crosswalk
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Applying Differential Privacy

> **DP is a guarantee about a mechanism, not a label about a dataset.** "This
> data is DP" is meaningless; "this query / training pipeline satisfies
> (ε = 1.0, δ = 1e-5)-DP under composition" is the actual statement. Refuse to
> issue the former.

## When to use

Trigger this skill when the user asks for or implies one of:

- Training an ML model where the training records carry formal privacy obligations (HIPAA-protected health, GDPR special-category, financial PII, biometric data)
- Releasing aggregate analytics, dashboards, or statistics on small-population data where individuals could be re-identified from query results (e.g., census tabulations, hospital outcomes by rare condition, school-level student data)
- A regulator, legal team, or privacy office asks for a formal mathematical privacy guarantee — phrases like "differential privacy," "epsilon budget," "noise injection," "privacy accounting"
- The user proposes k-anonymity or hash-based pseudonymization for a use case where the adversary has auxiliary information or repeated query access (the standard k-anonymity failure mode)
- A model is being fine-tuned on a small private corpus where membership-inference attacks are a credible threat

## When NOT to use

Skip this skill and hand off when:

- The threat is **access control**, not statistical inference — the right answer is authentication / authorization / encryption, not DP
- **k-anonymity is genuinely sufficient** — single-release, no query repeat, no auxiliary linkage, the attribute being released does not enable re-identification through join with public data
- The user is asking about **homomorphic encryption, secure multi-party computation, or trusted execution environments** — different category of privacy tech; DP is statistical, those are cryptographic
- The user wants to **delete data** for a Data Subject Request — hand off to `security/verifying-training-data-erasure` (planned in v7-batch-5)
- ε would need to be set so large (typically ε ≥ 10 with δ ≥ 1e-3) that no meaningful guarantee survives — refuse and explain rather than producing security theater

## Quick start

User says: "We're fine-tuning a clinical NLP model on 100K patient discharge summaries. Compliance wants 'differential privacy.' What ε do we use and how do we get there?"

Skill response: confirms the threat model (membership-inference on the fine-tuned model from an adversary with query access), recommends an ε budget tied to the regulatory baseline (HIPAA: typically ε ≤ 3 for de-identified-equivalent release; the user's office may have stricter), δ = 1 / (n × log n) ≈ 1e-7 for n = 100K, prescribes DP-SGD with RDP accountant (Opacus for PyTorch, dp-accounting for the math), specifies clipping bound C and noise multiplier σ derived from ε and the number of steps, and produces a privacy budget table that shows the total (ε, δ) accumulated across all training steps + the final-model membership-inference resistance estimate.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| threat_model | "membership-inference" \| "attribute-disclosure" \| "reconstruction" \| "query-aggregation" | yes | — | What the adversary is trying to learn. DP applies to all four but the right ε, mechanism, and accounting differ. |
| sensitivity_metric | "L2" \| "L1" \| "global" \| "local" | yes | — | The function-sensitivity metric. For DP-SGD with per-example gradient clipping, L2 is standard. For count queries, global L1 = 1. |
| epsilon_target | float | yes | — | The total privacy budget after composition. Smaller = stronger guarantee, more noise. Values commonly seen: ε = 0.1 (strict), 1.0 (standard ML research), 3.0 (regulatory baseline), 10+ (weak / often theatrical). |
| delta_target | float | yes | — | The probability that the ε guarantee fails to hold. Standard rule: δ ≤ 1 / (n × poly-log-n) where n is the dataset size. For n = 100K, δ ≈ 1e-7. |
| n_records | int | yes | — | Number of records in the protected set. Used to compute the recommended δ and to size noise. |
| mechanism | "gaussian" \| "laplace" \| "dp-sgd" \| "exp" | yes | — | Gaussian for L2-sensitivity continuous queries and DP-SGD training; Laplace for L1-sensitivity counts; DP-SGD for ML training; Exponential for selection mechanisms. |
| composition_budget | "advanced" \| "rdp" \| "basic" | no | "rdp" | RDP (Rényi DP) accountant gives tightest bounds for ML; basic linear composition over-counts; advanced composition is in between. |
| accounting_library | "opacus" \| "tensorflow-privacy" \| "dp-accounting" \| "custom" | no | "opacus" | The implementation used for noise + accounting. Match to the framework. |
| target_attack_evaluation | "lira" \| "shadow-models" \| "none" | no | "lira" | After applying DP, empirically evaluate membership-inference resistance. LiRA (Carlini et al. 2022) is the current standard attack. |

## Workflow

Copy this checklist into the response and check off items as each step completes:

```
DP application progress:
- [ ] Step 1: Declare the threat model (membership-inference / attribute-disclosure / reconstruction / query-aggregation)
- [ ] Step 2: Justify ε and δ against the threat model and dataset size (NOT a default; tied to regulatory / risk requirement)
- [ ] Step 3: Pick the mechanism (Gaussian / Laplace / DP-SGD / Exponential) by sensitivity metric and workload
- [ ] Step 4: Compute the per-step (or per-query) noise scale that achieves the target (ε, δ) under the chosen accountant
- [ ] Step 5: For DP-SGD: set the L2 clipping bound C (typical: C = 1.0 after normalization); compute noise multiplier σ; set batch size, sampling rate, and epoch count
- [ ] Step 6: Run the training / query workload with the noise mechanism in place
- [ ] Step 7: Track composition: every query / step consumes budget; the accountant returns the cumulative (ε, δ); stop when budget is exhausted
- [ ] Step 8: Empirically evaluate residual attack risk (LiRA or shadow-model membership inference) — DP guarantees an upper bound; the empirical attack tells you the realized risk
- [ ] Step 9: Produce the DP statement (ε, δ, mechanism, accountant, n, composition method, empirical attack result, what the guarantee does and does NOT cover)
```

### Step 1: Declare the threat model

DP defends against **statistical inference about individuals from query outputs**. It does NOT defend against:

- Direct database compromise (use access control + encryption)
- Adversaries with query access to the raw data (DP protects the *release*, not the storage)
- Re-identification from auxiliary information in non-DP releases of the same population (the holistic-privacy problem; DP one release does not anonymize another)

The four common ML-relevant threat models:

| Threat model | What the adversary learns | Typical ε range |
|---|---|---|
| Membership inference | "Was record X in the training set?" | ε ≤ 2 (strong), ε ≤ 8 (weak) |
| Attribute disclosure | "What is the value of attribute Y for record X?" | ε ≤ 1 (strong), ε ≤ 4 (weak) |
| Reconstruction | Recover the actual training record (from model gradients / embeddings) | ε ≤ 0.5 (strong), needs DP-SGD with small ε |
| Query aggregation | Infer individual values from a sequence of allegedly-aggregate queries (census reconstruction attack class) | Per-query ε small enough that total ε after composition ≤ 1.0 |

### Step 2: Justify ε and δ

There is no universal "right ε." Anchor to a baseline:

- **U.S. Census Bureau 2020 release:** ε ≈ 19.6 (block-level), much smaller for higher aggregations — *contested* as too high for meaningful protection of small blocks
- **Apple iOS telemetry:** ε ≈ 4 per data category per day (local DP, weaker per-event guarantee, very different composition story)
- **HIPAA Safe Harbor de-identification equivalent:** community estimates ε ≤ 3 with appropriate δ for membership-inference resistance comparable to Safe Harbor
- **Strong academic research:** ε ≤ 1.0 with δ ≤ 1e-5 — the band most published DP-ML papers target

If the user proposes ε = 10 or higher, push back: under standard composition, ε = 10 implies a posterior odds ratio of e^10 ≈ 22,000 between the "record present" and "record absent" hypotheses — the guarantee is mathematically present but practically weak.

δ MUST satisfy δ ≤ 1 / (n × poly-log-n). Otherwise the catastrophic-failure probability is too high. For n = 100K, δ ≈ 1e-7. δ = 1e-3 with n = 100K is sometimes seen in papers; it is sloppy.

### Step 3: Pick the mechanism

| Workload | Sensitivity | Mechanism |
|---|---|---|
| Counts, histograms | L1 = 1 | Laplace |
| Means / continuous queries | L2 = max change in output per record | Gaussian |
| ML training (gradient descent) | L2 of per-example gradient | DP-SGD (Abadi et al. 2016) |
| Discrete selection (top-k, classification) | n/a | Exponential mechanism |

### Step 4: Per-step noise scale

For DP-SGD, given target (ε, δ), batch sampling rate q = batch_size / n, and training steps T, the noise multiplier σ that achieves the target under RDP accounting is computed by the accountant. See `reference/dp-sgd-noise-calculator.md` for the exact formulas and a recipe.

Rule of thumb: for ε = 1.0, δ = 1e-5, n = 100K, batch = 256, epochs = 30 → σ ≈ 1.0 to 1.2 (depends on sampling assumptions).

### Step 5: DP-SGD specifics

Three knobs must all be set:

1. **L2 clipping bound C** — per-example gradient is clipped to L2 ≤ C. Typical: C = 1.0 after gradient normalization; tune downward if loss diverges, upward if loss plateaus.
2. **Noise multiplier σ** — Gaussian noise N(0, σ²C²I) added to the SUM of clipped per-example gradients.
3. **Sampling rate q** — batch is drawn by Poisson sampling (each example included with probability q), not deterministic batches. RDP accountant assumes Poisson sampling; deterministic batches give a slightly worse bound.

Opacus handles all three; do not hand-roll DP-SGD.

### Step 6: Run the workload

Train / query as usual but with the mechanism in place. Validate that gradients are clipped (Opacus logs) and that noise is being added (per-step accountant readout).

### Step 7: Track composition

Every step / query consumes budget. The accountant returns the cumulative (ε, δ) and the budget exhausts. STOP training when the per-step accountant returns ε ≥ ε_target. Continuing past the budget invalidates the guarantee.

### Step 8: Empirically evaluate

DP is a *mathematical upper bound* on attack success. The empirically-achieved attack success is usually lower. Run LiRA (Likelihood Ratio Attack, Carlini et al. 2022) or shadow-model membership inference on the trained model and report the empirical AUC. If empirical attack AUC > 0.6 despite a strong DP claim, something is wrong (implementation bug, accountant misuse, leakage outside the DP boundary).

### Step 9: DP statement

See `reference/dp-statement-template.md` for the canonical wording. Includes ε, δ, mechanism, accountant, n, composition method, what the guarantee covers, and what it does NOT cover.

## Outputs

A markdown report:

1. **Threat-model declaration**
2. **(ε, δ) justification** — what regulatory or risk baseline this matches; why this dataset size supports this δ
3. **Mechanism choice and noise scale** — with the formula and the library call
4. **Per-step / per-query budget consumption table** — cumulative (ε, δ) over the training / query workload
5. **Empirical attack result** — LiRA or shadow-model AUC after training
6. **Canonical DP statement** — the one-paragraph claim the model card / paper / release will carry
7. **What the guarantee does NOT cover** — non-DP releases of the same population, side channels, the storage / access layer, the prompt-distribution leakage in fine-tuned LLMs

## Failure modes

Known pitfalls and how this skill catches them:

- **DP-as-label** — calling a dataset "DP" instead of stating which mechanism with which budget. Caught by: required Step 9 statement that mentions the mechanism, ε, δ, accountant, n, and composition method.
- **ε ≥ 10 marketing** — applying minimal noise and claiming "DP" for a budget that provides no meaningful guarantee. Caught by: Step 2 requires ε to be tied to the threat model AND the skill explicitly refuses ε ≥ 10 with δ ≥ 1e-3 as security theater unless the user can defend the ratio against the threat model.
- **δ too large** — δ = 1e-3 with n = 100K means a 1-in-1000 probability of a catastrophic privacy failure per query. Caught by: Step 2 requires δ ≤ 1 / (n × poly-log-n).
- **Composition blindness** — running 100 DP queries each with ε = 1 and claiming the release is (ε = 1)-DP. Composition makes the total much larger; under basic composition, total ε = 100. Caught by: Step 7 requires an explicit accountant; budgets are reported as cumulative.
- **Deterministic batches with RDP accountant** — RDP accountant assumes Poisson subsampling; deterministic batches give a slightly worse-than-stated guarantee. Caught by: Step 5 explicit Poisson-sampling requirement.
- **Leakage outside the DP boundary** — DP protects the training gradients, but hyperparameter tuning on the validation set without DP leaks. Documentation, model-architecture choice driven by private data, prompt selection, all leak. Caught by: Step 9 statement requires naming what the guarantee does NOT cover.
- **Wrong-tool selection** — applying DP for an access-control problem (the right answer is authentication, not noise). Caught by: When-NOT-to-use list + threat-model declaration in Step 1.

## References

- `reference/dp-sgd-noise-calculator.md` — closed-form / iterative recipe to derive σ from (ε, δ, q, T)
- `reference/dp-statement-template.md` — the canonical paragraph for the model card / paper / release
- `reference/epsilon-baseline-table.md` — published ε values in deployed systems with citations
- [Dwork & Roth 2014, *The Algorithmic Foundations of Differential Privacy*](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf) — definitive textbook
- [Abadi et al. 2016, *Deep Learning with Differential Privacy*](https://arxiv.org/abs/1607.00133) — DP-SGD reference
- [Mironov 2017, *Rényi Differential Privacy*](https://arxiv.org/abs/1702.07476) — RDP composition reference
- [Carlini et al. 2022, *Membership Inference Attacks From First Principles*](https://arxiv.org/abs/2112.03570) — LiRA empirical attack reference
- [Opacus documentation](https://opacus.ai/) — PyTorch DP-SGD library

## Examples

### Example 1: Clinical NLP fine-tune under HIPAA-equivalent guarantee (happy-path)

Input: "We're fine-tuning a clinical NLP model on 100K patient discharge summaries. Compliance wants 'differential privacy.' What ε do we use and how do we get there?"

Output: skill confirms the threat model (membership inference on the fine-tuned model from query-access adversary), justifies ε = 2.0 against the HIPAA Safe Harbor equivalence band, sets δ = 1e-7 (= 1 / (n log n)), prescribes DP-SGD with Opacus (PyTorch), L2 clipping bound C = 1.0, noise multiplier σ ≈ 1.1 computed by Opacus's accountant for q = 256/100000, target 30 epochs. Produces the per-step (ε, δ) consumption table showing cumulative ε reaches 2.0 at epoch 28 → recommends early stop at epoch 28. Recommends running LiRA against the final model before promotion. Outputs the DP statement: "The fine-tuning procedure satisfies (ε = 2.0, δ = 1e-7)-DP with respect to record-level adjacency, under RDP composition with Poisson subsampling rate q = 0.00256. Guarantee covers membership inference on the released model; does NOT cover hyperparameter selection (run on a separate DP budget) or non-DP release of any other artifact derived from this corpus."

### Example 2: Composing 50 analytics queries on small-population data (edge-case)

Input: "We want to release 50 weekly dashboard tiles, each is a different aggregate over the same patient cohort of 8,000 people. Each individual query has noise added with ε = 0.5. Are we DP?"

Output: skill flags the composition problem explicitly. Under basic composition, 50 queries each at ε = 0.5 give total ε = 25 — no meaningful guarantee. Under advanced composition, total ε ≈ 5–7 depending on δ. Recommends: (a) use RDP accountant on the full query workload to get the tightest possible bound; (b) move to a privacy-preserving query system that allocates a single ε budget across all queries (e.g., PrivBayes, OpenDP, Tumult Analytics) rather than per-query allocation; (c) consider whether the same population deserves a fresh budget per week or a single annual budget — the second is much more honest. Refuses to certify the current per-query-ε release as (ε = 0.5)-DP.

### Example 3: k-anonymity sufficient (anti-trigger)

Input: "We're publishing a one-time release of average annual income by 5-digit ZIP code in the U.S. Should we apply differential privacy?"

Output: skill checks whether DP is the right tool. For 5-digit ZIP averages on a one-time release where the cohort per ZIP is large (typically thousands of households), the threat surface is small: k-anonymity with k ≥ 5 households per cell + suppression of small cells is the canonical defense and is usually sufficient. Recommends NOT applying DP here unless (a) the ZIP cells are tiny (e.g., rural ZIPs with < 100 households), (b) there are multiple correlated releases that compose, or (c) the regulator specifically requires a formal DP guarantee. Names the conditions under which the recommendation flips: "if you plan a series of releases on the same population, the composition argument flips this into a DP-required setting; we'd then revisit." Hands off to the privacy-engineering team for the k-anonymity threshold decision.

## See also

- `security/verifying-training-data-erasure` — adjacent privacy skill, different mechanism (planned v7-batch-5)
- `ml-datasci/auditing-synthetic-data-leakage` — synthetic data as an alternative privacy mechanism
- `ml-datasci/auditing-synthetic-data-utility` — synthetic data utility evaluation
- `security/threat-modeling-llm-app` — broader threat-modeling discipline that informs Step 1
- `ml-datasci/auditing-sft-dataset` — PII detection in fine-tuning corpora; pairs well before applying DP

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored fresh during v7-batch-4 (adversarial-ML + RLHF + DP cluster) per RCS PRAGMATIC discipline
