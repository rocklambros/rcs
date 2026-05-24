# Alternate-path recognition heuristics

A student arrives at the correct answer via a different method than the reference. The skill must distinguish a legitimate alternate (category C, mark correct) from a wrong path that happens to arrive at the right answer (category A, flag).

## The three-test check (from category-definitions.md)

1. **Same final answer** within rounding tolerance, including symbolic expressions reducible to the same form
2. **Each step uses a valid principle** — named, defensible, peer-explainable
3. **The path generalizes** — substitute different α / data shape / sample size; if it still produces the right answer, the path generalizes

ALL THREE must pass for category (C). Any failure → category (A) or (B).

## Common legitimate-alternate patterns by topic

### Statistics

- **Bayesian path arriving at the same numerical answer as frequentist reference** — common when the prior is uninformative (e.g., Beta(1,1) for a Bernoulli rate). The posterior probability that p > 0.5 will closely track the frequentist p-value's complement under flat priors. Mark correct; note framework difference.

- **Bootstrap CI arriving at the same coverage as the parametric CI** — when both methods agree, the bootstrap is a legitimate alternate. Generalizes to non-Normal data where the parametric fails.

- **Permutation test arriving at the same p-value as t-test** — legitimate alternate. Generalizes to small samples and non-Normal data where the t-test assumption fails.

- **Effect-size-and-CI approach replacing significance testing** — if the question is "is there an effect?", reporting effect size with 95% CI that excludes zero is a legitimate alternate to reporting p < α. Mark correct; some instructors actively prefer this.

### Linear algebra / calculus

- **Closed-form solution vs. iterative method** — for a system with a known closed form (e.g., OLS via normal equations vs. gradient descent), both arrive at the same answer. Both legitimate.

- **Substitution vs. integration by parts** — different integration techniques applied to the same integrand often yield the same antiderivative (differing only by constant). Both legitimate if the answer simplifies to the reference.

- **Eigendecomposition vs. SVD** — for symmetric matrices, both yield the same answer. Both legitimate.

### Programming / algorithms

- **Top-down memoization vs. bottom-up DP** — same problem, same complexity class, different implementation style. Both legitimate.

- **Iterative vs. recursive (with tail-call equivalence)** — for many problems, both produce the same output. Legitimate when the recursive version handles the same edge cases.

- **List comprehension vs. functional map/filter** — Python idiom difference; both produce the same output. Legitimate.

- **Different sort algorithms producing the same sorted output** — if the question is "sort this," any correct sort is legitimate. The instructor may grade on the specific algorithm if the question specifies (e.g., "implement merge sort"); in that case, the wrong algorithm is NOT a legitimate alternate.

### Probability

- **Direct enumeration vs. conditional probability formula** — for small finite sample spaces, brute-force counting and Bayes' theorem produce the same answer. Both legitimate.

- **Generating-function approach vs. recurrence** — for discrete distributions, both can compute the same moments. Both legitimate.

## Patterns that LOOK like alternates but FAIL the three-test check

### Fails test 2 (no valid principle, just coincidence)

- "I noticed the answer is always 7, so I wrote `return 7`." → not (C). No principle.
- "I copied the reference's pattern but with my own variable names." → not (C). Not actually a different path.
- "I tried things until something matched the expected output." → not (C). Empirical fitting, not reasoning.

### Fails test 3 (does not generalize)

- "I solved x^2 = 4 by trying x = 2." → fails on x^2 = 5 (no integer solutions; the trial-and-error does not generalize).
- "I computed P(A | B) by assuming A and B are independent." → fails when they are not.
- "I used the unbiased variance formula because the sample size happened to be 1 (no division-by-zero)." → fails on any sample size > 1.

### Fails test 1 (different answer, masked by rounding)

- Reference: 7.000; student: 7.001. → close but different. The student's method may be wrong AND happen to produce a near-match; test 3 (generalization) usually exposes this.

## When in doubt — ask the student

If the path's legitimacy is genuinely ambiguous, the highest-fidelity move is to ask the student to articulate the principle they applied at each step. If they can name a defensible principle, it is (C). If their explanation is "I just tried it," it is (A) or coincidental — flag accordingly.

In an automated grading context where asking is not possible, default to (A) (right-answer-wrong-reasoning) when the principle is not articulated in the work. Document the conservative call and let the student appeal.

## Instructor responsibility: harvest legitimate alternates for next year

A category (C) marked correct should also be noted for the instructor's records. If an alternate path appears in multiple student submissions, it is worth adding to next year's reference solution as a canonical alternate. This is how an answer key matures over years.
