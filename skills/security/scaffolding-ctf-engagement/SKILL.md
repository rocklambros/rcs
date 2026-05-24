---
name: scaffolding-ctf-engagement
description: >
  Scaffolds a paid CTF / red-team engagement or a bug-bounty submission before any
  attack runs — produces Rules of Engagement (RoE), scope inventory, finding template,
  severity rubric (CVSS-aligned), and proof-of-concept hygiene rules. Use when the
  user is about to start a paid CTF engagement against a third-party client, an
  authorized internal CTF rotation, or a bug-bounty submission against a program
  with a published scope. Refuses to engage for solo HackTheBox / TryHackMe practice
  on the operator's own throwaway lab where no scope, authorization, or external
  blast radius exists.
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - red-team
  - pen-tester
  - bug-bounty
evidence:
  - claude-secure-coding-rules
  - mac-harness-foundation-threat-model
  - rcs-batch-creation-plan
last-updated: 2026-05-23
---

# Scaffolding a CTF / Pen-test Engagement

> **Tooling, not professional advice.** This skill produces engagement scaffolding;
> it does NOT replace contractual review by counsel, the customer's authorized
> signer on the RoE, or the bug-bounty program's published rules.

## When to use

Trigger this skill when the user is about to start an authorized offensive-security engagement and one of:

- A paid CTF engagement, red-team exercise, or pen-test against a third-party client
- An internal CTF rotation against company-owned infrastructure (with management sign-off)
- A bug-bounty submission against a published program (HackerOne, Bugcrowd, Intigriti, self-hosted)
- A pre-deployment authorization test where the operator wants a documented finding pipeline

Keyword triggers: "starting a pen-test next week", "scope the CTF", "bug-bounty submission template", "PoC hygiene", "how should we report findings", "severity rubric for this engagement", "what counts as in-scope".

## When NOT to use

Skip this skill and hand off when:

- The user is doing solo HackTheBox / TryHackMe / VulnHub practice on a personal account against a throwaway lab — no third-party RoE, no client-side authorizer, no published scope
- The actual exploitation is the request, not the scoping — use a vulnerability-specific exploitation skill (planned) or domain skills like `running-prompt-injection-eval`
- The engagement is an AI-system red-team rather than a classic CTF / pen-test — use `scaffolding-red-team-engagement` (specialised for AI-system scope, kill-switch, and PII canaries)
- The user is responding to an active incident on production — that is IR, not pre-engagement scoping; hand off to `running-cloud-ir-runbook`

## Quick start

User says: "We just signed an SOW with ACME for a 2-week black-box pen-test of their external attack surface (acme.example, *.acme.example, the prod API at api.acme.example). Two pen-testers start Monday 2026-06-08. They want a PDF deliverable. Scaffold the engagement."

Skill produces six artifacts in a single response:

1. **Rules of Engagement (RoE)** — signed-off authorization, time window, contact list, communication channels
2. **Scope inventory** — in-scope hosts, apps, account types, attack classes allowed
3. **Out-of-scope list** — explicit no-go targets (DoS, social engineering, third-party hosted dependencies, subdomains belonging to other tenants)
4. **Finding template** — title / severity / CVSS vector / affected asset / reproduction / impact / remediation / evidence
5. **Severity rubric** — CVSS-aligned bands (Critical / High / Medium / Low / Informational) with concrete examples
6. **PoC hygiene rules** — never exfiltrate real customer data; use canaries; do NOT pivot beyond scope; preserve evidence in tamper-evident logs

Each artifact is filled with the engagement-specific values the user provided.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| engagement_type | "paid-pentest" \| "internal-ctf" \| "bug-bounty" | yes | — | Drives RoE template, severity model, and reporting cadence. |
| target_scope | string | yes | — | Hosts / domains / apps / endpoints in scope (verbatim from the SOW or program brief). |
| owner_authorizer | name + role | yes | — | Accountable customer-side signer of the RoE (paid/internal). For bug-bounty: the program identifier replaces this. |
| time_window | ISO-date range | yes | — | Engagement start and end; activity outside this window is unauthorized. |
| team_size | int | no | 1 | Number of testers; affects collision avoidance and reporting channels. |
| deliverable_format | "pdf" \| "markdown" \| "json" \| "platform-submission" | no | "markdown" | Final-report format. |
| severity_model | "cvss-v3.1" \| "cvss-v4.0" \| "program-custom" | no | "cvss-v3.1" | Scoring model; for bug-bounty, use the program's published model. |
| safe_harbor_required | bool | no | true | Whether the engagement letter must include safe-harbor language for the testers. |

## Workflow

Walk these steps in order. Do not skip the authorizer-signature step — an unsigned RoE turns the engagement into unauthorized access.

```
CTF / pen-test scaffolding checklist:
- [ ] Step 1: Confirm authorization source (signed SOW, internal exec memo, or published program scope)
- [ ] Step 2: Lock in scope (in-scope assets + attack classes allowed)
- [ ] Step 3: Document out-of-scope exclusions explicitly
- [ ] Step 4: Adopt a severity rubric (CVSS v3.1 unless program specifies otherwise)
- [ ] Step 5: Adopt a finding template with CVSS vector + repro + impact + remediation
- [ ] Step 6: Lock in PoC hygiene rules (canaries only, no exfiltration, no pivoting)
- [ ] Step 7: Circulate RoE for signature BEFORE any test traffic flows
```

### Step 1: Authorization source

Paid pen-test → executed SOW + named customer authorizer (typically VP Eng / CISO / authorized delegate). Internal CTF → an executive memo on file. Bug-bounty → the program's published rules + the user's enrolled-tester status; the program identifier is the authorization artifact.

For bug-bounty specifically, save a dated screenshot or hash of the program rules at engagement start — programs change scope without notice.

### Step 2: In-scope inventory

Hosts / domains / IP ranges / applications / account types / attack classes. List every target by exact name. Wildcards (`*.acme.example`) are allowed only when the SOW or program brief says so verbatim; do not infer them.

Attack classes allowed: web app, API, network, mobile, social engineering (only with explicit additional authorization), physical (only with explicit additional authorization).

### Step 3: Out-of-scope exclusions

Default-block list every engagement should include unless overridden in writing:

- Denial-of-service (volumetric, resource-exhaustion, cost-amplification)
- Social engineering of customer employees (unless explicitly authorized)
- Third-party hosted services (SaaS the customer does not own — Stripe, Twilio, Auth0 tenants, etc.)
- Sibling subdomains in shared infrastructure (e.g., other tenants of the same multi-tenant platform)
- Real customer PII exfiltration — synthetic / canary records only
- Persistence (backdoors, scheduled tasks, dropped binaries) beyond what the SOW requires for proof-of-impact

### Step 4: Severity rubric

Default: CVSS v3.1 vector for each finding, mapped to bands:

| Band | CVSS base | Examples |
|---|---|---|
| Critical | 9.0 – 10.0 | Unauthenticated RCE, auth bypass on prod, mass-PII exfiltration via SSRF |
| High | 7.0 – 8.9 | Authenticated RCE, IDOR exposing other tenants' data, stored XSS in admin |
| Medium | 4.0 – 6.9 | Reflected XSS, CSRF on sensitive action, weak crypto on token |
| Low | 0.1 – 3.9 | Verbose error, missing security header, rate-limit gap |
| Informational | 0.0 | Hygiene observations, no exploitable impact |

Bug-bounty programs frequently override these bands — use the program's published bounty table verbatim.

### Step 5: Finding template

Every finding produced by the engagement uses the same skeleton — see `reference/finding-template.md` for the full pattern.

Required fields: title (one-line), severity band + CVSS vector, affected asset (exact host / endpoint / parameter), reproduction (numbered steps a reader can replay), impact (concrete consequence on the business), remediation (specific fix with code-level direction when possible), evidence (screenshots / request-response pairs / hashed proof-of-impact ref).

### Step 6: PoC hygiene

- **Canaries only.** When proving impact requires touching data, use seeded canary records the customer pre-plants. Never exfiltrate real customer data.
- **No pivoting.** Do not move from an in-scope host to an out-of-scope host even if the in-scope host has the credentials. Stop and update the RoE if the SOW needs to expand.
- **No persistence.** Drop only the minimum proof-of-impact artifact (file, key, beacon) and remove it before the engagement closes.
- **Tamper-evident logs.** Every attempted exploit logs to append-only storage with the payload hash, response hash, timestamp, and tester id. See `reference/poc-hygiene.md` for the log schema.
- **Findings chains.** Multiple low-severity findings that chain to high impact (e.g., reflected XSS + CSRF + verbose error → account takeover) get reported as ONE chained finding at the chained-severity, with each link cross-referenced.

### Step 7: Pre-flight gate

No test traffic before the RoE is signed (paid / internal) or the bug-bounty program enrollment is confirmed and dated. The artifact pack from steps 1–6 is circulated, signed, and stored alongside the engagement logs.

## Outputs

A single response containing:

1. **RoE document** (Markdown, see `reference/roe-template.md`) ready for the authorizer to sign
2. **In-scope inventory table** and **Out-of-scope list**
3. **Severity rubric** (default CVSS v3.1 bands, overridable per program)
4. **Finding template** (Markdown) populated with the engagement-specific identifier
5. **PoC hygiene rules** (canary policy, no-pivot rule, no-persistence rule, log schema)
6. **Pre-flight gate reminder** — explicit "do not run attack traffic before RoE is signed / enrollment confirmed" sentence

## Failure modes

- **Verbal "go ahead" instead of a signed RoE** — a Slack ack is not a signed RoE. Caught by: Step 7 explicit gate; response includes the unsigned-RoE warning.
- **Inferred wildcard scope** — testers assume `*.acme.example` includes `internal.acme.example`. Caught by: Step 2 requires wildcards be written verbatim in the SOW.
- **Findings reported without CVSS vector** — severity becomes argumentative without a vector. Caught by: Step 5 requires CVSS vector per finding.
- **Trivial findings inflated to High** — "missing X-Content-Type-Options" reported as High. Caught by: Step 4 bands cap such findings at Low / Informational.
- **Bug-bounty program rules changed mid-engagement** — scope shrinks, testers lose authorization retroactively. Caught by: Step 1 requires a dated snapshot of the program rules at engagement start.
- **PoC exfiltrates real customer data** — tester pulls a real PII record "to prove the bug". Caught by: Step 6 canary-only rule; out-of-scope list (Step 3) excludes real PII exfiltration.
- **Findings chains reported as separate low-sevs** — the chain's true severity is lost. Caught by: Step 6 finding-chain rule.

## References

- `reference/roe-template.md` — full Rules-of-Engagement document template
- `reference/finding-template.md` — finding write-up structure with CVSS vector
- `reference/poc-hygiene.md` — canary policy + no-pivot + log schema
- [CVSS v3.1 Specification](https://www.first.org/cvss/v3.1/specification-document) — vector + base-score calculation
- [PTES Technical Guidelines](http://www.pentest-standard.org/index.php/PTES_Technical_Guidelines) — pen-test methodology baseline

## Examples

### Example 1: Paid 2-week external pen-test

Input: `engagement_type="paid-pentest"`, `target_scope="acme.example, *.acme.example, api.acme.example"`, `owner_authorizer="CISO, ACME Corp"`, `time_window="2026-06-08 to 2026-06-19"`, `team_size=2`, `deliverable_format="pdf"`, `severity_model="cvss-v3.1"`.

Output: RoE addressed to the ACME CISO with the engagement window; in-scope inventory naming the apex + the wildcard + the API host explicitly; out-of-scope list including DoS, social engineering, the Stripe/Twilio third-party dependencies, sibling subdomains belonging to other tenants, and real-customer PII exfiltration; CVSS v3.1 severity rubric; finding template populated with engagement id `ACME-2026-06`; PoC hygiene rules (canary-only, no pivoting, no persistence, append-only log schema); pre-flight gate sentence.

### Example 2: Bug-bounty submission against a published program

Input: `engagement_type="bug-bounty"`, `target_scope="program brief: production web app at app.example.com, API at api.example.com, browser extension v3"`, `owner_authorizer="<bug-bounty program: HackerOne handle: example-corp>"`, `time_window="ongoing"`, `team_size=1`, `severity_model="program-custom"`.

Output: Authorization-source snapshot (dated screenshot of the program rules); in-scope = the three named assets verbatim; out-of-scope per the program's published exclusions (typically: DoS, social engineering, physical, third-party); severity rubric pulled from the program's bounty table (NOT the default CVSS bands); finding template adapted to the program's submission format; PoC hygiene rules; reminder to verify enrollment status before any test traffic.

### Example 3: Solo HackTheBox practice (anti-trigger)

Input: "I'm bored on Saturday and want to do some HackTheBox boxes on my personal account. Scaffold an engagement with RoE and a severity rubric."

Output: Skill declines to scaffold a formal engagement. Explanation: HackTheBox / TryHackMe / VulnHub on a personal account against a sandboxed lab has no third-party authorizer to sign an RoE, no customer-side blast radius, no published scope to lock in. The binding constraint is the platform's published Terms of Service, not a custom RoE. Recommends keeping a personal lab notebook (notes on technique, not formal findings) and pointing at the platform's writeup rules if the user plans to publish.

## See also

- `security/scaffolding-red-team-engagement` — AI-system-specific red-team scoping with kill-switch + PII canaries
- `security/writing-pentest-finding` — finding write-up format with CVSS vector + repro + remediation
- `security/running-cloud-ir-runbook` — for when the engagement uncovers an in-progress incident
- `security/threat-modeling-llm-app` — for engagements that include an LLM feature
- `security/auditing-mcp-server-pre-trust` — when the engagement touches MCP servers

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 for v6.0-batch-2 per PRAGMATIC discipline.
