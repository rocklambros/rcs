# Agentic threat register — table template

Use this template to render the agentic threat-modeling output. One row per (catalog-item, boundary, STRIDE-category) triple. The **Agent concern** column tags the agentic class (EA / GH / MP / RL / TC / MAC / Other).

```markdown
## Agentic threat register — <agent-name> against <catalog-name> v<version>

| # | Catalog item | Boundary | STRIDE | Agent concern | Likelihood | Impact | Risk | Mitigation (data-plane / control-plane) | Owner | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | MAESTRO: tool-result injection | Tool result → next prompt | T | GH | H | M | H | data-plane: tag tool output as untrusted; control-plane: re-prompt before tool dispatch | ai-platform | Highest residual risk after mitigations. |
| 2 | MAESTRO: runaway loop | Loop self-reference | D | RL | M | H | H | control-plane: iteration cap of 12 (existing); add per-run cost cap; add no-progress detection | sre + ai-platform | Cost cap is missing in current design. |
| 3 | OWASP ASI: excessive agency on write tool | Planner → executor (post_comment) | E | EA | M | H | H | control-plane: require human approval for cross-PR posts; scope GitHub App install to single repo | security-eng | Identity blast-radius row. |
| 4 | OWASP ASI: memory poisoning | Scratchpad → next prompt | T | MP | M | M | M | data-plane: tag scratchpad entries with provenance; control-plane: clear scratchpad between independent sub-tasks | ai-platform | Scratchpad reuse risk. |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Runaway-loop / blast-radius

For each tool the agent can call, the worst-case effect at the iteration cap:

| Tool | Per-call effect | Max-N effect (at iteration cap) | Iteration cap exists? | Cost cap exists? |
|---|---|---|---|---|
| lint | read PR; no side effect | identical | yes (12) | no — recommend adding |
| security-scan | read PR; no side effect | identical | yes (12) | no — recommend adding |
| run-tests | run CI job; consumes runner minutes | up to 12 CI runs per agent invocation | yes (12) | no — recommend adding |
| post_comment | publish to PR | up to 12 PR comments | yes (12) | n/a (publishing is not budgeted but is rate-limited at the GitHub API) |

### Coverage gaps

- **Catalog items with no register row:**
  - MAESTRO multi-agent-collusion: not applicable — single-agent deployment.
- **Boundaries with no catalog coverage:**
  - Audit-log sink → SIEM: no catalog item addresses log integrity in this catalog version. Recommend supplementing.

### Top 3 residual risks

1. **Tool-result injection via lint / security-scan output** (row 1) — content in a PR diff could carry payloads that the lint/security-scan tools echo back into the planner. Requires both data-plane (tag) and control-plane (re-prompt-before-dispatch) mitigations.
2. **Excessive agency on post_comment via GitHub App scope** (row 3) — App installed at org level grants cross-repo posting capability. Control-plane scoping is the only durable fix.
3. **Missing cost cap on a 12-iteration loop with CI-job tool** (row 2) — iteration cap exists but cost cap does not; a runaway loop could consume significant runner minutes.
```

Notes on filling this in:

- The agent-concern column makes it possible to filter the register by class (EA, RL, etc.) when triaging.
- Mitigation column distinguishes data-plane vs control-plane — agentic threats often require both; control-plane-only or data-plane-only mitigation is a flag.
- The runaway-loop subsection is mandatory even if you conclude "iteration cap is sufficient" — explicitness defeats audit theater.
- If the agent has more than one identity (e.g., multiple service accounts) the register needs one row per identity for the blast-radius analysis.
