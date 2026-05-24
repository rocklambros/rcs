# Security Track

For security engineers, AI red-teamers, CISOs, GRC engineers, and AI security researchers.

This track encodes day-job disciplines: MCP pre-trust auditing, vulnerability triage, threat modeling (methodology-only — bring your own catalog), pen-test scaffolding, supply-chain hygiene, and adversarial-ML eval harnesses.

## Shipped skills

| Skill | What it does | When to use | Σ |
|---|---|---|---|
| [`auditing-pinned-dependencies`](auditing-pinned-dependencies/) | Greps install commands and CI for unpinned deps (`npx -y`, `@latest`, `pip install` without `==`, unpinned `uvx --from git+`, `curl|sh`); per-file findings with pinned-form suggestions | When reviewing a new repo, evaluating an MCP install command, or hardening a project against supply-chain risk | 19 |
| [`auditing-mcp-server-pre-trust`](auditing-mcp-server-pre-trust/) | Six-check audit (license, source, network, version pin, secret handling, tool subset) of any proposed MCP server before pre-trust | Whenever you are about to add an MCP server to your Claude Code config | 18 |
| [`triaging-vulnerability-findings`](triaging-vulnerability-findings/) | SARIF triage: parse → dedupe across tools → reachability → EPSS → rank → suppress-with-rationale → PR comment | When the user has SARIF / multi-tool finding dumps and needs to prioritize | 14 |
| [`auditing-transitive-vulnerabilities`](auditing-transitive-vulnerabilities/) | SBOM/lockfile + Grype/Trivy/OSV scan → dep-path → EPSS → reachability (callgraph/import-only) → ranked remediation | When deep transitive CVEs need prioritization and direct-dep scans aren't enough | 13 |
| [`threat-modeling-llm-app`](threat-modeling-llm-app/) | STRIDE-style threat-modeling walk over an LLM application (chatbot, RAG, single-turn completion API, content-generation pipeline) using a user-supplied catalog (OWASP LLM Top 10, MITRE ATLAS, MAESTRO, or custom); inventories components and trust boundaries (user→app, app→model, retriever→context, model→tool, model→output sink), maps each catalog item to STRIDE categories at each boundary, and produces an auditable threat register with likelihood, impact, mitigation, and owner per finding; methodology only — never ships a bundled catalog | The user is designing, reviewing, or shipping an LLM-powered application and needs a structured threat model before deployment; producing a threat register against a named catalog the user supplies; "threat-model my chatbot" / "STRIDE for our LLM" / "map OWASP LLM Top 10 to our architecture" requests | 13 |
| [`running-prompt-injection-eval`](running-prompt-injection-eval/) | Runs a generic single-turn prompt-injection eval harness against a deployed LLM using a user-supplied corpus — 7-step workflow (pre-flight RoE + scope + kill-switch + log-store check, corpus validation, dry-run, full dispatch, four-class outcome classification, per-class FN/FP analysis against expected_blocking_classes, finding pack with deduplicated signatures); refuses without a signed RoE, without a corpus, or against unauthorized production targets | Pre-deployment safety eval, guardrail / filter audit, regression suite gating a model swap or system-prompt change, or any authorized engagement with a single-turn injection corpus in hand | 13 |
| [`generating-sbom`](generating-sbom/) | CycloneDX / SPDX SBOM from any stack via syft + per-ecosystem fallbacks; software components only (not AI-BOM) | When the user needs an SBOM for compliance, vendor questionnaire, or downstream vuln scanning | 12 |
| [`scaffolding-red-team-engagement`](scaffolding-red-team-engagement/) | Scaffolds an AI red-team engagement before any attack runs — produces signed Rules of Engagement, in-scope / out-of-scope inventory, kill-switch protocol with named halt-authorities + ≤10-minute time-to-isolate, tamper-evident append-only logging schema with hash-chained / anchored records, and a coordinated-disclosure reporting template; refuses on solo personal jailbreak experiments where no third-party authorizer exists | About to red-team a deployed LLM application or agentic system for a paid engagement / internal team rotation / bug-bounty submission / regulatory exercise, or when an existing red-team has been operating without a signed RoE | 12 |
| [`running-multiturn-attack-suite`](running-multiturn-attack-suite/) | Runs a multi-turn attack suite — escalation, state-poisoning, retrieval-injection, role-drift, context-overflow, tool-state-abuse — with per-script session isolation, per-turn state snapshots (token count, citations, tool calls, summarization-event detection), per-turn (advanced/landed/rolled-back/stalled/inconclusive) AND per-script (passed/blocked/partial/inconclusive) outcome classes, cross-script pattern analysis, and turn-by-turn repro per finding; refuses on single-turn-only targets where multi-turn semantics do not apply | Conversational chatbot, agentic system with memory or summarization, retrieval-augmented system where poisoned context lingers, or any target where one turn alone is insufficient to land the attack | 12 |
| [`running-encoded-payload-suite`](running-encoded-payload-suite/) | Runs an encoded-payload filter-bypass audit — base64, hex, ROT13, URL encoding, Unicode confusables, zero-width, RTL override, leetspeak, language-switch, tokenizer-boundary tricks — with mandatory filter-presence sanity check, mandatory plain-text baseline, exclusion of never-blocked payloads from the gap matrix, per-encoding bypass-rate aggregation (NOT raw counts), and systematic-class findings (not per-payload duplicates); refuses against base models with no safety filter to bypass | Production safety-filter audit, pre-deployment regression suite gating a filter update, bug-bounty targeting filter-bypass via encoding, or defense-in-depth assessment of a multi-layer safety stack | 12 |
| [`threat-modeling-agentic-systems`](threat-modeling-agentic-systems/) | Threat-modeling walk for autonomous agents and multi-agent systems (tool-using agent, planner-executor loop, multi-step workflow, multi-agent collaboration) using a user-supplied catalog (MAESTRO, MITRE ATLAS, OWASP Agentic Security Initiative, or custom); extends LLM-app threat modeling with agent-specific boundaries (planner↔executor, memory↔next-turn, tool-result↔next-prompt, agent↔agent) and adds agentic concerns (excessive agency, goal hijacking, memory poisoning, runaway loops, tool composition, multi-agent cascade); mandatory runaway-loop / blast-radius subsection; methodology only — never ships a bundled catalog | The user is designing, reviewing, or shipping an autonomous agent that plans, calls tools, persists state across turns, or coordinates with other agents; producing a threat register against an agentic catalog the user supplies; reviewing an agent before deployment, audit, or compliance sign-off | 11 |

## Drafting skills

| Skill | What it does | Σ | Status |
|---|---|---|---|
| [`applying-secure-coding-rules`](applying-secure-coding-rules/) | Applies a user-supplied corpus (semgrep / SARIF / markdown / YAML / claude-secure-coding-rules) to a project, producing per-finding fixes and a skipped-rules report; refuses to fabricate rules from training memory | 15 | 🔨 drafting (2 of 3 eval scenarios failed materially during v4-batch-2 validation; anti-fabrication discipline empirically validated 3/3; see CHANGELOG for root-cause and promotion path) |

## Planned skills

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `scaffolding-CTF-engagement` | Engagement scope, rules of engagement, finding template, severity rubric | 10 | 📝 planned |
| `writing-pentest-finding` | CVSS scoring walk, repro steps, remediation pattern | 11 | 📝 planned |
| `running-cloud-IR-runbook` | Triage → evidence collection → comms → lessons-learned | 10 | 📝 planned |
| `writing-vdp-and-coordinated-disclosure` | Vulnerability disclosure policy template + coordinated-disclosure timeline | 12 | 📝 planned |
| `scaffolding-security-research-repo` | SECURITY.md, threat-model.md template, gitleaks/semgrep pre-commit, VDP, license | 13 | 📝 planned |
| `verifying-sigstore-signatures` | Cosign verification, in-toto policy check | 10 | 📝 planned |
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
