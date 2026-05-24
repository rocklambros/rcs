---
name: writing-decision-trees-as-skills
description: >
  Converts existing decision-tree expertise (test-selection trees, triage
  flowcharts, dispatch rules, troubleshooting trees) into a deterministic
  walk-the-tree skill where each predicate is a numbered step, each leaf is a
  named action, and the skill commits to checking predicates in order rather
  than letting the model shortcut to a leaf based on the user's framing. Use
  when the user has a written or implicit decision tree (or DAG) whose
  predicates are objectively checkable and whose leaves are deterministic, and
  wants the discipline encoded as a skill. Refuses to encode open-judgment
  domains as trees and refuses to silently drop cycles.
version: 0.1.0
status: shipped
track: claude-code-meta
audience: [skill-author, instructor, ai-security]
evidence:
  - RCS
  - DU-MSDSAI-4441-Final
  - selecting-statistical-test
last-updated: 2026-05-23
---

# Writing Decision Trees as Skills

## When to use

Trigger this skill when the user asks for or implies one of:

- "I have a decision tree / triage flowchart / dispatch matrix and want to package it as a skill"
- "How do I write a skill that walks predicates in order rather than letting Claude jump to a conclusion?"
- They have a stats-test selection tree, an alert-triage matrix, a vuln-severity scoring tree, a model-tier selection chart, or any similar structured decision logic
- They have noticed Claude shortcutting past a tree's predicates and want to enforce the walk
- They want to convert tacit expertise (a written or whiteboard tree) into a portable artifact

## When NOT to use

Skip this skill and hand off when:

- The domain is open-judgment with no fixed tree (novelty review, design critique, taste calls) → use a brainstorming-style or premortem-style skill instead; tree-as-skill discipline does not fit
- The user wants a single rule, not a tree — write a `claude-code-meta/writing-deny-allow-rules` rule file instead
- The "tree" is actually a lookup table with no branching logic — that's a reference doc, not a skill; ship it as `reference/<topic>.md` inside an existing skill
- The user wants to encode imperative procedural code that already has no decision points — that's a tool/script, not a tree-as-skill (point them at `claude-code-meta/authoring-skill` for general skill authoring or at a script in `scripts/`)

## Quick start

User says: *"I have a decision tree for picking a statistical test — 1 vs 2+ groups, paired vs independent, parametric vs non-parametric. Package it as a skill that walks the tree."*

Skill response:

1. Confirm the tree structure: list every predicate (yes/no or categorical question), every internal node, every leaf action.
2. Choose the slug — gerund form, names the discipline (e.g., `selecting-statistical-test`).
3. In the SKILL.md Workflow section, write each predicate as a numbered step with explicit branches; each branch points to the next step or to a leaf action.
4. Per predicate, document the precondition — what data must be in hand before the predicate can be evaluated. If absent, the skill requests input rather than guessing.
5. Add an explicit anti-shortcut clause: the skill commits to walking predicates in order; it does not jump to a leaf because the user mentioned a leaf in their question.
6. Evals: write a happy-path scenario that walks the full tree end-to-end, an edge-case where one predicate is ambiguous, and an anti-trigger where the user names a leaf directly and the skill still walks the tree.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| tree_source | file path / pasted text / dictation | yes | — | The decision tree to encode. Diagrams, flowcharts, or a bulleted "if X then Y" list all work. |
| domain | string | yes | — | What the tree decides (e.g., "statistical test selection", "vuln severity scoring", "model-tier selection"). |
| predicate_inventory | list of predicates | yes | — | Every yes/no or categorical question in the tree. Used to scope per-predicate precondition documentation. |
| leaf_inventory | list of leaf actions | yes | — | Every terminal action the tree can recommend. Used to write the leaf-action descriptions and the eval coverage matrix. |
| cycle_handling | "none" \| "state-enrichment" \| "state-machine" \| "revisit-cap" | yes | — | If the tree has back-edges, which of the three documented options the skill will use. |

## Workflow

Copy this checklist into the response and check off items as the tree is converted:

```
Tree-to-skill conversion progress:
- [ ] Tree extracted: every predicate, internal node, leaf action listed
- [ ] Cycle check: is the graph a tree (no back-edges) or a DAG-with-loops (back-edges)?
- [ ] If cycles: pick state-enrichment, state-machine, or revisit-cap; document the choice
- [ ] Slug chosen — gerund form, names the discipline
- [ ] Workflow section: each predicate is a numbered step with explicit branches
- [ ] Per predicate: precondition documented (what data is required)
- [ ] Per leaf: deterministic action stated (no "use judgment to decide")
- [ ] Anti-shortcut clause: skill walks predicates in order, does not jump to a leaf
- [ ] Evals: happy-path (full tree walk), edge-case (ambiguous predicate), anti-trigger (user names a leaf)
- [ ] Lint clean
```

### Step 1 — Tree extraction

List every predicate and every leaf. The mental model: a tree is a finite set of decisions where each internal node has a question and each leaf has an action.

```
Predicates:
P1. How many groups? (1 / 2 / 3+)
P2. Paired or independent?
P3. Continuous or categorical?
P4. Normal? (Shapiro p)
P5. Equal variance? (Levene p)

Leaves:
L1. One-sample t
L2. Two-sample t (pooled)
L3. Two-sample t (Welch)
L4. Wilcoxon signed-rank
L5. Mann-Whitney U
... (continue until every path through the tree terminates at a leaf)
```

### Step 2 — Cycle check

A pure tree has no back-edges; every path terminates at a leaf. If your "tree" has a leaf that says "go back to P3 and re-evaluate", it is no longer a tree. Pick one of three options:

- **State-enrichment**: enrich each predicate with iteration state ("first pass / second pass / third pass"). The same predicate evaluated with different state is effectively a different node. Convert to a strict tree this way.
- **State-machine**: name explicit states (e.g., `gathering-data`, `evaluating-assumptions`, `running-test`, `interpreting-result`) and explicit transitions between them. Document each state's exit conditions.
- **Revisit-cap**: allow back-edges but cap the maximum number of revisits (e.g., max 3 loops); on cap-hit, the skill requests human input rather than looping indefinitely.

If none of these fit because the back-edge reflects genuine open-ended judgment, the underlying logic is not a tree and tree-as-skill discipline does not apply. Hand off to brainstorming or premortem (see When-NOT-to-use).

### Step 3 — Slug and structure

Pick a gerund-form slug that names the discipline (`selecting-statistical-test`, `triaging-vulnerability-findings`, `recommending-model-tier`). Run the general skill-authoring discipline (`claude-code-meta/authoring-skill`) for everything else (frontmatter, 11 H2 sections, eval-first ordering).

### Step 4 — Workflow section per predicate

Each predicate becomes a numbered step in the Workflow section. Example for a stats-test tree:

```markdown
### Step 1 — How many groups?

Predicate: count of independent groups in the design.
Precondition: study design must be explicit (the user must say "two groups" or
"three or more groups", or the data must reveal it).

- One group → go to Step 2 (one-sample family)
- Two groups → go to Step 3 (two-sample family)
- 3+ groups → go to Step 4 (ANOVA / Kruskal family)

### Step 2 — One-sample: is the mean compared to a known constant?

Predicate: the design specifies a constant for comparison (mu_0).
Precondition: the user must name mu_0 explicitly OR the protocol must include it.

- Yes → check normality (go to Step 2a)
- No → request input; the design is incomplete

### Step 2a — One-sample, normality check

Predicate: Shapiro-Wilk p > 0.05 (normal) or ≤ 0.05 (non-normal)?
Precondition: Shapiro-Wilk result in hand. If absent, run it; request input if no data.

- Normal → leaf L1: one-sample t
- Non-normal → leaf L<X>: Wilcoxon signed-rank against mu_0
```

Note the structure: every step has a precondition (what is needed to evaluate the predicate) and explicit branches (no implicit defaults).

### Step 5 — Anti-shortcut clause

Add an explicit reminder to the When-to-use or Workflow section:

> Walking discipline: the skill commits to checking predicates in the
> documented order. The skill does NOT jump to a leaf because the user mentioned
> a leaf in their question. If the user says "I want to run a Wilcoxon", the
> skill walks the tree from Step 1 to confirm Wilcoxon is the right leaf for
> the user's data, rather than skipping straight to a Wilcoxon recommendation.

This counters the failure mode where Claude pattern-matches on a leaf name and skips the predicate chain.

### Step 6 — Evals

Write the three required eval scenarios so they exercise the tree-walking discipline:

- **happy-path**: a query with clear predicate values that walks the tree end-to-end to a single leaf
- **edge-case**: a query where one predicate is ambiguous; the skill requests input rather than guessing
- **anti-trigger**: a query where the user names a leaf directly; the skill still walks the tree from Step 1 to confirm

The anti-trigger eval is the critical one for tree-as-skill discipline. It is the test that catches the "skipped to leaf" failure mode.

## Outputs

A complete walk-the-tree skill artifact:

```
skills/<track>/<gerund-slug>/
├── SKILL.md                    # 11 H2 sections, Workflow mirrors the tree
├── evals/
│   ├── 01-happy-path-full-walk.json
│   ├── 02-edge-case-ambiguous-predicate.json
│   └── 03-anti-trigger-named-leaf.json
└── reference/
    ├── tree-diagram.md         # optional: visual rendering of the tree
    └── leaf-actions.md         # optional: per-leaf detailed action descriptions
```

The Workflow section of the SKILL.md is a direct, traversal-order encoding of the tree.

## Failure modes

Known pitfalls in converting trees to skills and how this skill catches them:

- **Shortcut to leaf.** Claude pattern-matches a leaf name in the user's question and skips the predicate walk. Caught by: Step 5 anti-shortcut clause + the anti-trigger eval that exercises the failure mode directly.
- **Implicit default branch.** Predicate has Yes/No branches in the diagram but the skill omits the No branch, defaulting silently. Caught by: Step 4 requires every branch to be explicit.
- **Missing precondition.** Predicate is documented but the data needed to evaluate it is not; Claude guesses. Caught by: Step 4 per-predicate precondition requirement + eval scenarios that include cases where the precondition is absent.
- **Silent cycle.** Tree has back-edges that are unhandled; skill loops indefinitely or reaches a "leaf" that says "go back". Caught by: Step 2 cycle check + cycle-handling argument requires explicit choice.
- **Open-judgment domain forced into tree.** Author tries to encode novelty review or design critique as a tree; the predicates are not objectively checkable. Caught by: When-NOT-to-use rejection.
- **Tree-as-reference instead of as-skill.** Author writes a lookup table with no branching logic and calls it a tree skill. Caught by: When-NOT-to-use suggests `reference/<topic>.md` inside an existing skill is the right fit.

## References

- `reference/walk-the-tree-template.md` — copy-paste Workflow-section template for a tree-walk skill
- `reference/cycle-handling-options.md` — detailed walkthrough of state-enrichment, state-machine, and revisit-cap with examples
- RCS `claude-code-meta/authoring-skill` — general skill-authoring discipline (run alongside this one)
- RCS `ml-datasci/selecting-statistical-test` — production example of a walk-the-tree skill
- RCS `security/triaging-vulnerability-findings` — production example of a walk-the-tree skill in a different domain
- RCS `ml-datasci/recommending-model-tier` — production example of a walk-the-tree skill that uses revisit-cap

## Examples

### Example 1: Stats-test selection tree (happy-path)

Input: *"I have a decision tree for picking a stats test — 1 vs 2+ groups, paired vs independent, parametric vs non-parametric. Package it."*

Output: Skill extracts the tree's predicates (P1: group count; P2: paired/independent; P3: continuous/categorical; P4: normal/non-normal; P5: equal/unequal variance) and leaves (one-sample t, paired t, Wilcoxon signed-rank, Mann-Whitney U, etc.). Writes a SKILL.md slug `selecting-statistical-test`. Workflow section has one numbered step per predicate, each with explicit branches and precondition (e.g., P4 requires a Shapiro-Wilk result in hand). Adds anti-shortcut clause: the skill walks from Step 1 even when the user names a specific test in the question. Writes three evals: happy-path (paired + non-normal + small n → Wilcoxon signed-rank); edge-case (Shapiro borderline at 0.06 — request follow-up); anti-trigger (user says "run a t-test" — skill walks the tree first to confirm t-test is correct).

### Example 2: Tree with a back-edge (edge-case)

Input: *"My tree has a back-edge: if the test result is inconclusive (p between 0.05 and 0.10), the user should go back and collect more data, then re-walk. Can I still package as walk-the-tree?"*

Output: Skill flags that the back-edge breaks the strict tree model — the graph is a DAG with loops. Walks the three options:

- **State-enrichment**: add an iteration counter to every predicate. First pass evaluates predicates against initial data; second pass against augmented data; etc. Each iteration is effectively a different node. Tree-walk discipline still applies.
- **State-machine**: name states like `initial-evaluation`, `inconclusive-result`, `collecting-additional-data`, `re-evaluation`. Each state has exit conditions. The skill walks state transitions rather than tree edges.
- **Revisit-cap**: allow back-edges but cap at 3 loops; on cap-hit, request human input rather than looping forever.

Recommends state-enrichment for this case because the back-edge has a clear semantic (re-evaluation with more data) that maps cleanly to an iteration counter. Cross-references brainstorming for cases where the back-edge reflects open judgment with no clear state.

### Example 3: Open-judgment domain rejection (anti-trigger)

Input: *"Help me package my novelty-review approach (deciding if a paper's contribution is actually new) as a walk-the-tree skill."*

Output: Skill answers no — novelty review is open-judgment. The predicate "is this novel?" is the entire question, not a step in a tree. There is no objectively checkable yes/no question that resolves the decision; novelty depends on context, audience, and the reviewer's reading of related work. Hands off to `workflow/running-adversarial-premortem` (which structures judgment without forcing a tree) or recommends a brainstorming-style skill where the reviewer's judgment is the deliverable. Notes that walk-the-tree discipline only fits when predicates are objectively checkable and leaf actions are deterministic — novelty review is neither.

## See also

- `claude-code-meta/authoring-skill` — general skill-authoring discipline (run alongside this one)
- `claude-code-meta/writing-deny-allow-rules` — for single-rule policy, not a tree
- `workflow/running-adversarial-premortem` — for open-judgment domains that resist tree encoding
- `workflow/auditing-mathematical-claims` — sibling discipline that structures audit without a tree

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
