---
name: threat-modeling-agentic-systems
description: >
  Walks a threat-modeling pass over an autonomous agent or multi-agent system
  (tool-using agent, planner-executor loop, multi-step workflow, multi-agent
  collaboration) using a user-supplied catalog (MAESTRO, MITRE ATLAS, OWASP
  Agentic Security Initiative, or a custom catalog). Extends LLM-app threat
  modeling with agent-specific boundaries — planner ↔ executor loop, memory ↔
  next-turn context, tool-result ↔ next prompt, agent ↔ agent — and adds
  agentic-specific concerns (excessive agency, goal hijacking, memory
  poisoning, runaway loops, multi-agent collusion). Methodology only — no
  bundled catalog; the user provides one. Use when the user is designing,
  reviewing, or shipping an agent system that plans, calls tools, persists
  state across turns, or coordinates with other agents.
version: 0.1.0
status: shipped
track: security
audience: [security-eng, ai-security, ml-engineer, architect]
evidence:
  - quality-contract-NIST-SP-800-218
  - claude-secure-coding-rules
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Threat Modeling an Agentic System

## When to use

Trigger this skill when the user asks for or implies one of:

- Designing a new autonomous agent (planner-executor, ReAct-style, multi-step workflow, MCP-backed agent, agentic IDE assistant)
- Designing a multi-agent system (orchestrator + workers, agent-to-agent collaboration, marketplace of agents)
- Reviewing an existing agent before deployment, audit, or compliance sign-off
- Producing a threat register against an agentic catalog the user supplies (e.g., MAESTRO, OWASP Agentic Security Initiative, MITRE ATLAS agentic techniques, an internal AI risk register)
- Phrases like "threat-model my agent", "MAESTRO for our agent", "review this agent design", "what are the threats to our planner-executor loop?"

## When NOT to use

Skip this skill and hand off when:

- The system is a single-turn LLM app with no planning loop, no persistent memory, no tool use that feeds back into the prompt → use `security/threat-modeling-llm-app` instead
- The system is pure non-LLM software (REST API, classical service) → use a conventional STRIDE / threat-modeling resource
- The user wants vulnerability *scanning* or red-team execution against a deployed agent — that is `security/running-prompt-injection-eval` (planned) or `security/running-multiturn-attack-suite` (planned); this skill produces a design-time model
- The user has not (and will not) supply a catalog — refuse to invent one. Point them at MAESTRO (public) or MITRE ATLAS (public) as a default starting catalog and stop

## Quick start

User says: "Threat-model our new code-review agent. It's a planner-executor that reads a PR diff, decides which of (lint, security-scan, run-tests, post-comment) tools to call, can call them in any order across up to 12 iterations, persists scratchpad notes between iterations, and posts a final review comment on the PR. It runs under a GitHub App identity with write access to PR comments. Use MAESTRO as the catalog."

Skill response: confirms catalog (MAESTRO), inventories agent components, identifies agent-specific boundaries (planner ↔ executor, scratchpad ↔ next-turn, tool-result ↔ next prompt), walks each MAESTRO tactic against each boundary, classifies hits, produces a register table emphasizing excessive-agency / runaway-loop / scratchpad-poisoning risks.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| agent_description | text or file path | yes | — | Description of the agent or multi-agent system: planner, executor, tools, memory, loop control, agent count, deployment identity, blast radius. |
| catalog | text, file path, or named reference | yes | — | The threat catalog the user wants to apply. Examples: "MAESTRO", "MITRE ATLAS", "OWASP Agentic Security Initiative", or an inline list. Skill refuses to invent a catalog. |
| focus | "full" \| "top-N" \| "component" | no | "full" | Restrict to top-N risks after rating, or to a single component (planner, memory, tool dispatcher). |
| likelihood_scale | "L/M/H" \| "1-5" \| custom | no | "L/M/H" | Carry through consistently. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response:

```
Agentic threat-modeling progress:
- [ ] Step 1: Confirm user-supplied catalog (refuse to proceed without one)
- [ ] Step 2: Inventory agent components (planner, executor, tools, memory, loop control, control plane, agent count)
- [ ] Step 3: Identify agentic-specific trust boundaries (in addition to LLM-app boundaries)
- [ ] Step 4: Walk catalog × boundary matrix; classify each hit by STRIDE; tag agent-specific concerns
- [ ] Step 5: Rate likelihood and impact per finding
- [ ] Step 6: Propose at least one mitigation per finding; name an owner; flag mitigations that require control-plane (not data-plane) changes
- [ ] Step 7: Produce the threat register table; list coverage gaps; produce a "runaway-loop / blast-radius" subsection
```

### Step 1: Confirm catalog

If the user did not supply a catalog, stop and request one. Public agentic-specific defaults to offer: MAESTRO, MITRE ATLAS (agentic techniques subset), OWASP Agentic Security Initiative. Do not proceed with an invented catalog.

### Step 2: Inventory agent components

In addition to the LLM-app component list, agents commonly add:

- **Planner**: the prompt + model call that decides next action
- **Executor / tool dispatcher**: the runtime that invokes tools the planner selects
- **Memory / scratchpad**: any state the agent reads or writes across iterations (working memory, episodic memory, long-term store)
- **Loop control**: iteration limit, stopping condition, escape hatch
- **Control plane**: the human-or-system that can pause, cancel, or override the agent
- **Identity**: the credentials / token / IAM role the agent runs under (and the blast radius that identity grants)
- **Agent roster**: in multi-agent systems, the list of agents and the communication topology

### Step 3: Identify agentic-specific trust boundaries

In addition to the LLM-app boundaries (covered in `security/threat-modeling-llm-app`), agents introduce:

- **Planner → executor**: planner emits a tool call; executor must validate before invoking
- **Tool result → next prompt**: tool output is fed back into the next planner call — attacker-controlled tool output becomes attacker-controlled prompt content
- **Memory write → next turn**: anything the agent writes to memory becomes part of its next prompt (memory poisoning)
- **Memory read → prompt**: long-term memory may have been written under different conditions / by different actors
- **Loop self-reference**: iteration N's output influences iteration N+1's input — small biases compound
- **Agent → agent** (multi-agent): one agent's output is another's input — same trust-boundary analysis recursively
- **Control plane → agent**: human override, pause, kill-switch — is it reachable? what if it's not?

### Step 4: Walk catalog × boundary matrix

For each item in the user-supplied catalog, identify which agentic-specific boundary(ies) it hits. Classify each hit by STRIDE. Additionally tag each row with the agent-specific concern class it represents — common classes:

- **Excessive agency**: the agent can take consequential action without authorization
- **Goal hijacking**: attacker shifts the agent's objective via injected content
- **Memory poisoning**: attacker writes content into agent memory that biases later iterations
- **Runaway loop**: agent loops without converging; resource exhaustion or unintended side effects
- **Tool-composition attack**: attacker chains low-privilege tools to achieve a high-privilege effect
- **Multi-agent collusion / cascade**: in multi-agent systems, malicious or compromised agent influences peers

### Step 5: Rate likelihood and impact

Use the user's scale. Note: impact ratings for agents often differ from LLM-app impact ratings — an agent with a refund tool and a 12-iteration loop has a higher blast-radius ceiling than a single-turn chatbot with the same tool.

### Step 6: Propose mitigations

Each row needs a mitigation + owner. Tag whether the mitigation is data-plane (input filter, output filter, validation) or control-plane (iteration cap, human-in-the-loop gate, kill switch, identity scoping). Agentic mitigations frequently require control-plane changes; flag rows where a data-plane mitigation alone is insufficient.

### Step 7: Produce register + gap list + runaway-loop section

The register columns are the same as `threat-modeling-llm-app` plus an "Agent concern" column (Excessive-agency / Goal-hijacking / Memory-poisoning / Runaway-loop / Tool-composition / Multi-agent-cascade / Other). Add a dedicated subsection: "Runaway-loop / blast-radius" — for each tool the agent can call, list the maximum effect of N invocations within the iteration cap, and confirm an iteration cap exists. If no iteration cap, that is automatically a high-risk finding.

## Outputs

A markdown report:

1. **Catalog cited** — name + version of the user-supplied catalog
2. **Component inventory** — agent-specific components
3. **Trust boundary diagram** — text-based, including the iteration loop
4. **Threat register table** — with the agent-concern column
5. **Runaway-loop / blast-radius subsection** — per-tool worst-case at the iteration cap
6. **Coverage-gap list** — catalog items with no register row, boundaries with no catalog coverage
7. **Top risks** — the 3-to-5 highest-risk rows for executive summary, prioritizing control-plane gaps

## Failure modes

- **Catalog invention** — the skill writes its own list of "common agent threats" instead of using the user-supplied catalog. Caught by: Step 1 refuses to proceed without a named catalog; report must cite catalog + version in section 1.
- **LLM-app-only thinking** — treating the agent as a single-turn LLM call and missing planner-loop, memory, and tool-result-as-prompt boundaries. Caught by: Step 3 explicitly enumerates agentic boundaries.
- **No iteration-cap check** — failing to confirm whether a runaway loop is bounded. Caught by: Step 7's runaway-loop subsection is mandatory.
- **Data-plane mitigation fallacy** — proposing only input/output filters for threats that need a control-plane fix. Caught by: Step 6 tags each mitigation as data-plane or control-plane and flags insufficient combinations.
- **Identity-blast-radius silence** — failing to note what the agent's identity can do outside the intended scope. Caught by: Step 2 inventories identity; the register must include at least one row about identity / IAM blast radius.

## References

- `reference/agentic-stride-mapping.md` — illustrative mappings of common agentic threats to STRIDE + agent-concern classes
- `reference/register-template.md` — the agentic threat-register table template with the agent-concern column
- MAESTRO framework (public docs from the framework's home)
- MITRE ATLAS — agentic techniques subset: https://atlas.mitre.org/
- OWASP Agentic Security Initiative: https://genai.owasp.org/initiatives/#agentic-security-initiative
- `security/threat-modeling-llm-app` — the LLM-app-only sibling

## Examples

### Example 1: Code-review agent with 4 tools and a 12-iteration loop (happy-path)

Input: "Threat-model our planner-executor code-review agent. Reads a PR diff, can call lint / security-scan / run-tests / post-comment in any order up to 12 iterations, persists scratchpad between iterations, posts a final review comment under a GitHub App identity with write access to PR comments. Catalog: MAESTRO."

Output: Skill confirms catalog. Inventories: planner (GPT-4o-mini call), executor (tool dispatcher), 4 tools, scratchpad memory, 12-iteration cap, GitHub App identity with `pull_requests:write`. Identifies agentic boundaries: planner → executor, tool-result → next prompt (lint output flows back), scratchpad → next prompt, identity → GitHub (blast radius: any PR the App is installed on). Walks MAESTRO tactics. Top concerns: (a) tool-result-as-prompt — a malicious diff could contain comments that the agent treats as instructions [Goal-hijacking + Tampering]; (b) post-comment + GitHub-App identity = excessive agency to publish on PRs across the org [Excessive-agency + Elevation]; (c) 12-iteration loop with no cost cap [Runaway-loop + DoS]; (d) scratchpad reuse across iterations [Memory-poisoning]. Mitigations: tag PR-diff content as untrusted, validate post-comment tool args against schema, require human approval for cross-PR posts, add per-run cost cap in addition to iteration cap. Most mitigations are control-plane (iteration cap, cost cap, human-approval gate). Identity row notes the GitHub App could in principle post to every PR — recommends scoping the App installation to a single repo.

### Example 2: Single-tool agent with one fixed tool (edge-case)

Input: "Threat-model our research agent. It has exactly one tool: web_search(query). It can call it up to 5 times. Then it produces a final answer. No memory across runs. Catalog: OWASP Agentic Security Initiative."

Output: Skill confirms catalog. Notes the system is on the boundary between LLM-app and agent — has a loop and tool use, but no persistent memory and a single read-only tool. Component inventory: planner, executor, one tool, 5-iteration cap, no memory. Identifies relevant agentic boundaries: planner → executor (small surface), tool-result → next prompt (web_search results are attacker-controllable content — high relevance). Walks OWASP ASI items. Most agentic concerns (memory poisoning, multi-agent collusion) have low or no applicability — listed in gap section with rationale. Concentrates on: (a) tool-result-as-prompt (web pages can carry injected instructions); (b) goal hijacking via injected content. Identifies that for a single read-only tool the blast radius is bounded by the tool's permissions; recommends confirming the web_search tool itself does not have side effects. Notes that if a second tool were added later this assessment must be re-run.

## See also

- `security/threat-modeling-llm-app` — sibling for single-turn LLM apps (no agentic loop)
- `security/auditing-mcp-server-pre-trust` — applies when agent tools are exposed via MCP
- `security/auditing-pinned-dependencies` — supply-chain hardening of the agent's runtime stack
- `workflow/adversarial-premortem-single` — complementary failure-mode discovery for the agent design

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored fresh per RCS v4-batch-3 (threat-modeling cluster); methodology only, no bundled catalogs per the public-skills-repo design
