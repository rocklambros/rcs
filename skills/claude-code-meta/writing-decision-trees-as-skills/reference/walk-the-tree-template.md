# Walk-the-tree Workflow-section template

Copy-paste template for the Workflow section of a tree-as-skill SKILL.md. Replace placeholders with your domain's predicates and leaves.

## Pattern

```markdown
## Workflow

Walking discipline: the skill commits to checking predicates in the order
below. The skill does NOT jump to a leaf because the user mentioned a leaf or
named a specific recommendation in the question. If the user names a leaf,
the skill walks from Step 1 and confirms the leaf is correct for the user's
data.

Copy this checklist into the response:

```
Tree-walk progress:
- [ ] Step 1: <Predicate P1>
- [ ] Step 2: <Predicate P2 or next predicate per P1 branch>
- [ ] Step 3: ...
- [ ] Leaf action selected: <L?>
- [ ] Precondition check for the leaf's recommended action satisfied
```

### Step 1 — <Predicate P1, in question form>

Predicate: <restate the predicate>.
Precondition: <what data must be in hand to evaluate this predicate>. If
absent, request input rather than guess.

- <Branch value 1> → go to Step 2 (<next predicate or leaf>)
- <Branch value 2> → go to Step 3 (<next predicate or leaf>)
- <Branch value 3> → go to Step 4 (<next predicate or leaf>)

### Step 2 — <Predicate P2, in question form>

Predicate: <restate>.
Precondition: <what data is required>.

- <Branch value 1> → leaf <L1>: <leaf action description>
- <Branch value 2> → leaf <L2>: <leaf action description>

### Step 3 — ...

(repeat for every internal node in the tree)

### Leaves

| Leaf ID | Action | Used by step | Precondition |
|---|---|---|---|
| L1 | <Action description> | Step 2 (yes-branch) | <data required for the action itself> |
| L2 | <Action description> | Step 2 (no-branch) | <data required> |
| ... | ... | ... | ... |
```

## What to leave out

- Imperative phrasing ("first do X, then do Y"). Use predicate-and-branch phrasing instead.
- "Use judgment to decide." If the predicate is "use judgment", it is not a tree predicate.
- Implicit default branches. Every branch value must be enumerated; "any other value" defaults are bug surfaces.

## What to include

- Per-predicate precondition: what data must be in hand
- Per-leaf precondition: what additional data the leaf action itself requires
- Anti-shortcut clause at the top of the Workflow section
- Numbered predicates so the walk has a documented order

## Example: from `selecting-statistical-test`

```markdown
## Workflow

### Step 1 — How many groups in the design?

Predicate: count of independent groups.
Precondition: study design must name the group count, or the data must reveal it.

- 1 group → go to Step 2 (one-sample family)
- 2 groups → go to Step 3 (two-sample family)
- 3+ groups → go to Step 5 (ANOVA / Kruskal family)

### Step 2 — One-sample: comparison to a known constant?

Predicate: a constant mu_0 is specified.
Precondition: mu_0 explicit.

- Yes → go to Step 2a (normality check)
- No → request input; the design is incomplete

### Step 2a — One-sample, normality

Predicate: Shapiro-Wilk p > 0.05?
Precondition: Shapiro-Wilk result in hand.

- p > 0.05 (consistent with normal) → leaf L1: one-sample t against mu_0
- p ≤ 0.05 (reject normality) → leaf L2: Wilcoxon signed-rank against mu_0
```

## Anti-pattern: implicit default branch

```markdown
### Step 2a — One-sample, normality

Predicate: is the data normal?

- Yes → one-sample t
```

Missing: the "No" branch. The skill will guess on non-normal data. Fix: enumerate every branch explicitly.
