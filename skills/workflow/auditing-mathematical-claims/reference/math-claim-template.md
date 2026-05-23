# Math-claim per-row audit template

Use one row per claim in scope. The four core fields are mandatory; severity / likelihood / detectability / priority follow if confidence_format = "calibrated".

| Field | Value |
|---|---|
| Claim | <theorem / lemma / corollary / equation / definition label> |
| Location | <section / page / line / file:line> |
| Concern | <strongest version of the worry — what could be wrong> |
| Strongest counter | <most generous defense of the claim; steel-man the author> |
| Stops mattering if | <falsifiable stopping condition — what would have to be true for the concern to dissolve> |
| Severity (1–5) | 1 = mildly embarrassing footnote; 5 = retraction / proof collapse |
| Likelihood (1–5) | calibrated probability the concern is real after Strongest-counter |
| Detectability (1–5) | 1 = invisible until a postmortem; 5 = caught by existing peer-review |
| Priority | Severity × Likelihood / Detectability |

## Worked filled-in example

| Field | Value |
|---|---|
| Claim | Theorem 1 |
| Location | Section 3, Theorem 1 statement |
| Concern | "Equivalent" is used loosely. The proof shows bijection between representation values, not preservation of the attention operation. Downstream behavior depends on the operation, not just the values. |
| Strongest counter | For sequence length ≤ 8, the head-output space is finite (at most 2^(8d) elements); a bijection of finite sets IS an isomorphism in the category of finite sets. If the paper's downstream argument uses only set-equality, the bijection suffices. |
| Stops mattering if | The paper either (a) restates as "isomorphic as sets" + confirms downstream arguments use only set-equality, OR (b) extends the proof to show the attention operation is preserved under the permutation. |
| Severity | 4 |
| Likelihood | 4 |
| Detectability | 2 |
| Priority | 8 |

## Anti-pattern rows

These are NOT acceptable rows; they indicate audit theater rather than engagement:

| Field | Anti-example | Why it fails |
|---|---|---|
| Concern | "The proof might be wrong" | No specifics; no implicit-assumption surfaced |
| Strongest counter | "The author probably knows what they're doing" | Not a steel-man; an appeal to authority |
| Stops mattering if | "If the result is correct" | Not falsifiable; circular |

If a Strongest-counter dissolves the Concern entirely, **remove the row** rather than retaining it as a low-priority noise concern.
