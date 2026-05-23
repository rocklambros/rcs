---
name: building-data-dictionary-with-consent-class
description: >
  Builds a per-field data dictionary annotated with a consent class — collected /
  inferred / derived / public / synthetic — alongside the usual schema fields
  (name, type, nullability, range, semantic class). Drives Data-Subject-Request
  (DSR) readiness: for any incoming "tell me what you have about me / delete
  it / export it" request, the dictionary names which fields are in scope, which
  must be propagated to derived stores, and which are safe to retain under
  legitimate-interest or public-domain carve-outs. Triggers when a project
  ingests user-related data and the user is preparing for GDPR / CCPA / HIPAA
  / DSR readiness, when a privacy review asks "what consent class is each
  field?", or when an ML pipeline derives features from PII and the derived
  features need a consent classification of their own. Refuses to classify a
  field as "public" without a documented source URL and access timestamp, and
  refuses to skip the inferred / derived classes (which are the easy fields to
  forget in a DSR sweep).
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-engineer
  - data-scientist
  - security-eng
  - ml-engineer
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - llm-toxicity-visual-analysis
  - genai_agentic_incidents
last-updated: 2026-05-23
---

# Building a Data Dictionary with Consent Class

## When to use

Trigger this skill when:

- A project is ingesting user-related data (customers, patients, employees, research subjects) and the team needs a per-field data dictionary that records both schema and **consent class** — collected from the user with consent, inferred by a model, derived by an aggregation, public-domain, or synthetic
- The user is preparing for GDPR Article 30 records of processing, CCPA disclosure obligations, HIPAA-data-use-agreement readiness, or any Data Subject Request (DSR) workflow (access / portability / deletion / rectification)
- A privacy / legal review is asking "what is the lawful basis and consent class for each field?"
- An ML pipeline is about to derive new features (embeddings, predictions, risk scores) from user data and the derived features need their own consent classification, not just inheriting the upstream
- A vendor questionnaire or DPIA (data protection impact assessment) requires a field-level inventory
- Keywords: data dictionary, consent class, DSR, Data Subject Request, GDPR Article 15 / 17 / 20, lawful basis, derived data, inferred data, public source, data lineage, processing inventory

## When NOT to use

Skip this skill and hand off when:

- The dataset is **pre-design / not yet collected** — at the design stage, write a data-collection consent form first; the dictionary is a downstream artifact of a real schema
- The dataset is **fully internal / non-user-related** (server logs of internal services, infrastructure metrics, model hyperparameters) — DSR has no purchase; the lighter `workflow/auditing-data-quality` data dictionary is enough
- The user wants a **technical-only** schema doc (column types, indexes, foreign keys) without privacy semantics — use a database tool (dbt docs, OpenAPI schema generator); this skill's added value is the consent class
- The dataset is a **third-party benchmark** (UCI, Hugging Face open datasets) — the consent class for every field is "public-domain"; the audit is one row of paperwork, not the full workflow
- The team needs a **formal DPIA narrative document** rather than a field-level inventory — this skill produces the inventory; the DPIA narrative wraps it
- The request is to **fulfill** an active DSR (right-now deletion / export) rather than build the inventory that supports future DSRs — different skill (planned: `security/fulfilling-dsr-request`)

## Quick start

User: "We have a SaaS product with 200k user records across 4 tables (users, sessions, predictions, audit_log). I need a data dictionary that tells legal and the DPO what each field is and whether it's collected directly, inferred, or derived, so we can answer GDPR DSRs in under 30 days. Help me build it."

Response: walks the 6-step workflow to produce a per-field row with this structure:

```
| field | table | type | nullable | description | semantic class | consent class | lawful basis | sensitive | DSR scope | propagated to |
```

Consent class is the load-bearing column. Five values: `collected`, `inferred`, `derived`, `public`, `synthetic`. Each row also names the derived / propagated downstream tables so a DSR sweep does not miss the cascade.

See `reference/consent-class-decision-tree.md` for the classification flowchart and `reference/dsr-scope-matrix.md` for which scope each consent class lands in for each DSR type.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `tables` | list[str] or schema export | yes | — | The tables / collections / DataFrames to inventory. Skill accepts SQL `INFORMATION_SCHEMA` exports, dbt manifest, Pydantic models, JSON Schema, or a directory of CSV / Parquet samples. |
| `data_source` | str | yes | — | Where the data came from — "direct collection from the user", "OAuth federated identity", "purchased third-party broker", "scraped public web", "generated by model X", "joined from internal system Y". Drives initial consent-class assignment. |
| `regulatory_scope` | list[str] | yes | — | Which regimes apply — GDPR, CCPA, HIPAA, COPPA, PIPEDA, FERPA, or others. Drives the DSR scope matrix and lawful-basis prompts. |
| `purpose_list` | list[str] | recommended | — | The processing purposes (account management, product analytics, marketing, model training, fraud detection). Each field must map to ≥ 1 purpose; orphan fields are a finding. |
| `existing_dictionary` | path | no | — | If a partial dictionary exists, the skill amends rather than rebuilds. Required for incremental schema-evolution audits. |
| `redact_examples` | bool | no | `true` | Whether the output redacts example values that look like PII (rather than echoing raw rows). Default true to keep the dictionary itself non-sensitive. |

## Workflow

Copy this checklist into the response and check items off as each step completes:

```
Data-dictionary-with-consent-class build progress:
- [ ] 0. Pre-flight: tables enumerated, data_source documented, regulatory_scope named, purpose_list complete
- [ ] 1. Schema extraction per table (name, type, nullable, foreign key, default)
- [ ] 2. Semantic class per field (ID / categorical / continuous / ordinal / text / datetime / boolean / blob)
- [ ] 3. Consent class per field via the decision tree (collected / inferred / derived / public / synthetic)
- [ ] 4. Lawful basis per consent class + purpose pairing (consent / contract / legal-obligation / vital-interest / public-task / legitimate-interest)
- [ ] 5. DSR scope tagging: for each DSR type (access / portability / deletion / rectification / restriction / objection), in-scope / out-of-scope / partial
- [ ] 6. Lineage / propagation: for each field, where it is copied / aggregated / embedded into; cascade tables get the same DSR scope
- [ ] 7. Sensitive-attribute flag (special category per GDPR Article 9 — health, race, sexual orientation, religion, biometric, genetic)
- [ ] 8. Orphan check: every field maps to ≥ 1 purpose; every purpose has ≥ 1 field
- [ ] 9. Sign-off block: data owner + DPO + last-reviewed date per table
```

### Step 0: Pre-flight

Refuse if:

- `data_source` is vague ("we have a dataset") — the source is the load-bearing input for consent class
- `regulatory_scope` is empty — the DSR scope matrix has no anchor without it
- Tables are listed but their column names are not accessible (schema-only, no introspection allowed) — escalate to a database admin to pull schema

### Step 1: Schema extraction

Per field: name, type (incl. nested types for JSON / arrays), nullable, default, foreign-key targets. From `INFORMATION_SCHEMA`, dbt manifest, Pydantic models, or pandas dtypes.

### Step 2: Semantic class

Independent of consent class. ID (user_id, session_id), categorical (country, plan_tier), continuous (revenue, latency), ordinal (severity_band), text (free-form), datetime, boolean, blob (file references). High-cardinality "categorical" with > 100 unique values is suspect — likely free text mis-typed; flag for review.

### Step 3: Consent class via the decision tree

For each field, walk `reference/consent-class-decision-tree.md`:

- **`collected`** — the user directly provided the value (form input, OAuth scope, file upload). Default for `data_source = "direct collection"`.
- **`inferred`** — a model or rule produced the value from other fields (predicted risk score, gender inferred from name, intent classification from message). Easy to miss in DSR sweeps because the field "wasn't given by the user". Inferred about a user is still about the user.
- **`derived`** — a deterministic aggregation / transformation of other fields (lifetime value = sum of transactions; embedding = encoder(user_text)). Distinct from inferred because reversible / re-computable; still in DSR scope.
- **`public`** — from a documented public source (Companies House registry, public GitHub profile, government open data). Requires a documented source URL and access timestamp; otherwise → collected.
- **`synthetic`** — generated without a real-user source (Faker output, SDG output trained on public-only sources). Synthetic fields about a real user (e.g. SDG fit on the user's real data) inherit the upstream consent class — NOT synthetic.

Refuse to classify as `public` without a URL + timestamp. The most common privacy failure here is "well, the user's email is on their public website" with no documentation; that's `collected`, not `public`.

### Step 4: Lawful basis per consent class + purpose

For each `(field, purpose)` pair, name the lawful basis. GDPR has six; CCPA has different framing but similar economic shape. The skill prompts for one of `consent / contract / legal-obligation / vital-interest / public-task / legitimate-interest`. Flag any pair where the lawful basis is ambiguous; do not default to "legitimate-interest" silently.

### Step 5: DSR scope tagging

For each field × DSR type, tag in-scope / out-of-scope / partial. See `reference/dsr-scope-matrix.md`. Common surprises:

- Inferred fields are in-scope for access and deletion under GDPR Article 15 / 17 (the user has the right to know what was inferred about them)
- Derived fields are in-scope for deletion but may stay in aggregated form (k-anonymized cohort metrics survive deletion of any single member)
- Public fields are out-of-scope for deletion (you cannot delete public data) but in-scope for access (the user has the right to know you hold a copy)
- Synthetic fields are out-of-scope if the synthesis was provably independent of the user's real data — but see consent-class rules above

### Step 6: Lineage / propagation

For each field, list every downstream table / index / cache / embedding / model checkpoint that copies, aggregates, or encodes the field. Cascade DSR scope: if the upstream field is in-scope for deletion, so is every copy. This is the step that catches "we deleted the user from `users` but forgot the embedding in `user_embeddings`" — the single most common DSR failure mode.

### Step 7: Sensitive-attribute flag

Tag GDPR Article 9 special categories — health, race, ethnic origin, political opinion, religion, trade union membership, genetic, biometric, sex life / sexual orientation. Sensitive attributes require explicit consent OR a specific carve-out; flag every Article 9 field for legal review even when the lawful basis seems clear.

### Step 8: Orphan check

- Every field must map to ≥ 1 purpose. Orphan fields are findings — collected but not used means an over-collection violation under GDPR Article 5(1)(c) data minimization
- Every purpose must have ≥ 1 field. Purposes with no fields are documented-but-not-implemented; flag for cleanup

### Step 9: Sign-off

Each table gets: data owner (engineer or product manager responsible), DPO sign-off (date), last-reviewed date. Without sign-off the dictionary is informational, not authoritative; a DSR review cannot rely on an unsigned dictionary.

## Outputs

The primary output is a per-field row in a Markdown / CSV / Parquet dictionary file:

| field | table | type | nullable | description | semantic_class | consent_class | lawful_basis | sensitive_special_category | dsr_access | dsr_portability | dsr_deletion | dsr_rectification | propagated_to | purposes | data_owner | dpo_signoff_date |

Plus three supporting documents:

1. **Orphan-fields report** — fields with no purpose mapping (data-minimization finding)
2. **Cascade map** — graph of field → downstream copies, for DSR sweep automation
3. **Sign-off ledger** — per-table data owner + DPO date

## Failure modes

- **"Public" without source documentation** — Caught by step 3 refusing to classify as public without URL + timestamp.
- **Inferred fields silently dropped from the dictionary** — Inferred-about-a-user fields are the easiest to miss because they were never explicitly collected. Caught by step 3 explicitly enumerating inferred/derived classes and step 5 putting them in DSR scope.
- **Derived fields treated as not-about-the-user** — A user embedding is still about the user. Caught by step 3 and step 6 cascade.
- **Lineage gaps (downstream copies missed)** — The largest DSR-failure class. Caught by step 6 requiring an explicit propagated_to list per field; orphan downstream tables flagged.
- **Default lawful basis "legitimate-interest" everywhere** — Convenient and wrong. Caught by step 4 explicit prompting per pair and flagging ambiguous cases for legal review, not silent defaulting.
- **Article 9 sensitive attributes missed** — Caught by step 7 explicit flag with legal review trigger.
- **Synthetic-but-derived-from-real misclassified as "synthetic"** — Synth from real-data fits is NOT synthetic for consent purposes; hand off to `auditing-synthetic-data-leakage`. Caught by step 3 explicit guard.
- **Over-collected orphan fields** — Caught by step 8 orphan check requiring every field to map to a purpose.
- **Stale dictionary** — Caught by step 9 sign-off requiring a `last-reviewed` date; recommend revision when schema changes are merged.

## References

- `reference/consent-class-decision-tree.md` — the per-field flowchart for collected / inferred / derived / public / synthetic
- `reference/dsr-scope-matrix.md` — DSR-type × consent-class matrix with in-scope / out-of-scope / partial verdicts
- [GDPR Article 5 (principles)](https://gdpr-info.eu/art-5-gdpr/) — data minimization (1.c), accuracy (1.d), accountability (2)
- [GDPR Articles 15-22 (data subject rights)](https://gdpr-info.eu/chapter-3/) — access, portability, deletion, rectification, restriction, objection, automated decisions
- [GDPR Article 9 (special categories)](https://gdpr-info.eu/art-9-gdpr/) — health, biometric, genetic, etc.
- [CCPA / CPRA disclosures](https://oag.ca.gov/privacy/ccpa) — California analogue with different lawful-basis framing
- [HIPAA 164.514 De-identification Standard](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html) — relevant when consent class = `derived` on protected health information

## Examples

### Example 1: SaaS product, 4 tables, mixed consent classes (happy-path)

Input: "200k-user SaaS, 4 tables: users (auth + profile), sessions (clickstream), predictions (model outputs per user), audit_log (admin actions on user records). Regulatory scope: GDPR + CCPA. Purposes: account management, product analytics, model training, security."

Output: skill produces ~80 field rows across the 4 tables. `users.email` → collected / consent / GDPR-Article-15-in-scope / propagated to `audit_log.actor_email`. `predictions.churn_score` → inferred / legitimate-interest with named balancing test / in-scope for access and deletion / propagated to `predictions_history`. `users.referrer_url` → derived from HTTP header / contract / in-scope for access only / not Article 9. `users.crm_lifecycle_stage` (sourced from a third-party marketing tool) → flagged as ambiguous between collected and inferred; sent for clarification. Orphan-fields report names 3 columns with no purpose mapping → data-minimization findings.

### Example 2: ML-derived embedding field, inferred-vs-derived gray area (edge-case)

Input: "We compute a 256-d embedding per user from their support-ticket text. We use it for support-routing predictions. What consent class is `user_embedding`?"

Output: Skill walks the decision tree. The embedding is computed from text the user provided (collected), so the upstream is collected. The embedding itself is `derived` (deterministic transformation of user input via the encoder), NOT inferred (no learned mapping to a label). DSR scope: in-scope for deletion (cascades from the upstream text). In-scope for access — the user has a right to know that an embedding exists, though they probably don't want the 256 raw floats; the skill suggests reporting "we hold a numerical representation of your support tickets used for routing" rather than the vector itself. Propagated_to: vector index, routing-prediction cache, model-training corpus snapshots. Recommends a periodic re-embedding cron when the encoder version changes — and a DSR-deletion job that purges every snapshot, not just the latest.

### Example 3: Dataset is not yet collected (anti-trigger)

Input: "We're designing a new product feature. We have a wireframe but no data has been collected yet. Build us a data dictionary with consent classes."

Output: Skill explains that a data dictionary is a downstream artifact of a real schema, not a design tool. At the pre-collection stage, the right outputs are (a) a data-collection consent form draft for legal review, (b) a planned-schema sketch with the consent class **intended** for each field (so the implementation can be checked against the intent later), (c) a privacy impact assessment outline. Hands off to a privacy-by-design workflow rather than running the full 9-step dictionary build on a schema that does not exist yet. Does NOT generate fictional dictionary rows.

## See also

- `ml-datasci/auditing-synthetic-data-leakage` — required when any field has `consent_class = synthetic` derived from real user data
- `ml-datasci/auditing-synthetic-data-utility` — sibling for synth datasets that the dictionary lists
- `workflow/auditing-data-quality` — the lighter, non-privacy dictionary for internal / non-user data
- `workflow/validating-temporal-fields` — required pre-step on any datetime field; year-fallback bugs leak into DSR access reports
- `security/scrubbing-PII-with-policy` (planned) — operationalizes the dictionary into a redaction policy
- `security/fulfilling-dsr-request` (planned) — uses this dictionary as input to execute access / portability / deletion

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-5, skill 3) via PRAGMATIC discipline
