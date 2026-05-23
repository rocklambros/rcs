# RCS Skills — Cross-Track Index

All RCS skills, organized first by audience track and then by ROI rank (Σ score from the v1 brainstorm).

## Shipped (v2.0-phase1 + v3.0-phase1)

Sorted by Σ desc.

| Skill | Track | Σ |
|---|---|---|
| [`enforcing-seed-hygiene`](workflow/enforcing-seed-hygiene/) | workflow | 20 |
| [`validating-temporal-fields`](workflow/validating-temporal-fields/) | workflow | 19 |
| [`auditing-pinned-dependencies`](security/auditing-pinned-dependencies/) | security | 19 |
| [`reporting-effect-sizes`](ml-datasci/reporting-effect-sizes/) | ml-datasci | 19 |
| [`evaluating-binary-classifiers`](ml-datasci/evaluating-binary-classifiers/) | ml-datasci | 19 |
| [`auditing-mcp-server-pre-trust`](security/auditing-mcp-server-pre-trust/) | security | 18 |
| [`selecting-statistical-test`](ml-datasci/selecting-statistical-test/) | ml-datasci | 18 |
| [`checking-test-assumptions`](ml-datasci/checking-test-assumptions/) | ml-datasci | 18 |
| [`auditing-train-test-split`](ml-datasci/auditing-train-test-split/) | ml-datasci | 18 |
| [`deduplicating-records`](workflow/deduplicating-records/) | workflow | 18 |
| [`authoring-skill`](claude-code-meta/authoring-skill/) | claude-code-meta | 18 |
| [`auditing-instruction-hierarchy`](claude-code-meta/auditing-instruction-hierarchy/) | claude-code-meta | 18 |
| [`running-adversarial-premortem`](workflow/running-adversarial-premortem/) | workflow | 17 |
| [`pinning-reproducible-environments`](workflow/pinning-reproducible-environments/) | workflow | 17 |
| [`auditing-data-quality`](workflow/auditing-data-quality/) | workflow | 17 |
| [`building-baseline-models`](ml-datasci/building-baseline-models/) | ml-datasci | 17 |
| [`evaluating-regression-models`](ml-datasci/evaluating-regression-models/) | ml-datasci | 17 |
| [`auditing-context-window-pressure`](workflow/auditing-context-window-pressure/) | workflow | 17 |
| [`auditing-jupyter-execution-order`](workflow/auditing-jupyter-execution-order/) | workflow | 16 |
| [`auditing-source-provenance`](workflow/auditing-source-provenance/) | workflow | 16 |
| [`pre-registering-eval-study`](workflow/pre-registering-eval-study/) | workflow | 16 |
| [`auditing-prompt-token-budget`](ml-datasci/auditing-prompt-token-budget/) | ml-datasci | 16 |
| [`evaluating-multiclass-classifiers`](ml-datasci/evaluating-multiclass-classifiers/) | ml-datasci | 16 |
| [`tuning-classification-threshold`](ml-datasci/tuning-classification-threshold/) | ml-datasci | 16 |
| [`running-chollet-ratio-check`](ml-datasci/running-chollet-ratio-check/) | ml-datasci | 16 |
| [`interpreting-conflicting-tests`](ml-datasci/interpreting-conflicting-tests/) | ml-datasci | 16 |
| [`building-deterministic-data-pipelines`](workflow/building-deterministic-data-pipelines/) | workflow | 15 |
| [`writing-successor-primers`](workflow/writing-successor-primers/) | workflow | 15 |
| [`writing-release-notes-as-postmortem`](workflow/writing-release-notes-as-postmortem/) | workflow | 15 |
| [`generating-data-dictionary`](ml-datasci/generating-data-dictionary/) | ml-datasci | 15 |
| [`analyzing-regression-diagnostics`](ml-datasci/analyzing-regression-diagnostics/) | ml-datasci | 14 |
| [`enforcing-leakage-firewall`](ml-datasci/enforcing-leakage-firewall/) | ml-datasci | 14 |
| [`comparing-models-fairly`](ml-datasci/comparing-models-fairly/) | ml-datasci | 14 |
| [`evaluating-rag-retrieval`](ml-datasci/evaluating-rag-retrieval/) | ml-datasci | 14 |
| [`profiling-llm-cost`](ml-datasci/profiling-llm-cost/) | ml-datasci | 14 |
| [`recommending-model-tier`](ml-datasci/recommending-model-tier/) | ml-datasci | 14 |
| [`auditing-notebook-narrative`](workflow/auditing-notebook-narrative/) | workflow | 13 |
| [`validating-schema-evolution`](workflow/validating-schema-evolution/) | workflow | 13 |
| [`auditing-mathematical-claims`](workflow/auditing-mathematical-claims/) | workflow | 13 |
| [`running-power-analysis`](ml-datasci/running-power-analysis/) | ml-datasci | 13 |
| [`writing-model-cards`](ml-datasci/writing-model-cards/) | ml-datasci | 13 |
| [`selecting-embedding-model`](ml-datasci/selecting-embedding-model/) | ml-datasci | 13 |

## By track

- **[security/](security/)** — Security engineers, AI red-teamers, GRC, vuln triage, MCP pre-trust, pen-test discipline.
- **[ml-datasci/](ml-datasci/)** — Data scientists, ML engineers, stats students, applied ML.
- **[workflow/](workflow/)** — Cross-cutting hygiene and research discipline for both audiences.
- **[teaching/](teaching/)** — Pedagogy patterns, rubrics, pset walkthroughs (no v1 skills; structure pre-allocated).
- **[claude-code-meta/](claude-code-meta/)** — Skill / plugin / hook / MCP / rule authoring meta.

## Status legend

- ✅ **shipped** — body + 3 passing evals + Layer-3 H2 sections; auto-invocable
- 🔨 **drafting** — visible to readers but not yet eval-validated; not auto-invocable
- 📝 **planned** — listed only; no directory yet

See `docs/conventions.md` for full status semantics.
