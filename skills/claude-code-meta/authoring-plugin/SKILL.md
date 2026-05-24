---
name: authoring-plugin
description: >
  Walks the plugin authoring workflow for the Claude Code host — the
  .claude-plugin/plugin.json manifest, the marketplace.json entry, the
  auto-discovered skills/ + commands/ + agents/ + hooks/ + .mcp.json
  subdirectory layout, version pinning, lifecycle metadata (install / update /
  uninstall), and the security review every bundled hook and MCP server needs
  before publication. Use when the user has 2+ artifacts (skills, commands,
  agents, hooks, MCP servers) to ship together, wants to publish a plugin to a
  marketplace, or asks how to package these artifacts for distribution. Hands
  off to the skill-authoring discipline for single-skill cases.
version: 0.1.0
status: shipped
track: claude-code-meta
audience: [skill-author, devops]
evidence:
  - RCS
  - superpowers
  - claude-plugins-official
last-updated: 2026-05-23
---

# Authoring a Plugin

## When to use

Trigger this skill when the user asks for or implies one of:

- "Help me package these skills as a plugin" / "scaffold a Claude Code plugin" / "publish to a marketplace"
- They have 2+ artifact types to ship together (skills + commands + agents + hooks + MCP servers)
- "How do I distribute my Claude Code stuff?" / "What's marketplace.json?"
- They are migrating from loose `~/.claude/skills/` symlinks to a versioned, installable plugin
- They want install / update / uninstall lifecycle for a bundled set of artifacts

## When NOT to use

Skip this skill and hand off when:

- The user has exactly one skill to share → use `claude-code-meta/authoring-skill`; a single SKILL.md ships fine as a symlink, git repo, or file copy without plugin overhead
- The user is writing the artifact itself (a skill, a hook, an MCP server, a deny/allow rule) rather than packaging it → use the corresponding authoring skill (`authoring-skill`, `writing-claude-code-hook`, `writing-mcp-server-securely`, `writing-deny-allow-rules`)
- The user is auditing an existing plugin before install → use `security/auditing-mcp-server-pre-trust` (the six-check pattern applies to plugin install commands too) plus this skill's "Failure modes" section
- The user is publishing to an internal-only registry where install is hand-curated and lifecycle is manual — packaging adds friction without benefit at that scale

## Quick start

User says: *"I have 5 skills, 2 slash commands, and 1 subagent definition. Bundle them as a plugin."*

Skill response:

1. Confirm the plugin slug (gerund-form or noun-form; the plugin naming is looser than skill naming, but lowercase-kebab is still required) and pick the directory it will live under.
2. Scaffold the directory layout — `.claude-plugin/plugin.json`, `skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json` (only the subdirs that apply).
3. Author `.claude-plugin/plugin.json` with required fields (name, version, description, license, author).
4. Author a `marketplace.json` entry (separate file at the marketplace repo root) describing the plugin for the catalog.
5. Run the per-artifact authoring discipline for each piece (`authoring-skill` for each SKILL.md; `writing-claude-code-hook` for each hook; etc.).
6. Security review every bundled hook and MCP server BEFORE publication.
7. Pin the version (SemVer 0.1.0 for first publish); commit a `LICENSE` and a `CHANGELOG.md`.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| plugin_slug | string | yes | — | Lowercase-kebab plugin name. Becomes the directory name and the `name` field in `plugin.json`. |
| artifact_inventory | list of artifact types | yes | — | Which artifact types the plugin bundles: any subset of `skills`, `commands`, `agents`, `hooks`, `mcp-servers`, `rules`. |
| target_marketplace | string | no | — | URL or slug of the marketplace repo the plugin will be listed under (e.g., a community marketplace, a private team marketplace). Empty means private / hand-distributed. |
| license | SPDX identifier | yes | — | MIT, Apache-2.0, BSD-3-Clause, etc. Required for any public marketplace listing. |
| version | SemVer string | no | "0.1.0" | First-publish version. Bump per the SemVer rules on subsequent releases. |

## Workflow

Copy this checklist into the response and check off items as the plugin is authored:

```
Plugin authoring progress:
- [ ] Slug: lowercase-kebab, ≤ 64 chars, no anthropic/claude reserved words
- [ ] Directory layout: .claude-plugin/plugin.json + per-artifact subdirs
- [ ] plugin.json: name, version, description, license, author, optional homepage / repository
- [ ] marketplace.json entry (separate file at the marketplace repo root)
- [ ] Per-artifact authoring: every SKILL.md / hook / MCP server / rule passes its own authoring discipline
- [ ] Security review: every bundled hook and MCP server passes the six-check pre-trust audit
- [ ] LICENSE file committed (matches plugin.json license field)
- [ ] CHANGELOG.md: entry for this version with shipped artifacts list
- [ ] README.md: install command (pinned), what the plugin does, per-hook risk surface, per-MCP tool subset
- [ ] Version pin: SemVer; first publish is 0.1.0; bump rules documented
```

### Step 1 — Directory layout

The standard Claude Code plugin layout. Only include subdirectories you actually populate:

```
<plugin-slug>/
├── .claude-plugin/
│   └── plugin.json            # required manifest
├── skills/                    # auto-discovered: each subdir with SKILL.md
│   └── <skill-slug>/
│       └── SKILL.md
├── commands/                  # auto-discovered: each .md file is a slash command
│   └── <command-slug>.md
├── agents/                    # auto-discovered: each .md file is a subagent
│   └── <agent-slug>.md
├── hooks/                     # NOT auto-discovered — referenced from plugin.json or settings
│   └── <hook-slug>.sh
├── rules/                     # NOT auto-discovered — referenced from plugin.json
│   └── <rule-slug>.md
├── .mcp.json                  # MCP server registrations (auto-loaded)
├── LICENSE
├── CHANGELOG.md
└── README.md
```

Skills, commands, and agents are convention-based discovery (place them in their named subdirs). Hooks and rules are explicit-registration — the plugin manifest or the consuming `settings.json` references them by path. MCP servers are configured in `.mcp.json` at the plugin root.

### Step 2 — plugin.json manifest

Required fields:

```json
{
  "name": "my-plugin-slug",
  "version": "0.1.0",
  "description": "One-line description of what the plugin bundles and who it is for.",
  "license": "MIT",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  }
}
```

Optional but recommended: `homepage`, `repository`, `keywords` (for marketplace search), `claude_code_version` (compatibility range), `hooks` (explicit hook registration), `rules` (explicit rule registration).

### Step 3 — marketplace.json entry

Marketplaces are git repositories with a `marketplace.json` file at the root listing each plugin. To publish, open a PR against the target marketplace adding an entry:

```json
{
  "plugins": [
    {
      "name": "my-plugin-slug",
      "source": "github:user/repo",
      "version": "0.1.0",
      "description": "Same one-line description as plugin.json",
      "license": "MIT",
      "categories": ["security", "ml-datasci"]
    }
  ]
}
```

`source` pins where the plugin code lives. `github:user/repo` is the canonical form for public GitHub plugins; private or self-hosted needs an explicit URL.

### Step 4 — Per-artifact authoring

Each bundled artifact has its own authoring discipline. Run the corresponding skill for each one BEFORE packaging:

- Each `SKILL.md` → `claude-code-meta/authoring-skill`
- Each hook script → `claude-code-meta/writing-claude-code-hook`
- Each MCP server registration → `claude-code-meta/writing-mcp-server-securely` for new MCP servers; `security/auditing-mcp-server-pre-trust` for third-party servers the plugin re-bundles
- Each deny/allow rule → `claude-code-meta/writing-deny-allow-rules`

A plugin's quality is the floor of its artifacts' quality. Do not let one unaudited hook or one first-person-POV description ship in the bundle.

### Step 5 — Security review for bundled hooks and MCP servers

Hooks and MCP servers wield permissions the consumer's session will grant on install. They are NOT exempt from the six-check pre-trust audit (license, source review, network egress, version pin, secret handling, tool/hook subset).

For every bundled hook:

- Document in the README: what it reads, what it writes, what tool calls it can block, what egress it performs
- For `PreToolUse` hooks: explicit list of which tools the hook gates
- For `SessionStart` hooks: explicit list of files the hook reads + any side effects
- For hooks that perform HTTP calls or shell execution: flag in the README as "elevated risk" and recommend the consumer review the script before install

For every bundled or re-bundled MCP server:

- Pin to a specific commit SHA or version tag in `.mcp.json` (never `@latest`, never unpinned)
- Document the tool subset the MCP exposes
- Document any secrets the MCP consumes and how (env vars, OAuth, config file)

### Step 6 — Lifecycle metadata

The plugin manifest can declare lifecycle hooks for install, update, and uninstall — useful for plugins that maintain state outside the plugin directory (caches, indices, registered cron jobs):

```json
{
  "lifecycle": {
    "post_install": "scripts/install.sh",
    "pre_uninstall": "scripts/cleanup.sh"
  }
}
```

Lifecycle scripts are themselves elevated-permission artifacts; apply the hook security review to them. If the plugin does NOT need lifecycle scripts, omit the field entirely.

### Step 7 — Version pin and CHANGELOG

First publish is `0.1.0`. SemVer rules per Claude Code plugin convention:

- PATCH (0.1.0 → 0.1.1): typo fix, doc tweak, no artifact behavior change
- MINOR (0.1.0 → 0.2.0): new skill / hook / command added, or existing artifact's behavior expanded backward-compatibly
- MAJOR (0.1.0 → 1.0.0): removed artifacts, changed slash-command syntax, changed hook trigger semantics, or any other breaking change for an existing installation

Every release bumps the `version` field in `plugin.json` AND adds a `CHANGELOG.md` entry. Marketplace tooling reads the changelog to surface release notes.

## Outputs

A complete plugin directory ready to publish:

```
<plugin-slug>/
├── .claude-plugin/plugin.json     # manifest with required fields
├── skills/                         # populated subdirs with SKILL.md per skill
├── commands/                       # populated with command .md files
├── agents/                         # populated with subagent .md files
├── hooks/                          # populated with hook scripts (referenced from manifest)
├── rules/                          # populated with allow/deny rule .md files
├── .mcp.json                       # MCP server registrations (pinned)
├── LICENSE
├── CHANGELOG.md                    # entry for the publish version
└── README.md                       # install command + per-artifact risk surface
```

Plus a `marketplace.json` PR opened against the target marketplace repo.

## Failure modes

Known pitfalls in plugin authoring and how this skill catches them:

- **Single-skill plugin overhead.** Packaging one SKILL.md as a plugin adds manifest + marketplace overhead without benefit. Caught by: the When-NOT-to-use section + handoff to `authoring-skill`.
- **Unaudited bundled hook.** A `PreToolUse` hook that runs shell commands gets shipped without security review; consumers install it sight-unseen. Caught by: Step 5 requirement + the README per-hook risk-surface entry.
- **Unpinned MCP in `.mcp.json`.** `npx -y` or `@latest` in the MCP registration means every install pulls a fresh, potentially-malicious version. Caught by: Step 5 requires explicit version pin; cross-references `security/auditing-mcp-server-pre-trust` Check 4.
- **First-person POV in plugin.json description.** The description shows up in the marketplace catalog; first-person POV breaks discovery the same way it breaks skill discovery. Caught by: third-person description rule (same Anthropic best-practice that applies to SKILL.md).
- **Missing LICENSE.** No LICENSE file = all rights reserved = consumers cannot legally redistribute. Caught by: workflow checklist requires the LICENSE file matching the plugin.json license field.
- **Lifecycle script that auto-executes elevated commands.** A `post_install` script that writes to `~/.claude/settings.json` or registers cron jobs without user consent. Caught by: Step 6 treats lifecycle scripts as elevated-permission artifacts requiring hook-grade security review.
- **Convention vs registration confusion.** Author drops a hook in `hooks/` expecting auto-discovery; nothing fires because hooks need explicit registration. Caught by: Step 1 layout table marks auto-discovered vs registered subdirs.

## References

- `reference/plugin-json-schema.md` — full plugin.json field reference with examples
- `reference/marketplace-json-schema.md` — marketplace.json field reference with examples
- [Claude Code plugins documentation](https://code.claude.com/docs/en/plugins.md) — official plugin authoring reference
- [Claude Code marketplace documentation](https://code.claude.com/docs/en/marketplaces.md) — marketplace publishing workflow
- RCS `docs/conventions.md` — Layer-3 H2 contract (applies to bundled skills)
- RCS `docs/eval-protocol.md` — eval requirements (applies to bundled skills)

## Examples

### Example 1: Bundling a 5-skill workflow plugin (happy-path)

Input: *"I have 5 ML-DS skills, 2 slash commands, and 1 subagent definition. Bundle them as a Claude Code plugin."*

Output: Skill confirms plugin slug `ml-ds-toolkit` (lowercase-kebab ✓). Scaffolds `.claude-plugin/plugin.json` with required fields (name, version 0.1.0, description, license MIT, author). Creates `skills/`, `commands/`, `agents/` subdirs and moves the artifacts in. Authors `marketplace.json` entry pointing at `github:user/ml-ds-toolkit`. Confirms each of the 5 SKILL.md files passes the authoring-skill discipline (gerund slug, third-person description, 11 H2 sections). Commits LICENSE (MIT), CHANGELOG.md (entry for 0.1.0 listing all 8 artifacts), README.md. Recommends opening the marketplace PR after smoke-testing install on a clean Claude Code session.

### Example 2: Plugin with elevated-permission hooks (edge-case)

Input: *"My plugin includes a PreToolUse hook that runs shell commands to enforce deny rules. Ship it."*

Output: Skill flags Step 5: the PreToolUse-shell hook requires explicit security review before publication. Recommends the plugin README document the hook's risk surface — what tools it gates, what shell commands it can run, what files it reads. Cross-references the six-check pre-trust pattern: a hook with shell-execution authority needs source review + network-egress check + secret-handling check the same way an MCP server does. Suggests the README include a "what this hook does and what it can do to your system" section so consumers can audit before install.

### Example 3: Single-skill author hands off (anti-trigger)

Input: *"I just wrote one skill, auditing-graphql-schemas, and want to share it. Should I package it as a plugin?"*

Output: Skill answers no — a single SKILL.md does not earn plugin packaging overhead. Hands off to `claude-code-meta/authoring-skill`. Explains the lighter options: symlink the skill into `~/.claude/skills/`, push the directory to a git repo and have teammates clone, or copy the directory into their `~/.claude/skills/`. Notes that plugin packaging earns its overhead when bundling 2+ artifact types (skills + commands + agents + hooks + MCP servers) or when marketplace distribution / install lifecycle / version pinning matters for the consumer.

## See also

- `claude-code-meta/authoring-skill` — per-skill authoring discipline (every bundled SKILL.md must pass this)
- `claude-code-meta/writing-claude-code-hook` — per-hook authoring discipline (every bundled hook must pass this)
- `claude-code-meta/writing-mcp-server-securely` — per-MCP-server authoring discipline (every bundled or re-bundled MCP must pass this)
- `claude-code-meta/writing-deny-allow-rules` — per-rule authoring discipline (every bundled rule must pass this)
- `security/auditing-mcp-server-pre-trust` — six-check pre-trust pattern; applies to plugin install commands and bundled MCP servers
- `claude-code-meta/auditing-instruction-hierarchy` — audit any CLAUDE.md the plugin contributes to the consumer's hierarchy

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
