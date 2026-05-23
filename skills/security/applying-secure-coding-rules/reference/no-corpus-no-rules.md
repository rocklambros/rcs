# No corpus, no rules — rationale for the refusal

This skill refuses to fabricate secure-coding rules from training memory when the user has not supplied a corpus. The refusal is non-negotiable. The rationale:

## 1. Unverifiable recommendations

Rules invented from training memory have no provenance. The user cannot trace a recommendation back to a policy document, a CVE class, a CWE entry, a SARIF rule pack, or a team standard. When a developer asks "why does the audit flag this?", the answer "because I remembered a pattern" is not acceptable for production security review.

## 2. Conflict with team policy

A model's training memory aggregates patterns from many sources. Some patterns will contradict the team's actual policy (e.g., the team uses argon2id but a training-memory rule recommends bcrypt; the team allows raw SQL with parameterized queries but a training-memory rule mandates ORM-only). Applying mismatched rules wastes review cycles and trains the team to ignore audit output.

## 3. Drift between runs

Without a fixed corpus, two audits of the same codebase can produce different findings depending on which patterns the model surfaces this run versus last run. The user cannot diff results meaningfully because the "rule pack" itself is non-deterministic.

## 4. Audit-theater risk

A model that fabricates rules will often produce a long, plausible-looking findings list. The list looks like work product but is not actionable: the developer cannot say "we applied rule pack X version Y" in a compliance report or audit trail.

## 5. The RCS v1 catalog-exclusion principle

Per the RCS public-skills-repo design (`docs/superpowers/specs/2026-05-22-rcs-public-skills-repo-design.md`) and the user's feedback memory: v1 deliberately ships NO bundled rule catalogs (no NIST control set, no OWASP rules, no CWE pack). Skills accept corpora as inputs; bundling catalogs is a later-version feature. Fabricating rules in this skill would violate that design principle by smuggling a de-facto catalog through the back door.

## The accepted alternatives

When the user does not have a corpus, suggest one of:

1. **claude-secure-coding-rules** — if the user has access to Rock's repository (or a fork) following that convention, point at it
2. **A published semgrep rule pack** — `p/python`, `p/javascript`, `p/security-audit`, `p/owasp-top-ten`, `p/ai`, or any community pack
3. **A SARIF rule pack exported from an existing SAST tool** — most SAST tools (CodeQL, Semgrep, Snyk Code) can export their rule sets as SARIF
4. **A markdown rule sheets repository following the `claude-secure-coding-rules` convention**
5. **A YAML rule pack** the team maintains internally

After the user picks one, re-invoke this skill with `corpus=<path>` and `target=<repo>`.

## What the refusal message says

The refusal MUST include:

1. The fact that no corpus was supplied
2. The list of accepted corpus formats (so the user can quickly produce one)
3. The reason (unverifiable + policy conflict + drift + audit theater)
4. A constructive next step (the four alternatives above)

The refusal MUST NOT:

- Fabricate even a "starter" rule list as a placeholder
- Pick a default corpus (e.g., OWASP Top 10) on the user's behalf
- Soften by offering "general principles I recall" — that is fabrication with extra steps
