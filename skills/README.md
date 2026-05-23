# RCS Skills — Cross-Track Index

All RCS skills, organized first by audience track and then by ROI rank (Σ score from the v1 brainstorm).

## Shipped (v1.0.0-phase2-thru-6)

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

## Drafting

| Skill | Track | Σ | Reason |
|---|---|---|---|
| [`auditing-context-window-pressure`](workflow/auditing-context-window-pressure/) | workflow | 17 | Batch 5 Sonnet happy-path eval scored 2/3; Step 7 body revision pending |

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
