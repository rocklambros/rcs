<!-- SECURITY.md template — used by scaffolding-security-research-repo. -->
<!-- Substitute <project_name>, <security_contact>, and version table. -->

# Security Policy

## Reporting a vulnerability

If you believe you have found a security vulnerability in `<project_name>`, please
report it privately by emailing **<security_contact>**. Do NOT open a public
GitHub issue, pull request, or post in any public channel.

### What to include

- A description of the vulnerability and its impact
- Steps to reproduce (proof-of-concept code is welcome but not required)
- The version of `<project_name>` you tested against
- Any suggested mitigations

### What to expect

- **Acknowledgement** within 5 business days of receipt
- **Initial triage assessment** within 10 business days
- **Coordinated disclosure** within the window documented in [VDP.md](./VDP.md)
  (default: 90 days from initial report)

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | :white_check_mark: |
| < 0.1 | :x: |

(Update this table on each release. Versions outside the supported table do
not receive security fixes — users should upgrade.)

## Disclosure

We follow coordinated disclosure. See [VDP.md](./VDP.md) for safe-harbor
language, scope, and the public-disclosure timeline.
