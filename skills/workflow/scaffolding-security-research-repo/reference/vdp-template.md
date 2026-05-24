<!-- VDP template — used by scaffolding-security-research-repo. -->
<!-- Safe-harbor language adapted from the disclose.io / Bugcrowd standard -->
<!-- and DOJ "Department of Justice Policy on Vulnerability Research" (2022). -->

# Vulnerability Disclosure Policy

`<project_name>` welcomes good-faith security research. This policy defines
the scope and rules of engagement so researchers can act with confidence.

## Safe harbor

We consider security research conducted in accordance with this policy to be:

- Authorized in view of any applicable anti-hacking laws (e.g., CFAA in the
  United States, the Computer Misuse Act in the UK, similar statutes elsewhere).
  We will NOT initiate or support legal action against good-faith researchers
  whose work falls within the scope below.
- Exempt from DMCA anti-circumvention claims for research conducted on systems
  the researcher owns or for which they have explicit authorization.
- Compatible with the terms of service of the project — to the extent any ToS
  restriction would otherwise apply, this policy waives it for good-faith
  research within scope.

You are responsible for complying with all applicable laws. If a third party
initiates legal action against you for research that was clearly within this
policy, we will make this authorization known.

## Scope

In scope:

- The `<project_name>` source code, build artifacts, and any official release
  distributed via this repository or its associated package registry entries
- Documentation and reference materials shipped in this repository

Out of scope:

- Third-party dependencies (report to the upstream project directly)
- Social-engineering attacks against contributors or maintainers
- Denial-of-service testing against shared infrastructure
- Physical attacks
- Issues that require physical access to a victim's machine

## Rules of engagement

- Do not access, modify, or destroy data that does not belong to you
- Do not run automated scans against shared third-party infrastructure
- Make a good-faith effort to avoid privacy violations and service disruption
- Provide enough information to reproduce the issue
- Give us a reasonable time to fix the issue before public disclosure

## Coordinated-disclosure window

We aim to publish a fix and an advisory within **90 days** of initial report.
If a fix requires longer (complex coordination across downstream consumers,
upstream dependency fixes, etc.), we will tell you and propose a revised
timeline.

## Reporting

See [SECURITY.md](./SECURITY.md) for the reporting channel and what to include.
