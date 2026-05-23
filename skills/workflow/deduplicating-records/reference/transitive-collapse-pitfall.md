# Greedy pairwise merging vs union-find — worked example

A small synthetic example showing why greedy pairwise merging produces the **transitive-collapse failure** and how union-find on a duplicate graph closes it.

## Input

Five records from three sources:

| record_id | source | title | doi |
|---|---|---|---|
| `A` | AIID | "GenAI medical-advice incident" | `10.1234/aiid-42` |
| `B` | OECD | "GenAI medical-advice incident" | `10.1234/aiid-42` |
| `C` | AIAAIC | "Generative-AI medical-advice incident" | `10.1234/aiid-42` |
| `D` | AIID | "Unrelated supply-chain incident" | `10.5678/aiid-43` |
| `E` | AIID | "Customer-service chatbot incident" | `10.9999/aiid-44` |

Three rules:

- Rule 1 (confidence 0.90): `doi` equality
- Rule 2 (confidence 0.85): `Jaro-Winkler(title) ≥ 0.92`
- Rule 3 (confidence 0.60): `source` equality (definitely below `review_threshold = 0.85`)

Both A↔B and A↔C and B↔C should merge by Rule 1; D and E should remain untouched.

## Greedy pairwise merging — the broken approach

```
Pass 1: scan all pairs; for each pair, if any rule fires, merge in-place.
  - (A, B): Rule 1 fires → merge B into A. Canonical id map: {A: A, B: A}.
  - (A, C): Rule 1 fires → merge C into A. Canonical id map: {A: A, B: A, C: A}.
  - (B, C): look up B → finds A. Look up C → finds A. Same. Skip.
  - Done. Component: {A, B, C}. Looks correct so far.

Pass 2 begins, but suppose we did NOT refresh indices and the next pass
operates on the original record list:
  - (A, B): canonical-id index still says B's canonical is B (not refreshed)
  - Re-merge B into A. Same outcome but the diff JSON now has two merge
    entries for B → A. Audit trail confused.
  - Worse: if Pass 1 ran in a different order, e.g. (B, C) first:
    - merge C into B. Canonical: {A: A, B: B, C: B}.
    - (A, B): Rule 1 fires → merge B into A. Canonical updated for B but
      NOT for C (the index of canonicals was not rebuilt).
    - Result: A merged with B; C still points at the now-merged-into B,
      not A. Component lookup for C returns B → returns A only if path
      compression is implemented correctly, which greedy pairwise typically
      omits. A↔C edge is "missed".
```

This is the `genai_agentic_incidents` 2.0.0 bug #2: the result depends on iteration order, and intermediate state pollutes subsequent merges.

## Union-find on the duplicate graph — the correct approach

```
Step 1: Build the graph (do NOT merge anything yet):
  Nodes: {A, B, C, D, E}
  Edges (rule, weight):
    (A, B, Rule 1, 0.90)
    (A, C, Rule 1, 0.90)
    (B, C, Rule 1, 0.90)

Step 2: Initialize union-find:
  parent = {A: A, B: B, C: C, D: D, E: E}

Step 3: Process every edge whose confidence ≥ review_threshold:
  union(A, B) → parent = {A: A, B: A, C: C, D: D, E: E}
  union(A, C) → parent = {A: A, B: A, C: A, D: D, E: E}
  union(B, C) → find(B) = A, find(C) = A; already same. No-op.

Step 4: Connected components:
  {A, B, C}, {D}, {E}
```

The result is **order-independent** — the same components emerge no matter which edge is processed first. The transitive case (A↔C) is closed automatically because A↔B and B↔C share a component.

## Why this matters

A dedup pipeline that processes 12,000 records in passes will hit the iteration-order trap *somewhere*. The bug is silent: the merge appears to work but the output has missed-merge errors that only surface when a downstream consumer notices duplicate components for the same incident.

The union-find approach is a one-pass O(n α(n)) algorithm — there is no performance reason to prefer greedy pairwise merging.

## If you are stuck with a pass-based pipeline

If you cannot rewrite the dedup as a single union-find pass (e.g. the corpus is too large to hold the duplicate graph in memory and you must process in blocking-key partitions):

1. **Within each partition**, build the partition's local graph and run union-find on it
2. **Between partitions**, only allow merges through a re-built canonical-id index — never trust the previous partition's in-memory state
3. **At the end of every partition**, rebuild the canonical-id index from the merged output before the next partition starts
4. After all partitions, run one **cross-partition** union-find pass over the residual edges that crossed partition boundaries

This preserves the order-independence guarantee while keeping memory bounded.
