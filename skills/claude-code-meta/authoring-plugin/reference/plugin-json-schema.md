# plugin.json field reference

The `.claude-plugin/plugin.json` manifest defines a Claude Code plugin. Required fields are flagged.

## Required fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Lowercase-kebab plugin slug. Matches the plugin directory name. ≤ 64 chars. No `anthropic` or `claude` reserved words. |
| `version` | string | SemVer (e.g., `0.1.0`). First publish is `0.1.0`. |
| `description` | string | Third-person one-line description of what the plugin bundles and the target audience. Appears in marketplace catalog. ≤ 200 chars recommended. |
| `license` | string | SPDX identifier (e.g., `MIT`, `Apache-2.0`, `BSD-3-Clause`). Must match the `LICENSE` file at the plugin root. |
| `author` | object | `{ "name": "...", "email": "..." }`. Email is optional but recommended for marketplace contact. |

## Optional fields

| Field | Type | Description |
|---|---|---|
| `homepage` | URL | Plugin documentation or marketing page. |
| `repository` | URL | Source repository (`https://github.com/user/repo`). |
| `keywords` | list of strings | Marketplace search keywords. |
| `claude_code_version` | string | Compatibility range (e.g., `">=1.0.0 <2.0.0"`). Marketplaces use this to filter incompatible plugins. |
| `hooks` | list of hook registrations | Explicit hook registration. See "Hook registration" below. |
| `rules` | list of rule paths | Explicit rule registration (paths to `.md` rule files relative to the plugin root). |
| `mcpServers` | object | Inline MCP server registrations, equivalent to `.mcp.json` at the plugin root. |
| `lifecycle` | object | `post_install`, `pre_uninstall`, `post_update` scripts. Each value is a path to a script relative to the plugin root. |
| `categories` | list of strings | Marketplace categories (e.g., `security`, `ml-datasci`, `workflow`). |

## Hook registration

Hooks are NOT auto-discovered. They must be declared in the manifest:

```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": "Bash",
      "command": "hooks/gate-bash.sh"
    },
    {
      "event": "SessionStart",
      "command": "hooks/audit-config.py"
    }
  ]
}
```

`event` must be one of: `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `Notification`. See `writing-claude-code-hook` for event semantics.

## Example: minimal manifest

```json
{
  "name": "ml-ds-toolkit",
  "version": "0.1.0",
  "description": "Bundle of ML/DS workflow skills, commands, and a stats-reviewer subagent for data scientists shipping models.",
  "license": "MIT",
  "author": {
    "name": "Jane Smith",
    "email": "jane@example.com"
  }
}
```

## Example: manifest with hooks and lifecycle

```json
{
  "name": "secure-shell-gate",
  "version": "0.2.1",
  "description": "Pre-tool-use Bash gating with deny rules for destructive commands; SessionStart audit of MCP config.",
  "license": "Apache-2.0",
  "author": { "name": "Security Team", "email": "sec@example.com" },
  "homepage": "https://example.com/secure-shell-gate",
  "repository": "https://github.com/example/secure-shell-gate",
  "claude_code_version": ">=1.5.0",
  "hooks": [
    { "event": "PreToolUse", "matcher": "Bash", "command": "hooks/gate-bash.py" },
    { "event": "SessionStart", "command": "hooks/audit-mcp-config.py" }
  ],
  "rules": ["rules/deny-destructive-git.md", "rules/deny-rm-rf-root.md"],
  "lifecycle": {
    "post_install": "scripts/install-cron.sh",
    "pre_uninstall": "scripts/cleanup-cron.sh"
  },
  "categories": ["security", "claude-code-meta"]
}
```
