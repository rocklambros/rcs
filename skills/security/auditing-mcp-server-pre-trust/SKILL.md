---
name: auditing-mcp-server-pre-trust
description: >
  Audits an MCP (Model Context Protocol) server against six security checks — license,
  source review, network egress, version pin, secret handling, and tool subset —
  before the server is registered into the Claude Code tool pool. Use whenever the
  user proposes adding an MCP server to ~/.claude/mcp.json, a project .mcp.json, or
  a plugin's mcpServers config. Produces a per-check verdict, a blocking-issues list,
  and a final integrate / integrate-with-constraints / reject recommendation.
version: 0.1.0
status: drafting
track: security
audience: [security-eng, ai-security, skill-author]
evidence:
  - jetson-runbook
  - RCAP
  - claude-secure-coding-rules
last-updated: 2026-05-22
---

# Auditing an MCP Server Before Pre-Trust

## When to use

Trigger this skill when the user asks for or implies one of:

- Adding a new MCP server to `~/.claude/mcp.json`, a project `.mcp.json`, or a plugin's `mcpServers` config
- Evaluating whether to install or trust a community / third-party MCP server
- Phrases like "should I add this MCP?", "is this MCP server safe?", "install <mcp-name>", "audit this MCP"

## When NOT to use

Skip this skill and hand off when:

- The user wants to *write* an MCP server, not audit an existing one → use `claude-code-meta/writing-mcp-server-securely` (planned)
- The MCP server is already registered and the question is "did it do something weird?" — that is incident-response, not pre-trust
- The user is configuring a first-party Anthropic MCP server bundled with Claude Code that has already gone through Anthropic's audit

## Quick start

User says: "I want to add the github-mcp-server from https://github.com/example/github-mcp to my Claude Code setup. Audit it."

Skill response: walks the six checks (license, source, network, version, secret, tool subset), produces a per-check verdict table, lists any blocking issues, and gives a final integrate / integrate-with-constraints / reject recommendation with rationale.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| mcp_source | URL or local path | yes | — | The MCP server source — GitHub URL, npm package name, local path, or PyPI package name. |
| install_scope | "user" \| "project" \| "plugin" | no | "user" | Where the MCP will be registered. Affects blast radius assessment. |
| permission_level | "default" \| "elevated" | no | "default" | Whether the MCP would run with default Claude Code permissions or elevated. |

## Workflow

Copy this checklist into the response and check off items as each check completes:

```
Pre-trust audit progress:
- [ ] Check 1: License — present, permissive, redistribution OK
- [ ] Check 2: Source review — last commit, contributor count, signed commits, suspicious patterns
- [ ] Check 3: Network egress — declared outbound calls, no exfiltration risks
- [ ] Check 4: Version pin — install command pins a specific version (not @latest, not unpinned)
- [ ] Check 5: Secret handling — how secrets are passed, never logged, never sent to upstream
- [ ] Check 6: Tool subset — list of tools the MCP exposes; principle of least privilege
- [ ] Final verdict: integrate / integrate-with-constraints / reject
```

### Check 1: License

- Verify a `LICENSE` file exists in the repo root or `pyproject.toml` / `package.json` declares a license
- Confirm the license is permissive enough for the user's context (MIT / Apache 2.0 / BSD typically fine; AGPL may not be)
- Flag any "no license = all rights reserved" cases as blocking

### Check 2: Source review

- Identify the latest commit date and the count of distinct contributors
- Note whether commits are signed (sigstore / GPG)
- Read source files (top file at minimum); look for: shell command execution with user-controlled input, dynamic import with user-controlled strings, telemetry endpoints, hardcoded credentials
- Flag obvious red flags (obfuscated code, base64-encoded payloads, suspicious network calls) as blocking

### Check 3: Network egress

- Read the README and source for documented outbound calls (API endpoints, telemetry, update checks)
- Compare against the MCP's stated purpose — a "filesystem tool" with HTTP calls is suspicious
- Confirm any documented endpoints are owned by the MCP author / well-known third party (GitHub API for a GitHub MCP, etc.)

### Check 4: Version pin

The install command MUST pin a specific version. Acceptable forms include npm-style `pkg@1.2.3`, pip-style `pkg==1.2.3`, or git-clone with explicit commit sha. Unpinned forms (latest, no version constraint, `npx -y`, `pip install pkg` without a constraint) are blocking.

### Check 5: Secret handling

- Identify how the MCP consumes secrets (env vars, config file, OAuth flow)
- Verify secrets are NOT logged (search for log/print calls near secret usage)
- Verify secrets are NOT included in error messages sent to a remote service
- For OAuth flows, confirm the callback URL is localhost or under the MCP author's domain

### Check 6: Tool subset

- List every tool the MCP exposes (`tools/list` output if available, or grep the source)
- Apply principle of least privilege — does this MCP need ALL these tools, or only some?
- If the MCP exposes destructive tools (file deletion, network requests, shell execution), flag for `permission_level: elevated` review

### Final verdict

- **Integrate**: all 6 checks pass; install
- **Integrate with constraints**: 4–5 checks pass; constraints required (subset of tools enabled, network egress blocked at firewall, etc.)
- **Reject**: ≥ 2 checks fail OR any single blocking issue identified

## Outputs

A markdown report:

1. **MCP identity** — name, version, source URL
2. **Per-check verdict table**: Check · Verdict (Pass / Warn / Fail) · Evidence · Notes
3. **Blocking issues list** (if any)
4. **Final recommendation** — integrate / integrate-with-constraints / reject — with rationale
5. **Install command** (if integrate or integrate-with-constraints) — exact pinned command

## Failure modes

- **Audit theater** — going through the checklist without genuine inspection. Caught by: required "Evidence" column on the verdict table (must cite specific files / lines / commits).
- **Permissive license bias** — assuming permissive license = safe code. License is necessary, not sufficient. Source review (Check 2) is separate.
- **Stale source review** — auditing one commit and integrating later versions. Caught by: Check 4 requires a specific version/sha pin AND a re-audit on version bumps.
- **Tool-subset omission** — installing an MCP and accepting all tools by default. Caught by: Check 6 requires explicit tool-subset declaration.

## References

- `reference/audit-table-template.md` — the per-check verdict table template
- `reference/red-flag-patterns.md` — specific code patterns that indicate compromise
- [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp.md)
- [MCP specification](https://modelcontextprotocol.io/)

## Examples

### Example 1: Pinned, licensed, low-privilege MCP (happy-path)

Input: "Audit github.com/anthropics/mcp-filesystem v1.2.3 for my project scope."

Output: Skill walks all six checks. License: MIT ✓. Source: 14 contributors, last commit 3 days ago, no signed commits but Anthropic ownership confirmed via GitHub org ✓. Network: no egress declared, source confirms no outbound calls ✓. Version: pinned to v1.2.3 ✓. Secrets: MCP accepts a working directory path; no secrets handled ✓. Tools: read_file, write_file, list_directory (3 tools, all expected for a filesystem MCP) ✓. Final: integrate.

### Example 2: Unknown MCP, no license (anti-trigger)

Input: "Add this random MCP I found: https://github.com/randomuser/cool-mcp"

Output: Skill begins audit, immediately fails Check 1 (no LICENSE file in repo root, no license declaration in pyproject.toml). Reports blocking issue. Final: reject. Recommends user contact the author for license clarification before re-audit.

## See also

- `security/auditing-pinned-dependencies` — broader supply-chain audit pattern
- `claude-code-meta/writing-mcp-server-securely` — the authoring side of this skill (planned)
- `workflow/running-adversarial-premortem` — for high-stakes MCP integration decisions

## Status & version

- Status: drafting
- Version: 0.1.0
- Last-updated: 2026-05-22
- Provenance: migrated from `~/.claude/skills/mcp-server-pre-trust-audit/`; reformatted to Layer-3 contract; slug renamed to enforce gerund convention
