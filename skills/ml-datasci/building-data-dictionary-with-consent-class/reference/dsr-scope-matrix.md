# DSR Scope Matrix (Consent Class × DSR Type)

For each (consent class, DSR type) pair, name the default verdict: in-scope / partial / out-of-scope. Use as the default for the dictionary row, then override per-field for documented carve-outs.

## GDPR

| Consent class | Access (Art. 15) | Portability (Art. 20) | Deletion (Art. 17) | Rectification (Art. 16) | Restriction (Art. 18) | Objection (Art. 21) |
|---|---|---|---|---|---|---|
| **collected** | in-scope | in-scope | in-scope (subject to retention overrides) | in-scope | in-scope | in-scope |
| **inferred** | in-scope | partial (only if the user provided the input that drove the inference) | in-scope | partial (correct only via correcting the input then re-inferring; the user cannot directly edit the inferred value) | in-scope | in-scope (Art. 22 if used for automated decisions with legal or similarly significant effect) |
| **derived** | in-scope | in-scope (the user has a right to a copy of derived data computed from their input) | in-scope; cascades to all downstream copies | partial (correct via correcting the upstream; the derivation re-runs) | in-scope | in-scope |
| **public** | in-scope (the user has the right to know you hold a copy) | partial (provide a copy or the source URL) | out-of-scope (you cannot delete from the public source; you can delete your local copy on request) | partial (correct your local copy; you cannot correct the public source) | in-scope (you can restrict processing of your local copy) | in-scope |
| **synthetic** | out-of-scope IF the synthesis was provably independent of the user's real data; otherwise inherit the upstream class until proven otherwise (see `consent-class-decision-tree.md` trap 4) | same | same | same | same | same |

## CCPA / CPRA highlights

CCPA frames rights as: right to know, right to delete, right to correct, right to opt-out-of-sale/sharing, right to limit use of sensitive PI. Map to GDPR matrix as:

- Right to know ≈ access; same scope as GDPR access
- Right to delete ≈ deletion; same scope as GDPR deletion (CCPA has a narrower set of retention carve-outs, but the per-consent-class verdicts are the same)
- Right to opt-out-of-sale/sharing ≈ objection; applies to fields shared with third parties for value
- Right to limit sensitive PI ≈ restriction; applies to fields tagged as sensitive_special_category

## Cascade rule

When a field is in-scope for deletion, every downstream copy in `propagated_to` is also in-scope. The cascade is not optional; failing to cascade is the single most common DSR failure mode and produces "ghost data" that survives an apparently-successful deletion.

Verify the cascade by:

1. Listing `propagated_to` for every in-scope field
2. For each downstream table / index / cache / checkpoint, write a deletion runbook that names how to remove or re-derive without the deleted upstream
3. Automate the cascade where possible (foreign-key ON DELETE CASCADE, scheduled re-embedding jobs, model-checkpoint refresh)

## Sensitive-attribute overlay (GDPR Article 9)

Special categories — health, race, ethnic origin, political opinion, religion, trade union, genetic, biometric, sex life / sexual orientation — get a stricter overlay regardless of consent class:

- Default lawful basis ≠ legitimate-interest; requires explicit consent or a specific Article 9(2) carve-out
- Access / portability requests are mandatory same-day-acknowledged; deletion requests have a 30-day cap (vs the standard 30-day with possible 60-day extension)
- Sharing with third parties is severely restricted

The dictionary's `sensitive_special_category` boolean is the trigger for this overlay; legal review is required before processing begins, not after a DSR arrives.

## Retention-override priority

When a field is in-scope for deletion under a consent class but a documented retention override applies (statutory retention, ongoing litigation hold, fraud investigation), the override wins for the duration of the override and the field is then deleted. Record the override in the dictionary row's `retention_override` column with the legal basis, start date, and review date.

Common overrides:

- Tax law (typically 7 years on financial records)
- Litigation hold (until matter closed)
- Fraud investigation (until investigation concluded)
- Regulatory recordkeeping (varies by sector)

A retention override does NOT remove the field from the DSR access scope — the user still has the right to know you hold the data and why.
