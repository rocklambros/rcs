# Agentic STRIDE × boundary — mapping examples

This file is **illustrative**, not a threat catalog. The skill always works against a user-supplied catalog (MAESTRO, MITRE ATLAS, OWASP Agentic Security Initiative, etc.). These examples calibrate how common agentic threats are typically classified, including the additional **Agent concern** column the agentic register uses.

## Notation

- **Boundary** is shorthand for the data crossings in `SKILL.md` § Step 3.
- **STRIDE letter:** S, T, R, I, D, E (same as conventional STRIDE).
- **Agent concern:** EA = Excessive-agency, GH = Goal-hijacking, MP = Memory-poisoning, RL = Runaway-loop, TC = Tool-composition, MAC = Multi-agent-cascade.

## Examples

### Planner → executor

| Threat (illustrative) | STRIDE | Concern | Notes |
|---|---|---|---|
| Planner emits a tool call with attacker-influenced arguments derived from prior tool output | T, E | TC, GH | Most common agentic vector. Executor must validate tool args before dispatch. |
| Planner exhausts iteration budget on noise / no convergence | D | RL | Iteration cap is necessary; cost cap is also recommended. |
| Planner chains low-privilege tools to achieve high-privilege effect | E | TC | E.g., read_file → upload_to_public_bucket → share_link. |

### Tool result → next prompt

| Threat (illustrative) | STRIDE | Concern | Notes |
|---|---|---|---|
| Tool output (web page, file, API response) contains content that instructs the planner | T | GH | Indirect prompt injection through the tool channel. The most underestimated agentic risk. |
| Tool output contains sensitive data the agent then leaks to a public output sink | I | EA | Read tool reads more than the agent needs, output tool publishes it. |
| Tool output is silently truncated; agent acts on partial information | T | Other | Not adversarial but still a threat to correctness. |

### Memory write → next turn

| Threat (illustrative) | STRIDE | Concern | Notes |
|---|---|---|---|
| Attacker influences a turn that writes to memory; later turns trust that memory | T | MP | Time-shifted prompt injection. |
| Memory grows unbounded; recent turns crowd out earlier safety instructions | D, T | MP, GH | Memory budget management is a security concern, not just a performance one. |
| Memory persisted across users / sessions / tenants without isolation | I | Other | Multi-tenant memory hygiene. |

### Memory read → prompt

| Threat (illustrative) | STRIDE | Concern | Notes |
|---|---|---|---|
| Long-term memory written under prior policy now affects current behavior | T | MP | Memory schema versioning + audit trail recommended. |
| Memory contains stale credentials / paths that point to since-changed resources | T | Other | Particularly painful in agents with retry-after-failure logic. |

### Identity → external system

| Threat (illustrative) | STRIDE | Concern | Notes |
|---|---|---|---|
| Agent identity (service account, GitHub App, IAM role) grants more access than the agent needs for the current task | E | EA | Per-task scoping or per-installation scoping recommended. |
| Identity is reusable across agents / tenants; one compromised agent compromises all | E | MAC | Per-instance credentials, short-lived tokens. |
| Audit log does not include which identity made which tool call | R | Other | Forensic gap. |

### Agent → agent (multi-agent)

| Threat (illustrative) | STRIDE | Concern | Notes |
|---|---|---|---|
| One agent's output is consumed as instructions by a peer agent | T, E | MAC, GH | Recursively apply the threat model. |
| Compromised orchestrator can direct workers to perform unauthorized actions | E | MAC, EA | Orchestrator-as-trust-center anti-pattern. |
| Workers collude (intentionally or via shared compromised content) to bypass any single agent's policy | E | MAC | Hardest to detect; requires cross-agent monitoring. |

### Control plane

| Threat (illustrative) | STRIDE | Concern | Notes |
|---|---|---|---|
| No iteration cap; agent can run indefinitely | D | RL | Default fail. |
| No human kill-switch / cancel path during a long-running task | E, D | EA, RL | Especially important for state-changing agents. |
| Kill-switch exists but takes effect only at iteration boundaries; ongoing tool call cannot be aborted | E | RL | Define semantics of "cancel" explicitly. |

## How to use this file

1. Identify your real agentic boundaries from the user's agent description (component count, loop structure, memory model, identity, multi-agent topology).
2. For each catalog item the user supplied, ask which agentic boundary(ies) it lives at and which STRIDE + agent-concern category(ies) it implicates.
3. Use this table to sanity-check classifications, never as a substitute for walking the user-supplied catalog.
