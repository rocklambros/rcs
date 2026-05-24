---
name: writing-mcp-server-securely
description: >
  Walks the MCP (Model Context Protocol) server authoring workflow with the six
  pre-trust checks baked in as design constraints from day one — license
  declaration, source-review friendliness, explicit network egress
  documentation, version pin discipline, secret handling, and a tightly-scoped
  tool subset. Use when the user is writing a new MCP server, refactoring an
  existing server to pass pre-trust audit, or preparing to publish an MCP for
  third-party install. Hands off to the pre-trust audit skill when the user is
  evaluating someone else's server, and skips most of the workflow for
  no-behavior-change republishes.
version: 0.1.0
status: shipped
track: claude-code-meta
audience: [skill-author, security-eng, ai-security]
evidence:
  - RCS
  - jetson-runbook
  - claude-secure-coding-rules
last-updated: 2026-05-23
---

# Writing an MCP Server Securely

## When to use

Trigger this skill when the user asks for or implies one of:

- "Help me write a new MCP server" / "scaffold an MCP server" / "I want to build an MCP for X"
- They have an existing MCP server that needs to pass pre-trust audit for distribution
- They are about to publish an MCP server to npm, PyPI, a GitHub release, or a Claude Code marketplace
- They are refactoring an existing MCP to add new tools, new egress, or new secret handling
- Phrases like "how do I make my MCP safe to install?", "what does a good MCP look like?", "what should I bake in before publishing?"

## When NOT to use

Skip this skill and hand off when:

- The user is auditing someone else's MCP server before installing it → use `security/auditing-mcp-server-pre-trust`
- The user is registering an MCP in their own `.claude/mcp.json` and just wants the config format → use the MCP server reference docs directly
- The user is republishing an existing MCP with no behavioral change — this skill points to the lighter "CHANGELOG + PATCH bump + re-run audit" path in its anti-trigger handling
- The user is writing a Claude Code skill, hook, or plugin (different artifacts, different authoring discipline) → use `authoring-skill`, `authoring-tool-hook`, or `authoring-plugin`

## Quick start

User says: *"I want to write a Python MCP server that wraps our internal incident database. Tools: search_incidents, get_incident, list_recent."*

Skill response:

1. Confirm the six pre-trust checks as design constraints to bake in from day one (license, source review, network egress, version pin, secret handling, tool subset).
2. Scaffold the project — `pyproject.toml` with SPDX license + pinned dependencies, `LICENSE` file at repo root, `README.md` documenting tool subset + egress + secret handling.
3. Implement the MCP server with explicit tool registration (no dynamic eval, no catch-all dispatch).
4. Document network egress in the README (which endpoints, why, with what auth).
5. Document secret handling — env-var-only, no logging, no echoing in errors.
6. Pin the package version (SemVer), publish, and document the pinned install command in the README so consumers cannot install an unpinned form.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| mcp_purpose | string | yes | — | What the MCP wraps or exposes (e.g., "wraps internal incident database", "exposes filesystem read-only access"). |
| language | "python" \| "node" \| "rust" \| "go" | yes | — | Implementation language. Affects packaging + lockfile conventions. |
| tool_inventory | list of tool names | yes | — | Every tool the MCP will expose. Used to scope the tool-subset declaration (Check 6 baked in). |
| egress_targets | list of URLs or "none" | yes | — | Every outbound endpoint the MCP will call. Used to scope Check 3 (network egress). |
| secret_inventory | list of secret types or "none" | yes | — | Every secret the MCP consumes (API tokens, OAuth flows, certificates). Used to scope Check 5 (secret handling). |
| license | SPDX identifier | yes | — | MIT, Apache-2.0, BSD-3-Clause, etc. Required for any public publication. |

## Workflow

Copy this checklist into the response and check off items as the MCP is authored:

```
MCP authoring progress (baking the six pre-trust checks):
- [ ] Check 1 (License): SPDX in pyproject.toml / package.json + LICENSE file at repo root
- [ ] Check 2 (Source review): code is readable, no obfuscation, no base64 payloads, no dynamic import of user input
- [ ] Check 3 (Network egress): every endpoint documented in README + an auditable manifest field
- [ ] Check 4 (Version pin): dependencies pinned in lockfile; release tagged with SemVer; install command includes version
- [ ] Check 5 (Secret handling): env-var-only consumption; no logging or echoing secrets; least-privilege scopes
- [ ] Check 6 (Tool subset): tools/list is explicit; no eval; no dynamic dispatch; no catch-all
- [ ] CHANGELOG entry for the publish version
- [ ] README documents: what the MCP does, install command (pinned), tool subset, egress targets, secret handling
```

### Check 1 — License (baked in)

Declare the license in package metadata AND commit a matching `LICENSE` file at the repo root. For Python, `pyproject.toml` includes:

```toml
[project]
license = { text = "MIT" }
```

For Node, `package.json` includes `"license": "MIT"`. The license must be permissive enough for the consumer's context. AGPL is acceptable only when the MCP author intends to restrict commercial integration; otherwise prefer MIT, Apache-2.0, or BSD-3-Clause.

### Check 2 — Source review (baked in)

Write code that PASSES a source-review check rather than only WORKS:

- No obfuscation; no minification on published source
- No `eval()`, `exec()`, `Function()`, `new Function()`, or dynamic import with user-controlled strings
- No base64-encoded payloads that get decoded at runtime
- No shell execution with unescaped user input
- No suspicious side effects (file writes outside the documented scope, network calls beyond documented egress)

If the MCP must do anything that could trigger a source-review red flag (e.g., spawning a subprocess), document the reason explicitly in the README and in a code comment so the auditor can verify intent.

### Check 3 — Network egress (baked in)

Every outbound network call must be documented before the first publish:

- README has an "Egress targets" section listing every endpoint, the auth method, and why the call is needed
- The MCP manifest declares egress in a structured field auditors can grep for (e.g., `"egress": ["api.github.com/repos"]` in a custom manifest section if no standard field exists)
- The egress target is configurable via env var so the consumer can override (e.g., point at a proxy, restrict to a single host)
- The MCP does NOT phone home to telemetry endpoints without explicit opt-in; if telemetry is shipped, default-off and documented

### Check 4 — Version pin (baked in)

Pin every dependency in the lockfile (`uv.lock`, `package-lock.json`, etc.) and commit it. Publish the MCP with an explicit SemVer tag, never `main` or `latest`. Document the install command in the README with the pinned version:

```bash
# README install snippet (pinned)
npm install my-mcp-server@1.2.3
# or
uvx --from "git+https://github.com/me/my-mcp-server@v1.2.3" my-mcp-server
```

Reject any documentation that suggests `@latest` or `npx -y` for install. Those forms fail Check 4 of the consumer's audit.

### Check 5 — Secret handling (baked in)

Secrets enter the MCP via environment variables only. No config files committed to the repo. No hardcoded tokens. No prompting the user for the secret on every call.

Per-secret rules:

- Read once at startup from env var; do not re-read on every request
- Never log the secret, including in DEBUG-level logs
- Never include the secret in error messages sent to remote logging or to upstream telemetry
- Never include the secret in tool-call results returned to Claude (Claude's conversation can be persisted, summarized, or compacted; treat all returned data as potentially exfiltrable)
- For OAuth flows, redirect callback URL is localhost or the MCP author's verified domain
- Request the least-privilege scope — fine-grained PAT over classic PAT, read-only over read-write when read-write is not needed

### Check 6 — Tool subset (baked in)

Declare tools explicitly. The `tools/list` MCP method returns a fixed list known at build time. No dynamic registration based on user input. No catch-all tool that accepts an opcode and dispatches. No eval-style tools.

Each tool's input schema is explicit (JSON Schema with `type`, `properties`, `required` fields). Each tool's behavior is documented in its description so a consumer can decide whether to allow it without reading the source.

If the MCP has read-only and write tools, separate them so consumers can selectively enable only the read-only subset.

### Final review

Before publishing, do the consumer's pre-trust audit on your own MCP:

1. Pretend a security-conscious user is about to install. Run `security/auditing-mcp-server-pre-trust` against your repo.
2. Fix any check that fails.
3. Publish. Tag the release. Update the marketplace entry (if applicable).

## Outputs

A publishable MCP server repository with:

```
my-mcp-server/
├── pyproject.toml             # SPDX license + pinned deps
├── uv.lock                    # pinned dependency lockfile (committed)
├── LICENSE                    # matches pyproject license field
├── README.md                  # install command (pinned) + tool subset + egress + secrets
├── CHANGELOG.md               # per-version release notes
├── src/
│   └── my_mcp_server/
│       ├── __init__.py
│       ├── server.py          # explicit tool registration; no eval; no dynamic dispatch
│       └── tools/             # one module per tool, schemas explicit
└── tests/
    ├── test_tools.py
    └── test_egress_documented.py
```

Plus a published package (PyPI, npm, GitHub release) tagged with the SemVer version that the README pins.

## Failure modes

Known pitfalls in MCP authoring and how this skill catches them:

- **License-as-afterthought.** Publishing without a LICENSE file leaves consumers unable to install legally; "all rights reserved" by default. Caught by: Check 1 baked in at scaffolding time + workflow checklist requires the LICENSE file.
- **Catch-all dispatch tool.** A single tool that accepts an opcode and runs arbitrary actions makes the tool-subset declaration meaningless. Caught by: Check 6 forbids dynamic dispatch + the consumer's audit will reject the tool subset.
- **Hardcoded telemetry endpoint.** MCP phones home to the author's analytics on every tool call. Caught by: Check 3 requires egress documentation; an undocumented endpoint fails source review.
- **Secret in error message.** Server logs the bearer token when an upstream call fails; the log gets persisted in Claude conversation history. Caught by: Check 5 explicitly forbids including secrets in error messages.
- **Default-off becomes default-on after upgrade.** Author flips a telemetry default in a minor release without a CHANGELOG entry. Caught by: workflow checklist requires CHANGELOG entry per release + consumer's audit re-runs on version bumps.
- **First-person POV in README description.** "I built this MCP to..." — same Anthropic best-practices violation as for skills. Caught by: this skill's Quick start guides third-person framing.
- **Republish drift.** Author ships a "no-change" version that quietly pulls in a transitive dependency upgrade with new egress behavior. Caught by: this skill's anti-trigger handling requires re-running the six-check audit even on no-behavior-change republishes.

## References

- `reference/secure-mcp-skeleton.md` — copy-paste Python MCP skeleton with the six checks baked in
- `reference/audit-self-check.md` — pre-publish self-audit checklist mirroring the consumer's pre-trust audit
- [MCP specification](https://modelcontextprotocol.io/) — official protocol spec
- [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp.md) — host-specific install + registration
- RCS `security/auditing-mcp-server-pre-trust` — the consumer's pre-trust audit; this skill's design constraints mirror its six checks

## Examples

### Example 1: New Python MCP from scratch (happy-path)

Input: *"I want to write a Python MCP server that wraps our internal incident database. Tools: search_incidents, get_incident, list_recent."*

Output: Skill confirms the six checks as design constraints. Scaffolds the project: `pyproject.toml` with `license = { text = "MIT" }` and pinned deps via `uv lock`; LICENSE file (MIT); README documenting the three tools + egress (the internal DB host, via env-configurable URL) + secret handling (DB connection string via env var, never logged). Implements the server with explicit `tools/list` returning only the three named tools — no eval, no dynamic dispatch. Adds tests that assert the documented egress targets match the runtime config. Publishes with a v0.1.0 tag and README install snippet pinned to v0.1.0.

### Example 2: MCP with external egress and a secret (edge-case)

Input: *"My MCP needs to call api.github.com using a personal access token. How do I design it safely?"*

Output: Skill recommends documenting `api.github.com` as the explicit egress target in the README and in an auditable manifest field. Recommends consuming the token via the `GITHUB_TOKEN` env var with no fallback to a config file; never logs the token; never includes it in error messages. Recommends a fine-grained personal access token with read-only scopes for the specific repos the MCP queries, instead of a classic PAT with full repo access. Adds a startup check that fails fast if the token is missing rather than continuing without auth (avoids silently falling back to unauthenticated requests that may succeed for public repos but fail unexpectedly for private ones).

### Example 3: No-behavior-change republish (anti-trigger)

Input: *"I'm republishing my MCP with no behavior changes — just bumping the version because the upstream package I depend on had a security update. Do I need to redo the whole authoring workflow?"*

Output: Skill answers no — the full authoring workflow is for new servers or behavior-changing refactors. Recommends a SemVer PATCH bump (e.g., 0.2.1 → 0.2.2), a CHANGELOG entry naming the upstream-dependency security update, a tag, and a republish. BUT — flags that even a no-behavior-change republish should re-run the six-check audit (license, source, egress, version pin, secret handling, tool subset) because an upstream dependency update can quietly change egress behavior, secret handling, or license terms. Cross-references `security/auditing-mcp-server-pre-trust` for the re-audit.

## See also

- `security/auditing-mcp-server-pre-trust` — the consumer's pre-trust audit; this skill bakes its checks into the design
- `claude-code-meta/authoring-plugin` — packaging discipline for a plugin that bundles this MCP
- `security/auditing-pinned-dependencies` — the dependency-pin discipline that Check 4 relies on
- `claude-code-meta/authoring-tool-hook` — sibling authoring discipline for Claude Code hooks (similar elevated-permissions concerns)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
