# Rule-application report template

Markdown template for the report. Fill every section. Do not omit the skipped-rules table — silent skipping is the failure mode this skill exists to prevent.

```markdown
# Secure-coding rule application — <target name>

Run date: <YYYY-MM-DD>
Target: <repo path> @ <commit-sha>
Corpus: <corpus path> @ <corpus revision> (<format>)
Rules indexed: <N>
Applicable rules: <M>
Skipped rules: <N - M>

## Stack manifest

- Languages: <list>
- Frameworks: <list>
- AI/ML stack: <list or "none detected">
- Data layer: <list>
- Runtime: <list or "none detected">

If any line is wrong, re-run with `stack_overrides: {...}`.

## Findings (severity ≥ <severity_floor>)

| Rule id | Title | File | Line | Severity | Fix |
|---|---|---|---|---|---|
| <id> | <title> | <path> | <line> | <severity> | <one-line fix> |
| ... |

Counts (all severities):
- Critical: <n>
- High: <n>
- Medium: <n>
- Low: <n>
- Informational: <n>

(Findings below severity_floor=<value> are not enumerated. Re-run with a lower floor to see them.)

## Skipped rules

| Rule id | Reason skipped |
|---|---|
| <id> | applies to Flask, project uses FastAPI |
| <id> | applies to JavaScript, project is Python-only |
| <id> | precondition unmet: requires file-upload endpoint, none detected |
| ... |

## Open questions

Each is a precondition the user must resolve before the corresponding rule can be applied:

- <rule-id>: <question — e.g., "Does the /admin/users/{id}/export route accept file uploads?">
- <rule-id>: <question>

## Conflicts

Where two corpus rules give contradictory guidance, both are surfaced; the user picks the authoritative policy:

- <rule-id-a> vs <rule-id-b>: <description of conflict, e.g., "bcrypt cost ≥ 12 vs argon2id required">

(Empty section if no conflicts.)

## Next steps

- Re-verify findings with: `<concrete command, e.g., semgrep --config <selected-subset> .>`
- Open issues for high+ findings against the team's tracker
- Re-run this skill after the corpus is updated (point to new corpus revision)
- For skipped rules whose preconditions were unmet: confirm with the user whether to add an upstream control or document the exclusion

## Provenance

- Corpus commit SHA: <sha>
- Target commit SHA: <sha>
- Skill version: <semver>
- Run date: <YYYY-MM-DD>
```

## Notes on the template

- **Always include the stack manifest at the top.** This is the first thing the user reads. If it is wrong, every finding below is suspect.
- **Skipped-rules table is mandatory.** Even if every rule applied, write `(no rules skipped)` explicitly.
- **Open-questions section is mandatory.** Even if zero open questions, write `(none)` explicitly. The user must know that the absence is a positive finding, not an omission.
- **Conflicts section may be empty.** Most corpora are internally consistent. Write `(no conflicts)` if so.
- **Provenance section is mandatory.** Without it, the audit is not reproducible.
