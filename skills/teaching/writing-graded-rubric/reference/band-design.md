# Writing observable-evidence band descriptors

The single most important rule in this skill: every band descriptor names what a grader would OBSERVE in the work. Not what the work "is" in the abstract.

## The vague vs. observable distinction

| Vague descriptor (bad) | Observable descriptor (good) |
|---|---|
| Good methodology | Method choice justified per data characteristics; assumption checks performed |
| Excellent writing | Argument clearly stated; each claim supported by ≥ 1 cited source; transitions present between paragraphs |
| Strong analysis | Effect size + 95% CI reported per the standard; ≥ 1 sensitivity analysis on a key parameter |
| Adequate reproducibility | Code shared with pinned environment file; seed set; one re-run reproduces reported results |
| Thoughtful conclusion | Conclusion restates the question, names the answer, names ≥ 1 limitation of the answer |

**Diagnostic for vagueness:** if two graders could disagree on whether the descriptor applies to a specific piece of work, the descriptor is vague. Tighten until disagreement is rare.

## Templates that meet the observable bar

| Template | Example |
|---|---|
| "[Action] performed and acted on / performed but not acted on / not performed" | "Assumption checks performed and acted on / performed but not acted on / not performed" |
| "Justified per [property] / partially justified / unjustified" | "Method choice justified per data characteristics / partially justified / unjustified" |
| "[Element] reported / mentioned / absent" | "Effect size + 95% CI reported / mentioned without CI / absent" |
| "Stated explicitly / partially / not at all" | "Research question stated explicitly / partially / not at all" |
| "[Count] of [N] required elements present" | "3 of 3 required sections (data / methods / results) present" |
| "[Threshold]-level evidence / [lower-threshold] / no evidence" | "Pre-registered hypothesis / hypothesis stated post-hoc / no hypothesis" |
| "[Specific check] passed / partial / failed" | "Code runs end-to-end on fresh environment / runs with manual fixes / does not run" |

## Per-artifact descriptor patterns

### Essay / writing assignments

| Criterion | Novice | Developing | Proficient | Advanced |
|---|---|---|---|---|
| Thesis | No clear thesis | Thesis stated, vague | Thesis stated, defensible | Thesis defended + counter-argument addressed |
| Evidence | Claims unsupported | Some claims with evidence | All claims with ≥ 1 cited source | All claims + sources contextualized |
| Structure | No discernible organization | Sections present, weak transitions | Clear sections + transitions | Structure serves argument; non-trivial section ordering |
| Language | Frequent errors impede meaning | Errors present but meaning clear | Few errors; clear voice | Errors absent; voice intentional |

### Code submissions

| Criterion | Novice | Developing | Proficient | Advanced |
|---|---|---|---|---|
| Correctness | Does not produce required output | Produces output for happy path only | Produces output for happy path + ≥ 1 edge case | Handles all spec'd cases + documents unhandled |
| Code quality | No structure; one giant function | Functions present, no separation of concerns | Modular, named functions, single responsibility | Modular + tested + typed |
| Testing | No tests | ≥ 1 test of happy path | Tests for happy path + ≥ 1 edge case | Tests cover happy + edge + error paths; CI runs them |
| Reproducibility | No environment info | Environment listed, not pinned | Pinned env, seed set, re-runs reproduce | Pinned env + seed + lockfile + CI |

### Applied data analysis / research write-up

| Criterion | Novice | Developing | Proficient | Advanced |
|---|---|---|---|---|
| Problem framing | No research question | Question vague | Question specific + falsifiable | Pre-registered hypothesis + stated limitations |
| Methodology | Method unjustified | Justification partial | Method justified per data characteristics | Method + alternates considered + sensitivity analysis |
| Assumption checking | No checks | Checks reported, not acted on | Checks reported + acted on | Checks + diagnostics + robust alternative when failed |
| Effect size + uncertainty | Bare p-value | Effect size, no CI | Effect size + CI + direction | Effect size + CI + practical-significance discussion |
| Reproducibility | Code / data not shared | Shared, not pinned | Pinned + seed + reruns same | Pinned + lockfile + structured output |

### Oral defense / presentation

| Criterion | Novice | Developing | Proficient | Advanced |
|---|---|---|---|---|
| Clarity | Audience lost within first 2 minutes | Audience follows most of the time | Audience follows throughout | Audience follows + emerges with new questions to ask |
| Q&A | Defers / cannot answer most questions | Answers ≥ 50% of questions accurately | Answers most questions + cites uncertainty when appropriate | Answers all + reframes weak questions to be more useful |
| Visual aids | Slides illegible / overloaded | Slides legible, contain most content | Slides support the spoken content | Slides + spoken content together exceed either alone |

## Distinguishing adjacent bands

A common failure: novice and developing look the same, or proficient and advanced look the same. Each adjacent pair must differ on at least one observable element.

- Novice → Developing: the thing went from absent to present (even if poorly done)
- Developing → Proficient: the thing went from present-but-flawed to present-and-correct
- Proficient → Advanced: the thing went from present-and-correct to present-and-extended (with sensitivity analysis, counter-arguments, alternates, or other forms of going beyond)

If two adjacent bands have identical text with one different word ("good" → "great"), they are not actually distinguishable; collapse them or rewrite both.

## Anti-patterns

- **"Above expectations" / "meets expectations" / "below expectations"** — these are reactions, not evidence. What did the work do or not do?
- **Adjective inflation up the bands** ("good → very good → excellent → outstanding") — graders cannot apply this; tighten with evidence.
- **Multi-criterion compound descriptors** ("good methodology AND clear writing AND reproducible") — split into separate criteria.
- **Negative-only descriptors at novice** ("did not do X") — also state what they would have done; otherwise the band signals nothing about what they DID do.
- **Descriptors that require the grader to know the student's intent** ("the student tried but failed") — graders grade the artifact, not the intent.
