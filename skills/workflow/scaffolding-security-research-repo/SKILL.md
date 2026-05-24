---
name: scaffolding-security-research-repo
description: >
  Scaffolds a greenfield security-research repository with the security-specific
  artifacts that distinguish it from a generic project: SECURITY.md, a starter
  threat-model template, a vulnerability disclosure policy (VDP), gitleaks +
  semgrep wired into pre-commit, an MIT or Apache-2.0 license appropriate for
  security tooling, a security-specific .gitignore that ignores common artifact
  classes (PCAPs, exploit binaries, credential dumps, raw payloads), and a
  CONTRIBUTING.md that documents the coordinated-disclosure expectation. Use
  whenever the user is starting a NEW security-research, AI-security, red-team,
  defensive-tooling, or vulnerability-research project from an empty directory.
  Refuses to scaffold on top of an existing mature project (different concern)
  and refuses for non-security greenfield work (hands off to
  scaffolding-ml-research-notebook).
version: 0.1.0
status: shipped
track: workflow
audience: [security-eng, ai-security, devops, skill-author]
evidence:
  - genai_agentic_incidents
  - ai-security-framework-crosswalk
  - incident-rank-validation
last-updated: 2026-05-23
---

# Scaffolding a Security-Research Repository

## When to use

Trigger this skill when the user:

- Is starting a brand-new security-research, AI-security, red-team tooling, defensive-tooling, vulnerability-research, threat-modeling, or incident-corpus project from an empty directory
- Asks "how should I structure a security project from day one" or "what files does a security-research repo need"
- Is about to publish a security tool / dataset / corpus and needs the disclosure / governance scaffolding before first commit
- Wants gitleaks + semgrep wired into pre-commit from commit zero (not added later, after credentials have already leaked)

## When NOT to use

Skip this skill and hand off when:

- The project is not security-focused — use `workflow/scaffolding-ml-research-notebook` (ML/DS) or `workflow/scaffolding-llm-eval-harness` (LLM evals)
- The project already exists with a populated structure — this skill scaffolds greenfield only; adding security artifacts to a mature project is a separate retrofit task
- The work is a one-off CTF practice run or solo experiment — the SECURITY.md + VDP + disclosure machinery exceeds the benefit (see `security/scaffolding-red-team-engagement` if you need RoE for a paid engagement instead)
- The user wants a generic open-source-project template — that is a different scaffold (no skill exists yet)

## Quick start

User: *"I'm starting a public repo to release a tool that fuzzes LLM safety filters. Empty directory. Set me up properly."*

Skill walks the 10-step checklist (Workflow below), produces: `SECURITY.md` (contact + supported versions + disclosure timeline), `VDP.md` (safe-harbor language + scope), `THREAT-MODEL.md` (starter STRIDE / OWASP-LLM-style template the maintainer fills in), `CONTRIBUTING.md` (coordinated-disclosure expectation), `LICENSE` (Apache-2.0 default for security tooling — patent-grant matters), `.gitignore` (security-specific patterns including PCAPs, exploit binaries, credential dumps, payload corpora), `.pre-commit-config.yaml` (gitleaks + semgrep + ruff), `.github/ISSUE_TEMPLATE/security-issue.md` (private-channel redirect), and a README with the responsible-use note.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| project_name | string | yes | — | The project slug. Used for the repo dir name, README header, and SECURITY.md references. |
| project_kind | "offensive-tool" \| "defensive-tool" \| "research-corpus" \| "threat-modeling" \| "ai-red-team" | no | "defensive-tool" | Drives which threat-model template gets scaffolded and which language goes in the VDP. |
| license | "Apache-2.0" \| "MIT" \| "AGPL-3.0" | no | "Apache-2.0" | License file to write. Apache-2.0 is the default for security tooling because of the explicit patent grant; MIT is acceptable for libraries with no patent exposure; AGPL-3.0 only when the user explicitly wants strong copyleft. |
| security_contact | email | yes | — | The security@... or named email that lands in SECURITY.md. Without a real address, SECURITY.md is theater. |
| disclosure_window | int (days) | no | 90 | Coordinated-disclosure window written into VDP.md. 90 days is the most common standard (Google Project Zero, CERT/CC, ZDI). |
| include_pre_commit | bool | no | true | Whether to scaffold gitleaks + semgrep + ruff hooks. |

## Workflow

Copy this checklist into the response and check off each item as the scaffold lands:

```
Scaffold progress:
- [ ] 1. Verify empty target directory (refuse if any project structure exists)
- [ ] 2. Verify security_contact arg is a real email; refuse if placeholder
- [ ] 3. Write SECURITY.md (contact, supported versions, disclosure window)
- [ ] 4. Write VDP.md (safe-harbor language, scope, out-of-scope)
- [ ] 5. Write THREAT-MODEL.md (starter template appropriate to project_kind)
- [ ] 6. Write CONTRIBUTING.md (coordinated-disclosure expectation for contributors)
- [ ] 7. Write LICENSE file (Apache-2.0 default — patent grant matters for security tooling)
- [ ] 8. Write .gitignore (security-specific: PCAPs, exploit binaries, credential dumps, payload corpora)
- [ ] 9. Write .pre-commit-config.yaml (gitleaks + semgrep + ruff)
- [ ] 10. Write .github/ISSUE_TEMPLATE/security-issue.md (redirect to private channel)
- [ ] Print "what's next" pointer (run gitleaks against history, install hooks, fill in TODO blocks)
```

### Step 1 — Verify empty target

Same discipline as `scaffolding-ml-research-notebook`: refuse if `SECURITY.md`, `LICENSE`, `README.md` with content, `pyproject.toml`, `src/`, `.git/` with > 0 commits exist. Greenfield only.

### Step 2 — Verify security_contact

A SECURITY.md without a real reporting address is worse than no SECURITY.md — it signals "we have a process" but routes nothing. Refuse if the argument looks like a placeholder (`security@example.com`, `your-email-here`, etc.).

### Step 3 — SECURITY.md

Anthropic-style SECURITY.md: contact email, response SLA (e.g., "we acknowledge within 5 business days"), supported versions table, scope (in / out), and the disclosure timeline target. See `reference/security-md-template.md`.

### Step 4 — VDP.md

Vulnerability Disclosure Policy with explicit **safe-harbor** language (Bugcrowd / DOJ-aligned phrasing — researchers acting in good faith will not be pursued under CFAA / DMCA / contract). Document scope, out-of-scope, and the coordinated-disclosure window. See `reference/vdp-template.md`.

QC.1 (NIST SP 800-218) requires a VDP for any public project — this is one of the gates Rock's harness checks for.

### Step 5 — THREAT-MODEL.md

A starter template appropriate to `project_kind`:

- `offensive-tool` / `ai-red-team` → "who can use this for harm" + dual-use mitigation + abuse-resistant publication strategy
- `defensive-tool` → STRIDE walk for the deployed system + assumed-adversary capability
- `research-corpus` → re-identification / leakage risk + downstream-misuse risk + license-of-data
- `threat-modeling` → meta-skeleton: the threat model itself is the deliverable

The template is a starter, not a finished threat model — the maintainer fills in TODO blocks. See `reference/threat-model-templates/`.

### Step 6 — CONTRIBUTING.md

States the coordinated-disclosure expectation: vulnerabilities go to the SECURITY.md address, NOT a public issue, NOT a PR. Cite the VDP. Documents the PR-and-issue workflow for non-security contributions normally.

### Step 7 — LICENSE

Default Apache-2.0. Reasoning (recorded in the scaffold's "what's next" output): security tooling frequently includes novel algorithms or detection techniques; the explicit Apache-2.0 patent grant protects downstream users from patent-troll claims. MIT lacks this. AGPL only if the user explicitly wants strong copyleft.

### Step 8 — .gitignore

Security-specific patterns layered on top of the standard set:

```
# Payload / exploit artifacts
*.pcap
*.pcapng
exploits/*.bin
exploits/*.elf
payloads/*.raw

# Credentials / secrets (defense-in-depth alongside gitleaks)
*.pem
*.key
*.p12
*.kdbx
.env
.env.*
!.env.example

# Test corpora that might contain sensitive material
corpus/raw/
corpus/private/
```

Plus the generic Python / Node / OS patterns as in `scaffolding-ml-research-notebook/reference/gitignore-template`.

### Step 9 — .pre-commit-config.yaml

Wires:

- **gitleaks** — detect-secrets-in-staged-changes. Blocks the credential class entirely from entering git history.
- **semgrep** — language-aware SAST. Default to the `p/security-audit` rule pack; project owner can narrow.
- **ruff** — lint + format for Python.

See `reference/pre-commit-security-template.yaml`.

### Step 10 — .github/ISSUE_TEMPLATE/security-issue.md

A GitHub issue template that REDIRECTS the reporter to the private channel (SECURITY.md email) instead of opening a public issue. Reduces accidental public-disclosure of in-the-wild vulnerabilities.

## Outputs

A populated repository with the following files (greenfield, all new):

```
<project_name>/
  README.md
  SECURITY.md
  VDP.md
  THREAT-MODEL.md
  CONTRIBUTING.md
  LICENSE
  .gitignore
  .pre-commit-config.yaml
  .github/
    ISSUE_TEMPLATE/
      security-issue.md
  src/<pkg>/__init__.py        (stub — language-agnostic; can be removed if non-Python)
```

Plus a printed "what's next" 5-line action list:

```
Done. Next:
  pre-commit install                     # wire git hooks (gitleaks runs from commit 1)
  gitleaks detect --source . --no-git    # baseline scan; should be clean on empty repo
  Edit THREAT-MODEL.md TODO blocks       # the threat model is yours to fill in
  Edit SECURITY.md supported-versions    # specific to your release plan
  git add -A && git commit -m "Initial security-research scaffold"
```

## Failure modes

Known pitfalls and how this skill catches them:

- **SECURITY.md with placeholder email** — signals "we have a process" but routes nothing; worst-of-both. Caught by Step 2 (refuse on placeholder address).
- **VDP without safe-harbor language** — chills good-faith research; legally exposes researchers to CFAA / DMCA / contract claims. Caught by the template providing Bugcrowd/DOJ-aligned safe-harbor language as the default body.
- **gitleaks added later (after credentials already leaked)** — credentials in git history are permanent without history rewrite. Caught by Step 9 wiring gitleaks at commit zero.
- **Wrong license picked (MIT instead of Apache-2.0)** — for security tooling with novel techniques, MIT leaves users exposed to patent claims. Caught by Apache-2.0 default + the "what's next" reasoning note.
- **Threat-model template that the user never fills in** — a TODO-block document treated as done. Caught by THREAT-MODEL.md template using explicit `<!-- TODO: fill in -->` markers + the "what's next" pointer.
- **Wrong skill engaged for non-security project** — would miss `data/`, `notebooks/`, seed helper. Caught by "When NOT to use" handoff to `scaffolding-ml-research-notebook`.

## References

- `reference/security-md-template.md` — SECURITY.md skeleton
- `reference/vdp-template.md` — VDP.md with Bugcrowd/DOJ-aligned safe-harbor language
- `reference/threat-model-templates/` — per-project_kind starter templates
- `reference/pre-commit-security-template.yaml` — gitleaks + semgrep + ruff config
- `reference/security-issue-template.md` — GitHub ISSUE_TEMPLATE that redirects to SECURITY.md
- [Bugcrowd disclose.io standard](https://disclose.io/) — the safe-harbor language reference
- [NIST SP 800-218 (SSDF)](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) — the VDP requirement (PO.4)

## Examples

### Example 1: Public AI-red-team tool (happy-path)

Input: *"I'm starting a public repo to release a tool that fuzzes LLM safety filters. Empty directory. Set me up properly. My security contact is security@rockcyber.com."*

Output: Skill walks all 10 steps. Writes SECURITY.md routing to security@rockcyber.com with 5-business-day acknowledgement SLA. Writes VDP.md with safe-harbor language scoped to good-faith research within the tool's intended testing envelope. Writes THREAT-MODEL.md from the `ai-red-team` template (dual-use mitigation + abuse-resistant publication). Picks Apache-2.0 LICENSE (patent grant). gitleaks + semgrep + ruff wired into pre-commit. .gitignore covers PCAPs + exploit binaries + payload corpora. .github/ISSUE_TEMPLATE redirects reporters to the SECURITY.md address. Prints the 5-line "what's next" pointer.

### Example 2: Non-security ML project (anti-trigger handoff)

Input: *"I'm starting a project to train a fraud-detection classifier. Empty directory. Set me up."*

Output: Skill hands off to `scaffolding-ml-research-notebook` — explains that fraud detection is an ML project, not a security-research project. (The distinction: security-research projects need SECURITY.md + VDP + threat-model because they intentionally study attacks or release defensive tools; an ML classifier needs reproducible deps + seed hygiene + data layout. Some fraud-detection projects WILL also need security artifacts — at which point both scaffolds can be combined, but the primary scaffold is the ML one.)

### Example 3: SECURITY.md placeholder rejection (edge-case)

Input: *"Scaffold my security tool. security_contact = security@example.com."*

Output: Skill REFUSES to write SECURITY.md with the placeholder address. Explains that an unrouted SECURITY.md is worse than none — it signals process while dropping reports on the floor. Asks the user to provide a real reporting address (security@<project-domain>, a named maintainer's email, or a HackerOne / Bugcrowd handle).

## See also

- `workflow/scaffolding-ml-research-notebook` — sibling: greenfield for ML / data-science research
- `workflow/scaffolding-llm-eval-harness` — sibling: greenfield for LLM-eval pipelines
- `security/scaffolding-red-team-engagement` — RoE for a specific paid engagement (different concern — engagement, not repo)
- `security/auditing-pinned-dependencies` — audit that the scaffolded repo stays supply-chain-clean over time
- `workflow/running-adversarial-premortem` — pairs well after the threat model is filled in

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
