# Rules of Engagement (RoE) — Template

> Customize the bracketed fields. The signed PDF (or signed Markdown commit) is the
> binding authorization artifact for the engagement. Without a signature, no test
> traffic may flow.

## 1. Parties

- **Customer / Authorizer:** [Customer legal name + authorizer name + role]
- **Testing party:** [Testing-firm legal name + lead tester name]
- **Engagement identifier:** [unique id, e.g. `ACME-2026-06`]

## 2. Engagement type

[paid-pentest | internal-ctf | bug-bounty-submission]

## 3. Time window

- **Start:** [ISO date + timezone]
- **End:** [ISO date + timezone]
- Activity outside this window is unauthorized. Renewals require a fresh signature.

## 4. In-scope assets

| Asset | Type | Notes |
|---|---|---|
| [hostname or URL] | [web app / API / network / mobile] | [protocol, ports, account types allowed] |

Wildcards: only as written verbatim in the SOW or program brief.

## 5. Allowed attack classes

- [ ] Web application
- [ ] API
- [ ] Network (perimeter only, no internal lateral movement unless authorized in §6)
- [ ] Mobile app
- [ ] Social engineering (only if checked AND specifically scoped below)
- [ ] Physical (only if checked AND specifically scoped below)

## 6. Out-of-scope (explicit)

Default-blocked unless explicitly overridden:

- Denial-of-service (volumetric, resource-exhaustion, cost-amplification)
- Social engineering of customer employees or partners
- Third-party hosted services (SaaS / vendor-managed)
- Sibling subdomains in multi-tenant infrastructure
- Real customer PII exfiltration (canaries only)
- Persistence beyond minimum proof-of-impact

## 7. Authorization

- **Customer authorizer signature:** _________________
- **Date:** _________________
- **Testing-party lead signature:** _________________
- **Date:** _________________

## 8. Contact list

| Role | Name | Phone | Email | Backup |
|---|---|---|---|---|
| Customer authorizer | | | | |
| Customer technical lead | | | | |
| Customer IR contact | | | | |
| Testing party lead | | | | |
| Testing party backup | | | | |

## 9. Communications channels

- **Daily standup channel:** [Slack / Teams / email thread]
- **Findings drop:** [secure file-share, signed-PDF upload, bug-bounty platform]
- **Emergency / halt channel:** [phone tree + backup channel]

## 10. Safe harbor

The customer agrees the testing-party's good-faith actions within scope and time window will not result in civil or criminal claims, and that findings disclosed to the customer under this RoE are subject to the embargo in §11.

## 11. Disclosure embargo

Public disclosure of findings is embargoed for [90] days after delivery of the final report, unless the customer publishes earlier or extends the embargo in writing.

## 12. Deliverables

- Final report in [pdf / markdown / json / platform format]
- Per-finding evidence pack (request/response captures, screenshots, hashed PoC refs)
- Retest plan and verification window

## 13. Termination

Either party may terminate the engagement with [24h] written notice. On termination, all testing activity halts immediately, evidence is preserved in append-only storage, and the partial-engagement report is delivered within [5 business days].
