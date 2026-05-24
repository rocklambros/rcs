# Rule file template

Copy-paste skeleton for a single rule file under `~/.claude/rules/`, `./.claude/rules/`, or a plugin's `rules/` directory.

## Skeleton

```markdown
---
name: <deny-or-allow-prefix>-<short-slug>
decision: deny | allow | ask
tool: Bash | Edit | Write | Read | * | <other tool name>
matcher: "<regex / glob / structured matcher>"
severity: low | medium | high | critical
---

# <Title that mirrors the filename, more readable>

## Rationale

<Why this rule exists. Write for a reviewer six months from now who has no
context. Include incident references, threat-model citations, or compliance
mandates if applicable.>

## Allowed alternatives

<If the rule is a deny, what should the user do instead? List concrete
alternatives so the rule is not just a blocker but a redirect.>

## Audit notes

<Optional: related rules, dates of policy changes, links to incident
postmortems, links to compliance docs.>
```

## Example: deny rule

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
CI/CD downstream pipelines that assume linear history.

## Allowed alternatives

- Force-push to a feature branch: `git push --force origin my-feature` (this rule does NOT match feature branches)
- Reset main locally and push a new commit instead of force-pushing
- If you truly need to overwrite main (e.g., security incident requires history rewrite), temporarily disable the rule with explicit rationale in the commit message

## Audit notes

- Incident reference: 2026-Q1, lost 8 hours of release-engineering work after a force-push to main
- Related rule: `deny-force-push-on-release-branches.md`
```

## Example: allow rule (overrides a broader deny)

```markdown
---
name: allow-etc-cron-writes
decision: allow
tool: Write
matcher: "/etc/cron.d/**"
severity: medium
---

# Allow writes under /etc/cron.d

## Rationale

The broader `deny-etc-writes-broad.md` rule denies writes to `/etc/**`. This
allow rule is more specific and applies only to `/etc/cron.d/**`, which is the
documented location for adding cron job definitions in this environment. Per
the precedence model, more-specific wins over less-specific.

## Allowed alternatives

(Not applicable — this IS the allowed path.)

## Audit notes

- Documented requirement: ops runbook section 4.2 requires cron jobs in `/etc/cron.d/`, not `/etc/crontab`
- Related rule: `deny-etc-writes-broad.md`
```

## Example: ask rule

```markdown
---
name: ask-edit-production-config
decision: ask
tool: Edit
matcher: "config/production/**"
severity: medium
---

# Ask before editing production config

## Rationale

Production config changes are not strictly denied — there are legitimate
reasons to edit them (rotation, incident response) — but they should be
explicit per-action approvals rather than silent edits during a refactor.

## Allowed alternatives

(Not applicable — this is a per-action prompt, not a deny.)
```
