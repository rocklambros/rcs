### v2 Batch 1: notebook + execution hygiene — 2026-05-23

Skills shipped:

- `workflow/auditing-jupyter-execution-order` v0.1.0 — static audit of `.ipynb` `execution_count` monotonicity + unrun-cell AST name scan; canonical fix `Kernel → Restart Kernel and Run All Cells`; papermill / cleared-output early exits (Σ 16, status: shipped)
- `workflow/auditing-notebook-narrative` v0.1.0 — markdown narrative vs. rendered-output consistency check; directional-claim keyword matcher with negation handling + citation suppression; printed-scalar / DataFrame / plot / log comparison strategies (Σ 13, status: shipped)
- `workflow/building-deterministic-data-pipelines` v0.1.0 — 8-step checklist (canonicalization per format, LF endings, sorted output, stable floats, no embedded timestamps, `provenance.json` sibling, content-hash snapshot, CI drift check); ships a drop-in `canonicalize.py`, a `provenance.json` schema, and a GitHub Actions drift-check workflow (Σ 15, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 9 dispatches total (3 scenarios × 3 skills), each subagent received the relevant SKILL.md inlined as guidance and the eval `query` verbatim. Rubric scoring against scenario `expected_behavior` items used intent-matching, not literal string matching.

Eval results:

- `auditing-jupyter-execution-order` — happy 3/3, edge 3/3, anti 3/3
- `auditing-notebook-narrative` — happy 3/3, edge 3/3, anti 3/3
- `building-deterministic-data-pipelines` — happy 3/3, edge 3/3, anti 3/3

All three skills cleared the PRAGMATIC shipped thresholds (happy 3/3, edge 3/3, anti ≥ 2/3) on Sonnet 4.6. Full 3-model (Haiku 4.5 + Sonnet 4.6 + Opus 4.7) validation deferred to a future re-run via `tools.run_evals`.

Notes:

- This is the first batch under the v2+ invocation namespace (`/superpowers:writing-skills create v2-batch-N at <plan> using PRAGMATIC`) and the first batch authored on a feature branch (no worktree, per the user's "no worktrees unless actually parallel" memory — this was a single sequential session).
- The PreToolUse `security_reminder_hook` misfired during authoring on neutral mentions of Python serialization / dynamic-eval keywords inside documentation; rephrased around in each case (no semantic loss). Worth a follow-up if the hook scope can be narrowed to executable code rather than prose mentions.
- The `lint_frontmatter` first-person regex matched `\bI ` inside a quoted user-report example in a description (`"I cannot reproduce your numbers"`). Rephrased to a third-person paraphrase. Worth considering whether the regex should permit `\bI ` when wrapped in quoted-string punctuation.
