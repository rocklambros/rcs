# Rubric-writing guide

How to write the three `expected_behavior` rubric items per eval scenario so a judge model can mark them pass / fail without subjective interpretation.

## The core rule

Every rubric item is a **third-person checkable assertion** about the candidate model's response. A reader (human or judge model) should be able to mark `pass: true | false` against the response without partial credit.

## Bad rubric items and why

| Bad rubric | Why it fails | Fix |
|---|---|---|
| "Response is helpful" | Not checkable. "Helpful" is subjective. | "Response identifies the leakage between train and test sets" |
| "Mentions Wilcoxon" | Too literal. A response that says "rank-based non-parametric paired test" should pass; the literal-string rule fails it. | "Recommends Wilcoxon signed-rank (or names the rank-based non-parametric paired test)" |
| "Does the right thing" | Circular. Defines pass as pass. | "Refuses to recommend a parametric test before checking the Normality assumption" |
| "Includes a code example" | Vague. What kind of code? Working code? Pseudocode? Any block? | "Includes a runnable Python snippet that calls `scipy.stats.wilcoxon(before, after)` with the user's two arrays" |
| "Addresses both points" | Ambiguous. Which two points? | (split into two rubric items, each naming the specific point) |
| "Response is well-formatted" | Format isn't behavior. | Drop. Format is not a quality signal at this layer. |

## Good rubric item patterns

### Pattern 1: "Recommends X (and not Y)"

When the skill must produce a specific recommendation:

- *"Recommends Wilcoxon signed-rank, NOT paired t-test"*
- *"Recommends `secrets.token_bytes(...)`, NOT a seeded random number"*
- *"Recommends Fisher exact test, NOT chi-squared, because expected counts fall below 5"*

The "NOT Y" half catches the most common wrong answer.

### Pattern 2: "Identifies / names X"

When the skill must surface a specific concept:

- *"Names the Shapiro-Wilk p-value as the gating assumption check"*
- *"Identifies the group-leakage where the same patient appears in train and test"*
- *"Names CPU-pin / platform-determinism as the cause of cross-machine non-reproducibility"*

### Pattern 3: "Does NOT X"

For anti-trigger scenarios where the skill must hold back:

- *"Does NOT recommend a fixed seed for cryptographic nonce generation"*
- *"Does NOT immediately recommend a test before asking about design / scale / assumption status"*
- *"Does NOT engage the full audit workflow on a 3-message API call"*

### Pattern 4: "Explains / cites X"

When the skill must produce a justification, not just an action:

- *"Cites the max-year-fallback anti-pattern as the cause of the spurious 2027 date"*
- *"Explains that nullability tightening is a breaking change for existing API consumers"*
- *"Explains why seeded RNG is wrong for cryptographic use (predictability)"*

### Pattern 5: "Produces a structured output with field X"

When the skill must produce a specific report shape:

- *"Produces a per-claim audit table with columns Location, Concern, Strongest counter, Stops-mattering-if"*
- *"Produces a prioritized remediation list ordered by severity × likelihood / detectability"*

## Process rubrics for open-ended skills

For skills where the output is genuinely open-ended (brainstorming, creative work, exploratory analysis), use process rubrics instead of outcome rubrics:

- *"Response asks at least one clarifying question before generating"*
- *"Response produces at least 5 distinct ideas spanning at least 2 different framings"*
- *"Response does NOT collapse to a single recommendation without enumeration"*
- *"Response explicitly names tradeoffs for each candidate option"*

Process rubrics test discipline and structure rather than canonical correctness — useful when canonical correctness does not exist.

## Anti-trigger rubrics

Anti-trigger scenarios are the most-skipped and most-important. Their rubric items must check that the skill DECLINES to engage AND does so with a useful explanation. Pattern:

1. *"Identifies the artifact / query as <not-the-skill's-domain>"* (the recognition check)
2. *"Declines to engage the <skill-name> workflow"* (the hold-back check)
3. *"Recommends the correct alternative (skill, tool, or pattern)"* (the hand-off check)

Without all three, the anti-trigger eval tests too little.

## When to revise a rubric item vs the skill body

If a rubric item fails repeatedly across revisions, ask:

- Is the rubric item achievable from the SKILL.md body? (If no, the body is incomplete.)
- Is the rubric item unambiguous? (If no, the rubric needs rewriting.)
- Is the judge model interpreting the rubric correctly? (If no, the judge prompt needs adjustment, or the rubric needs to be more literal-friendly.)

Revising the rubric to match a body that you cannot improve is rationalization. Revise the body first; revise the rubric only if the rubric itself was wrong from the start.
