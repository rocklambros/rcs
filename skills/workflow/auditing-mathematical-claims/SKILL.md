---
name: auditing-mathematical-claims
description: >
  Audits a written or claimed mathematical result (theorem, lemma, bound,
  identity, asymptotic argument, definition) by walking each formal claim
  through a four-field per-claim table — Location · Concern · Strongest
  counter · Stops-mattering-if — and producing a prioritized remediation list.
  Adapts the ATACE math-flags template into a generalized, repo-agnostic
  format. Use when the user has finished a proof, paper section, theoretical
  argument, or formal bound and wants an adversarial audit of the mathematics
  specifically, distinct from empirical-claim red-teaming.
version: 0.1.0
status: shipped
track: workflow
audience: [skill-author, ml-engineer, data-scientist, ai-security, security-eng]
evidence:
  - ATACE
  - incident-rank-validation
  - adversarial-premortem-single
last-updated: 2026-05-23
---

# Auditing Mathematical Claims

## When to use

Trigger this skill when the user asks for or implies one of:

- A finished proof, theorem, lemma, bound, identity, asymptotic argument, or definition needs an adversarial audit
- A paper section is presenting a formal result and the user wants to stress-test the math BEFORE submission
- A claim of the form "we prove that X" or "this bound is tight" needs scrutiny
- A safety / security / regulatory argument depends on a formal upper-bound, lower-bound, or convergence claim
- Phrases like "audit the math", "are these claims tight?", "is the proof airtight?", "what assumptions am I sneaking in?", "stress-test this theorem"

This skill is the narrower, mathematics-focused sibling of `workflow/adversarial-premortem-single`. Premortem covers any high-stakes artifact (designs, plans, code, papers); this skill specializes on the *formal mathematics* portion.

## When NOT to use

Skip this skill and hand off when:

- The claim is **empirical**, not formal — "our system reduces error by 12% on the benchmark" — that is a measurement / methodology audit, route to `workflow/adversarial-premortem-single` (round 1 covers methodology failure)
- The artifact is a **whole system / plan / spec** with the math as one component — run `workflow/adversarial-premortem-single` first, then invoke this skill on the math portion specifically
- The user wants help **constructing** the proof, not auditing a finished one — that is a different (planned) skill `workflow/constructing-formal-proofs`
- The math is **already peer-reviewed** in a top venue and the user wants a literature review — different concern

## Quick start

User says: "I just finished my paper. Theorem 1 claims that for any sequence of attention heads `H₁, ..., Hₙ` of length ≤ 8, the heads are equivalent under a permutation isomorphism. Can you audit the math?"

Skill response: walks the four-field audit template per claim — Location (Theorem 1 statement + step in proof) · Concern (e.g., "equivalent" used loosely; bijection of representations does not imply bijection of operations or behavior) · Strongest counter (the steel-manned defense of the claim) · Stops-mattering-if (falsifiable condition under which the concern dissolves). Produces a prioritized remediation list ordered by severity × likelihood / detectability.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| artifact | file path or pasted text | yes | — | The proof, paper section, or formal statement to audit. |
| claim_scope | "theorems-only" \| "lemmas-and-theorems" \| "all-formal-statements" | no | "lemmas-and-theorems" | Which claims to audit; "all-formal-statements" includes definitions, identities, and worked examples (the broadest sweep). |
| max_claims | integer | no | 10 | Cap on the number of claims audited per pass; prevents noise when a paper has 40+ small lemmas. |
| confidence_format | "calibrated" \| "binary" \| "qualitative" | no | "calibrated" | Severity / Likelihood / Detectability format. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check items off as the audit progresses:

```
Math-audit progress:
- [ ] Step 1: Enumerate every formal claim within claim_scope and locate it (theorem N / lemma N / equation N / definition N)
- [ ] Step 2: For each claim, identify the implicit assumptions (norm, measure, domain, finiteness, smoothness)
- [ ] Step 3: For each claim, write the four-field row: Location · Concern · Strongest counter · Stops-mattering-if
- [ ] Step 4: Score each surviving concern: Severity × Likelihood / Detectability
- [ ] Step 5: Prioritized remediation list — top half by priority — with proposed fix per claim
- [ ] Step 6: Calibrated confidence statement — what the audit might still miss
```

### Step 1: Enumerate formal claims

Walk the artifact top-to-bottom. For each "theorem", "lemma", "corollary", "proposition", "definition", "claim", boxed equation, or assertion-of-fact, record:

- A short label (Theorem 1, Lemma 2.3, Equation 14, Definition 1.2)
- The location (section / page / line / file:line if code)
- The plain-English statement of what the claim says

Cap by `max_claims`. If the artifact has more, audit the highest-stakes claims first (those that the paper's main result depends on most directly).

### Step 2: Surface implicit assumptions per claim

For each claim, ask: what is *not* written that the claim quietly depends on? Common implicit-assumption families:

- **Norm**: which norm is "equivalent" under? L¹? L²? L∞? Operator norm? Frobenius?
- **Measure**: are we ignoring measure-zero sets? Almost-everywhere vs everywhere?
- **Domain**: does the claim assume bounded, compact, finite, smooth, convex, connected?
- **Smoothness**: is differentiability assumed? Which order? Lipschitz?
- **Finiteness**: are sums finite? Series absolutely convergent? Expectations finite?
- **Operation preservation**: if "equivalent" or "isomorphic", does the claim cover all the operations users will care about, or just the obvious ones?
- **Boundary conditions**: corner cases — empty input, n = 1, length = 0, dimension = 1?
- **Constants**: bounds with "O(f(n))" or "≤ C·f(n)" — what is the constant? Does the proof depend on the constant being small?

Write the assumption explicitly in the per-claim row.

### Step 3: Four-field per-claim row

For each claim, fill:

```
Claim: <theorem/lemma/equation label>
Location: <section / page / line>
Concern: <strongest version of the worry — what could be wrong with this claim>
Strongest counter: <the most generous defense of the claim — steel-man the author>
Stops mattering if: <falsifiable stopping condition — what would have to be true to dissolve the concern>
```

The **Strongest counter** field is the discipline check that prevents premortem theater (going through the motions without engagement). The **Stops-mattering-if** field is the discipline check against worry — every concern needs a falsifiable stop condition or it is not actionable.

### Step 4: Score and triage

Severity × Likelihood / Detectability, each 1–5:

- **Severity** — 1 (mildly embarrassing footnote) → 5 (retraction / proof collapse / safety claim invalidated)
- **Likelihood** — calibrated probability the concern is real after the strongest-counter
- **Detectability** — 1 (invisible until a postmortem) → 5 (caught by an existing CI / peer-reviewer / standard counterexample)

Sort claims by priority descending.

### Step 5: Prioritized remediation

For the top half by priority, propose a fix per claim:

- **Tighten** — add the missing assumption to the statement (norm, measure, smoothness, finiteness)
- **Restrict** — narrow the claim's scope (a result about "all transformers" becomes "all transformers with property P")
- **Weaken** — replace "equivalent" with the strictly true weaker form (e.g., "isomorphic as sets" instead of "isomorphic as algebras")
- **Disprove** — if the audit finds a counterexample, the claim must be retracted or restricted
- **Defer** — if the audit cannot reach a verdict, mark the claim as "audit-deferred" and recommend an external reviewer

### Step 6: Calibrated confidence

State what the audit might still miss:

- Audit had access only to <X>; claims requiring <Y> were not checkable
- The audit relied on the strongest-counter steel-manning the author; a determined adversary might find a stronger objection
- Some implicit-assumption families (e.g., choice of model of set theory, large-cardinal assumptions, foundational axioms) are out of scope

## Outputs

A markdown report:

1. **Executive summary** — top 1–3 highest-priority math concerns and the single recommended next step
2. **Per-claim audit table** — one row per claim: Claim · Location · Concern · Strongest counter · Stops-mattering-if · Severity · Likelihood · Detectability · Priority
3. **Prioritized remediation list** — top half by priority with proposed fix per claim
4. **Calibrated confidence statement** — what this audit might still miss

## Failure modes

- **Math-audit theater** — walking the table without actual mathematical engagement (filling Concern with "the proof might be wrong" with no specifics). Caught by: the **Strongest counter** field requires steel-manning the author; you cannot fill it without engaging with the claim's actual structure.
- **Empirical-and-math conflation** — auditing an empirical claim ("on benchmark X we score Y") as if it were a math claim. Caught by: When-NOT-to-use routes empirical claims to `workflow/adversarial-premortem-single`; the math audit declines to engage and explains why.
- **Implicit-assumption blind spots** — auditing only the statement and not the assumptions the statement depends on. Caught by: Step 2 enumerates implicit-assumption families (norm, measure, domain, smoothness, finiteness, operation preservation, boundary, constants) explicitly.
- **Counterexample-as-disproof without verification** — claiming a counterexample exists without checking it satisfies the claim's premises. Caught by: the remediation `Disprove` requires the counterexample to be exhibited explicitly, not asserted.
- **Notation-pedantry overflow** — auditing every notational ambiguity at the same priority as substantive concerns. Caught by: Step 4 prioritization formula (Severity weight dominates); notation issues typically score Severity ≤ 2.
- **Generosity drift** — the Strongest-counter field over time becomes weaker than the actual best defense. Caught by: if the strongest-counter dissolves the concern entirely, the row should be **removed** from the table, not retained as a low-priority concern.

## References

- [`reference/math-claim-template.md`](reference/math-claim-template.md) — the four-field per-claim row template + worked filled-in example
- [`reference/implicit-assumption-checklist.md`](reference/implicit-assumption-checklist.md) — the families of implicit assumptions to surface in Step 2
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — for workflow-checklist pattern
- Lakatos, *Proofs and Refutations* (1976) — origin of the "stretching the concept" critique pattern this skill formalizes
- Polya, *How to Solve It* — chapter on "looking back" maps to the audit discipline

## Examples

### Example 1: Theorem with implicit assumption (happy-path)

Input: "Theorem 1: for any transformer attention heads `H₁, ..., Hₙ` with sequence length ≤ 8, the heads are equivalent under a permutation isomorphism. Audit this."

Output:

```
Claim: Theorem 1
Location: Section 3, Theorem 1 statement
Concern: "Equivalent" is used loosely. The proof exhibits a bijection between
        the representations (head outputs viewed as elements of ℝ^d). It does
        NOT show that the operations the heads perform (the attention
        computation as a function of query, key, value) are preserved under
        the bijection. Two structures can be bijective as sets without being
        isomorphic as algebraic objects, and downstream behavior depends on
        the operation, not just the set.
Strongest counter: For sequence length ≤ 8, the head output space is a finite
        set with at most 2^(8d) elements, and any bijection of finite sets
        IS an isomorphism in the category of finite sets. If the paper's
        downstream argument only uses set-theoretic equality of outputs,
        the bijection suffices.
Stops mattering if: The paper either (a) restates the theorem as "isomorphic
        as sets" and confirms downstream arguments use only set-equality, OR
        (b) extends the proof to show the attention operation is preserved
        under the permutation, not just the output values.
Severity: 4 (the main "equivalence" claim is the paper's headline result)
Likelihood: 4 (calibrated: a determined reviewer will catch this)
Detectability: 2 (would survive a casual read; caught on careful read)
Priority: 4·4/2 = 8 → top priority
```

Remediation: tighten by restating the theorem as "isomorphic as sets" or extend the proof to operation-preservation. The skill recommends (a) as lower-risk if it does not break the downstream argument.

### Example 2: Bound with implicit constant (edge-case)

Input: "Lemma 3: the convergence rate is `O(1/n)`. Audit."

Output:

```
Claim: Lemma 3
Location: Section 4, Lemma 3
Concern: The bound `O(1/n)` hides the constant. The proof shows
        `error ≤ C/n` for some C. If C depends on the dimension d, the
        problem's condition number κ, or any hyperparameter, the "rate"
        is misleading for any practical setting where those quantities
        grow.
Strongest counter: If the paper's experimental section runs at fixed d, κ,
        the asymptotic claim is consistent with the empirical scaling.
        Big-O notation is the standard idiom and a reader can ask for the
        constant in the appendix.
Stops mattering if: The paper exhibits the constant C explicitly in the
        proof (or in an appendix), AND states which problem parameters C
        depends on.
Severity: 3 (medium — the claim is still asymptotically true but the
        constant could swamp the rate)
Likelihood: 3
Detectability: 3 (a careful reviewer asks for the constant; a casual reviewer
        accepts the O-notation)
Priority: 3·3/3 = 3 → mid-priority
```

Remediation: report C explicitly with its dependence on (d, κ, hyperparameters).

### Example 3: Empirical claim, not math (anti-trigger)

Input: "Our system achieved 87.3% accuracy on the GLUE benchmark, a 2.1% improvement over the previous state of the art. Audit this claim."

Output: This is an **empirical** claim, not a formal-math claim. The skill declines to engage and hands off to `workflow/adversarial-premortem-single`. The premortem skill covers methodology-failure (eval bias, test-set leakage, multiple-hypothesis fishing, base-rate cherry-picking) which is the right toolset for an empirical-claim audit. The skill names what would have to be different for the math-audit template to apply (e.g., if the user had a formal theorem about the algorithm's optimality, that theorem could be math-audited; the benchmark score itself cannot).

## See also

- `workflow/adversarial-premortem-single` — the broader artifact-audit skill; this one is the math-specialization
- `ml-datasci/checking-test-assumptions` — for the statistical-claim variant focused on hypothesis-test gating
- `ml-datasci/analyzing-regression-diagnostics` — for the regression-claim variant focused on inferential validity
- `ml-datasci/reporting-effect-sizes` — for the reporting side of empirical claims that ultimately need formal-math support

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
