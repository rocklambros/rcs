---
name: writing-deny-allow-rules
description: >
  Walks the .claude/rules/*.md authoring workflow — one rule per file, with a
  tool matcher, an action matcher (path glob, regex, structured input),
  decision (allow / deny / ask), severity, and an auditable rationale section.
  Covers precedence (user > project > plugin; more-specific > less-specific),
  composition across files, and the choice between a structured rule file
  versus a settings.json permissions entry for trivial allowlists. Use when
  the user wants reviewable, version-controlled, multi-line allow/deny policy
  beyond what fits in a one-line settings.json entry.
version: 0.1.0
status: shipped
track: claude-code-meta
audience: [skill-author, security-eng, devops]
evidence:
  - RCS
  - rocks-mac-harness
  - claude-plugins-official
last-updated: 2026-05-23
---

# Writing Deny/Allow Rules

## When to use

Trigger this skill when the user asks for or implies one of:

- "I want a rule that denies X" / "block this pattern" / "allow this only when Y"
- They are tightening permissions on a project that has outgrown a one-line settings.json allowlist
- They are authoring a plugin that ships an opinionated policy (e.g., `secure-shell-gate` plugin shipping its own rules)
- They need an auditable rationale ("WHY is this denied?") next to the rule itself, not buried in a commit message
- They want multi-line, reviewable, version-controlled policy rather than a settings.json string

## When NOT to use

Skip this skill and hand off when:

- The user wants a single trivial allowlist entry (e.g., always allow `ls`) → use the `update-config` skill to add it to `settings.json` `permissions.allow`
- The user wants to write a hook that ENFORCES rules at runtime → use `claude-code-meta/authoring-tool-hook`; rules are declarative data, hooks are the executors
- The user is configuring auto-mode or `--dangerously-skip-permissions` bypass behavior → those are session-level settings, not rules
- The user wants to write a CLAUDE.md instruction ("avoid using X") rather than a deterministic gate → CLAUDE.md is advisory, rules are enforced

## Quick start

User says: *"I want to deny `git push --force` or `-f` against main and master, repo-wide."*

Skill response:

1. Pick the scope — user (`~/.claude/rules/`) for cross-project; project (`./.claude/rules/`) for repo-specific; plugin (in the plugin manifest) for shipped policy.
2. One rule per file. Name the file after the rule's intent (e.g., `deny-force-push-on-main.md`).
3. Write the rule with: tool matcher (Bash), action matcher (regex for `git push (--force|-f).*\b(main|master)\b`), decision (deny), severity (high), rationale (why this is denied).
4. Test by attempting the denied action; confirm the deny fires and the rationale shows.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| rule_slug | string | yes | — | Lowercase-kebab rule name; becomes the filename (e.g., `deny-force-push-on-main.md`). Use `deny-` or `allow-` prefix to make the decision visible from the filename alone. |
| scope | "user" \| "project" \| "plugin" | yes | — | Where the rule lives. User-scope covers all projects; project-scope is repo-specific; plugin-scope ships with a plugin. |
| tool_matcher | string | yes | — | Tool name(s) the rule scopes to (e.g., `Bash`, `Edit`, `Write`, or `*` for all). Prefer the smallest scope that meets the need. |
| action_matcher | regex / glob / structured | yes | — | What the rule matches on within the tool — command regex for Bash, path glob for Edit/Write, etc. |
| decision | "allow" \| "deny" \| "ask" | yes | — | What happens on a match. `ask` prompts the user (default for tool calls without an explicit rule). |
| severity | "low" \| "medium" \| "high" \| "critical" | yes | — | Used by audit log + by reviewers to triage rule violations. |

## Workflow

Copy this checklist into the response and check off items as the rule is authored:

```
Rule authoring progress:
- [ ] Scope chosen (user / project / plugin)
- [ ] Filename uses deny- or allow- prefix so the decision is visible at the directory listing
- [ ] One rule per file (single tool matcher + single action matcher + single decision)
- [ ] Action matcher catches the variants you care about (e.g., --force AND -f for git push)
- [ ] Rationale section explains WHY (incident reference, threat model, compliance citation)
- [ ] Severity assigned (used by audit log and reviewer triage)
- [ ] Precedence understood: user > project > plugin; more-specific > less-specific
- [ ] Tested by attempting the denied action; deny fires; rationale shows
```

### Step 1 — Scope

| Scope | Location | Use when |
|---|---|---|
| User | `~/.claude/rules/<rule>.md` | Cross-project policy you carry to every repo (e.g., never `rm -rf $HOME`) |
| Project | `./.claude/rules/<rule>.md` | Repo-specific policy (e.g., this repo's `main` branch is protected) |
| Plugin | declared in `plugin.json` `rules` array | Opinionated policy a plugin ships to consumers |

Plugin-scope rules ship with the plugin install and are removed on uninstall. Document them in the plugin README so consumers can see the policy they are accepting.

### Step 2 — Rule file structure

Each rule lives in its own `.md` file under the rules directory. The structure:

```markdown
---
name: deny-force-push-on-main
decision: deny
tool: Bash
matcher: "git push (--force|-f).*\\b(main|master)\\b"
severity: high
---

# Deny force-push to main/master

## Rationale

Force-push to a shared default branch overwrites teammates' commits and breaks
CI/CD downstream pipelines that assume linear history. Allowed alternatives:

- Force-push to a feature branch: `git push --force origin my-feature` (this rule does NOT match feature branches)
- Reset main locally and push a new commit instead of force-pushing

## Audit notes

- Incident reference: 2026-Q1 lost 8 hours of release-engineering work after a force-push to main
- Compliance: SOC 2 change-management requires immutable main branch
```

Frontmatter fields (required):

- `name` — rule slug; matches filename
- `decision` — `allow` / `deny` / `ask`
- `tool` — tool name (`Bash`, `Edit`, `Write`, etc.) or `*` for all
- `matcher` — regex, glob, or structured matcher per the tool
- `severity` — `low` / `medium` / `high` / `critical`

Body sections (recommended):

- `## Rationale` — WHY the rule exists (auditable; survives the original author leaving)
- `## Audit notes` — incident references, compliance citations, related rules

### Step 3 — Matcher discipline

Catch the variants you care about, not just the literal form you typed:

- `git push --force` AND `git push -f` AND `git push --force-with-lease`? Decide which variants to include and write a regex that matches the set.
- Path globs: `**/.ssh/**` for "anywhere under any .ssh directory" vs `~/.ssh/**` for "only the user's home .ssh".
- Tool name: `Bash` only, or `*` for all? Prefer the narrowest.

For complex matchers, split into multiple single-purpose rules rather than one mega-rule. Each rule file should be independently reviewable in 30 seconds.

### Step 4 — Precedence model

When multiple rules match the same action:

1. **More-specific wins over less-specific.** A rule scoped to `Bash` + `git push --force.*main` overrides a broader rule scoped to `Bash` + `git push.*` regardless of decision.
2. **Deny wins over allow at the same specificity.** A tie between `deny` and `allow` resolves to `deny`.
3. **Scope precedence: user > project > plugin.** A user-scope rule overrides a project-scope rule at the same specificity. (Anthropic's documented precedence; verify in your version of Claude Code.)

Make precedence visible by listing all matching rules in the audit log on every decision. If precedence is unclear, the rule set is too tangled; refactor.

### Step 5 — Composing across files

Complex policy: split into multiple single-purpose files. Example for the SSH + /etc policy:

```
~/.claude/rules/
├── deny-ssh-key-writes.md         # tool: Write, matcher: "**/.ssh/**"
├── deny-etc-writes-broad.md        # tool: Write, matcher: "/etc/**"
└── allow-etc-cron-writes.md        # tool: Write, matcher: "/etc/cron.d/**" (more specific → wins)
```

Three files, each independently reviewable. The more-specific `allow-etc-cron-writes.md` wins over the broader `deny-etc-writes-broad.md` per Step 4.

### Step 6 — Test

Attempt the denied action and confirm:

1. The deny fires
2. The audit log shows the rule slug + severity + rationale
3. The allowed counterparts still work

If a deny fires when it should not, check precedence: did a broader rule shadow a more-specific allow?

## Outputs

A complete rule set as a directory of single-purpose `.md` files:

```
~/.claude/rules/                     # user scope
├── deny-force-push-on-main.md
├── deny-rm-rf-root.md
├── deny-ssh-key-writes.md
└── ...

./.claude/rules/                     # project scope (per repo)
├── deny-modify-migrations-without-review.md
└── ...
```

Each rule file is independently reviewable and version-controlled. Plugin-scope rules are declared in `plugin.json` `rules` array.

## Failure modes

Known pitfalls in rule authoring and how this skill catches them:

- **Mega-rule with conditional logic.** A single rule file packing multiple matchers and exceptions becomes unreviewable. Caught by: Step 5 split into single-purpose files.
- **Brittle exact-string matcher.** Rule matches `--force` but not `-f`; user discovers the gap only after the bypass. Caught by: Step 3 variant discipline.
- **Missing rationale.** Rule denies an action but no one remembers why; six months later, it gets removed because "this is annoying." Caught by: Step 2 requires a `Rationale` section.
- **Wrong scope.** User puts a project-specific rule in user scope and breaks unrelated projects. Caught by: Step 1 scope decision matrix.
- **Precedence surprise.** User expects a project-scope `allow` to override a user-scope `deny` but it doesn't (or vice versa). Caught by: Step 4 precedence model documented in the rule file's rationale, plus per-decision audit logging.
- **Rule vs hook confusion.** User writes a hook that re-implements rule evaluation. Caught by: this skill's See-also points to `authoring-tool-hook` for the executor / evaluator distinction.
- **Rule vs CLAUDE.md confusion.** User writes a CLAUDE.md instruction ("avoid X") and is surprised when Claude does X anyway. Caught by: When-NOT-to-use clarifies CLAUDE.md is advisory, rules are enforced.

## References

- `reference/rule-template.md` — copy-paste rule file with frontmatter + rationale skeleton
- `reference/matcher-patterns.md` — common matcher patterns per tool (Bash regex, Edit/Write path globs, structured matchers)
- [Claude Code permissions and rules documentation](https://code.claude.com/docs/en/permissions.md) — official reference for `.claude/rules/*.md` and `settings.json` permissions
- RCS `claude-code-meta/authoring-tool-hook` — how PreToolUse hooks invoke the rule evaluator
- RCS `claude-code-meta/authoring-plugin` — plugin manifest `rules` array for shipping rules with a plugin

## Examples

### Example 1: Deny force-push on main (happy-path)

Input: *"Deny `git push --force` or `-f` against main/master, repo-wide."*

Output: Skill writes `~/.claude/rules/deny-force-push-on-main.md` (user scope for cross-project coverage). Rule frontmatter: `decision: deny`, `tool: Bash`, `matcher: "git push (--force|-f).*\\b(main|master)\\b"`, `severity: high`. Rationale section names the incident class (lost teammate commits) and acceptable alternatives (force-push to a feature branch is unmatched and remains allowed; reset-and-new-commit is the recommended path on main). Cross-references the executor: the rule is declarative; the runtime (or a PreToolUse hook calling into the rule evaluator) is what enforces it.

### Example 2: Complex SSH + /etc policy across multiple files (edge-case)

Input: *"Deny writes to ~/.ssh and /etc, but allow writes to /etc/cron.d. Reads stay allowed."*

Output: Skill splits the policy into three single-purpose files:

- `deny-ssh-key-writes.md` — `tool: Write`, `matcher: "**/.ssh/**"`, `decision: deny`
- `deny-etc-writes-broad.md` — `tool: Write`, `matcher: "/etc/**"`, `decision: deny`
- `allow-etc-cron-writes.md` — `tool: Write`, `matcher: "/etc/cron.d/**"`, `decision: allow`

Explains the precedence: the third rule is more specific than the second, so it wins for paths under `/etc/cron.d`. The first two are independent and target different roots. Recommends a per-decision audit log row so the user can verify the right rule fired on each match.

### Example 3: Trivial allowlist handoff (anti-trigger)

Input: *"I just want to always allow `ls` without being prompted."*

Output: Skill answers no — a single trivial allowlist entry does not earn a rule file. Recommends adding `"Bash(ls *)"` to the `permissions.allow` array in `~/.claude/settings.json` (or `.claude/settings.local.json` for project-scope-not-committed). Cross-references the `update-config` skill. Explains rule files earn their overhead when the matcher is complex, the rationale needs to be auditable, or the same logic needs to be reused across projects.

## See also

- `claude-code-meta/authoring-tool-hook` — the executor side; hooks call into the rule evaluator at runtime
- `claude-code-meta/authoring-plugin` — bundle rules into a plugin via `plugin.json` `rules` array
- `claude-code-meta/auditing-instruction-hierarchy` — instruction files (CLAUDE.md) are advisory; rules are enforced — audit which is which
- `security/auditing-mcp-server-pre-trust` — for plugin-scope rules shipped by a third-party MCP plugin; the rule set itself becomes part of the six-check audit (Check 6: tool subset includes the rule set)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
