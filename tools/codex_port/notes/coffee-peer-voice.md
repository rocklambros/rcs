Differences from the claude.ai source:

- Scripts: run them with `python3 -I` at the absolute paths written in this file. The port pinned those paths at build time, so there is no base directory to derive and no placeholder to expand.
- Where the source says the Write or Edit tool, make the file change with `apply_patch` and keep the same one-pass discipline.
- Where the source mentions Claude Code allow rules, Codex's approval policy applies instead. The single-command rule still holds: one script call per command, no shell chaining.
- Sibling skills are invoked as `$skill-name`. Skills named here that are not installed under `~/.codex/skills` belong to the Claude Code library. Apply the named guidance inline instead of invoking them.
