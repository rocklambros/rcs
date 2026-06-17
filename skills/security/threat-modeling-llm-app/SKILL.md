---
name: threat-modeling-llm-app
description: >
  Walks a STRIDE-style threat-modeling pass over an LLM application (chatbot,
  RAG system, single-turn completion API, content-generation pipeline) using a
  user-supplied catalog (OWASP LLM Top 10, MITRE ATLAS, MAESTRO, or a custom
  catalog). Inventories components and trust boundaries, maps each catalog item
  to one or more STRIDE categories at each boundary, and produces an auditable
  threat register with likelihood, impact, and mitigation per finding. Use when
  the user is designing, reviewing, or shipping an LLM-powered application and
  needs a structured threat model before deployment. The skill is methodology
  only — it never ships a bundled threat catalog; the user provides one.
version: 0.1.0
status: shipped
track: security
audience: [security-eng, ai-security, ml-engineer, architect]
evidence:
  - quality-contract-NIST-SP-800-218
  - claude-secure-coding-rules
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Threat Modeling an LLM Application

## When to use

Trigger this skill when the user asks for or implies one of:

- Designing a new LLM-backed product (chatbot, RAG, summarizer, classifier, code generator) and asks "what could go wrong?"
- Reviewing an existing LLM application before deployment, audit, or compliance sign-off
- Producing a threat register against a named catalog the user supplies (e.g., OWASP LLM Top 10, MITRE ATLAS, MAESTRO, the user's internal AI risk register)
- Phrases like "threat-model my chatbot", "STRIDE for our LLM", "map OWASP LLM Top 10 to our architecture", "what are the threats to our RAG pipeline?"

## When NOT to use

Skip this skill and hand off when:

- The system has no LLM component (pure REST API, classical ML service, database query layer) → use a conventional STRIDE / threat-modeling resource, not this skill
- The system is an autonomous **agent** with tool use, planning, or multi-turn state — that adds an attack surface this skill does not cover; use `security/threat-modeling-agentic-systems` instead
- The user wants vulnerability *scanning* or pen-test execution against a deployed system — this skill produces a design-time model, not runtime findings
- The user has not (and will not) supply a catalog — the skill refuses to invent one. Point them at OWASP LLM Top 10 (free, public) as a default starting catalog and stop

## Quick start

User says: "Threat-model our customer-support chatbot. It uses GPT-4o-mini, takes user messages, retrieves from our Confluence via embeddings, and can call two internal tools: `lookup_order(order_id)` and `refund_order(order_id)`. Use OWASP LLM Top 10 v1.1 as the catalog."

Skill response: confirms the catalog source, inventories components and trust boundaries, walks each LLM Top 10 item against each boundary, classifies each finding by STRIDE category, and produces a threat register table with likelihood, impact, and a proposed mitigation per row.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| app_description | text or file path | yes | — | Description of the LLM app: components, data flow, who provides inputs, where the model output goes. A simple text description is fine — formal DFD not required. |
| catalog | text, file path, or named reference | yes | — | The threat catalog the user wants to apply. Examples: "OWASP LLM Top 10 v1.1", "MITRE ATLAS", "MAESTRO tactics", or an inline list. Skill refuses to invent a catalog. |
| focus | "full" \| "top-N" \| "component" | no | "full" | "full" = every catalog item × every boundary; "top-N" = produce only the top-N highest-risk rows after rating; "component" = restrict to one named component (e.g., the RAG retriever). |
| likelihood_scale | "L/M/H" \| "1-5" \| custom | no | "L/M/H" | Scale used for likelihood and impact in the register. Carry through consistently. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off as each step completes:

```
Threat-modeling progress:
- [ ] Step 1: Confirm user-supplied catalog (refuse to proceed without one)
- [ ] Step 2: Inventory components (model, prompts, retrievers, tools, output sinks)
- [ ] Step 3: Identify trust boundaries (user → app, app → model, retriever → context, output → downstream)
- [ ] Step 4: Walk catalog × boundary matrix; classify each hit by STRIDE
- [ ] Step 5: Rate likelihood and impact per finding (using the chosen scale)
- [ ] Step 6: Propose at least one mitigation per finding; name an owner
- [ ] Step 7: Produce the threat register table; list any gaps (catalog items with no clear boundary hit, or boundaries with no catalog coverage)
```

### Step 1: Confirm catalog

If the user did not supply a catalog, stop and request one. Suggested defaults to offer (public, free): OWASP Top 10 for LLM Applications, MITRE ATLAS, OWASP Machine Learning Security Top 10. Do not proceed with an invented catalog — the resulting model would be unauditable.

### Step 2: Inventory components

List every component that touches model input or output. Common components in LLM apps: client / frontend prompt construction, system prompt, user message, retrieval source (RAG corpus, vector store, function output), context-assembly stage, model gateway / API client, tool list and their implementations, post-processing (parsing, validation, redaction), output sink (UI, database write, downstream API).

### Step 3: Identify trust boundaries

A trust boundary exists wherever data crosses between zones of differing trust. For an LLM app the recurring boundaries are:

- **User → app**: any user-supplied content (messages, file uploads, URL params)
- **App → model**: the assembled prompt context sent to the LLM
- **Retriever → context**: documents pulled from RAG / function results injected into the prompt
- **Model → tool**: tool-call arguments the model generates
- **Model → output sink**: model output rendered to UI, persisted, or forwarded

For each boundary, ask: who controls the data on each side, what can the upstream side influence, what's the impact if that data is malicious?

### Step 4: Walk catalog × boundary matrix

For each item in the user-supplied catalog, ask which boundary (or boundaries) it applies to. Classify each hit by STRIDE category — Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege. A single catalog item commonly maps to multiple STRIDE categories at multiple boundaries; record each as a separate row in the register.

### Step 5: Rate likelihood and impact

Use the scale the user picked (default L/M/H). Rate each row consistently. If the user has no scale preference, use Low / Medium / High and document the working definitions ("High likelihood = expected to occur under normal use"; "High impact = customer-data loss, regulatory exposure, or material financial loss"). Risk = Likelihood × Impact, rendered in the same scale.

### Step 6: Propose mitigations

Each row needs at least one mitigation and a named owner (team or role, not a person). Common mitigation classes: input validation / allowlist, output filtering / redaction, prompt-injection defense (delimiter-tagging, system-prompt hardening, retrieval allowlist), rate limiting, audit logging, model-gateway policy enforcement, tool-call sandboxing, human-in-the-loop gate. If a mitigation requires a specific technology choice, mark it as a design decision pending confirmation rather than a settled fact.

### Step 7: Produce the threat register + gap list

The register is a table — Catalog-item · Boundary · STRIDE · Likelihood · Impact · Risk · Mitigation · Owner · Notes. After the table, list any catalog items that produced no register row (with rationale — "not applicable: app has no RAG", etc.) and any boundary that no catalog item touched (flag as a coverage gap; recommend supplementing the catalog).

## Outputs

A markdown report:

1. **Catalog cited** — name + version of the user-supplied catalog
2. **Component inventory** — bullet list of components
3. **Trust boundary diagram** — text-based DFD-lite (component → boundary → component) suffices; ASCII fine
4. **Threat register table** — columns above
5. **Coverage-gap list** — catalog items with no register row, and boundaries with no catalog coverage
6. **Top risks** — the 3-to-5 highest-risk rows pulled out for executive summary

## Failure modes

- **Catalog invention** — the skill writes its own list of "common LLM threats" instead of using the user-supplied catalog. Caught by: Step 1 refuses to proceed without a named catalog; report MUST cite catalog name + version in section 1.
- **Boundary blindness** — model gateway and RAG retriever boundaries are common omissions; Step 3 explicitly enumerates them so the report cannot silently drop them.
- **STRIDE-as-checkbox** — assigning STRIDE labels mechanically without analysis. Caught by: each register row pairs the STRIDE label with a one-sentence justification.
- **Mitigation hand-waving** — vague mitigations ("improve security", "add monitoring"). Caught by: Step 6 requires at least one concrete mitigation class and a named owner per row.
- **Coverage-gap silence** — failing to flag catalog items that don't fit or boundaries with no catalog coverage. Caught by: Step 7's gap list is mandatory, even when empty (state "no gaps identified").

## References

- `reference/stride-prompt-mapping.md` — concrete examples of how common LLM threats map to STRIDE categories (illustrative, not a catalog)
- `reference/register-template.md` — the threat-register table template
- OWASP Top 10 for LLM Applications: https://genai.owasp.org/llm-top-10/ (user-supplied catalog example)
- MITRE ATLAS: https://atlas.mitre.org/ (user-supplied catalog example)
- NIST SP 800-218 / SP 800-53 STRIDE reference

## Examples

### Example 1: Customer-support chatbot with RAG and tools (happy-path)

Input: "Threat-model our customer-support chatbot. GPT-4o-mini, RAG over Confluence, tools `lookup_order` and `refund_order`. Catalog: OWASP LLM Top 10 v1.1."

Output: Skill confirms catalog (OWASP LLM Top 10 v1.1). Inventories components: client → system prompt → user message → embedding retriever → Confluence corpus → context assembly → model gateway → tool dispatcher (`lookup_order`, `refund_order`) → response renderer. Identifies five boundaries. Walks LLM01 (prompt injection), LLM02 (insecure output handling), LLM06 (sensitive info disclosure), LLM07 (insecure plugin design — maps to the tool dispatcher), LLM08 (excessive agency — maps to `refund_order` having state-changing power) against each boundary. Classifies each hit by STRIDE. Rates likelihood and impact (L/M/H). Produces the register table with ~14 rows; top risks include LLM07 + LLM08 on the refund tool (T + E) and LLM01 on the retriever (T + I). Each row has a concrete mitigation (e.g., refund_order requires human-in-the-loop gate; tool dispatcher enforces argument-allowlist; retrieval allowlists Confluence space IDs). Names owners (security-eng, ai-platform-team, support-engineering). Notes that LLM10 (model theft) is out of scope for this hosted-API deployment — listed in gap section.

### Example 2: Batch summarization pipeline, no user input (edge-case)

Input: "Threat-model our nightly batch pipeline that summarizes internal incident reports using Claude. The reports come from our PagerDuty webhook; output goes to a private Slack channel. No external user input. Catalog: MITRE ATLAS."

Output: Skill confirms catalog. Notes that the user-input boundary is internal (PagerDuty), not external — adjusts boundary inventory accordingly. Walks ATLAS tactics; many user-facing tactics (e.g., ATLAS TA0043 reconnaissance via prompt) are low-likelihood here. Retains: training-data poisoning (low — using a hosted model the user doesn't train), prompt-injection via incident-report content (possible if PagerDuty content is attacker-controlled — Medium likelihood + Medium impact since output goes to a small private channel), insecure output handling (Slack rendering markdown; risk of phishing-style content in summary). Produces register with ~6 rows. Gap section notes that ATLAS techniques targeted at training pipelines do not apply to this hosted-inference deployment.

## See also

- `security/threat-modeling-agentic-systems` — sibling skill for autonomous-agent designs (tool use + planning + multi-turn state)
- `security/auditing-mcp-server-pre-trust` — for any MCP servers integrated into the LLM app
- `security/auditing-pinned-dependencies` — supply-chain layer for the LLM app's runtime
- `workflow/running-adversarial-premortem` — complementary failure-mode discovery for the design as a whole

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored fresh per RCS v4-batch-3 (threat-modeling cluster); methodology only, no bundled catalogs per the public-skills-repo design
