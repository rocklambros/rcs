# Implicit-assumption checklist for math audits

For each formal claim, walk this checklist to surface assumptions that are not written but the claim quietly depends on.

## Norm

If the claim involves "equivalence", "isomorphism", "approximation", "convergence", or any quantitative bound, which **norm** is in play?

- L¹ (sum of absolute values) vs L² (Euclidean) vs L∞ (max) vs L^p general
- Operator norm vs Frobenius norm for matrices
- Wasserstein vs KL vs TV for distributions
- Spectral norm vs nuclear norm for low-rank arguments

A claim "A ≈ B" without naming the norm is suspect.

## Measure

Are we working **everywhere** or **almost everywhere**?

- "f = g" — pointwise or up to a measure-zero set?
- Integration: Lebesgue, Riemann, counting? Which σ-algebra?
- Probability claims: w.p. 1? In expectation? In probability? Almost surely?
- Are measure-zero exceptions documented (e.g., a measure-zero set of inputs where the claim fails)?

## Domain

What is the claim's **domain of definition**?

- Bounded vs unbounded?
- Compact vs open?
- Finite vs countable vs uncountable?
- Convex vs general?
- Connected vs disconnected?
- For ML: train distribution, test distribution, deployment distribution — same or different?

## Smoothness

What **regularity** is assumed?

- Continuous (C⁰)? Differentiable (C¹)? Twice-differentiable (C²)? Smooth (C^∞)?
- Lipschitz (with what constant)? Hölder?
- For optimization: convex, strongly convex, weakly convex, semi-convex?
- For sequences: monotone? Bounded? Cauchy?

## Finiteness

Are any quantities implicitly assumed **finite**?

- Sums absolutely convergent vs conditionally?
- Expectations finite (does the second moment exist)?
- Information-theoretic quantities (does the entropy converge)?
- Variance assumed finite for CLT-style arguments?
- For neural-network arguments: weights bounded, activations bounded?

## Operation preservation

If "equivalent", "isomorphic", or "preserves" appears, what is being preserved?

- Set equality only (bijection of points)?
- Algebraic operations (group / ring / vector-space morphism)?
- Topological structure (continuity preserved)?
- Probabilistic structure (measure preserved, conditional structure preserved)?
- Order / metric / inner product?

A bijection of sets does NOT imply isomorphism of algebras. A homeomorphism does NOT imply differentiable equivalence.

## Boundary conditions

What happens at the **corners**?

- n = 0? n = 1? n → ∞?
- Empty input? Single-element input?
- Dimension d = 1? d = 0? d → ∞?
- Length = 0? Length = 1?
- Probability = 0 or 1 (vs strictly 0 < p < 1)?

Many proofs handle "the generic case" and silently break at boundaries.

## Constants

When a bound has "O(f(n))" or "≤ C·f(n)", what is **C**?

- Does C depend on the dimension, the condition number, the smoothness constant, the Lipschitz constant?
- Is C polynomial in those? Exponential? Super-exponential?
- For practical interpretation: at the problem's actual scale, how large is C?
- Is the bound tight, or could it be vastly loose?

A polynomial rate with a 2^d hidden constant is exponentially-bad in d.

## Existence vs constructive

Does the proof **construct** the object or merely show it **exists**?

- Existence proofs (axiom of choice, compactness) do not give an algorithm
- For ML / engineering claims, constructive is usually required
- "There exists a separating hyperplane" is different from "we can find it efficiently"

## Quantifier order

Watch for sneaky quantifier swaps:

- "∀ε ∃N ∀n > N: |a_n − a| < ε" — uniform convergence
- "∀n ∃ε ∀..." — pointwise convergence

These have different consequences. Audit which order the proof actually uses, not which order is stated.

## Identification of "the same"

When the proof says "without loss of generality" or "by symmetry", verify the symmetry actually holds:

- Does the claimed symmetry preserve all relevant structure (norm, measure, operations)?
- Or does it only preserve some structure and silently break others?

## Recursion / induction soundness

For inductive proofs:

- Is the base case actually checked?
- Does the inductive step assume the correct hypothesis (often there is a subtle over-statement)?
- Are there any uniform-vs-pointwise mismatches in the induction?
- For transfinite induction: is the limit step verified?

## Numerical conditioning

For numerical claims:

- Is the proof in exact arithmetic, but the implementation in floating-point?
- Does the implementation's error accumulate in a way the proof does not address?
- Are constants chosen for theoretical convenience that have terrible numerical conditioning?

## Closure of references

For claims that rely on cited results:

- Does the cited result actually say what the citing paper claims it says?
- Are the cited result's assumptions actually met in the citing context?
- Does the cited proof hold in the citing paper's setting (different domain, different norm, different regularity)?

A citation chain is only as strong as its weakest link.
