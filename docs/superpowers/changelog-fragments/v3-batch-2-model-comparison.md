### v3-batch-2: model comparison + cards — 2026-05-23

Skills shipped:
- `ml-datasci/enforcing-leakage-firewall` v0.1.0 — four-check leakage defense (LOFO sweep + hub-firewall + group-aware split + no-row-in-two-splits row-hash invariant) for supervised pipelines on multi-source / grouped data; refuses to trust a held-out metric until all four checks pass (Σ 14, status: shipped)
- `ml-datasci/comparing-models-fairly` v0.1.0 — paired-test library for head-to-head model comparison (McNemar / DeLong / paired-t / Wilcoxon signed-rank / Friedman + Nemenyi) with mandatory multiple-comparison correction for 3+ models and effect-size + bootstrap CI reporting; refuses unpaired tests on per-fold metrics (Σ 14, status: shipped)
- `ml-datasci/writing-model-cards` v0.1.0 — Mitchell-2019 model card + AIBOM addendum (intended use + out-of-scope use, subgroup-disaggregated metrics with CIs, data provenance, concrete harms paired with mitigations, dependencies + versions + hashes); refuses vague language and refuses to author for throwaway research artifacts (Σ 13, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 9 dispatches (3 scenarios × 3 skills); all scored 3/3 against intent. Full 3-model (Haiku / Sonnet / Opus) validation deferred to a future re-run.

Notes: Two skills required a description trim (over the 1024-char Anthropic spec cap on first draft); shortened in-line and re-linted clean. No eval failures or calibration corrections; all three skills retained `status: shipped`.
