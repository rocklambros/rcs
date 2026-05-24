# Σ (sigma) score

What the number in every catalog row means, where it came from, and what it does and does not tell you.

## The short answer

Σ is a return-on-investment estimate on a 1-to-20 scale, assigned to a skill at the time it was triaged for inclusion in RCS. It approximates *how often the gap the skill closes appears in real practice* times *how costly it is to get the gap wrong without the skill*. Higher Σ means higher expected impact across more readers.

It is not a quality score. A Σ 7 skill is not a worse skill than a Σ 17 skill. It is a smaller-audience skill or a lower-cost-failure skill.

## How Σ is computed

Roughly:

```
Σ ≈ frequency × cost-of-getting-it-wrong
```

Both terms are scored on a 1-to-5 scale. The product lands in 1-25; the result is rounded into a 1-20 catalog-visible range (the top end of the cell is collapsed because no real skill saturates both axes).

### Frequency (how often the gap appears)

How often, across the projects an RCS-typical practitioner works on, does this specific gap come up?

| Frequency score | Interpretation |
|---|---|
| 5 | Every project of this kind hits this gap. Universal |
| 4 | Most projects of this kind hit this gap |
| 3 | Common but not universal; depends on stack or domain |
| 2 | Niche but recurring; specific to certain workflows |
| 1 | Rare; appears in edge cases |

### Cost of getting it wrong

If the practitioner does not have this discipline and proceeds without it, how bad is the result?

| Cost score | Interpretation |
|---|---|
| 5 | Catastrophic. Misleading conclusion in a high-stakes domain (security, regulated ML, clinical), or silent bias that ships to production |
| 4 | Significant. Wrong recommendation, wasted compute, or non-reproducible result that costs days |
| 3 | Real but recoverable. Wrong on first pass, caught on review |
| 2 | Annoying. Stylistic or efficiency loss |
| 1 | Cosmetic. The reader can fix it post-hoc |

A skill that closes a gap appearing in every project (frequency 5) AND causes a catastrophic failure when missed (cost 5) lands at Σ 20. That is `enforcing-seed-hygiene`: every ML project hits the cross-platform determinism gap, and missing it produces unreproducible results that have caused real published-paper retractions.

A skill that closes a gap appearing in a small audience (frequency 2) with a recoverable cost (cost 3) lands at Σ 6-8. That is `auditing-rlhf-reward-hacking` (Σ 7): only RLHF-trained models hit this, and reward hacking is usually caught in eval before deployment.

## Why Σ exists

When triaging which gaps to encode as skills, finite author time forces ranking. Σ makes the ranking explicit and revisitable. A skill with Σ 18 is worth authoring before a skill with Σ 9, all else being equal.

Σ also tells a reader where to invest attention. The [root README](../../README.md) catalog teaser shows the top 10 by Σ; those are the skills with the highest expected payoff for the largest audience. A reader with limited time should install those first.

## What Σ does not tell you

- **It does not predict whether the skill applies to YOU.** A Σ 20 skill is universal across the RCS audience, but your project might not be in that audience. `enforcing-seed-hygiene` (Σ 20) is irrelevant if you do not write ML code.
- **It does not measure how well the skill is written.** Quality is measured by eval scores. Σ is about audience and stakes
- **It does not change over time.** Σ was assigned during the original triage. If a gap becomes more or less common in practice, the Σ on the catalog row may drift from reality. Future RCS releases may re-triage; the original Σ stays as a historical anchor in the meantime
- **It is not a confidence interval or a statistical measurement.** It is a triage judgment

## How Σ was actually computed in practice

The first 16 skills (the v1 catalog) were triaged in a single brainstorm session that produced rough scores for both axes. Subsequent skills (v2 through v7) were Σ-assigned by hand against the v1 anchors. The grading is fuzzy by design; Σ is a sort key, not a measurement.

Two Σ-12 skills are not measurably equal in impact. They are within the same band. The bands are roughly:

- **Σ 17-20**: hit-everyone, high-cost gaps. The catalog's flagship skills
- **Σ 13-16**: track-specific recurring gaps. Most of the catalog
- **Σ 9-12**: niche or lower-cost gaps. Still worth shipping, narrower audience
- **Σ 7-8**: specialty skills for specific stacks or contexts

A skill in the 7-8 band is not "less good." It is more specialized. A reader in its audience may rank it as their personal Σ 20.

## Why bother with a numeric score at all

A binary "include / exclude" decision is too coarse for triage when the candidate pool is in the hundreds. A 1-20 scale lets the author batch-rank candidates and stop at the cutoff that fits available author time. Once the skill ships, the number lets readers sort the catalog and find the high-payoff entries quickly.

The alternative would be no triage and ad-hoc ordering. That would produce a catalog where the first skills a reader sees are whatever the author thought of first, not whatever is most useful.

## Σ in the catalog

Every shipped skill carries its Σ in three places:

- The frontmatter (not lint-enforced; informational)
- The track-README shipped table (visible to readers browsing by track)
- The root README catalog teaser and `skills/README.md` cross-track index

The cross-track index is roughly Σ-sorted within each batch wave. The root README's top-10 teaser is strictly Σ-sorted. To find the highest-Σ skills overall, use the teaser.
