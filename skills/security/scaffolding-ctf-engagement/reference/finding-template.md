# Finding write-up template

> One finding per file. Filename: `findings/<engagement-id>-<NNN>-<short-slug>.md`
> where `<NNN>` is a zero-padded sequence number per engagement.

```markdown
# [Finding title — one line, ≤ 80 chars]

- **Engagement id:** [from RoE]
- **Finding id:** [engagement-id]-[NNN]
- **Severity band:** [Critical | High | Medium | Low | Informational]
- **CVSS v3.1 base score:** [N.N]
- **CVSS v3.1 vector:** [`CVSS:3.1/AV:.../AC:.../PR:.../UI:.../S:.../C:.../I:.../A:...`]
- **Status:** [draft | submitted | accepted | rejected | duplicate | won't-fix]
- **Date discovered:** [ISO date]
- **Reporter:** [tester handle]

## Affected asset

- **Host / URL:** [exact host + port + path]
- **Endpoint / parameter:** [endpoint path, HTTP method, parameter name]
- **Account / role:** [auth state required: unauthenticated, user role, admin]

## Summary

[One paragraph explaining what the vulnerability is, in plain language.]

## Reproduction

Step-by-step, numbered, replay-able by a reader who has the engagement environment:

1. [Setup: auth, prerequisites]
2. [The triggering request — full curl / HTTP payload]
3. [The observed response — relevant fields only, with PII redacted]
4. [Confirmation: what the reader should see that demonstrates impact]

Include the exact request and response (sanitized) in evidence.

## Impact

[Business consequence in concrete terms — what an attacker gains, what the customer loses. Bullet the impacts:]

- [Data exposure: which data class, how many records, accessed by whom]
- [System integrity: what can be modified, by whom, with what side effects]
- [Availability: what gets denied, to whom, for how long]
- [Lateral movement: what new attack surface this enables]

## Remediation

[Specific fix — code-level direction when possible:]

1. [The recommended fix, at the right level: input validation, auth check, library upgrade, config change]
2. [Why the alternative ("just rate-limit it") is insufficient]
3. [Test to add: regression test that would have caught this]

## Evidence

- Request capture: `evidence/[finding-id]/request.http`
- Response capture: `evidence/[finding-id]/response.http`
- Screenshot: `evidence/[finding-id]/screenshot.png`
- PoC payload: `evidence/[finding-id]/payload.txt` (hashed in attack log)

## References

- [CVE-YYYY-NNNNN] (if applicable)
- [OWASP category link]
- [Vendor advisory link]

## Findings chain (if applicable)

If this finding chains with others to a higher-impact path, list the chain:

1. [Finding-id A] (Low) →
2. [Finding-id B] (Medium) →
3. [This finding] (combined: High)

Reference the chain in each linked finding.
```

## Severity-band quick reference

| Band | CVSS base | Examples |
|---|---|---|
| Critical | 9.0 – 10.0 | Unauth RCE, auth bypass on prod, mass-PII exfiltration via SSRF |
| High | 7.0 – 8.9 | Authenticated RCE, IDOR exposing other tenants, stored XSS in admin |
| Medium | 4.0 – 6.9 | Reflected XSS, CSRF on sensitive action, weak crypto on token |
| Low | 0.1 – 3.9 | Verbose error, missing security header, rate-limit gap |
| Informational | 0.0 | Hygiene observations, no exploitable impact |
