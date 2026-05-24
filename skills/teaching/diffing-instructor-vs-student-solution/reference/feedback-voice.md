# Feedback voice — naming principles, not symptoms

The single biggest difference between formative and non-formative feedback is whether the student reads it and learns the GENERAL rule or only the SPECIFIC correction.

## The principle / symptom distinction

| Symptom feedback (low value) | Principle feedback (high value) |
|---|---|
| *"You used the wrong test."* | *"You ran a two-sample t-test because the data has two columns. For paired data — same subject measured twice — the test family is paired, not two-sample. Principle: design determines the test family before any numbers are computed."* |
| *"Your answer is wrong."* | *"Your final value comes from a one-sign error in the chain rule at step 3 (the derivative of cosine carries a negative). Everything before and after is correct."* |
| *"You got it right, but..."* | *"You arrived at 7 by rounding the mean to the nearest integer. The mode is the most frequent value; it happens to be 7 here. On [1, 5, 7, 7, 9] the mode is 7 but the rounded mean is 6 — the same approach would fail there."* |

The student should be able to read the feedback, close the document, and answer a variation of the problem correctly.

## Voice rules

### 1. Address the student in second person ("you"), not third ("the student")

This is a piece of writing for the student to read, not for an instructor to file. "You ran a two-sample t-test" lands; "the student ran a two-sample t-test" does not.

### 2. Name the step number explicitly

"At step 2, the assumption check..." anchors the feedback. The student can find step 2 in their work and see exactly what the comment refers to.

### 3. One feedback message per step, not stacked

Multiple comments on the same step compound and overwhelm. If a step has multiple things wrong, pick the ROOT cause and address it; the others are likely cascades or follow naturally from the root fix.

### 4. Name the principle, not the topic

"Test selection" is a topic. "Design determines the test family before any numbers are computed" is a principle. Topics tell the student what to study; principles tell them what to KNOW.

### 5. Give a one-variation counter-example for category (A)

When the student is right-for-wrong-reason, a single counter-example on a slightly varied dataset proves the wrong method fails. This is the most efficient way to convince a student that "I got the right answer" is not enough.

### 6. Confirm what was right in category (B)

When the student has a single-misstep cascade, lead the per-step feedback with what was correct downstream. Without the affirmation, the student over-corrects and loses confidence in steps that were actually right.

### 7. Keep length proportional to the work

Feedback longer than the student's attempt itself overwhelms. Cap feedback at roughly 1x the attempt length. If your draft exceeds 2x, collapse to the conceptual gaps + mechanical errors summary only.

### 8. End with one next-action

The student should leave with one concrete next step: re-read section X / re-do problem Y / try variation Z. Not a list — one action.

## Voice anti-patterns

- **Sarcasm or shaming.** "Obviously you did not..." erodes trust and makes the next attempt less likely. Use neutral, declarative voice.
- **Hedging the verdict.** "This might be wrong..." when it is unambiguously wrong wastes the student's attention. Be definite.
- **Praising effort without naming what worked.** "Great effort!" without specifics teaches nothing. If you affirm, name what was right.
- **Listing everything wrong without prioritizing.** A student who reads "12 things to fix" fixes none of them. Prioritize to 1-3.
- **Comparing to other students.** Per-student feedback should not reference what the rest of the class did. Compare to the principle, not to peers.

## Tier-appropriate vocabulary

The feedback's vocabulary matches the student's tier (per `teaching/writing-pset-walkthrough` tier definitions). High-school-tier feedback uses "spread" instead of "variance"; grad-tier feedback uses jargon directly. Mismatched tier patronizes (over-explained) or confuses (under-explained).

## Length per category

| Category | Typical feedback length per step |
|---|---|
| (A) right-answer-wrong-reasoning | 2-4 sentences (the counter-example is the bulk) |
| (B) wrong-answer-right-reasoning | 1-3 sentences (name the misstep, confirm what was right) |
| (C) legitimate-alternate-path | 1 sentence (mark correct, note the path differs from the reference) |
| (D) uncorrelated-error | 1 sentence (name the mechanical error, recommend slowdown not study) |
| Cascade marker | half a sentence ("cascade from step N") |
