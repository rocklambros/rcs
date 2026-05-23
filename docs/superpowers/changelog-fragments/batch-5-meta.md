### Batch 5: meta — 2026-05-23

Skills shipped:

- `claude-code-meta/authoring-skill` v0.1.0 — Layer-3 + Anthropic best-practices authoring discipline for new skills; gerund-form slug, third-person description, 11 H2 sections, eval-first ordering (Σ 18, status: shipped)
- `claude-code-meta/auditing-instruction-hierarchy` v0.1.0 — agent-instruction file hierarchy audit: 400-line size cap, cache-hygiene (no timestamps in the cached prefix), drift detection (Σ 18, status: shipped)
- `workflow/auditing-context-window-pressure` v0.1.0 — multi-turn session pressure audit: context %, cache-hit-rate, CLAUDE.md hierarchy size, tool-result bloat, system-reminder accumulation, /compact vs /clear triage (Σ 17, status: drafting — see Notes)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Full 3-model validation (Haiku / Sonnet / Opus) deferred to a future re-run via `tools.run_evals.py`.

Eval results (Sonnet, intent-matched scoring):

| Skill | 01-happy-path | 02-edge-case | 03-anti-trigger |
|---|---|---|---|
| authoring-skill | 3/3 ✓ | 3/3 ✓ | 3/3 ✓ |
| auditing-instruction-hierarchy | 3/3 ✓ | 3/3 ✓ | 3/3 ✓ |
| auditing-context-window-pressure | 2/3 ✗ | 3/3 ✓ | 3/3 ✓ |

Notes:

- **Slug rename deviation from plan.** The plan named two skills `writing-claude-code-skill` and `auditing-claude-md-hierarchy`. Both slugs contain the reserved word `claude` per `tools/lint_frontmatter.py`. Because the per-batch isolation contract forbids touching `tools/**` and `docs/*.md`, the slugs were renamed under user direction to `authoring-skill` and `auditing-instruction-hierarchy` respectively. Cross-references within Batch 5 (e.g., See-also links) updated to match. Future batches that reference these skills should use the renamed slugs.
- **`auditing-context-window-pressure` demoted to drafting.** 01-happy-path scored 2/3: Sonnet's triage plan in response to "my session is slow" led with `/compact` and CLAUDE.md trim, but did not surface the subagent-summary or file-offload triage steps that the SKILL.md teaches in Step 4 and Step 7. The skill body is correct; the gap is signal strength — the triage list needs to be more discoverable in the workflow body. Re-eval planned after a Step 7 body revision that elevates subagent-summary and file-offload as named, mandatory triage steps before `/compact`.
- **Workflow shipped-fragment intentionally absent.** Only one Batch 5 skill targets the `workflow/` track, and it ships as `drafting` rather than `shipped`. No row belongs in the workflow Shipped-skills table this batch, so no `skills/workflow/shipped-fragments/batch-5.md` file was written. The skill directory itself is in place under `skills/workflow/auditing-context-window-pressure/`; Batch 6 will not move it into the Shipped table.
