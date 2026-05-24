# Cycle-handling options for tree-as-skill conversion

A strict tree has no back-edges. If your decision logic has a node that points back to an earlier predicate, you need one of these three patterns to preserve walk-the-tree discipline.

## Option 1 — State-enrichment (convert to a strict tree)

Replace the back-edge by enriching the state per visit. The same predicate, evaluated on different state, is effectively a different node.

### When to use

- The back-edge represents "re-evaluate with more data" or "re-check with a different lens"
- The state difference between visits is concrete (iteration counter, augmented data set, alternative measurement)
- You can enumerate the maximum useful number of iterations

### How to apply

Add an iteration counter as an implicit predicate gate. Each iteration unrolls the tree into a fresh copy with the counter incremented.

```markdown
### Step N (iteration k) — <Predicate>

Predicate: <same predicate, but on the iteration-k data set>.
Precondition: iteration-k data set is available (initial data plus k rounds of follow-up).

- <Branch leading to a leaf> → leaf
- <Branch leading to inconclusive> → start iteration k+1 (go to Step 1 with augmented data)
```

The skill caps iterations explicitly (e.g., k ≤ 3) and requests human input on cap-hit.

### Example

Stats-test inconclusive result (p between 0.05 and 0.10):

- Iteration 1: run the test on the original data. If p < 0.05 or p > 0.10, take the leaf. If p in [0.05, 0.10], collect more data → start iteration 2.
- Iteration 2: re-run the test on the augmented data. Same branches.
- Cap: iteration 3 → human input required (the design is underpowered or the effect is at the boundary; needs judgment).

## Option 2 — State-machine (explicit states and transitions)

Replace the tree-walk metaphor with an explicit state machine. Each state has named entry conditions, named exit conditions, and named transitions to other states.

### When to use

- The decision logic naturally has named phases (gathering, evaluating, executing, interpreting)
- Multiple paths can lead to the same state (a strict tree forbids this; a state machine allows it)
- The back-edge represents a phase change, not just a re-evaluation

### How to apply

Document each state in its own H3 section under the Workflow. Per state: entry conditions, exit conditions, allowed transitions, action on each transition.

```markdown
### State: gathering-data

Entry conditions: user has named the question but not yet provided data.
Exit conditions: data is in hand for at least the first predicate.
Allowed transitions:
- data sufficient → state: evaluating-assumptions
- user aborts → state: end

### State: evaluating-assumptions

Entry conditions: data in hand.
Exit conditions: all required assumption checks reported.
Allowed transitions:
- assumptions met → state: running-test
- assumptions violated → state: selecting-alternative-test
- assumption check ambiguous → state: requesting-clarification
```

### Trade-off

State machines are more expressive than trees but the walking discipline is more complex; the skill must enforce that only documented transitions fire. Use only when the tree model genuinely breaks.

## Option 3 — Revisit-cap (allow back-edges, cap the loops)

Allow the back-edge to remain in the tree, but add an explicit revisit counter that caps the maximum number of loops.

### When to use

- The back-edge is rare (most walks terminate without looping)
- State enrichment or state-machine conversion would be overkill
- The cap-hit behavior (human input request) is acceptable

### How to apply

Add a revisit-counter predicate at the back-edge:

```markdown
### Step 5 — Inconclusive result

If revisit count < 3:
- Increment revisit count, go to Step 2 with augmented data

If revisit count ≥ 3:
- Cap hit. Request human input. The design is at a boundary that walk-the-tree
  cannot resolve without judgment.
```

### Trade-off

This option preserves the tree-walk skill structure but admits a small amount of non-tree behavior. Document the cap value and the cap-hit behavior visibly so the user is not surprised by a loop or an unexpected human-input request.

## Picking among the three

| Pattern | Pick when | Avoid when |
|---|---|---|
| State-enrichment | Back-edge means "re-evaluate with more data", iteration count is meaningful | Back-edge means "go to a different phase", state difference is qualitative |
| State-machine | Multiple paths to the same state, named phases | Linear tree with one rare back-edge (overkill) |
| Revisit-cap | Rare back-edge, simple cap-hit fallback acceptable | Frequent back-edges (will hit cap routinely, user experience degrades) |

If none of the three fits, the underlying logic is likely not a tree. Hand off to a brainstorming or premortem-style skill where judgment is the deliverable.
