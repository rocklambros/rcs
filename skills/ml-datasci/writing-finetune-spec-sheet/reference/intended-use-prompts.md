# Intended-use and out-of-scope-use checklist

This reference is the prompt-checklist invoked by Step 7 of `writing-finetune-spec-sheet`. The skill asks the user about each item; the user's answer goes into the spec sheet's Section 7 (primary or out-of-scope, or "not applicable to this deployment").

The checklist is deliberately broad. Most fine-tunes will mark most of these as out-of-scope; the goal is to make the deployer's life easier by enumerating the spaces the model was NOT designed for.

## Domain-specific deployment questions

### Healthcare

- [ ] Used for clinical diagnosis or treatment recommendations?
- [ ] Used for triage or routing decisions affecting patient care?
- [ ] Used to interpret medical imagery or lab results?
- [ ] Used in any HIPAA-covered context (with PHI in prompts)?
- [ ] Used by patients directly without clinician oversight?
- [ ] If any of the above: was an eval conducted in that specific clinical context, with appropriate domain experts, and was the regulatory pathway (FDA SaMD, EU MDR) considered?

### Legal

- [ ] Used to provide legal advice to consumers?
- [ ] Used to draft contracts, wills, or other binding documents?
- [ ] Used in jurisdiction-specific contexts where local statutes matter?
- [ ] Used to interpret case law or precedent for litigation purposes?
- [ ] Used by self-represented litigants without attorney review?

### Financial

- [ ] Used to provide investment advice or recommendations?
- [ ] Used to make credit / lending / underwriting decisions?
- [ ] Used in algorithmic trading or market-making?
- [ ] Used to evaluate creditworthiness, employment-screening, or housing access?
- [ ] If any of the above: ECOA / fair-lending / anti-discrimination evaluation completed?

### Safety-critical systems

- [ ] Used in vehicles, robotics, industrial control, or other physical-actuation systems?
- [ ] Used in medical devices?
- [ ] Used in emergency-response or 911-adjacent contexts?
- [ ] If any of the above: domain safety analysis (FMEA / HAZOP) completed?

### Demographic and protected-class

- [ ] Used in contexts involving minors (under 13, under 16, under 18 — specify)?
- [ ] Used in contexts involving protected classes where output may differentially affect them?
- [ ] Used in contexts where the model's outputs may stereotype, demean, or harm specific groups?
- [ ] Was a fairness evaluation conducted (link to `ml-datasci/auditing-model-fairness` if so)?

### Adversarial and red-team

- [ ] Used in user-facing contexts where adversarial prompts (jailbreaks, prompt injection) are expected?
- [ ] Was a prompt-injection eval conducted (link to `security/running-prompt-injection-eval` if so)?
- [ ] Is the model deployed behind a content-filter, output-moderation, or human-review layer?

### Language and locale

- [ ] What languages was the model trained on? (List explicitly; the absence of a language is itself a limitation.)
- [ ] Is the model deployed in a locale outside the training-language mix? If so, expect degraded quality and document it explicitly.
- [ ] Cultural-context expectations: was the model trained on data reflecting a specific cultural context that may not generalize?

### Privacy and surveillance

- [ ] Used to identify individuals from text (deanonymization)?
- [ ] Used in surveillance, mass-monitoring, or law-enforcement contexts?
- [ ] Used in contexts where the user is not aware that an AI is producing the output?
- [ ] Used to generate content impersonating a specific real person?

### Critical-infrastructure and security

- [ ] Used in authentication, authorization, or access-control decisions?
- [ ] Used to detect or respond to security incidents?
- [ ] Used to generate code that runs in production systems?
- [ ] If any of the above: was a security review conducted? Was an adversarial-robustness eval conducted?

## How to use this checklist

The skill walks the user through each section. For each item:

- **Yes, intended:** add to `primary_use_cases` with a one-line rationale
- **Yes, but only with constraints:** add to `primary_use_cases` with the constraint stated, OR to `out_of_scope_use_cases` if the constraints exclude common deployment patterns
- **No, not intended:** add to `out_of_scope_use_cases`
- **Not applicable to this deployment:** skip; the section will not include it

The spec sheet's Section 7 lists every item the user marked as either primary or out-of-scope. The user can edit the resulting lists for clarity. Items marked "not applicable" do not appear.

## Default out-of-scope clauses for a public publication

For `audience="public"`, the skill includes these default out-of-scope clauses unless the user explicitly marks them as primary:

- Medical, legal, or financial advice to consumers
- Decisions affecting access to credit, employment, housing, or insurance
- Identification or impersonation of specific real persons
- Safety-critical actuation systems
- Surveillance or mass-monitoring without legal authority and notice
- Use against minors without parental / institutional consent and oversight
- Use in jurisdictions where the model's training data violates local AI / data-protection regulation

These defaults are not arbitrary; they reflect categories where downstream harm is well-documented in the AI-incident literature. The user can override any default with an explicit "this fine-tune is intended for [specific exception]" — but the override is recorded, not silent.
