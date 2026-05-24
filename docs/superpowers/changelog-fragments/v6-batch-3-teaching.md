### v6-batch-3: Teaching / pedagogy — 2026-05-23

Establishes the `teaching/` track (previously zero shipped skills in v1-v5) with 5 skills authored via PRAGMATIC discipline.

Skills shipped:

- `teaching/writing-onboarding-guide` v0.1.0 — multi-audience onboarding-doc authoring (per-audience sections, depth ceilings, shared glossary) (Σ 12, status: shipped)
- `teaching/writing-pset-walkthrough` v0.1.0 — four-part walkthrough template (What-asking · Why-works · Result · Gotcha) with gotcha-catalog discipline (Σ 11, status: shipped)
- `teaching/diffing-instructor-vs-student-solution` v0.1.0 — four-category diff (right-answer-wrong-reasoning / wrong-answer-one-misstep / legitimate-alternate-path / uncorrelated-error) with cascade recognition (Σ 11, status: shipped)
- `teaching/explaining-statistical-concept` v0.1.0 — Socratic 5-part explanation structure (probe → targeted-explanation-naming-misconception → concrete → application-check → bridge) (Σ 9, status: shipped)
- `teaching/writing-graded-rubric` v0.1.0 — criterion-referenced rubric authoring (4-6 criteria with observable-evidence proficiency bands; pre-registration enforced) (Σ 7, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline (15 Sonnet dispatches across 5 skills × 3 scenarios). Full 3-model validation (Haiku + Sonnet + Opus) deferred to a future re-run.

Eval results:

- `writing-onboarding-guide`: 3/3 happy + 3/3 edge + 3/3 anti
- `writing-pset-walkthrough`: 3/3 happy + 3/3 edge + 3/3 anti
- `diffing-instructor-vs-student-solution`: 3/3 happy + 3/3 edge + 3/3 anti
- `explaining-statistical-concept`: 3/3 happy + 3/3 edge + 2/3 anti (passed at the ≥ 2/3 anti-trigger threshold; one rubric item judged as marginal because the subagent's refusal was terse and did not fully elaborate why audience-tier mismatch wastes the explanation)
- `writing-graded-rubric`: 3/3 happy + 3/3 edge + 3/3 anti

All 5 skills pass PRAGMATIC Sonnet thresholds (happy 3/3, edge 3/3, anti ≥ 2/3) and retain `status: shipped`.

Notes:

- This batch establishes the `teaching/` track, which had zero shipped skills through v1-v5. The 5 skills span the four major teaching artifact families: pedagogy (`explaining-statistical-concept`), assessment authoring (`writing-graded-rubric`), worked-solution authoring (`writing-pset-walkthrough`), formative-feedback diffing (`diffing-instructor-vs-student-solution`), and multi-audience documentation (`writing-onboarding-guide`).
- Three skills (`writing-pset-walkthrough`, `diffing-instructor-vs-student-solution`, `explaining-statistical-concept`) explicitly cross-reference `ml-datasci/` siblings (`selecting-statistical-test`, `checking-test-assumptions`, `reporting-effect-sizes`) so the teaching skills compose with the underlying stats discipline rather than duplicating it.
- The `writing-onboarding-guide` skill is the only one in this batch with broad cross-track applicability (engineering / science / executive / security / auditor onboarding) and is the highest-Σ skill in the batch.
- Per-batch isolation: authored in worktree `../RCS-batch-3` on branch `feature/v6.0-batch-3-teaching`. No edits to root README, `skills/README.md`, `CHANGELOG.md`, or any track READMEs — deferred to Batch 6 (integration).
