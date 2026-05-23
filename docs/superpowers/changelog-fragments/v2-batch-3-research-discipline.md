### v2-batch-3: research-discipline — 2026-05-23

Skills shipped:

- `workflow/pre-registering-eval-study` v0.1.0 — locks hypothesis, falsification, stopping rule, and power justification BEFORE data observation (Σ 16, status: shipped)
- `workflow/writing-successor-primers` v0.1.0 — cold-pickup handoff doc with founding-principles, false-confidence warnings, glossary, and "what is NOT here" (Σ 15, status: shipped)
- `workflow/writing-release-notes-as-postmortem` v0.1.0 — six-field per-fix postmortem entries with severity sort and "regressions NOT yet fixed" section (Σ 15, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Each skill ran 3 scenarios (happy-path, edge-case, anti-trigger) through one general-purpose subagent dispatch per scenario; rubric items scored intent-matched, not by literal phrasing. Full 3-model validation (Haiku + Sonnet + Opus) deferred to a future re-run.

Eval results (Sonnet-only):

| Skill | Happy-path | Edge-case | Anti-trigger | Verdict |
|---|---|---|---|---|
| pre-registering-eval-study | 3/3 | 3/3 | 3/3 | PASS |
| writing-successor-primers | 3/3 | 3/3 | 3/3 | PASS |
| writing-release-notes-as-postmortem | 3/3 | 3/3 | 2/3 | PASS |

Notes: writing-release-notes-as-postmortem anti-trigger scored 2/3 — the response correctly declined postmortem structure for a v0.1.0 first release and handed off to feature-announcement notes, but did not explicitly note that postmortem-style notes become appropriate starting with the first patch release after v0.1.0. Above the ≥ 2/3 anti-trigger threshold; status stays shipped.
