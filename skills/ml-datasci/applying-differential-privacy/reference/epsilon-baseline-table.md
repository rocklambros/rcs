# Epsilon Baselines in Deployed Systems

Anchor ε choices against published baselines, NOT against a "default" number. Every system below is contested in some way; the table is a starting point for negotiation, not a settled answer.

| System | Reported ε | Notes |
|---|---|---|
| U.S. Census Bureau 2020 PL94-171 redistricting release | ε ≈ 19.61 (total) | Allocated across age × race × geography. The block-level allocation is the controversial part; aggregate-level allocations are tighter. Widely criticized as too high for small-block protection. |
| U.S. Census 2020 Demographic and Housing Characteristics (DHC) | ε ≈ 11.0 | Lower than PL94-171 for the same data. |
| Apple iOS local DP (per category, per day) | ε ≈ 1–8 | Local DP — each user adds noise on-device. Different composition story than central DP; per-event guarantee is weaker than per-user. |
| Google RAPPOR local DP | ε ≈ 4 per event | Same local-DP class as Apple. |
| Microsoft DP for telemetry (LinkedIn analytics) | ε ≈ 0.15 daily | Strong, narrow-window guarantee. |
| OpenDP-deployed academic systems | ε ≤ 1.0 with δ ≤ 1e-5 typical | Research target. |
| HIPAA Safe Harbor de-identification (no formal DP claim) | n/a | Community estimates ε ≤ 3 would provide comparable membership-inference resistance to Safe Harbor for typical n. NOT an official equivalence. |
| Strong academic ML papers (DP-SGD on MNIST / CIFAR) | ε = 0.5–3.0, δ = 1e-5 | Common publication target. |
| Most "we use DP" marketing claims | ε ≥ 10 or unstated | Effectively meaningless. Demand the full (ε, δ, mechanism, composition) statement before trusting. |

## How to pick

1. Identify the **regulatory floor** — is there a legal or industry mandate? (HIPAA, GDPR Article 89, state-level health-data laws.)
2. Identify the **threat model** — membership-inference vs attribute-disclosure vs reconstruction.
3. Pick the **strongest ε that is computationally / utility feasible** — the question is "how low can we go before utility drops below the acceptable floor?" not "what ε do other people use?"
4. **Compose the budget across the whole release lifecycle** — train + eval + dashboard + downstream queries. The ε for a single training run is only one chunk.

## Anti-patterns to refuse

- **"Let's just use ε = 5 because that's typical"** — typical ≠ justified
- **"We'll start with ε = 10 and tighten later"** — there is no "later" with DP; the data has been released
- **"ε is computed by the framework so we don't need to think about it"** — the framework computes ε given σ, q, T; the choice of σ, q, T was a privacy decision the framework cannot make for you
- **Citing only Apple / Google ε values** — those are local-DP per-event, not central-DP cumulative; the numbers do not compare directly to DP-SGD ε for a trained model

## Recommended starting band by use case

| Use case | Suggested (ε, δ) band |
|---|---|
| Production ML model on protected health data | ε ∈ [0.5, 2.0], δ ≈ 1 / (n log n) |
| Released aggregate analytics with composition over a year | total ε ∈ [1, 3], split across queries |
| One-shot research analysis on de-identified data | ε ∈ [1, 5] depending on what's at stake |
| Fine-tuning an LLM on a small private corpus | ε ∈ [0.5, 2.0]; LiRA empirical check mandatory because the theory is least understood here |
| Public-facing dashboard tile on small-population data | ε per tile ≤ 0.5, total ε ≤ 3 across all tiles in the release |
