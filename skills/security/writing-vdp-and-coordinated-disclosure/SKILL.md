---
name: writing-vdp-and-coordinated-disclosure
description: >
  Drafts a public Vulnerability Disclosure Policy (VDP) and a coordinated-disclosure
  timeline for an organization that ships software, APIs, or a SaaS to external users.
  Produces the VDP page itself (scope, safe-harbor language, submission channel, severity
  triage, response SLAs), the coordinated-disclosure runbook (acknowledgement window,
  triage SLA, fix-and-disclose timeline, embargo policy, credit policy), and a security.txt
  pointer. Use when an organization is publishing a VDP for the first time, when a private
  bug bounty needs a public companion policy, when the security team is being asked "where
  do researchers report bugs", or when a regulator (CISA BOD 20-01, EU CRA Article 11,
  ISO/IEC 29147) requires a documented disclosure process. Refuses to draft a public-style
  VDP for purely internal tools with no external user surface.
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - grc
  - product-security
  - executive
evidence:
  - claude-secure-coding-rules
  - mac-harness-foundation-threat-model
  - rcap-c2m2-disclosure-controls
last-updated: 2026-05-23
---

# Writing a VDP and Coordinated-Disclosure Policy

> **Scaffolding, not legal advice.** This skill produces a working draft suitable for
> internal review. Safe-harbor language MUST be reviewed by counsel before publication.
> Coordinated-disclosure timelines that touch regulated software (medical devices, ICS,
> safety-critical systems) may have sector-specific minimums set by regulators (FDA,
> CISA, ENISA) — flag these for sector-specialist review.

## When to use

Trigger this skill when the user is preparing a vulnerability disclosure surface for an
organization that ships software to external users, and one of:

- First-time VDP for a SaaS, mobile app, hardware product, or public API
- Adding a public VDP alongside an existing private bug-bounty program (e.g., HackerOne,
  Bugcrowd, Intigriti) so non-program-members have a documented channel
- Compliance-driven: CISA Binding Operational Directive 20-01 (US federal civilian),
  ISO/IEC 29147 (vuln disclosure), ISO/IEC 30111 (vuln handling), EU Cyber Resilience
  Act Article 11 (single-point-of-contact for vuln reporting), C2M2 ARCHITECTURE-2c
- A `security.txt` (RFC 9116) is being added to a domain for the first time
- The team needs a coordinated-disclosure runbook to handle inbound researcher reports
  consistently (acknowledgement, triage, fix, credit, public disclosure)

Keyword triggers: "we need a VDP", "vulnerability disclosure policy", "where do researchers
report bugs", "coordinated disclosure timeline", "safe harbor for security researchers",
"security.txt", "responsible disclosure".

## When NOT to use

Skip this skill and hand off when:

- The organization ships nothing externally — pure-internal corp IT tools have no
  external-researcher surface, so a public VDP would be aspirational at best. Recommend
  internal channels (IR runbook, employee reporting) instead.
- The user is responding to an active researcher report mid-flight — that is incident-side
  triage, not policy-drafting. Hand off to `security/running-cloud-IR-runbook` (planned)
  or the org's existing IR process.
- The user wants to design a *paid* bug bounty (pricing, payout tiers, scope tiering,
  triager workflow) — VDP is the unpaid baseline; bug-bounty design is a separate
  workflow. Recommend a bounty-platform's onboarding (HackerOne, Bugcrowd, Intigriti).
- The user is drafting a *coordinated vulnerability disclosure* request to a third-party
  vendor (i.e., they found a bug in someone else's product) — that is researcher-side
  workflow, not policy-publisher-side. Hand off to a finding-write-up skill
  (`security/writing-pentest-finding`).

## Quick start

User says: "We're a 60-person SaaS that ships a B2B analytics product. Researchers
have been emailing security@ ad-hoc — sometimes ignored, sometimes panicked. Set up a
real VDP."

Skill produces a six-artifact pack:

1. **VDP page** — Markdown ready for `/.well-known/vdp.md` or a docs site, with scope,
   safe-harbor language, submission channel, response SLAs, and severity rubric
2. **`security.txt`** — RFC 9116 file for `/.well-known/security.txt`
3. **Coordinated-disclosure runbook** — internal SOP for triage, fix, embargo, credit
4. **Severity rubric** — CVSS v4.0 base-score thresholds mapped to triage SLAs
5. **Researcher-facing acknowledgement templates** — first-touch, triage-result, fix-shipped
6. **Implementation checklist** — what must be in place before publishing the VDP

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| product_summary | freeform string | yes | — | 1–3 sentence description of the externally-shipped product (SaaS, mobile app, hardware, API). |
| primary_domain | string | yes | — | The canonical domain where the VDP and `security.txt` will live (e.g., `example.com`). |
| in_scope_assets | list of strings | yes | — | Domains, mobile app stores, API endpoints, hardware SKUs in scope. |
| out_of_scope_assets | list of strings | no | sensible defaults | Marketing site, third-party hosted services, social-engineering, physical attacks. Skill ships defaults. |
| submission_channel | "email" \| "form" \| "platform" | yes | — | `security@` mailbox, a web form, or a bug-bounty platform inbound. |
| ack_sla_hours | int | no | 72 | Time-to-acknowledge a new report. |
| triage_sla_days | int | no | 10 | Time from acknowledgement to severity verdict + initial action plan. |
| fix_target_days_critical | int | no | 30 | Target time to ship a fix for Critical findings. |
| fix_target_days_high | int | no | 60 | Target time to ship a fix for High findings. |
| coordinated_disclosure_days | int | no | 90 | Embargo window after fix-ship (or after report) before public disclosure. |
| safe_harbor | "DOJ-good-faith" \| "DOJ-CFAA-2022" \| "custom" | no | DOJ-CFAA-2022 | Baseline safe-harbor language to start from. |
| credit_policy | "always" \| "researcher-choice" \| "never" | no | researcher-choice | Whether the org publicly credits reporters. |
| has_bug_bounty | bool | no | false | Whether a paid program already exists; affects "scope of this policy" wording. |

## Workflow

Walk these steps in order. Steps 1, 2, and 8 are non-negotiable — skipping any of them
means the published policy is unsafe (no scope, no safe harbor, or no working channel).

```
VDP authoring checklist:
- [ ] Step 1: Define scope (in-scope and out-of-scope assets) explicitly
- [ ] Step 2: Draft safe-harbor language (counsel-reviewable baseline)
- [ ] Step 3: Specify submission channel (and verify it actually receives mail)
- [ ] Step 4: Set response SLAs (acknowledge / triage / fix targets)
- [ ] Step 5: Define severity rubric (CVSS v4.0 thresholds mapped to SLAs)
- [ ] Step 6: Draft coordinated-disclosure timeline + embargo + credit policy
- [ ] Step 7: Write security.txt (RFC 9116) pointing to the VDP
- [ ] Step 8: Pre-publish gate — counsel review + channel test + IR-team brief
```

### Step 1: Scope inventory

Enumerate every asset researchers may test: production domains, mobile app store listings
(by exact bundle/package id), public APIs (by base URL), hardware SKUs (by model number).
Out-of-scope defaults include: marketing/CMS sites the org does not control, third-party
hosted services (CDN, analytics, payments), social-engineering of staff or customers,
physical attacks, denial-of-service, and any pre-production / staging environment unless
explicitly authorized.

### Step 2: Safe-harbor language

Authorize good-faith research within scope. Baseline from the US DOJ 2022 CFAA policy
revision: prosecution declined for "good-faith security research". Adapt to the
jurisdiction. Always state explicitly: (a) researchers acting within scope and within the
policy will not face legal action from the org, (b) third-party data is not authorized as
a research target (PII exfiltration is never in-scope), (c) the safe-harbor does not bind
third parties (researchers must respect each affected party's terms).

### Step 3: Submission channel

Pick one of: dedicated `security@<domain>` mailbox, a hosted form, or a bug-bounty
platform inbound. The channel MUST: (a) be monitored on the `ack_sla_hours` cadence,
(b) accept PGP-encrypted mail (publish the key fingerprint or link to a keyserver),
(c) have an auto-acknowledgement that sets researcher expectations. Test the channel
end-to-end before publishing.

### Step 4: Response SLAs

Three commitments:
- **Acknowledge** (`ack_sla_hours`, default 72h) — human reply confirming receipt
- **Triage** (`triage_sla_days`, default 10 days) — severity verdict + initial action plan
- **Fix targets** — Critical `fix_target_days_critical` (default 30d), High `fix_target_days_high` (default 60d), Medium 90d, Low 180d

State that SLAs are targets, not guarantees, but commit to status updates at SLA intervals
even when a fix slips.

### Step 5: Severity rubric

Use CVSS v4.0 base-score thresholds (skill recommends v4.0 since 2024; v3.1 acceptable
fallback):

| Severity | CVSS v4.0 base | Triage SLA | Fix target |
|---|---|---|---|
| Critical | 9.0 – 10.0 | 24h | 30 days |
| High | 7.0 – 8.9 | 72h | 60 days |
| Medium | 4.0 – 6.9 | 10 days | 90 days |
| Low | 0.1 – 3.9 | 10 days | 180 days |

Document org-specific severity adjustments (e.g., authentication bypass on a
multi-tenant SaaS may auto-escalate to Critical regardless of base score).

### Step 6: Coordinated disclosure

State the disclosure model:
- **Embargo window:** `coordinated_disclosure_days` (default 90) from fix-ship date
  (or from report date if no fix is feasible), after which the researcher may publicly
  disclose
- **Joint disclosure:** the org will work with the researcher on coordinated public
  disclosure including credit (per `credit_policy`)
- **CVE assignment:** the org will request a CVE for any vulnerability that affects
  shipped software with multiple customers (CNA via MITRE if not a self-CNA)
- **Active exploitation override:** if exploitation is observed in the wild, the embargo
  shortens to the time needed to coordinate notification with affected parties

### Step 7: security.txt

RFC 9116 file at `https://<primary_domain>/.well-known/security.txt`:

```
Contact: mailto:security@<primary_domain>
Contact: https://<primary_domain>/security/vdp
Expires: <ISO-8601 date, 1 year from publish>
Encryption: https://<primary_domain>/.well-known/pgp-key.txt
Policy: https://<primary_domain>/security/vdp
Acknowledgments: https://<primary_domain>/security/hall-of-fame
Preferred-Languages: en
Canonical: https://<primary_domain>/.well-known/security.txt
```

Sign the file with the org's PGP key. Set a calendar reminder to refresh `Expires:`
annually — an expired `security.txt` is a discoverability failure.

### Step 8: Pre-publish gate

NO publication before: (a) counsel signs off on the safe-harbor language, (b) the
submission channel has been tested end-to-end with a synthetic report, (c) the IR / on-call
team has been briefed on the new inbound channel and the SLAs, (d) the `security.txt`
expiry calendar reminder is set.

## Outputs

A single response containing:

1. **VDP page** (Markdown) — scope, safe-harbor, channel, SLAs, severity rubric,
   coordinated-disclosure timeline, credit policy
2. **`security.txt`** (RFC 9116) ready for `/.well-known/security.txt`
3. **Coordinated-disclosure runbook** (internal SOP) — triage workflow, embargo handling,
   credit handling, CVE workflow
4. **Severity rubric** (CVSS v4.0 thresholds)
5. **Researcher-facing email templates** — first-touch acknowledgement, triage-result,
   fix-shipped-and-disclosure-window-starting
6. **Pre-publish checklist** — counsel review, channel test, IR brief, expiry reminder

## Failure modes

- **Safe-harbor language not counsel-reviewed** — the org publishes prosecution-disclaim
  language without legal sign-off. Caught by: Step 8 explicit gate; skill output includes
  the unreviewed-safe-harbor warning at the top.
- **Submission channel goes to nobody** — `security@` aliases to a defunct mailing list.
  Caught by: Step 8 channel test gate; skill recommends an end-to-end test with a
  synthetic report.
- **`security.txt` expires** — `Expires:` field set once, never refreshed. Caught by:
  Step 7 explicit annual reminder; skill recommends calendaring on publish.
- **Embargo too short for active exploitation** — 90-day default applies even when
  active exploitation is observed. Caught by: Step 6 active-exploitation override clause.
- **Scope drift via undocumented "ad-hoc rewards"** — researchers report bugs out of
  scope, get paid informally, then expect rewards for everything. Caught by: scope is a
  closed list in Step 1; any change requires a versioned VDP update.
- **Conflating VDP with bug bounty** — promising payment in a VDP without budget approval.
  Caught by: skill keeps the VDP unpaid by default; bounty design is a separate workflow.
- **No CVE process when one is needed** — the org ships software to multiple customers
  but never requests CVEs. Caught by: Step 6 CVE clause; skill recommends MITRE CNA or
  becoming a CNA if shipping affects 5+ external customers.

## References

- [RFC 9116 — security.txt](https://datatracker.ietf.org/doc/html/rfc9116)
- [ISO/IEC 29147:2018 — Vulnerability disclosure](https://www.iso.org/standard/72311.html)
- [ISO/IEC 30111:2019 — Vulnerability handling processes](https://www.iso.org/standard/69725.html)
- [CISA BOD 20-01 — Develop and publish a vulnerability disclosure policy](https://www.cisa.gov/news-events/directives/bod-20-01-develop-and-publish-vulnerability-disclosure-policy)
- [DOJ 2022 CFAA policy revision — good-faith security research](https://www.justice.gov/opa/pr/department-justice-announces-new-policy-charging-cases-under-computer-fraud-and-abuse-act)
- [CVSS v4.0 specification](https://www.first.org/cvss/v4-0/specification-document)

## Examples

### Example 1: First-time VDP for a 60-person B2B SaaS

Input: `product_summary="B2B analytics SaaS with multi-tenant dashboards"`,
`primary_domain="analytics.example.com"`,
`in_scope_assets=["analytics.example.com", "api.example.com/v1", "admin.example.com"]`,
`submission_channel="email"`, defaults otherwise.

Output: VDP page addressed at researchers, explicit scope (the three domains), out-of-scope
(marketing site `www.example.com`, the third-party Stripe integration, social-engineering,
DoS, physical attacks). Safe-harbor language anchored on the DOJ 2022 CFAA policy with
the no-third-party-data clause. `security@example.com` as the channel with a published
PGP key fingerprint. 72h ack / 10d triage / 30d-Critical / 60d-High SLAs. CVSS v4.0
severity rubric. 90-day coordinated-disclosure window with a CVE process via MITRE CNA.
`security.txt` ready for `/.well-known/security.txt` with a 2027-05-23 expiry. Pre-publish
checklist explicitly gates publication on counsel review.

### Example 2: VDP alongside an existing private HackerOne program

Input: `product_summary="Consumer mobile fitness app, 5M MAU"`,
`primary_domain="fitapp.example"`, `in_scope_assets=["api.fitapp.example", "fitapp iOS app bundle id com.example.fitapp", "fitapp Android package com.example.fitapp"]`,
`submission_channel="form"`, `has_bug_bounty=true`, `credit_policy="always"`.

Output: VDP page distinguishes the public VDP (no payment) from the private HackerOne
program (paid, invite-only) — researchers outside the program use the VDP, in-program
researchers use HackerOne. Submission form at `https://fitapp.example/security/report` with
explicit "no PII exfiltration as research target" clause (since the app holds health
data). Public hall-of-fame at `/security/hall-of-fame` for credit. `security.txt` lists
both channels. The coordinated-disclosure runbook bridges VDP intake into the existing
HackerOne triage queue so reporting via either channel reaches the same triager.

### Example 3: Internal-only tool (anti-trigger)

Input: "We have an internal HR portal. Write us a VDP."

Output: Skill declines to engage as a public VDP. Explains that a public VDP is a
commitment to *external* researchers, and an internal-only tool has no external research
surface — there is no audience for the policy. Recommends instead: an internal-employee
reporting channel (`security-bugs@` distribution to the security team), pointer to the
org's existing IR runbook, and inclusion in the org's annual internal pen-test scope.
Offers to draft those instead.

## See also

- `security/scaffolding-red-team-engagement` — pre-engagement scaffolding for paid red-teams
- `security/scaffolding-ai-policy-doc` — org-wide AI use policy (complementary governance)
- `security/writing-pentest-finding` (planned) — finding-write-up format for the report side
- `security/auditing-mcp-server-pre-trust` — applies when researchers report MCP-server bugs
- `workflow/writing-release-notes-as-postmortem` (planned) — postmortem-style release-notes
  pattern that pairs well with coordinated-disclosure timelines

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 for v6.0-batch-1 per PRAGMATIC discipline.
