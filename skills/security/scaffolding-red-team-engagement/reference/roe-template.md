# Rules of Engagement (RoE) — AI Red-Team Template

> Fill in every `<<placeholder>>`. Unsigned RoE = unauthorized activity.

## 1. Parties

- **Operator (system owner):** <<legal entity name + address>>
- **Authorizer (signs this RoE):** <<name, role, email>>
- **Testing party:** <<vendor / internal team name + lead contact>>
- **Engagement ID:** <<short identifier, e.g., RT-2026-06-ACME>>

## 2. Authorization

The Authorizer represents that they hold the authority to authorize security testing against the systems listed in Section 4. This RoE constitutes written authorization for the time window in Section 3. Activity outside that window, or against systems not in Section 4, is NOT authorized.

## 3. Time window

- **Start (inclusive):** <<ISO date + timezone>>
- **End (inclusive):** <<ISO date + timezone>>

## 4. In-scope inventory

| Asset class | Identifier | Notes |
|---|---|---|
| Endpoint | <<URL>> | <<rate limit, auth method>> |
| Model deployment | <<exact model id + gateway>> | |
| Tool | <<exact tool name>> | <<read-only / write capabilities>> |
| Data class | <<e.g., synthetic-canary records only>> | |

## 5. Out-of-scope (explicit)

The following are NOT authorized targets:

- Production customer PII exfiltration as a success criterion (synthetic / canary records only)
- Third-party APIs not owned by the Operator
- Payment processing endpoints
- Denial-of-service / cost-amplification / request-flooding patterns
- Any system not enumerated in Section 4
- <<add operator-specific exclusions>>

## 6. Kill-switch

- **Abort triggers:** observed real-user impact; data exposure beyond canaries; cost spike > <<$X>>/hour above baseline; target-side rate limit at saturation; any law-enforcement contact
- **Halt authority (any one may halt):** the Authorizer; the lead red-teamer; <<named backup>>
- **Halt mechanism:** revoke red-team API keys; disable test account; network ACL block of red-team egress IPs
- **TTI target:** ≤ 10 minutes from halt-trigger to traffic-stopped
- **Preservation on halt:** logs preserved untouched; access frozen pending Authorizer review

## 7. Logging

The testing party will log every attack attempt against the schema in `reference/logging-schema.md`. Logs are stored append-only with hash-chaining or anchored periodically to make tampering detectable. Retention: <<N>> days minimum from engagement end.

## 8. Reporting

- **Delivery:** final report delivered to the Authorizer within <<N>> business days of engagement end
- **Format:** executive summary, findings (per CVSS or operator-preferred severity), repro steps, remediation, retest plan
- **Embargo:** public disclosure embargoed for <<coordinated_disclosure_days>> days after report delivery, unless the Operator publishes earlier
- **Safe-harbor:** the Operator will not pursue legal action against the testing party for actions within scope and within the time window

## 9. Confidentiality

Findings, repro details, and operator-side data observed during testing are confidential to the parties named in Section 1 until disclosure under Section 8.

## 10. Signatures

| Role | Name | Signature | Date |
|---|---|---|---|
| Authorizer | <<name>> | | |
| Testing-party lead | <<name>> | | |

Engagement begins ONLY after both signatures are captured and stored alongside the engagement-id record.
