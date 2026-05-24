### v6-batch-6: eval-driven dev + grad-school scaffolding — 2026-05-23

Skills shipped:
- `claude-code-meta/running-eval-driven-skill-development` v0.1.0 — walks the evals-first → body → dispatch-and-judge workflow for authoring a new Claude Code skill per Anthropic best-practices; refuses on trivial one-line wrappers (Σ 13, status: shipped)
- `workflow/scaffolding-grad-school-pset` v0.1.0 — scaffolds a graded statistics pset notebook (Jupyter / RMarkdown / Quarto) with the 6-section discipline baked in: header+seed+imports → data audit → assumption-checks (BEFORE tests) → tests → effect-sizes + 95% CIs → interpretation with direction sentence; refuses on programming-only psets and research notebooks (Σ 12, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 6 dispatches total (2 skills × 3 scenarios). All scenarios scored 3/3 against intent-matched rubrics. Full 3-model validation (Haiku + Sonnet + Opus) deferred to a future re-run.

Eval results:
- `running-eval-driven-skill-development` 01 happy-path: 3/3 · 02 edge-case (process rubrics for open-ended skills): 3/3 · 03 anti-trigger (one-line wrapper): 3/3
- `scaffolding-grad-school-pset` 01 happy-path (BP comparison + regression): 3/3 · 02 edge-case (programming-only algorithms pset): 3/3 · 03 anti-trigger (research notebook): 3/3

Notes: no deviations or calibration corrections. Both skills' anti-triggers held — scenario 03 of skill 1 correctly recommended a smoke test instead of evals; scenario 03 of skill 2 correctly handed off to `scaffolding-ml-research-notebook` (planned). The edge-case for skill 1 (process rubrics for open-ended skills) is a real gap this skill addresses — without it, agents would conclude eval-driven dev is inapplicable to creative / open-ended skills.
