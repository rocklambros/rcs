# The Socratic explanation structure

Every explanation follows this five-part pattern. The pattern is rigid because skipping any part degrades the learning in a specific way.

## The five parts

### 1. Probe (one open question)

Surfaces the learner's current mental model so the explanation can be calibrated against it.

- *"Before I explain X, what is your current intuition for X?"*
- *"If I said [common phrasing], what would you take that to mean?"*
- *"Walk me through what you think X is supposed to do."*

**Why mandatory:** without the probe, the explanation lands on top of whatever wrong intuition the learner already has, leaving them with two conflicting beliefs and choosing the older one.

### 2. Targeted explanation (with misconception named)

States the concept correctly, and EXPLICITLY names the misconception being corrected.

- ❌ "X is defined as..." (textbook recitation)
- ✅ "You may have learned X as Y. Here is what gets lost: the actual meaning is Z."

**Why mandatory:** acknowledging the wrong intuition by name disarms it. Glossing over it lets the learner reconcile the textbook definition against the wrong intuition and pick the wrong intuition.

### 3. Concrete example (small numbers, requested domain)

One example with specific small numbers in the domain the learner cares about.

- For medicine students: clinical trial / diagnostic test example
- For product analysts: A/B test / conversion example
- For ML engineers: model accuracy / dataset example
- For fundamentals: coin flip / dice roll example

**Why mandatory:** abstract symbols never land. The example provides the mental object the explanation can point to in future references.

### 4. Check-for-understanding (application question)

One question whose right answer requires applying the explanation, not repeating it.

- ❌ "Now tell me back what a p-value is." (tests memorization)
- ✅ "If your test reports p = 0.04, can you tell your manager there is a 96% chance the treatment is better?" (tests application of the conditional-probability framing)

**Why mandatory:** without an application check, the learner believes they understood it (because the words made sense) but cannot use it on the next problem.

### 5. Variation (alternate framing for failed check) + bridge

**Variation** — if the check fails, give a DIFFERENT framing (not the same explanation louder).

**Bridge** — one sentence connecting this concept to the adjacent concept the learner will encounter next.

**Why mandatory:** the variation handles the case where the primary explanation did not land for this learner's prior background; the bridge gives the learner a hook to anticipate the next gap.

## Common templates per concept

### P-value (undergrad-intro / practitioner tier)

```
**Probe:** Before I explain, what is your current intuition for what a p-value tells you?

**Common wrong intuition (named):** "the probability the null is true." This is the most common misinterpretation; it gets it backwards. We address it head-on.

**Targeted explanation:** A p-value is the probability of seeing your data — or anything more extreme — IF the null hypothesis is true. The "if" is the whole game. It is a tail-area under an assumed-null world, not a probability about the null itself.

**Concrete:** [domain-appropriate example with small numbers and a computed p-value]

**Check:** [application question that requires the learner to deny the wrong intuition]

**Bridge:** Confidence intervals share this same conditional-probability framing. Watch for it.
```

### Confidence interval (undergrad-intro tier)

```
**Probe:** If I told you the 95% CI for the mean is [3, 7], what would you take that to mean?

**Common wrong intuition:** "the true mean has a 95% chance of being between 3 and 7." This is the Bayesian-flavored interpretation applied to a frequentist tool — wrong under frequentist semantics, right under Bayesian semantics. We address it head-on.

**Targeted explanation:** A 95% CI is a property of the PROCEDURE that produced it. The procedure has the property that 95% of the intervals it generates (across hypothetical repeated experiments) contain the true value. Once you have a specific interval [3, 7], the true value either is or is not in it — frequentist semantics does not put a probability on the parameter.

**Concrete:** [simulation framing or repeated-sample example]

**Check:** [question that exposes the difference between interval-as-procedure and interval-as-Bayesian-statement]

**Bridge:** When you read "posterior credible interval" in a Bayesian paper, that IS the 95%-probability-on-the-parameter interpretation. Different formalism, same word.
```

### Central limit theorem (undergrad-intro tier)

```
**Probe:** Before we get into the math, what do you think the CLT is claiming?

**Common wrong intuition:** "data becomes Normal as the sample size grows." The CLT is not about the data — it is about the sampling distribution of the mean. We address it head-on.

**Targeted explanation:** The CLT says: if you take many samples of size n from a distribution (any shape, finite variance), and you compute the MEAN of each sample, the distribution of those means becomes Normal as n grows. The original data does not become Normal — it stays whatever shape it was.

**Concrete:** [example showing exponential data with sample means becoming Normal]

**Check:** [question that tests the data-vs-sampling-distribution distinction]

**Bridge:** This is why the t-test "assumes Normality" — it assumes the SAMPLING distribution of the mean is Normal, which the CLT gives you at moderate n even when the data is not.
```

## Tier-default prerequisites

The skill assumes these prerequisites at each tier:

| Tier | Prerequisites assumed |
|---|---|
| high-school | Algebra, descriptive statistics (mean, median, spread) |
| undergrad-intro | Calc 1, basic probability, knows what a random variable is |
| undergrad-advanced | Linear algebra, joint distributions, knows MLE conceptually |
| grad | Measure-theoretic probability OR strong applied equivalent; familiar with research methods |
| practitioner | Once knew the prerequisites; may have decayed; jargon recognition intact |

When a learner cannot follow an explanation given their tier's prerequisites, the most likely diagnosis is a prerequisite gap — recommend stepping back to the prerequisite concept and returning.
