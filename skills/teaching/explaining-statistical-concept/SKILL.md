---
name: explaining-statistical-concept
description: >
  Explains one statistical concept (p-value, confidence interval, central
  limit theorem, hypothesis test, regression coefficient, Bayes' theorem,
  power, effect size, etc.) to one explicit audience tier (high-school,
  undergrad-intro, undergrad-advanced, grad, practitioner) using a
  Socratic structure — open question → probe of the student's current
  mental model → targeted explanation → check-for-understanding question
  → variation if the check fails. Triggers when a learner asks "what is
  X" or "explain X to me," when a TA prepares office-hour material, when
  an instructor needs a tier-appropriate restatement of a textbook
  definition that students are bouncing off, or when a practitioner wants
  a quick refresher framed for their level. Refuses to engage when the
  audience tier is unspecified and ambiguous (pick the wrong tier and the
  explanation lands in the gap between tiers), and refuses to lecture
  past the check-for-understanding step without confirming the student
  followed the previous step.
version: 0.1.0
status: shipped
track: teaching
audience:
  - instructor
  - ta
  - stats-student
  - skill-author
evidence:
  - DU-MSDSAI-4441-Final
  - DU-MSDSAI-4441-Probability
last-updated: 2026-05-23
---

# Explaining a Statistical Concept

## When to use

Trigger this skill when:

- A learner asks *"what is a p-value?"*, *"what does a 95% confidence interval mean?"*, *"explain the central limit theorem,"* or any open-ended *"what is X / explain X"* on a stats / probability concept
- A TA is preparing office-hour material and wants a tier-appropriate explanation that students who are bouncing off the textbook will follow
- An instructor needs an alternate restatement of a concept that the textbook is not landing for a particular cohort
- A practitioner wants a quick refresher framed at the practitioner tier (not patronizing, not over-explained)
- A student says *"I read the chapter but I do not get it,"* signaling that the textbook tier does not match their current vocabulary
- A peer review of a manuscript surfaces a need to re-explain a method in the introduction for a more general audience

## When NOT to use

Skip this skill and hand off when:

- The user has a specific problem in hand and wants worked steps (`teaching/writing-pset-walkthrough`)
- The user has a student attempt to grade or diff (`teaching/diffing-instructor-vs-student-solution`)
- The user wants an assessment rubric (`teaching/writing-graded-rubric`)
- The user wants a multi-audience launch document (`teaching/writing-onboarding-guide`)
- The concept is genuinely a prerequisite for the audience tier (a grad student should not need an explanation of "mean") — explanation here would be patronizing; recommend a brief reference instead
- The user wants a research-paper-grade derivation with proofs — use a textbook reference or formal derivation, not the Socratic explanation format
- The audience tier is genuinely ambiguous and the user cannot or will not specify one — picking the wrong tier wastes the explanation

## Quick start

User: *"Explain the p-value to a junior analyst on my team. They just finished an intro stats course but never use it day to day."*

Response: identify the tier (practitioner, but with shallow recent exposure → treat as undergrad-intro for vocabulary), open with a probe of the analyst's current mental model, give the targeted explanation with one concrete example, then ask a check-for-understanding question. Do NOT recite the textbook definition straight.

```markdown
**Probe:** Before I explain, what's your current intuition for what a p-value tells you?
(Common intuitions: "the probability the null is true" — wrong but extremely common, and the explanation must address it head-on.)

**Targeted explanation:** A p-value is the probability of seeing your data — or anything more extreme — IF the null hypothesis is true. Not the probability the null is true. The "if" matters. It's a tail-area under an assumed-null world.

**Concrete:** You flip a coin 10 times and get 9 heads. If the coin were fair (null: p = 0.5), the chance of seeing 9 or more heads is about 1%. That 1% is the p-value. It does NOT say "there's a 99% chance the coin is unfair" — it says "9-or-more is unusual under fair."

**Check:** If you got 9 heads and the p-value is 0.01, can you conclude the coin is unfair with 99% certainty? (Correct answer: no. The 1% is conditional on a fair coin; it is not P(coin unfair | data).)
```

See `reference/socratic-structure.md` for the five-part probe-explain-check pattern, `reference/concept-catalog.md` for the canonical concepts with tier-by-tier explanations (p-value, CI, CLT, hypothesis test, regression coefficient, Bayes, power, effect size), and `reference/common-misconceptions.md` for the concept-by-concept list of student intuitions to address head-on.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `concept` | string | yes | — | The concept to explain. Should be one named statistical concept, not a chapter (e.g., `p-value`, not `inference`). |
| `audience_tier` | enum | yes | — | `high-school` \| `undergrad-intro` \| `undergrad-advanced` \| `grad` \| `practitioner`. Drives vocabulary, depth ceiling, and the type of example. Required — the skill refuses on ambiguity. |
| `prerequisite_assumed` | string list | no | tier-default | Concepts the student is assumed to already own. If unspecified, use the tier defaults (see `reference/socratic-structure.md`). |
| `learner_context` | string | no | none | Optional context about the specific learner / cohort ("they have data-engineering background, no formal stats" → adjust the example domain accordingly). |
| `addressed_misconception` | string | no | tier-default | If known, the specific student intuition the explanation must address head-on. If absent, the skill uses the canonical misconception from `reference/common-misconceptions.md`. |
| `example_domain` | enum | no | `general` | `clinical` \| `business` \| `engineering` \| `social-science` \| `coin-flips` \| `general`. The concrete example uses this domain so it lands with the learner. |

## Workflow

```
Explanation authoring progress:
- [ ] 0. Confirm audience tier; if ambiguous, refuse and ask
- [ ] 1. Identify the canonical misconception for this concept at this tier; the explanation must address it head-on
- [ ] 2. Probe: ask one open question about the learner's current mental model
- [ ] 3. Targeted explanation: state the concept correctly, naming the misconception being corrected
- [ ] 4. Concrete: one example in the requested domain (no abstract symbols only)
- [ ] 5. Check-for-understanding: one question whose right answer requires the learner to apply the explanation (not just repeat it)
- [ ] 6. Variation: if the learner fails the check, give one alternate framing; do NOT just repeat the same explanation louder
- [ ] 7. Bridge: one sentence connecting this concept to the next adjacent concept the learner will encounter
```

### Step 1: Identify the canonical misconception

Most stats concepts have one or two student intuitions that the textbook definition does not address head-on. The explanation must NAME the misconception and correct it explicitly. Examples:

- **p-value:** "the probability the null is true" → address head-on; restate as conditional probability under the null world
- **95% CI:** "95% probability the true value is in this interval" (Bayesian framing applied to a frequentist tool) → address; restate as "95% of intervals constructed this way contain the true value"
- **CLT:** "data becomes Normal as n grows" → address; restate as "the sampling distribution of the MEAN becomes Normal as n grows; the data itself does not change shape"
- **Regression coefficient:** "X causes Y by this amount" → address; restate as "associated change in Y per unit change in X, holding other predictors fixed"
- **Statistical significance:** "real / meaningful" → address; restate as "unlikely under the null at the chosen α"
- **Power:** "the test is reliable" → address; restate as "probability of detecting a true effect of a specified size"

Without naming the misconception, the explanation lands ON TOP OF the misconception, and the learner walks away unchanged.

### Step 2: The probe is one open question

Not a quiz. Not a multi-part question. ONE open question that surfaces the learner's current mental model. Examples:

- *"What is your current intuition for what a p-value tells you?"*
- *"If I said a 95% confidence interval is [3, 7], what would you take that to mean?"*
- *"Before we get into the math, what do you think the central limit theorem is claiming?"*

The probe matters because the explanation is calibrated against the answer. If the learner says "the probability the null is true," the explanation leads with that misconception. If they already have the right intuition, the explanation can skip the correction and go straight to the formalization.

### Step 3: Targeted explanation — name the misconception inside the explanation

Do not say "the textbook definition is..." Say "you probably learned X, and here is the part that gets lost: ..." The explanation acknowledges the learner's starting point and pivots from it. The pivot is where the learning happens.

### Step 4: Concrete is mandatory

Abstract symbols only never lands. Every explanation must include at least one concrete example using small numbers in a domain the learner cares about (clinical for med students, A/B test for product analysts, coin flips for fundamentals, etc.). The example is half the explanation.

### Step 5: Check-for-understanding must require application

A check that only requires repeating the explanation is not a check. The right check requires the learner to APPLY the concept to a small variation. Examples:

- After p-value: *"If you got 9 heads in 10 flips and p = 0.01, can you conclude the coin is unfair with 99% certainty?"* (Answer: no — common misconception inverted.)
- After CI: *"If your 95% CI is [3, 7] and someone else runs the same study, will their CI also contain the true value 95% of the time?"* (Answer: 95% of intervals from this procedure will contain it, not that any one specific interval contains it with 95% probability.)
- After CLT: *"If your data is exponentially distributed and you take 1000 samples of size n = 50 and compute the mean each time, will the distribution of those 1000 means be Normal?"* (Answer: yes, approximately — CLT applies to the sampling distribution.)

### Step 6: Variation, not repetition

If the learner fails the check-for-understanding, do NOT repeat the same explanation louder or longer. Give an ALTERNATE framing that approaches the concept from a different angle. Examples of alternates:

- **p-value:** if conditional-probability framing failed, try the "anti-fraud detector" framing (a p-value is the prosecutor's evidence that the null cannot easily explain the data; the JURY decides whether to reject)
- **CI:** if interval-around-estimate framing failed, try the "long-run frequency of confidence procedures" framing
- **CLT:** if sampling-distribution framing failed, try the convolution / averaging-smooths-things framing

If two alternate framings both fail, the prerequisite is probably missing; recommend the learner step back to the prerequisite concept and return.

## Outputs

A markdown explanation containing:

1. **Probe** — one open question about the learner's current mental model
2. **Targeted explanation** — the concept stated correctly, naming the misconception being corrected
3. **Concrete example** — small-numbers example in the requested domain
4. **Check-for-understanding** — application question whose right answer requires applying (not repeating) the explanation
5. **Variation (conditional)** — alternate framing if the check fails; included as a fallback section ready to deploy
6. **Bridge** — one sentence connecting this concept to the next adjacent concept

Length: typically 200-600 words. Above 800, the explanation has too much; trim or split.

## Failure modes

Known anti-patterns and how this skill catches them:

- **Reciting the textbook definition that the learner already bounced off** — caught by step 1 misconception identification; the explanation must pivot from the misconception
- **Skipping the probe and lecturing at the learner** — caught by step 2 mandatory probe; the explanation is calibrated against the learner's mental model, not assumed
- **Abstract symbols with no concrete example** — caught by step 4 concrete-mandatory rule
- **Check-for-understanding that only tests repetition** — caught by step 5 application-required rule
- **Repeating the same explanation louder when the check fails** — caught by step 6 alternate-framing rule
- **Tier mismatch (high-school explanation to a grad student, or vice versa)** — caught by step 0 tier confirmation; the skill refuses on ambiguous tier
- **Bridging to the wrong adjacent concept** — caught by the tier-default bridges in `reference/concept-catalog.md`
- **Lecturing past where the learner is following** — caught by step 5 check-for-understanding gate; do not proceed without confirming the previous step landed

## References

- `reference/socratic-structure.md` — the five-part probe-explain-concrete-check-variation pattern with templates
- `reference/concept-catalog.md` — canonical concepts with tier-by-tier explanations and the bridges to adjacent concepts (p-value, CI, CLT, hypothesis test, regression coefficient, Bayes' theorem, power, effect size)
- `reference/common-misconceptions.md` — concept-by-concept list of student intuitions to address head-on
- [Cohen, *The Earth is Round (p < .05)*, American Psychologist 1994](https://psycnet.apa.org/record/1995-12080-001) — canonical reference on the p-value misinterpretation; the explanation pattern for p-value derives from this
- [Greenland et al., *Statistical Tests, P Values, Confidence Intervals, and Power: A Guide to Misinterpretations*, European Journal of Epidemiology 2016](https://link.springer.com/article/10.1007/s10654-016-0149-3) — twenty-five canonical misinterpretations of p, CI, and significance; targets for the misconception-addressing step

## Examples

### Example 1: P-value to a junior analyst (happy-path)

Input: *"Explain the p-value to a junior analyst on my team. They just finished an intro stats course but rarely use it day to day. Domain: A/B testing."*

Output: skill opens with a probe (*"Before I explain, what is your current intuition for what a p-value tells you?"*). Notes the canonical misconception (probability that the null is true). Targeted explanation pivots from the misconception: *"You may have heard a p-value as 'the probability the null is true.' The 'if' that gets lost: the p-value is the probability of seeing the data — or anything more extreme — IF the null is true. It is a tail-area under an assumed-null world, not a probability about the null itself."* Concrete A/B example: control conversion = 5%, treatment = 6%, n = 1000 per arm; computed p = 0.04; explain in product terms. Check-for-understanding: *"If your A/B test shows p = 0.04, can you tell your PM there is a 96% chance the treatment is better than control?"* (Correct answer: no — the 4% is conditional on no-effect, not on the treatment being better.) Bridge: *"Next concept that will trip you up the same way: confidence intervals. The same conditional-probability framing applies."*

### Example 2: Confidence interval to a grad student who got the intro version (edge-case)

Input: *"A grad student says 'I know what a CI is from intro stats but my advisor says I am explaining it wrong in my thesis.' Help them upgrade their understanding."*

Output: skill identifies the tier as grad (advanced), and the canonical misconception is the Bayesian-flavored framing applied to a frequentist CI. Probe: *"How are you explaining the 95% CI in your thesis right now?"* Targeted explanation pivots from the (probably wrong) Bayesian-flavored answer: *"A 95% CI is not 'the true value has a 95% chance of being in this interval.' That is a credible-interval statement. A 95% CI is a frequentist procedure: 95% of intervals constructed this way, across hypothetical repeated experiments, would contain the true value. Once you have a specific interval [3, 7] from your one experiment, the true value either is or is not in it — there is no probability on the parameter under frequentist semantics."* Concrete: explain with a small simulation framing the grad student would code (1000 repeated samples, count coverage). Check-for-understanding: *"In your thesis, can you say 'we are 95% confident that the population mean is in [3.2, 4.1]'? What is the most defensible rephrasing?"* (Correct answer: rephrase as a property of the procedure, not of the specific interval — e.g., "the 95% CI for the population mean was [3.2, 4.1]" or "using a procedure that yields 95% coverage in repeated sampling.") Bridge: *"Adjacent: when you read 'posterior credible interval' in a Bayesian paper, that IS the 'true value has 95% probability of being in this interval' framing — different formalism, same word."*

### Example 3: Ambiguous tier (anti-trigger)

Input: *"Explain the central limit theorem."*

Output: skill identifies the input as missing an audience tier. Refuses to proceed without it. Explains briefly why: a high-school-tier explanation of CLT is unrecognizable as the same topic as a grad-tier explanation; the same words land totally differently. Asks one focused question to disambiguate: *"Who is the explanation for — a high-school stats student, an undergraduate in their first stats course, an undergraduate in their third stats course or first ML course, a grad student, or a practitioner who took stats years ago? The explanation changes substantially across these tiers."* Does NOT default to "intro" or guess.

## See also

- `teaching/writing-pset-walkthrough` — when a problem is in hand and the learner wants worked steps, not a pure conceptual explanation
- `teaching/diffing-instructor-vs-student-solution` — when the explanation is in service of grading a specific student attempt
- `teaching/writing-graded-rubric` — when authoring an assessment for the concept rather than explaining it
- `teaching/writing-onboarding-guide` — multi-audience format; this skill is single-audience-per-explanation
- `ml-datasci/selecting-statistical-test` — the underlying decision tree; explanations of test selection often invoke this
- `ml-datasci/reporting-effect-sizes` — the canonical companion concept to p-value; the bridge from p-value explanations often points here

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v6-batch-3, skill 1) via PRAGMATIC discipline
