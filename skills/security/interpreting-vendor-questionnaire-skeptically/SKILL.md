---
name: interpreting-vendor-questionnaire-skeptically
description: >
  Reads a third-party security questionnaire response (SIG, CAIQ, SOC 2 attestations,
  custom security review) skeptically and produces a structured findings report flagging
  hedge words, missing artifacts, internal contradictions, scope mismatches, attestation
  staleness, and answers that cannot be verified from the evidence provided. Use when a
  procurement, security, or risk team is reviewing a vendor's questionnaire response
  before contract signature, when an existing vendor's annual re-attestation has arrived,
  when an AI vendor (LLM API, AI-coding tool, embedded ML feature) is being onboarded, or
  when leadership has been told "the vendor is compliant" and wants a real read. Refuses
  to declare a vendor "approved" — produces evidence-tied findings, not a go / no-go
  verdict.
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - grc
  - procurement
  - executive
evidence:
  - claude-secure-coding-rules
  - mac-harness-foundation-threat-model
  - rcap-c2m2-third-party-controls
last-updated: 2026-05-23
---

# Interpreting a Vendor Security Questionnaire Skeptically

> **Findings, not verdicts.** This skill produces a structured findings report for the
> reviewer. It does NOT certify a vendor as "approved", "compliant", or "low-risk" —
> those are decisions for an accountable risk owner with knowledge of the contract,
> the data flows, and the org's risk appetite. The skill's job is to surface what the
> response says, what it does not say, and where the two diverge from what was claimed.

## When to use

Trigger this skill when a vendor security questionnaire response is in hand and needs a
skeptical read, and one of:

- A new vendor is in procurement and has returned a Standardized Information Gathering
  (SIG) Lite / SIG Core, a Consensus Assessments Initiative Questionnaire (CAIQ), a
  SOC 2 Type 1 or Type 2 report, an ISO 27001 / 42001 certificate, or a custom security
  review form
- An existing vendor has delivered the annual re-attestation and a fresh read is needed
- An AI vendor is being onboarded (LLM API provider, AI-coding-assistant company,
  ML-feature-as-a-service) and the response makes AI-specific claims (no-train, data
  residency, model-output safety)
- Leadership has been handed a "we are SOC 2 compliant" line and wants an evidence-tied
  read of what that actually demonstrates
- A risk-acceptance memo is being drafted and needs a documented basis tied to the
  questionnaire response

Keyword triggers: "vendor security questionnaire", "SIG response", "CAIQ review",
"SOC 2 attestation", "vendor risk assessment", "third-party security review", "vendor
risk management", "TPRM".

## When NOT to use

Skip this skill and hand off when:

- No questionnaire response exists yet — the vendor has not returned anything. The skill
  reads what exists; it does not generate questionnaires (use a procurement-side
  questionnaire-authoring workflow instead).
- The reviewer wants the skill to *decide* whether to onboard the vendor — the skill
  surfaces findings tied to the response; the accept / reject decision is a risk-owner's
  call, not the skill's. Decline to issue a verdict.
- The vendor is being assessed via a penetration test or technical security assessment —
  that is hands-on testing, not document review. Hand off to
  `security/scaffolding-red-team-engagement`.
- The user wants to assess a vendor's *AI safety* posture specifically (red-team coverage,
  model evals, jailbreak resilience) — that is a technical AI-security review. The
  questionnaire-review skill flags AI-specific claims and recommends a technical AI-safety
  audit as a follow-up, but does not itself perform that audit.

## Quick start

User says: "Here's the SIG Lite response from a vendor we're considering. Also their
SOC 2 Type 2 report. Read these skeptically and tell me what's wrong before I sign."

Skill produces:

1. **Findings table** — per finding: claim made · evidence cited · gap / concern · severity
2. **Missing-artifact list** — what was claimed but not evidenced (e.g., a policy named
   without a link or attachment)
3. **Contradiction list** — where two answers, or a SIG answer and a SOC 2 control,
   disagree
4. **Stale-evidence list** — attestations / certificates past or near their valid-from
   window
5. **AI-specific overlay** (if AI vendor) — no-train claims, data residency, model-output
   handling, fine-tuning data flow
6. **Recommended follow-up questions** — what to send back to the vendor before sign

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| questionnaire_type | "SIG-Lite" \| "SIG-Core" \| "CAIQ" \| "SOC2-T1" \| "SOC2-T2" \| "ISO27001" \| "ISO42001" \| "custom" | yes | — | What the reviewer is reading. Drives the framework-specific overlay. |
| response_text | string or file path | yes | — | The vendor's response (questionnaire fill, attestation report, certificate). |
| attached_evidence | list of strings | no | [] | Supporting evidence the vendor attached (policies, diagrams, audit reports). |
| vendor_type | "infrastructure" \| "SaaS" \| "AI-LLM-API" \| "AI-tool" \| "data-processor" \| "other" | yes | — | Drives sector-specific concerns (AI-train clauses, GDPR DPA terms, sub-processor lists). |
| data_classes_in_scope | list of strings | yes | — | What data classes the vendor will touch (PII, PHI, customer source code, prompts, embeddings). |
| existing_relationship | bool | no | false | Whether this is annual re-attestation vs. new onboarding. |
| risk_appetite | "conservative" \| "balanced" \| "lenient" | no | balanced | Calibrates which findings are flagged as Blocking vs. Concerning. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Walk these steps in order. Steps 2, 3, and 6 are non-negotiable — they catch the failure
modes that bypass the rest of the review (claims with no evidence, internal contradictions,
and stale attestations).

```
Skeptical vendor-questionnaire review checklist:
- [ ] Step 1: Pin the scope (what data classes, what vendor surface)
- [ ] Step 2: Walk every answer — for each, claim · evidence · gap
- [ ] Step 3: Hedge-word scan (best-effort, intend to, aim to, generally, typically)
- [ ] Step 4: Missing-artifact scan (named policy with no link, named control with no test)
- [ ] Step 5: Contradiction scan (cross-answer, cross-document)
- [ ] Step 6: Attestation staleness check (valid-from, period-covered, opinion-date)
- [ ] Step 7: AI-specific overlay (if AI vendor)
- [ ] Step 8: Compile findings + follow-up questions
```

### Step 1: Pin the scope

Restate, in the reviewer's own words, what data classes the vendor will touch and what
the vendor's surface is in the relationship. The questionnaire review is anchored on this
scope — findings that fall outside the scope are noted but de-prioritized.

### Step 2: Walk every answer

For each question / control / assertion in the response, capture three things:

| Field | What goes here |
|---|---|
| Claim | The vendor's literal answer, verbatim |
| Evidence | What was attached or referenced to back it up |
| Gap | What is missing to verify the claim, or what is unclear |

This is the core mechanic. Most weak responses survive review because the reviewer
skims for the keyword and stops there. The skill forces a per-answer pass.

### Step 3: Hedge-word scan

Flag answers that hedge in ways that materially weaken the claim:

- "best-effort", "reasonable efforts", "commercially reasonable" (vs. a hard commitment)
- "intend to", "aim to", "plan to", "will pursue" (vs. "have implemented")
- "generally", "typically", "in most cases", "usually" (vs. "always")
- "supports", "is capable of", "can be configured to" (vs. "is configured to")
- "no known issues", "not aware of any" (the speaker's awareness is not evidence)
- "industry-standard", "best practices" (named without specifying which standard)

Hedge words are not automatic disqualifications — they are signals to dig.

### Step 4: Missing-artifact scan

For each policy, control, or process named in an answer, verify an artifact is attached
or linked:

- "We have a documented Incident Response policy" → is the policy itself attached or
  linked?
- "We perform annual penetration tests" → is the most recent pen-test summary attached
  (or at least the date and scope)?
- "We have a vulnerability management program" → is the SLA documented and is there an
  attestation of compliance?
- "Encryption in transit and at rest" → which algorithm / key lengths / key-management
  service, and is a configuration excerpt or diagram attached?
- "Background checks on employees" → for which roles, what jurisdictions, what scope?

Named-without-artifact = a finding to surface back to the vendor.

### Step 5: Contradiction scan

Cross-check answers against each other and against attached artifacts:

- SIG says "multi-factor auth required for all admin access"; the attached architecture
  diagram shows a SSH bastion with key-only authentication — these can both be true, but
  they can also indicate scope confusion
- SOC 2 Type 2 lists a sub-processor that the SIG response does not disclose in its
  sub-processor list
- The CAIQ says "no customer data is used for AI model training"; the public privacy
  policy reserves a right to "improve our services using aggregated, de-identified usage
  data" — flag for clarification on whether prompts / outputs fall under that clause
- The certificate lists a scope (e.g., "ISO 27001 covers the SaaS production environment
  in `us-east-1`") that does not match the geography the customer relationship will use

### Step 6: Attestation staleness check

For each attestation / certificate / report:

| Item | What to check |
|---|---|
| Period covered | SOC 2 Type 2 period (e.g., 2024-10-01 to 2025-09-30); flag if > 12 months old |
| Opinion date | The auditor's signing date; flag if > 15 months old |
| Certificate expiry | ISO certificates; flag if expired or expiring < 90 days |
| Bridge letter | Required if the period-covered ends before the contract starts and the next attestation is not yet issued |
| Exception list | SOC 2 reports often have exceptions; surface them — they are findings the vendor's auditor flagged |

### Step 7: AI-specific overlay

If `vendor_type` is `AI-LLM-API` or `AI-tool`, additionally check:

- **No-train commitment** — is the no-train commitment in the *master agreement / DPA*,
  not just the marketing page or the tier-description blog post? Marketing-page promises
  are not contractually binding.
- **Data residency** — for the inference path AND any logging / abuse-detection retention,
  not just the inference path
- **Sub-processor list** — for AI vendors, sub-processors include the model-hosting cloud
  provider, the abuse-detection service, the human-in-the-loop review vendor (if any), and
  the model provider itself if the vendor is reselling
- **Output handling** — does the vendor retain prompts, completions, or embeddings? For
  what purpose, for how long, with what access controls?
- **Fine-tuning data flow** — if the customer fine-tunes models with the vendor, where
  does the training data live, who has access, what happens to the fine-tuned weights
  on contract termination?
- **Model versioning** — can the customer pin a specific model version, or does the
  vendor reserve the right to silently swap?

### Step 8: Compile findings + follow-up questions

Output a structured report (see Outputs). The "Recommended follow-up questions" section
lists the exact questions to send back to the vendor before contract sign-off, derived
from Steps 3 through 7.

## Outputs

A single response containing:

1. **Findings table** — per finding: claim · evidence · gap · severity (Blocking / Concerning / Note)
2. **Missing-artifact list**
3. **Contradiction list**
4. **Stale-evidence list**
5. **AI-specific overlay findings** (if applicable)
6. **Recommended follow-up questions** — the exact questions to send back to the vendor
7. **Explicit non-verdict** — a single sentence: "This is a findings report, not an
   approval; the risk-acceptance decision is the risk owner's."

## Failure modes

- **Skim-and-approve** — reviewer reads the answers, sees the keywords, signs off. Caught
  by: Step 2 mandatory per-answer claim · evidence · gap walk.
- **Hedge words pass as commitments** — "best-effort encryption" reads as "encryption".
  Caught by: Step 3 hedge-word scan.
- **Named policy with no artifact** — vendor cites a policy that does not exist or is not
  attached. Caught by: Step 4 missing-artifact scan.
- **Marketing-page promise treated as contractual** — "we don't train on customer data"
  appears on the marketing site but is silent in the DPA. Caught by: Step 7 explicit
  master-agreement / DPA verification for AI no-train claims.
- **Stale SOC 2** — Type 2 from two years ago treated as current. Caught by: Step 6
  staleness check.
- **Scope mismatch** — ISO certificate covers a region or product the customer is not
  buying. Caught by: Step 1 scope pin + Step 6 staleness check.
- **Issuing a verdict** — skill says "approved" or "low-risk" without an accountable risk
  owner. Caught by: Step 8 explicit non-verdict statement; skill output includes the
  "findings, not approval" sentence verbatim.
- **Risk-appetite mismatch** — `risk_appetite="lenient"` is set by a reviewer who lacks
  authority to set risk appetite. Caught by: skill output flags the risk-appetite setting
  back to the reviewer and asks who set it.

## References

- [SIG Questionnaire (Shared Assessments)](https://sharedassessments.org/sig/)
- [CSA CAIQ v4](https://cloudsecurityalliance.org/research/cloud-controls-matrix/)
- [AICPA SOC 2 Trust Services Criteria](https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2)
- [ISO/IEC 27001:2022](https://www.iso.org/standard/27001)
- [ISO/IEC 42001:2023 — AI management systems](https://www.iso.org/standard/81230.html)
- [CSA STAR Registry](https://cloudsecurityalliance.org/star/) — public CAIQ submissions

## Examples

### Example 1: AI vendor with thin no-train evidence

Input: `questionnaire_type="custom"`, `vendor_type="AI-LLM-API"`,
`data_classes_in_scope=["customer prompts", "customer completions", "support-ticket text"]`,
`response_text` is a marketing-style FAQ with answers like "We never train on customer
data" and "Enterprise-grade encryption protects your data in transit and at rest",
`attached_evidence=["marketing FAQ page", "blog post on Enterprise tier"]`.

Output: Findings include — (1) "Never train on customer data" claim cites only the
marketing FAQ; flag that this commitment must appear in the master agreement or DPA, not
the marketing page, before being relied on; (2) "Enterprise-grade encryption" is a hedge;
ask for AES-256 / TLS 1.2+ specifics and key-management documentation; (3) No sub-processor
list attached — required for AI vendors since model-hosting cloud, abuse-detection
service, and any human-in-the-loop review vendor are downstream data processors; (4) No
data-residency commitment for the abuse-detection retention path. Recommended follow-up
questions enumerate the contractual no-train language, the sub-processor list, the
data-residency for both inference and abuse-retention, and the model-versioning commitment.
Closes with the explicit non-verdict sentence.

### Example 2: SOC 2 Type 2 with strong narrative but stale opinion date

Input: `questionnaire_type="SOC2-T2"`, `vendor_type="SaaS"`,
`data_classes_in_scope=["customer financial records"]`, the report has a strong control
narrative but the period-covered is 2023-07-01 to 2024-06-30 and the opinion date is
2024-08-15. Today is 2026-05-23. No bridge letter attached.

Output: Stale-evidence finding: the SOC 2 Type 2 opinion is ~21 months old; the
period-covered ends ~23 months before today. Industry practice is to refuse reliance on
SOC 2 Type 2 reports older than 12 months without a bridge letter. Findings include —
(1) Stale attestation as a Blocking finding; ask the vendor for the most recent Type 2
or a bridge letter covering the gap; (2) Strong narrative is noted but does not substitute
for current evidence; (3) Customer-financial-records scope makes the staleness more
material. Recommended follow-up: request the most recent Type 2 (period ending no earlier
than 2025-05-23) or a CPA-issued bridge letter. Closes with the explicit non-verdict
sentence.

### Example 3: Pre-RFP — no response yet (anti-trigger)

Input: "We are about to send a vendor our security questionnaire. Read it skeptically."

Output: Skill declines to engage. Explains that the questionnaire-review skill reads
what a vendor has returned; the user is at the questionnaire-issuance stage, not the
review stage. Recommends instead: drafting the questionnaire (a SIG Lite is a reasonable
starting baseline, sector-overlay questions added for AI / health / finance), and inviting
the vendor to respond with attached evidence rather than free-text answers. Offers to
review the response once it returns.

## See also

- `security/writing-vdp-and-coordinated-disclosure` — disclosure policy (complementary)
- `security/scaffolding-ai-policy-doc` — org AI use policy whose vendor inventory feeds
  this review when an AI vendor is being onboarded
- `security/auditing-mcp-server-pre-trust` — pre-trust audit for MCP servers; overlaps
  this skill when the vendor delivers an MCP server
- `security/triaging-vulnerability-findings` — once vendor pen-test outputs are in hand
- `security/threat-modeling-llm-app` — feeds the AI-specific overlay when the vendor's
  product is an LLM app

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 for v6.0-batch-1 per PRAGMATIC discipline.
