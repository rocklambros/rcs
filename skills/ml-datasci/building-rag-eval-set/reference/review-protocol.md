# Human-review protocol

The step-4 review pass in `building-rag-eval-set`. Every Q-A — including human-authored ones — gets reviewed before entering the golden set.

## Per-row review checklist

For each candidate Q-A, the reviewer fills in:

| Field | What the reviewer checks |
|---|---|
| `reviewed_by` | Self-identifier (must match one of the `reviewers` input to the skill) |
| `reviewed_at` | ISO 8601 timestamp; auto-stamped by the review tool |
| `ground_truth_verified` | The answer text matches what the source span actually says — true / false |
| `difficulty` | Difficulty band assigned: easy / medium / hard |
| `ambiguity_flag` | Query is ambiguous (multiple defensible answers exist) — true / false |
| `notes` | Free-text (e.g., "answer depends on date range; flagged for revisit") |

Rule: `ground_truth_verified = false` blocks the row from entering the golden set. The row stays in the candidate pool until either it's fixed or it's discarded.

## Difficulty calibration

Reviewers can disagree on difficulty bands. The skill enforces:

| Pattern | Action |
|---|---|
| Single reviewer per row | Accept their difficulty as-is; flag for spot-check if their distribution skews (e.g., >70% of their reviews are "easy") |
| Two reviewers per row, agree | Accept |
| Two reviewers per row, disagree by one band (easy vs medium, medium vs hard) | Accept the harder band as the final assignment |
| Two reviewers per row, disagree by two bands (easy vs hard) | Flag for a third-reviewer tiebreaker; do not auto-resolve |

The reviewer-attribution table in step 6's output reports per-reviewer counts and per-reviewer ambiguity-flag rate as calibration sanity checks. If one reviewer flags 80% ambiguous and another flags 5%, recalibrate (re-discuss what "ambiguous" means in this domain).

## When to discard a candidate

A reviewer can mark a candidate for discard if:

- The query is malformed (typo, ungrammatical, off-domain)
- The answer is wrong AND cannot be fixed (the source span doesn't actually answer the query)
- The Q-A is a near-duplicate of another candidate (mark the duplicate for discard, keep the better-phrased one)
- The query asks for information that has changed since the source doc was authored (stale ground truth)

Discarded candidates are recorded in `eval-set/discarded.jsonl` with the reason. This prevents the same bad candidate from being re-drafted by an LLM on a later expansion.

## Reviewer onboarding

For new reviewers, run 5-10 already-reviewed rows past them blind and check inter-rater agreement on `difficulty` and `ground_truth_verified`. Disagreement above ~20% suggests the review protocol needs documenting more explicitly for this domain before the new reviewer starts on fresh candidates.

## What review will NOT catch

- A systematic bias in the LLM drafter (if the drafter always avoids hard multi-hop questions, the reviewer can only review what was drafted; the coverage matrix in step 1 is the gate that catches this)
- A corpus-wide ground-truth error (if the source doc itself is wrong, the reviewer marks `ground_truth_verified=true` against the wrong document; this is a corpus problem, not an eval-set problem)
- Ambiguity that the reviewer also missed (if both the drafter and the reviewer are domain experts who share a mental model that excludes a defensible alternative, the row enters as unambiguous when it isn't — caught only by downstream eval failures or by independent re-review)
