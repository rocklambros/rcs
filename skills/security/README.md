# Security Track

For security engineers, AI red-teamers, CISOs, GRC engineers, and AI security researchers.

This track encodes day-job disciplines: MCP pre-trust auditing, vulnerability triage, threat modeling (methodology-only — bring your own catalog), pen-test scaffolding, supply-chain hygiene, and adversarial-ML eval harnesses.

## Shipped skills

_Populated in Phase 1._

| Skill | What it does | When to use | Σ |
|---|---|---|---|

## Planned skills

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-mcp-server-pre-trust` | Six-check audit (license, source, network egress, version pin, secret handling, tool subset) before registering an MCP server | 18 | 📝 planned (Phase 1) |
| `auditing-pinned-dependencies` | Greps for unpinned installs, flags supply-chain risk | 19 | 📝 planned (Phase 2) |
| `threat-modeling-llm-app` | Walks an LLM app through STRIDE-style threats; user supplies the checklist as input | 13 | 📝 planned |
| `threat-modeling-agentic-systems` | MAESTRO/STRIDE walk for an agent design; user supplies the catalog | 11 | 📝 planned |
| `triaging-vulnerability-findings` | SARIF processing: dedupe → EPSS-enrich → blast-radius → suppress with pragma | 14 | 📝 planned |
| `applying-secure-coding-rules` | Surfaces secure-coding rules per language + framework + AI/ML stack | 15 | 📝 planned |
| `scaffolding-CTF-engagement` | Engagement scope, rules of engagement, finding template, severity rubric | 10 | 📝 planned |
| `writing-pentest-finding` | CVSS scoring walk, repro steps, remediation pattern | 11 | 📝 planned |
| `running-cloud-IR-runbook` | Triage → evidence collection → comms → lessons-learned | 10 | 📝 planned |
| `writing-vdp-and-coordinated-disclosure` | Vulnerability disclosure policy template + coordinated-disclosure timeline | 12 | 📝 planned |
| `scaffolding-security-research-repo` | SECURITY.md, threat-model.md template, gitleaks/semgrep pre-commit, VDP, license | 13 | 📝 planned |
| `generating-sbom` | CycloneDX/SPDX SBOM from any stack | 12 | 📝 planned |
| `auditing-transitive-vulnerabilities` | Dependency graph walk, EPSS scoring | 13 | 📝 planned |
| `verifying-sigstore-signatures` | Cosign verification, in-toto policy check | 10 | 📝 planned |
| `scaffolding-red-team-engagement` | RoE, scope, kill-switch, logging template for AI red-team | 12 | 📝 planned |
| `running-prompt-injection-eval` | Generic harness; corpus is user-supplied | 13 | 📝 planned |
| `running-multiturn-attack-suite` | Multi-turn prompt-injection eval harness | 12 | 📝 planned |
| `running-encoded-payload-suite` | Base64 / ROT13 / unicode / zero-width payload harness | 12 | 📝 planned |
| `evaluating-jailbreak-judge-agreement` | Cohen's κ between LLM judges on jailbreak outcomes | 13 | 📝 planned |
| `running-adversarial-perturbation-suite` | FGSM / PGD / AutoAttack for vision/tabular | 8 | 📝 planned |
| `auditing-rlhf-reward-hacking` | Reward-model probing for goodharting | 7 | 📝 planned |
| `scrubbing-PII-with-policy` | PII detection + redaction with user-supplied policy | 12 | 📝 planned |
| `verifying-training-data-erasure` | DSR-proof workflow for AI: dataset → embeddings → fine-tune | 10 | 📝 planned |
| `interpreting-vendor-questionnaire-skeptically` | Skeptical pass over vendor security questionnaires | 9 | 📝 planned |
| `scaffolding-ai-policy-doc` | AI use policy template | 10 | 📝 planned |

## Cross-track references

- Most security work pairs with `workflow/` for cross-cutting hygiene (seed, dedup, reproducibility).
- For Claude Code skill / MCP / hook authoring, see `claude-code-meta/`.

## Track-specific conventions

- Security skills MUST disclaim that they are tooling, not professional advice (per repo-wide disclaimer in root README; restate per skill).
- Skills that touch credentials, secrets, or supply-chain artifacts MUST document the exact files they read and write in the `## Outputs` section.
