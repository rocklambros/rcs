---
name: scaffolding-ai-policy-doc
description: >
  Scaffolds an organization-wide AI Use Policy covering acceptable use, prohibited use,
  human-oversight requirements, incident-response triggers, third-party AI vendor inventory,
  and a per-employee acknowledgement workflow. Produces the policy document, a one-page
  employee-facing summary, an AI-vendor inventory spreadsheet template, and an
  incident-response addendum that bridges the AI policy into the org's existing IR runbook.
  Use when an organization is publishing its first AI use policy, when employees have
  started using generative-AI tools without governance, when a regulator (EU AI Act,
  NIST AI RMF, ISO/IEC 42001, sector-specific guidance like FDA / OCC / DORA) is asking
  for a documented AI policy, or when leadership is asking "who's allowed to use what AI
  for what". Refuses to draft a policy for an organization that does not yet use AI in any
  form (no current usage means no concrete decisions to encode).
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - grc
  - executive
  - legal
  - hr
evidence:
  - claude-secure-coding-rules
  - mac-harness-foundation-threat-model
  - rcap-c2m2-governance-controls
last-updated: 2026-05-23
---

# Scaffolding an Organization-Wide AI Use Policy

> **Scaffolding, not legal advice.** This skill produces a working draft for internal
> review. Acceptable-use and prohibited-use clauses, employee-acknowledgement language,
> and any data-protection sections MUST be reviewed by counsel and HR before publication.
> Sector-specific AI guidance (FDA on AI/ML-enabled medical devices, OCC/FDIC on AI in
> banking, EU AI Act risk tiers, DORA on financial-services digital operational
> resilience) may impose additional requirements — flag these for specialist review.

## When to use

Trigger this skill when an organization with at least some current AI usage is preparing
documented governance, and one of:

- First-time AI use policy for an org where employees are already using generative-AI tools
  (ChatGPT, Claude, Copilot, Gemini) without a documented stance
- Compliance-driven publication: ISO/IEC 42001 (AI management systems), NIST AI RMF 1.0,
  EU AI Act conformity preparation (especially for high-risk-tier deployments), sector
  rules (FDA SaMD AI/ML, OCC Model Risk Management bulletin 2011-12 applied to AI)
- Board / executive request after a publicized AI-related incident at a peer org
- Onboarding a third-party AI vendor (LLM API provider, AI-assisted coding tool, AI-driven
  HR screening) that requires the org to attest to a governance posture
- Customer / partner request: enterprise customers requiring an AI policy attestation as
  part of vendor onboarding

Keyword triggers: "AI use policy", "generative AI policy", "can employees use ChatGPT",
"AI governance", "AI vendor inventory", "AI risk management policy", "EU AI Act prep",
"ISO 42001 readiness", "NIST AI RMF policy".

## When NOT to use

Skip this skill and hand off when:

- The organization currently uses no AI at all, has no AI in its product, and no employee
  uses generative-AI tools at work — the policy would encode imagined decisions, not real
  ones. Recommend revisiting once usage starts.
- The user wants a *technical* AI security policy (model security, prompt-injection
  defense, MCP-server registration) — that is the threat-modeling and skill-authoring
  layer. Hand off to `security/threat-modeling-llm-app`,
  `security/threat-modeling-agentic-systems`, `security/auditing-mcp-server-pre-trust`.
- The user wants a customer-facing AI feature disclosure (e.g., "this product uses AI for
  X, you can opt out") — that is product / privacy disclosure, not org-wide governance.
  Recommend a privacy-policy-update workflow instead.
- The user is responding to an active incident involving AI (data leak via LLM, hallucinated
  decision in a regulated workflow) — that is IR, not policy authoring.

## Quick start

User says: "We're a 400-person company. Half the engineering team uses Copilot and
ChatGPT daily. Marketing pastes copy into Gemini. Legal is panicking. We need an AI use
policy."

Skill produces a four-artifact pack:

1. **AI Use Policy** — full document with acceptable use, prohibited use, oversight,
   IR triggers, vendor inventory, employee acknowledgement
2. **One-page employee summary** — what an employee needs to know in 60 seconds
3. **AI vendor inventory template** — spreadsheet schema for tracking each AI tool the
   org sanctions
4. **AI-incident addendum to the IR runbook** — what counts as an AI incident, who to call,
   what to preserve

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| org_size | "startup" \| "mid-size" \| "enterprise" | yes | — | < 50 \| 50–1000 \| > 1000. Adjusts policy depth and oversight structure. |
| sector | string | yes | — | Health / finance / public-sector / SaaS / industrial / etc. Drives sector-specific overlay. |
| current_ai_usage | list of strings | yes | — | Known AI tools in use today (e.g., "Copilot", "ChatGPT", "Claude API in product", "Gemini for marketing copy"). |
| has_ai_in_product | bool | yes | — | Whether the org's product itself uses AI (vs. AI only used internally). |
| regulators | list of strings | no | [] | Active regulators (e.g., "EU AI Act", "FDA", "OCC", "ISO 42001"). |
| data_classes | list of strings | no | sensible defaults | Data classes employees may handle (PII, PHI, financial, IP, customer data). |
| acknowledgement_cadence | "once" \| "annual" \| "role-change" | no | annual | How often employees re-acknowledge the policy. |
| third_party_ai_review_required | bool | no | true | Whether a new third-party AI tool needs security-review sign-off before adoption. |

## Workflow

Walk these steps in order. Steps 1 and 7 are non-negotiable — without them the policy
either misses the actual decisions being made (Step 1) or has no enforcement surface
(Step 7).

```
AI Use Policy authoring checklist:
- [ ] Step 1: Inventory current AI usage (real, not aspirational)
- [ ] Step 2: Define acceptable use (per data class, per tool)
- [ ] Step 3: Define prohibited use (concrete blocking examples)
- [ ] Step 4: Specify human-oversight requirements (per decision class)
- [ ] Step 5: Define AI-incident triggers (what counts, who responds)
- [ ] Step 6: Stand up the AI-vendor inventory (per-tool data class + risk tier)
- [ ] Step 7: Acknowledgement workflow + review cadence
- [ ] Step 8: Pre-publish gate — counsel + HR + IR-team sign-off
```

### Step 1: Inventory current AI usage

Document what is actually in use today, not what leadership wishes were in use.
Engineering's Copilot. Marketing's Gemini paste-ins. Sales's auto-summarized call
transcripts. Anything employees do regularly with AI tools — including personal-account
usage on work tasks — is in scope. The inventory anchors the policy in reality so it
encodes decisions about real usage, not hypothetical usage.

### Step 2: Acceptable use

For each (data class × tool) cell, state explicitly: allowed, allowed-with-controls,
or prohibited. Example: "Public-tier marketing copy may be pasted into Gemini; customer
PII may not. Source code at confidentiality tier 2 or lower may be processed by Copilot;
tier 3+ source must use the on-premise Copilot deployment only."

Reference each tool by exact product name and deployment (consumer ChatGPT ≠ ChatGPT Team
≠ ChatGPT Enterprise; they have materially different data-handling guarantees).

### Step 3: Prohibited use

Concrete examples beat abstract prohibitions. Include at minimum:

- No customer PII / PHI / payment data into any consumer-tier AI tool
- No source code at the org's highest confidentiality tier into externally-hosted AI
  tools without an executed DPA + data-residency / no-training clauses
- No AI-generated content represented as human-authored to customers without disclosure
- No autonomous AI execution against production systems without human-in-the-loop
  approval at each material action (see Step 4 oversight rules)
- No use of AI tools to make legally-binding decisions about people (hiring, promotion,
  termination, credit, healthcare) without the human-oversight pattern in Step 4

### Step 4: Human-oversight requirements

Tier decisions by impact:
- **Reversible, low-impact** (drafting an internal memo): no required human review beyond
  the employee using the tool
- **Reversible, customer-facing** (a marketing email): human review of the output before
  it ships
- **Hard-to-reverse, internal** (a code refactor in production): two-person review
  including the AI's output as a starting point, not a finished product
- **High-impact, regulated** (a hiring screen, a credit decision, a clinical
  recommendation): human-in-the-loop required at each material decision; the AI's role
  is documented; the human reviewer is named and accountable; this category is the EU AI
  Act high-risk tier in many cases

### Step 5: AI-incident triggers

Define what counts as an AI incident:
- Confidential data inadvertently sent to an AI tool (paste of customer PII into a
  consumer tool)
- AI-generated output published or acted on that turned out to be materially wrong
- A vendor security incident at an AI provider the org uses
- An autonomous AI workflow that executed an unintended action
- Discovery that a tool in use has changed its data-training stance materially

For each trigger: who reports, who triages, what gets preserved (chat logs, prompts,
outputs, timestamps), what gets notified externally (customers, regulators) if a data
class was implicated.

### Step 6: AI vendor inventory

Stand up a per-tool record:

| Field | Example |
|---|---|
| Tool | Claude API (Anthropic) |
| Deployment | Enterprise tier with no-train commitment |
| Primary use | Internal coding assistant |
| Data classes allowed | Source code tier ≤ 2; no PII |
| Risk tier | Medium |
| Reviewer | Director of Security |
| DPA executed | Yes, 2026-03-12 |
| Re-review date | 2027-03-12 |

Annual re-review; new tool requires the Step 7 acknowledgement and a security review
before adoption.

### Step 7: Acknowledgement + cadence

Every employee acknowledges the policy on onboarding and at the cadence in
`acknowledgement_cadence` (default annual). Role-change triggers a re-acknowledgement
when access to new data classes is granted. HR maintains the acknowledgement record.

### Step 8: Pre-publish gate

NO publication before: (a) counsel signs off on prohibited-use language and any
employee-monitoring clauses, (b) HR signs off on acknowledgement workflow and
disciplinary implications, (c) the IR team is briefed on the AI-incident addendum, (d)
the executive sponsor (often the CIO, CISO, or General Counsel) approves the policy.

## Outputs

A single response containing:

1. **AI Use Policy** (Markdown) — full document with sections 1–7
2. **One-page employee summary** — what's allowed, what's prohibited, what to do if unsure
3. **AI vendor inventory template** — spreadsheet schema with the Step 6 fields
4. **AI-incident addendum to the IR runbook** — triggers, response, preservation,
   external-notification thresholds
5. **Pre-publish checklist** — counsel, HR, IR, executive-sponsor sign-offs

## Failure modes

- **Aspirational policy disconnected from reality** — the policy prohibits behavior that
  employees do routinely, so it is ignored on day one. Caught by: Step 1 mandatory
  inventory of *actual* current usage; the policy must encode decisions about that usage,
  not hypothetical usage.
- **Tool name without deployment tier** — "ChatGPT is allowed" without distinguishing
  consumer ChatGPT from ChatGPT Enterprise. Caught by: Step 2 explicit deployment-tier
  naming.
- **Prohibited use as vague principle, not concrete rule** — "do not use AI inappropriately"
  is unenforceable. Caught by: Step 3 requires concrete examples per category.
- **No human-oversight tier for high-impact decisions** — the policy is silent on
  AI-in-hiring or AI-in-credit. Caught by: Step 4 explicit tiering with the
  high-impact-regulated category named.
- **No acknowledgement record** — no enforcement surface when an employee violates the
  policy. Caught by: Step 7 HR-maintained acknowledgement workflow.
- **Counsel and HR bypassed in haste** — policy published to meet a customer-attestation
  deadline. Caught by: Step 8 explicit pre-publish gate with named sign-offs.
- **Vendor inventory drift** — tool gets adopted ad-hoc, never enters the inventory,
  re-review never happens. Caught by: Step 6 annual re-review + Step 2's gating of new
  tools on the Step 7 acknowledgement and security review (via
  `third_party_ai_review_required`).
- **Sector-specific gaps** — EU AI Act high-risk tier, FDA SaMD AI/ML requirements, or
  OCC model-risk-management expectations not reflected. Caught by: skill output explicitly
  flags `sector` and `regulators` overlays and recommends specialist review.

## References

- [NIST AI RMF 1.0](https://www.nist.gov/itl/ai-risk-management-framework)
- [ISO/IEC 42001:2023 — AI management systems](https://www.iso.org/standard/81230.html)
- [EU AI Act (Regulation (EU) 2024/1689)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689)
- [OWASP AI Security and Privacy Guide](https://owasp.org/www-project-ai-security-and-privacy-guide/)
- [OCC Bulletin 2011-12 — Supervisory Guidance on Model Risk Management](https://www.occ.gov/news-issuances/bulletins/2011/bulletin-2011-12.html)

## Examples

### Example 1: 400-person SaaS with existing ad-hoc AI use

Input: `org_size="mid-size"`, `sector="SaaS"`,
`current_ai_usage=["GitHub Copilot Business (engineering)", "consumer ChatGPT (marketing, sales)", "Gemini (marketing copy)"]`,
`has_ai_in_product=false`,
`regulators=["EU AI Act preparation"]`,
`data_classes=["customer PII", "source code tier 1-3", "internal financials"]`.

Output: Policy explicitly names Copilot Business as allowed for tier ≤ 2 source code with
the existing Anthropic-style DPA-equivalent in place; consumer ChatGPT prohibited for
customer PII (and recommends migrating marketing/sales to ChatGPT Enterprise or Claude
Team with no-train commitments); Gemini allowed for public-tier marketing copy with a
prohibition on customer-data paste-in. Step 4 tiers: low-impact internal drafting unreviewed;
customer-facing copy reviewed; production code change two-person review. AI-incident
triggers include the consumer-ChatGPT PII-paste case. Vendor inventory pre-populated with
the three current tools and their data-class allowances. EU AI Act prep flagged as a
sector overlay requiring specialist review since the SaaS product itself is not yet
AI-enabled but the prep posture matters.

### Example 2: Mid-size health provider with AI in clinical workflows

Input: `org_size="mid-size"`, `sector="health"`,
`current_ai_usage=["ambient-scribe AI for clinical notes", "AI-assisted radiology second-read"]`,
`has_ai_in_product=true`,
`regulators=["HIPAA", "FDA SaMD AI/ML guidance", "EU AI Act high-risk tier"]`,
`data_classes=["PHI", "clinical decisions", "billing data"]`.

Output: Policy escalates clinical-decision AI to Step 4's high-impact-regulated tier with
explicit human-in-the-loop requirements (the licensed clinician is named accountable for
each AI-assisted decision; AI output is documented but never autonomous). Prohibited use
includes any clinical-decision automation without clinician sign-off. Vendor inventory
flags both tools for FDA SaMD specialist review; EU AI Act high-risk-tier overlay is
explicitly noted. AI-incident triggers include any clinical-note discrepancy attributable
to the ambient-scribe AI, with mandatory preservation of the source audio and the
generated note. Pre-publish gate requires Chief Medical Officer sign-off in addition to
counsel + HR + IR.

### Example 3: Pre-AI organization (anti-trigger)

Input: "We're a 30-person manufacturing shop. We don't use any AI. Write us a policy."

Output: Skill declines to draft the full policy. Explains that an AI use policy encodes
decisions about *actual* usage; a pre-AI organization has no concrete decisions to encode,
so the policy would be aspirational and detached from operations. Recommends instead:
a one-page "before adopting any AI tool, consult security and legal" stance, and revisiting
the full policy workflow when the first AI tool is actually being adopted. Offers to draft
the one-pager.

## See also

- `security/scaffolding-red-team-engagement` — engagement scaffolding (complementary)
- `security/writing-vdp-and-coordinated-disclosure` — external-researcher disclosure
- `security/interpreting-vendor-questionnaire-skeptically` — vendor-security review used
  when onboarding an AI vendor from this policy's inventory workflow
- `security/threat-modeling-llm-app` — threat-model the LLM apps this policy governs
- `security/threat-modeling-agentic-systems` — threat-model the agentic systems this
  policy governs
- `security/auditing-mcp-server-pre-trust` — MCP-server review feeds into the vendor
  inventory

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 for v6.0-batch-1 per PRAGMATIC discipline.
