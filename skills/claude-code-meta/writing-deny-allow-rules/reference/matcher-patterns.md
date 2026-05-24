# Matcher patterns per tool

Common matcher patterns for rules scoped to each tool type.

## Bash (regex on the command string)

| Intent | Matcher |
|---|---|
| Deny any rm -rf at filesystem root | `\\brm\\s+-rf\\s+/` |
| Deny rm -rf $HOME and aliases | `\\brm\\s+-rf\\s+(~|\\$HOME|/Users/[^/\\s]+)\\b` |
| Deny git push --force or -f on main/master | `git push (--force|-f).*\\b(main|master)\\b` |
| Deny --dangerously-skip-permissions invocation | `--dangerously-skip-permissions` |
| Deny curl \| sh pattern | `curl\\b.*\\|\\s*(sh|bash)` |
| Deny unpinned npm/npx install | `(npx -y|npm install [^@]+)$` |
| Deny systemctl mutations | `\\bsystemctl\\s+(start|stop|restart|enable|disable|mask|unmask)\\b` |

Variants to consider for any Bash rule:

- Flags can appear in different orders; use `.*` or character classes
- Short forms (`-f`) and long forms (`--force`) often map to the same action
- Subcommands (`git push`, `git push origin`) can be variants of the same intent
- Pipes and substitutions can defeat naive matchers; test against the variants you care about

## Edit / Write / Read (path glob)

| Intent | Matcher |
|---|---|
| Deny any write under .ssh | `**/.ssh/**` |
| Deny any write to /etc | `/etc/**` |
| Allow writes under /etc/cron.d (overrides above when more specific) | `/etc/cron.d/**` |
| Deny edits to lockfiles | `**/*.lock` |
| Deny edits to CI workflows | `.github/workflows/**` |
| Deny direct edits to migration files (require review) | `**/migrations/*.sql` |
| Ask before editing production config | `config/production/**` |

Globs follow standard shell-glob semantics:

- `*` — any chars except `/`
- `**` — any chars including `/` (multi-segment)
- `?` — single char
- `[abc]` — char class

When you need conditional logic that does not fit a single glob, split into multiple single-purpose rules per `writing-deny-allow-rules` Step 5.

## Tool name = "*" (cross-tool rules)

Cross-tool rules apply to every tool invocation. Use sparingly — they fire on every call and the matcher must be deterministic. Common patterns:

| Intent | Matcher |
|---|---|
| Deny any tool call referencing a secret-looking string | (cross-tool; pattern depends on the secret format you can detect) |
| Audit-log every Edit/Write to a sensitive directory | (combine an audit-logging hook with a more-specific rule; cross-tool is the wrong layer here) |

Cross-tool rules are rare in practice. Most real policies are per-tool. If a cross-tool rule is needed, prefer a PreToolUse hook with explicit per-tool logic (see `authoring-tool-hook`).

## Structured matchers

For tools with structured input (JSON), some Claude Code versions support structured matchers on individual input fields rather than a regex on the serialized input:

```yaml
matcher:
  tool: Bash
  field: command
  pattern: "git push --force"
```

Or:

```yaml
matcher:
  tool: Write
  field: file_path
  glob: "/etc/**"
```

Structured matchers are more precise than regex on serialized input but require version support. Check your Claude Code version's permissions documentation before relying on them.

## Testing matchers

Before committing a rule, test the matcher against the variants you care about:

```bash
# For a Bash regex matcher:
echo "git push --force origin main" | grep -E 'git push (--force|-f).*\b(main|master)\b'
echo "git push -f main" | grep -E 'git push (--force|-f).*\b(main|master)\b'
echo "git push --force-with-lease main" | grep -E 'git push (--force|-f).*\b(main|master)\b'  # decide: should this match?
echo "git push origin feature/x --force" | grep -E 'git push (--force|-f).*\b(main|master)\b'  # decide: should this NOT match (it does not target main)
```

For path globs, list the files matched by the glob using shell `ls`:

```bash
ls -d /etc/**  # see what /etc/** matches
```

A matcher that does not catch the variants you care about is a false-negative bug. A matcher that catches too much is a false-positive bug. Both fail the rule's intent.
