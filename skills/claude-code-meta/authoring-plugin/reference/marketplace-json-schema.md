# marketplace.json field reference

A Claude Code marketplace is a git repository with a `marketplace.json` file at its root listing each plugin available for install. Publishing a plugin means opening a PR that adds an entry to a target marketplace's `marketplace.json`.

## Top-level structure

```json
{
  "name": "my-marketplace",
  "description": "What this marketplace curates and who it is for.",
  "plugins": [
    { ... plugin entry 1 ... },
    { ... plugin entry 2 ... }
  ]
}
```

## Per-plugin entry fields

| Field | Required | Description |
|---|---|---|
| `name` | yes | Plugin slug. Matches the `name` field in the plugin's `plugin.json`. |
| `source` | yes | Pin to where the plugin code lives. Forms: `github:user/repo`, `github:user/repo@v1.2.3`, `https://...`, `git+ssh://...@<sha>`. |
| `version` | yes | Plugin version to install. SemVer. Must match a tag or commit in the source repo. |
| `description` | yes | One-line description for the catalog. Recommended to match `plugin.json#description`. |
| `license` | yes | SPDX identifier. Marketplaces use this to surface license filters. |
| `categories` | no | List of marketplace categories the plugin belongs to. |
| `keywords` | no | Search keywords (in addition to plugin.json keywords). |
| `homepage` | no | URL for plugin documentation. |

## Example: marketplace.json with two plugins

```json
{
  "name": "rcs-marketplace",
  "description": "Public skills repo (RCS) — production-grade workflow, security, ml-datasci, teaching, and claude-code-meta plugins.",
  "plugins": [
    {
      "name": "ml-ds-toolkit",
      "source": "github:rocklambros/ml-ds-toolkit@v0.3.0",
      "version": "0.3.0",
      "description": "Bundle of ML/DS workflow skills, commands, and a stats-reviewer subagent for data scientists shipping models.",
      "license": "MIT",
      "categories": ["ml-datasci"],
      "keywords": ["statistics", "model-evaluation", "leakage"]
    },
    {
      "name": "secure-shell-gate",
      "source": "github:rocklambros/secure-shell-gate@v0.2.1",
      "version": "0.2.1",
      "description": "Pre-tool-use Bash gating with deny rules for destructive commands; SessionStart audit of MCP config.",
      "license": "Apache-2.0",
      "categories": ["security", "claude-code-meta"]
    }
  ]
}
```

## Publishing workflow

1. Fork the target marketplace repository.
2. Add an entry to `marketplace.json` for your plugin. Pin `source` to a specific git tag or SHA.
3. Open a PR. The marketplace maintainer reviews the plugin (license, source code, hook safety) per the marketplace's own admission policy.
4. On merge, `/plugin install <plugin-name>` from the marketplace becomes available to Claude Code consumers.

## Updating a published plugin

Bump `version` in BOTH `plugin.json` (your plugin repo) AND the marketplace entry (the marketplace repo). Tag the new version in your plugin repo. Open a marketplace PR updating the `version` and `source` ref. Per the SemVer rules in the plugin manifest reference, MINOR bumps are auto-upgradable; MAJOR bumps require the consumer to opt in.

## Marketplace admission anti-patterns

Marketplace maintainers should reject entries that:

- Pin `source` to a branch name (e.g., `github:user/repo@main`) instead of a tag or SHA — branches move, breaking reproducible install
- Bundle MCP servers without pinned versions in the plugin's `.mcp.json`
- Bundle hooks without per-hook risk-surface documentation in the plugin README
- Use first-person POV in the `description` field (breaks discovery in the catalog UI)
- Have no LICENSE file in the source repo
