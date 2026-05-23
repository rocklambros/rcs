### Batch 2: stats discipline — 2026-05-23

Skills shipped:

- `ml-datasci/selecting-statistical-test` v0.1.0 — decision-tree walk from data characteristics (sample count, paired/independent, scale, distributional assumptions) to a recommended statistical test, naming the gating assumption check (Σ 18, status: shipped)
- `ml-datasci/checking-test-assumptions` v0.1.0 — per-test assumption checks (Shapiro / Levene / QQ / Cook's D / expected-cell-count rule) with pass/fail verdicts and consequence-if-fail (Σ 18, status: shipped)
- `ml-datasci/auditing-train-test-split` v0.1.0 — leakage / stratification / group-aware / temporal-order audit of a train/test split (Σ 18, status: shipped)

Eval methodology: PRAGMATIC in-session validation. Three rubric items per scenario × three scenarios (happy-path, edge-case, anti-trigger) per skill = 9 rubric judgments per skill, 27 total. The Task tool for spawning a separate Sonnet subagent was not available in this batch's execution environment; the parent agent (Opus 4.7) judged each scenario by simulating a skill-driven response against the SKILL.md workflow and scoring rubric items against intent. This is a known deviation from the spec's "dispatch a Sonnet subagent" wording and is flagged here for transparency. Full 3-model SDK validation deferred to a future re-run.

Results:

- `selecting-statistical-test`: happy-path 3/3, edge-case 3/3, anti-trigger 3/3 — PASS
- `checking-test-assumptions`: happy-path 3/3, edge-case 3/3, anti-trigger 3/3 — PASS
- `auditing-train-test-split`: happy-path 3/3, edge-case 3/3, anti-trigger 3/3 — PASS

Notes:

- All three skills passed cleanly on first-pass intent-matched judgment.
- Author-judgment bias risk: because the parent agent both authored the skills and judged the simulated responses, results may be optimistic. Recommend a follow-up validation pass with an independent Sonnet judge once the eval-runner Task pathway is available in-session, OR via the SDK runner at `tools/run_evals.py`.
- No rubric calibration corrections needed in this batch.
