<!-- THREAT-MODEL.md — offensive-tool / ai-red-team variant. -->
<!-- Used by scaffolding-security-research-repo for projects that intentionally -->
<!-- enable adversarial testing (AI-red-team harnesses, fuzzers, exploit dev). -->

# Threat Model — `<project_name>` (offensive / dual-use)

> **Status:** Starter template. Fill in every `<!-- TODO -->` block before
> publishing v0.2 or later.

## Intended use

Who is this tool for, and what are they authorized to do with it?

<!-- TODO: define authorized-use envelope (paid pentest, internal red team, -->
<!-- bug bounty in scope, academic research with IRB-equivalent approval). -->

## Misuse / abuse cases

How could this tool be misused, and by whom?

<!-- TODO: enumerate misuse cases (unauthorized testing, mass-targeting, -->
<!-- credential harvesting at scale, supply-chain compromise). -->

## Dual-use posture

This is a dual-use tool. Document the publication-strategy decision:

- What level of detail is in the public release? <!-- TODO -->
- What is intentionally withheld? <!-- TODO -->
- Why is the chosen level appropriate (raises the bar for naive abuse without -->
<!-- meaningfully impeding legitimate research)? <!-- TODO -->

## Abuse-resistant features

What is built into the tool to make misuse harder?

- Authentication / authorization required? <!-- TODO -->
- Rate-limiting or scope-restriction defaults? <!-- TODO -->
- Logging that would reveal misuse to a victim or to the maintainers? <!-- TODO -->
- Telemetry kill-switch? <!-- TODO -->

## Coordinated-disclosure expectations on USERS of this tool

If a user discovers a vulnerability while using this tool, what is the
expected disclosure path?

<!-- TODO: cite the upstream's VDP / SECURITY.md; cite our preferred reporting -->
<!-- chain if we maintain an aggregated disclosure channel. -->

## Residual risk

What misuse cases CANNOT be mitigated within the tool itself?

<!-- TODO: explicit list. -->
