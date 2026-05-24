---
name: writing-graded-rubric
description: >
  Writes a criterion-referenced rubric for grading open-ended student work
  (essays, design docs, research write-ups, code submissions, project
  reports) using proficiency bands (novice / developing / proficient /
  advanced) per criterion, with observable-evidence descriptors so two
  independent graders land on the same band. Forces the author to commit
  to the criteria BEFORE seeing submissions to prevent drifting the
  rubric to match work in hand. Triggers when grading open-ended work
  with no single canonical answer, when an existing rubric produces
  inter-grader disagreement, when student appeals reveal ambiguous
  criteria, or when peer grading needs a structure non-experts can
  apply. Refuses on binary pass / fail tasks where bands are overkill,
  refuses to author a rubric after submissions are in hand, and refuses
  vague band descriptors ("good," "excellent") that do not name the
  observable evidence.
version: 0.1.0
status: shipped
track: teaching
audience:
  - instructor
  - ta
evidence:
  - DU-MSDSAI-4441-Final
last-updated: 2026-05-23
---

# Writing a Graded Rubric

## When to use

Trigger this skill when:

- An instructor / TA is grading open-ended student work (essay, design doc, research write-up, code submission, project report) where no single canonical answer exists
- An existing rubric is producing inter-grader disagreement (two graders give different scores to the same work) — symptom of vague band descriptors
- A student appeals a grade and the rubric reveals its criteria were ambiguous
- Peer grading needs a structure that non-experts can apply consistently — the rubric is the only thing keeping peer scores meaningful
- A new course is being designed and assessment artifacts have not been written yet
- A graded artifact (final project, capstone) needs documented criteria for accreditation / audit / external review

## When NOT to use

Skip this skill and hand off when:

- The task is a binary correctness check (right / wrong answer) — proficiency bands are overkill; use a key
- A canonical reference solution exists and the grading is "match the reference" — use `teaching/diffing-instructor-vs-student-solution` instead
- The artifact is a problem-set walkthrough or pure explanation (`teaching/writing-pset-walkthrough`, `teaching/explaining-statistical-concept`)
- The work has already been submitted and the rubric does not exist yet — DO NOT author a rubric to fit observed work (criterion-referenced means the rubric is committed before the work is seen)
- The user wants a holistic single-number score for one piece of work — that is a judgment, not a rubric; use direct judgment instead
- The criteria genuinely cannot be made observable (e.g., "the writing is beautiful") — flag as a rubric-resistant criterion, recommend it be removed or operationalized

## Quick start

User: *"I'm designing a grad-level applied stats course and need a rubric for the final project — a 10-page applied analysis on a dataset of the student's choosing. Help me write it before students submit so I am not tempted to drift the criteria."*

Response: produce a criterion-referenced rubric with 4-6 criteria, each with four proficiency bands (novice / developing / proficient / advanced), and each band describing observable evidence that two independent graders would identify the same way. Refuse to use vague descriptors ("good methodology"). Commit the rubric to the syllabus BEFORE the submission window opens.

```markdown
## Final project rubric

| Criterion | Novice (1) | Developing (2) | Proficient (3) | Advanced (4) |
|---|---|---|---|---|
| Problem framing | No research question stated; analysis goal unclear | Question stated but ambiguous; success criteria implicit | Specific question; success criteria stated; scope appropriate to dataset | Question explicit, falsifiable, with pre-registered hypotheses and stated limitations |
| Methodology choice | Test / method chosen without justification; multiple inappropriate choices | Justification present but partial; some methods miscalibrated to data | Method choice justified per data characteristics; assumption checks performed | Method choice justified, alternates considered, sensitivity analysis on a key choice |
| Assumption checking | No assumption checks; or checks performed but ignored | Some checks performed, results reported but not acted on | All assumptions for chosen tests checked, results reported, action taken on failures | Assumption checks + diagnostics, robust alternatives proposed where assumptions fail |
| Effect size + uncertainty | Only p-values reported, no effect size | Effect size mentioned but no CI; or CI without interpretation | Effect size + 95% CI + direction reported per the standard | Effect size + CI + practical-significance discussion + comparison to prior literature |
| Reproducibility | No code / data shared; cannot rerun | Code shared, not pinned, breaks on re-run | Code + pinned environment + seed; reruns produce same results | Code + pinned env + seed + CI / lockfile + structured-output for downstream use |
```

See `reference/band-design.md` for the rules on writing observable-evidence band descriptors, `reference/criterion-selection.md` for the heuristics to pick 4-6 criteria (not 12, not 2), and `reference/inter-grader-calibration.md` for the pre-grading norming session that drops the inter-grader disagreement rate.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `assessment_artifact` | enum | yes | — | `essay` \| `design-doc` \| `research-writeup` \| `code-submission` \| `project-report` \| `oral-defense` \| `peer-review`. Drives which criterion templates apply. |
| `learning_objectives` | string list | yes | — | The course / assignment learning objectives the rubric must measure. Drives criterion selection: each criterion should map to at least one objective. |
| `criterion_count` | integer | no | 4-6 | Number of criteria. Default range 4-6. Above 8: rubric is too granular; graders cannot hold the criteria in working memory. Below 3: rubric is too coarse; reduces to a holistic score. |
| `band_count` | integer | no | 4 | Number of proficiency bands per criterion. Default 4 (novice / developing / proficient / advanced). 5 (adds "exemplary" above advanced) for capstones. 3 (novice / proficient / advanced) for low-stakes assignments. |
| `grader_pool` | enum | no | `expert` | `expert` (instructor / TA) \| `peer` (students grading other students) \| `mixed`. Peer grading requires tighter band descriptors and a mandatory norming session. |
| `pre_registration` | bool | no | `true` | If `true`, the rubric is committed to the syllabus / public location BEFORE submissions open; the skill refuses to retroactively author a rubric on observed work. |
| `weight_per_criterion` | dict | no | uniform | Optional per-criterion weights (e.g., methodology weighted 30%, reproducibility 10%). Default uniform. |

## Workflow

```
Rubric authoring progress:
- [ ] 0. Confirm pre-registration scope: rubric committed BEFORE submissions in hand; if not, refuse
- [ ] 1. Enumerate learning objectives the rubric must measure
- [ ] 2. Pick 4-6 criteria; each criterion maps to ≥ 1 objective; no objective is uncovered
- [ ] 3. Per criterion, write 4 (or 3 or 5) band descriptors with observable evidence
- [ ] 4. Inter-grader test: two reviewers read a sample work; do they pick the same band per criterion? If not, tighten descriptors
- [ ] 5. Edge-case pass: write 3 hypothetical works that exercise boundary cases; map each to a band; verify the rubric does the work consistently
- [ ] 6. Weights: assign per-criterion weights; document why each weight reflects its importance to the learning objectives
- [ ] 7. Commit: lock the rubric in the syllabus / assignment page; release alongside the assignment, NOT after submission
- [ ] 8. Norming session (if grader_pool includes peers or new TAs): all graders apply the rubric to a sample work together before grading begins
```

### Step 2: Criterion selection — 4-6, not more

Too few criteria → the rubric reduces to a holistic score; "did I like this work overall" leaks in.

Too many criteria → graders cannot hold the criteria in working memory; they grade by gestalt and fill in the rubric afterward (rubric becomes documentation, not the actual grading mechanism).

The sweet spot is 4-6 criteria that ALL graders can keep active while reading the work. Each criterion must map to at least one learning objective; no learning objective should be uncovered. If 7+ criteria are required to cover the objectives, the rubric is being asked to do too much — split the assignment into two parts, or collapse criteria that measure the same underlying skill.

### Step 3: Observable evidence per band

The single most important rule: every band descriptor names what a grader would OBSERVE in the work. Not what the work "is" in the abstract.

- ❌ "Good methodology choice" (what does "good" mean? two graders disagree.)
- ✅ "Method choice justified per data characteristics; assumption checks performed" (a grader can scan the work and check this.)

Common band descriptor templates that meet the observable-evidence bar:

- "Stated explicitly / partially / not at all"
- "Performed and acted on / performed but not acted on / not performed"
- "Justified per [data property] / partially justified / unjustified"
- "Effect size + CI reported / effect size only / neither"
- "Reproducible (code + pinned env + seed) / partial / not reproducible"

### Step 4: Inter-grader test — the rubric's correctness check

Before deploying, two graders independently apply the rubric to one sample work. Compare band assignments per criterion.

- All match → rubric is tight; deploy.
- Off by 1 band on 1-2 criteria → tighten those descriptors; re-test.
- Off by 2+ bands or off on most criteria → rubric is broken; rewrite. Likely cause: vague descriptors.

Skipping this test deploys a rubric that produces inter-grader disagreement, which produces appeals, which produces re-grades — far more cost than a 30-minute pre-deployment calibration.

### Step 5: Edge-case pass

Write three hypothetical submissions that exercise rubric boundary cases:

1. A submission strong on some criteria, weak on others (does the rubric produce a defensible mixed score?)
2. A submission that does something unusual but legitimate (does the rubric have a band for it, or does the work fall through the cracks?)
3. A submission that meets the letter of a band descriptor without the spirit (does the descriptor need tightening?)

Map each to bands per criterion. If any case lands ambiguously, fix the rubric before deployment.

### Step 7: Pre-registration discipline

The rubric is committed (syllabus, assignment page, public location) BEFORE the submission window opens. The skill refuses to author a rubric after submissions are in hand because:

- Authoring a rubric to fit observed work defeats the criterion-referenced purpose
- The rubric becomes a post-hoc justification, not a grading instrument
- Students who submitted before the rubric existed had no notice of the criteria
- The rubric drift makes grading unfair to early submitters who could have done better had they known the criteria

If submissions are already in and the rubric does not exist, the cleanest path is to grade holistically (without a rubric, with an explicit note) and use this skill to author the rubric for NEXT term.

## Outputs

A criterion-referenced rubric containing:

1. **Criterion list** — 4-6 named criteria, each mapped to ≥ 1 learning objective
2. **Per-criterion band table** — 4 (or 3 or 5) bands with observable-evidence descriptors
3. **Per-criterion weight** — explicit weights summing to 100%, with rationale per weight
4. **Norming notes** — for grader_pool that includes peers or new TAs, a one-paragraph norming protocol
5. **Pre-registration commitment** — a statement that the rubric was committed BEFORE the submission window opened (with date)

Length: typically 1-2 pages for a 4-criterion / 4-band rubric. Capstone rubrics may extend to 3-4 pages.

## Failure modes

Known anti-patterns and how this skill catches them:

- **Vague band descriptors ("good," "excellent")** — caught by step 3 observable-evidence rule; descriptors must name what a grader would observe
- **Too many criteria (graders cannot hold them in working memory)** — caught by step 2 4-6 criteria target
- **Too few criteria (reduces to holistic score)** — caught by step 2 lower bound
- **Authoring rubric AFTER submissions are in hand** — caught by step 0 pre-registration scope refusal
- **No inter-grader calibration** — caught by step 4 mandatory inter-grader test before deployment
- **Edge cases not considered** — caught by step 5 three-hypothetical pass
- **Criteria not mapped to learning objectives** — caught by step 2; orphan criteria signal scope creep
- **Uniform weights when criteria differ in importance** — caught by step 6; weights are explicit, with rationale, not default
- **Peer grading without a norming session** — caught by step 8 mandatory for non-expert grader pools
- **"Rubric-resistant" criteria (e.g., "writing is beautiful") forced into bands** — caught informally; flagged for removal or operationalization

## References

- `reference/band-design.md` — rules for writing observable-evidence band descriptors with worked examples per artifact type
- `reference/criterion-selection.md` — heuristics for picking 4-6 criteria mapped to learning objectives
- `reference/inter-grader-calibration.md` — pre-grading norming protocol that drops inter-grader disagreement rate
- [Sadler, *Formative assessment: revisiting the territory*, Assessment in Education 1998](https://www.tandfonline.com/doi/abs/10.1080/0969595980050104) — academic source on criterion-referenced assessment
- [Andrade, *Teaching with Rubrics*, College Teaching 2005](https://www.tandfonline.com/doi/abs/10.3200/CTCH.53.1.27-31) — practitioner guide on rubric design

## Examples

### Example 1: Capstone applied-stats project rubric (happy-path)

Input: *"Final project for grad applied stats: 10-page applied analysis on a dataset of the student's choosing. Help me write the rubric BEFORE I see any submissions. Learning objectives: (a) frame a research question, (b) choose appropriate statistical methods, (c) check assumptions, (d) report effect sizes with uncertainty, (e) document reproducibly."*

Output: skill produces a 5-criterion rubric (problem framing / methodology / assumption checking / effect-size-reporting / reproducibility) with 4 bands per criterion. Each band descriptor names observable evidence (e.g., "assumption checks performed and acted on" rather than "good assumption checking"). Each criterion maps to one of the named learning objectives. Weights: methodology 25% + assumption-checking 20% + effect-size-reporting 20% + reproducibility 20% + problem-framing 15%, with one-sentence rationale per weight. Notes the inter-grader test step: instructor + one TA should apply the rubric to one sample work before any real grading begins. Commits the rubric to the syllabus dated before the submission window opens.

### Example 2: Inter-grader disagreement on existing rubric (edge-case)

Input: *"Our existing essay rubric has 8 criteria with bands like 'good,' 'excellent,' 'satisfactory.' Two TAs grade the same essay and consistently disagree by 1-2 bands per criterion. Help me fix it."*

Output: skill diagnoses two failures: (a) 8 criteria is above the 4-6 target — graders cannot hold them in working memory; (b) "good / excellent / satisfactory" are not observable-evidence descriptors. Recommends collapsing the 8 criteria into 4-5 that map to the learning objectives without overlap. Rewrites each band descriptor to name observable evidence specific to the artifact (essay) — e.g., for "argument quality": novice = no thesis / thesis unclear; developing = thesis stated but not defended; proficient = thesis stated + ≥ 2 supporting points with evidence; advanced = thesis defended + counter-argument addressed. Proposes the inter-grader test on the next batch of essays: if disagreement persists after the rewrite, the remaining gap is in grader interpretation, not the rubric (norming session needed).

### Example 3: Rubric authoring AFTER submissions (anti-trigger)

Input: *"My students submitted their final projects last week. I did not write a rubric ahead of time. Help me write one now so I can grade consistently."*

Output: skill refuses to author the rubric and explains why: criterion-referenced means the rubric is committed BEFORE the submissions are seen; authoring it after defeats the purpose (the rubric drifts to fit observed work, becomes post-hoc justification, and is unfair to students who submitted without knowing the criteria). Recommends two paths: (a) grade this batch holistically with an explicit note in the syllabus that the rubric was not pre-registered for this assessment, OR (b) commit to a pre-registered rubric for next term and use a different grading approach (e.g., comparative judgment by paired comparison) for this batch. Offers to help with the next-term rubric.

## See also

- `teaching/diffing-instructor-vs-student-solution` — when a canonical reference solution exists and "matching the reference" is the grading mode
- `teaching/writing-pset-walkthrough` — for authoring the reference solution that a closed-form pset rubric would grade against
- `teaching/explaining-statistical-concept` — when the rubric criterion is the student's grasp of a concept and the explanation pattern is needed
- `teaching/writing-onboarding-guide` — multi-audience format; rubrics here are single-audience (grader)
- `ml-datasci/reporting-effect-sizes` — the underlying standard often invoked in the "effect-size reporting" rubric criterion for stats work

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v6-batch-3, skill 2) via PRAGMATIC discipline
