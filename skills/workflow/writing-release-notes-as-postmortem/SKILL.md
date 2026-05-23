---
name: writing-release-notes-as-postmortem
description: >
  Writes release notes that double as miniature postmortems for every fixed
  regression. Each fix entry names the file/function where the bug lived, the
  root-cause class (off-by-one, race, schema drift, dependency CVE, etc.), the
  user-visible symptom, the test that was added to prevent recurrence, and the
  commit SHA. Use when shipping a bug-fix release, a security patch, a
  regression-fix sprint, or a stability-focused minor version where the
  audience needs to know not just what changed but why the bug existed and
  what stops it from coming back. Refuses to apply postmortem structure to a
  first release or to a pure-feature-announcement release where no regressions
  are being fixed; those need feature-announcement notes instead.
version: 0.1.0
status: shipped
track: workflow
audience: [data-scientist, ml-engineer, security-eng, devops]
evidence:
  - incident-rank-validation
  - ATACE
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Writing Release Notes as Postmortem

## When to use

Trigger this skill when the user requests or implies one of:

- A bug-fix, regression-fix, security-patch, or stability release
- Phrases like "release notes for the patch", "what fixed", "incident-driven release", "postmortem-style notes", "we shipped a hotfix"
- A minor/patch SemVer bump dominated by fixes rather than features (typical x.y.Z or x.Y.0 releases)
- A release where downstream teams need to know whether THEIR workflow was affected by the regression
- A regulated or audit-context release where remediation traceability matters (security advisories, GDPR fixes, SOC2 control failures)

## When NOT to use

Use feature-announcement notes (or a different skill) when:

- The release is v0.1.0 or any first release — there are no prior regressions to postmortem
- The release is pure feature work (new endpoints, new UI, new SKUs) with no fixes
- The release is a documentation-only, dependency-bump-only, or build-config-only release where no behavior changed
- The release ships to end consumers who care about features, not internals — write user-facing notes and link to internal postmortem notes separately
- Internal-only "boring releases" that ship continuously and have no notable changes

## Quick start

User says: *"We're cutting v2.3.1 — it's a patch release that fixed 4 bugs found in production over the last two weeks. Help me write the release notes."*

Skill response: produces release notes where every fix entry has six fields — Bug ID + symptom + file/function + root-cause class + test added + commit SHA. Notes are grouped by severity (critical → major → minor → cosmetic). A summary line at the top reports total fixes, total severity-weighted impact, and the cumulative test-coverage delta. Marketing language is stripped; sentences are declarative and engineering-flavored.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| version | string | yes | — | The version being released (e.g., "v2.3.1"). |
| changelog_source | "git-log" \| "issue-tracker" \| "user-paste" | yes | — | Where to pull the fix list from. |
| severity_taxonomy | "cvss" \| "internal-1-5" \| "user-paste" | no | "internal-1-5" | Severity scale to apply. |
| postmortem_depth | "minimal" \| "standard" \| "deep" | no | "standard" | Minimal = one line per fix; standard = six-field entries; deep = adds prevention plan + ownership. |
| audience | "engineer" \| "customer" \| "regulator" | no | "engineer" | Customer and regulator audiences strip internal jargon but preserve the six fields. |

## Workflow

Copy this checklist into the response and check off each item as the notes take shape:

```
Release-notes-as-postmortem progress:
- [ ] List every fix in the release (from git log / issues / user paste)
- [ ] For each fix, fill the six fields (ID, symptom, file:function, root cause, test, SHA)
- [ ] Classify each fix by severity (critical / major / minor / cosmetic)
- [ ] Sort by severity descending
- [ ] Write the executive summary line (count, weighted impact, coverage delta)
- [ ] Strip marketing language ("seamless", "blazing", "magical") from every sentence
- [ ] Add a "regressions NOT yet fixed" section if any are known but deferred
- [ ] Cross-link to the prior release's notes for context
```

### Step 1 — Enumerate the fixes

Pull the fix list from `git log <prev-tag>..HEAD --grep=fix` or the issue tracker's "fixed in vX.Y.Z" filter or the user's manual list. Each entry must trace to a commit SHA.

### Step 2 — Six fields per fix

For each fix, produce exactly:

1. **Bug ID** — issue number, CVE, or internal tracking ID
2. **Symptom** — one sentence in user-visible terms ("login button silently failed after 2-minute idle")
3. **Location** — `path/to/file.py:function_name` (or class, if more useful)
4. **Root-cause class** — choose from a small taxonomy: off-by-one, race condition, schema drift, dependency CVE, integer overflow, NULL deref, auth bypass, time-zone mishandling, encoding mismatch, leaky abstraction, missing validation, retry-storm, etc.
5. **Test added** — name the test that locks the fix in (`tests/test_auth.py::test_idle_session_reauth`); if no test was added, flag this entry as a follow-up
6. **Commit SHA** — short SHA + a link if a public viewer exists

### Step 3 — Severity sort

Critical → Major → Minor → Cosmetic. Severity comes from the configured taxonomy (CVSS for security, internal 1–5 otherwise). Tie-break by user-visible impact, not by author alphabetical.

### Step 4 — Executive summary line

One sentence at the top of the notes: count of fixes by severity, severity-weighted impact (sum of severities), coverage delta (new tests added / total). Example: *"v2.3.1 fixes 1 critical + 2 major + 1 cosmetic regression. Weighted severity = 11. Coverage +4 tests / +0.6% line coverage."*

### Step 5 — Strip marketing language

Specific banlist: seamless, blazing, magical, transformative, holistic, robust (without a number), comprehensive, exciting, delightful. Replace with the concrete fix or remove the sentence. Engineering-flavored notes survive audit; marketing-flavored notes don't.

### Step 6 — "Regressions NOT yet fixed"

If the team knows about regressions that did NOT make this release, list them with the planned target release. This section prevents the customer or successor team from interpreting silence as "no known issues" — a common postmortem failure mode is hidden-known-issues.

### Step 7 — Cross-link prior release

Link to the prior release's notes. A reader landing on v2.3.1 should be able to walk backward to v2.3.0 and v2.2.x with one click.

## Outputs

A markdown document at `CHANGELOG.md` (appended) or `releases/vX.Y.Z.md` (new), structured as:

1. **Header** — version + date + git tag
2. **Executive summary** — one sentence with the counts + weighted impact + coverage delta
3. **Fixes** — grouped by severity descending; each fix entry has the six fields
4. **Regressions NOT yet fixed** — known but deferred
5. **Operational notes** — migration steps, schema changes, env-var renames if any
6. **Prior release** — link
7. **Contributors** — git-shortlog-style list of authors of the fixed commits

Length scales with fix count; entries are terse — six fields per fix, three lines max each.

## Failure modes

Known pitfalls in release-notes-as-postmortem and how this skill catches them:

- **Marketing fluff** ("seamlessly resolves authentication friction"). Caught by: Step 5 explicit banlist and the replacement rule.
- **Hidden known issues** (the team knows about a regression and ships silently). Caught by: Step 6 "Regressions NOT yet fixed" is a required section, not optional.
- **No test added** (the fix is in but no regression test locks it). Caught by: Step 2 field 5; if the user cannot name a test, the entry is flagged as a follow-up rather than omitted.
- **Severity inflation** (every fix marked "critical" to make the release look impactful). Caught by: Step 3 taxonomy is configured; severity must trace to the taxonomy, not the marketing instinct.
- **Root-cause class glossed over** ("fixed an edge case"). Caught by: Step 2 field 4 forces a class from the taxonomy; "edge case" is not in the taxonomy.
- **Reverse-chronological-only changelog rot** (notes are a flat list of commits with no severity sort). Caught by: Step 3 severity sort is required.

## References

- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) — the categorical structure this skill builds on; this skill adds postmortem fields per-fix
- [SRECon postmortem culture talks](https://www.usenix.org/conferences/byname/925) — context for the postmortem-flavored writing style
- [CVSS v4.0 specification](https://www.first.org/cvss/v4.0/specification-document) — the severity taxonomy for security-focused fixes

## Examples

### Example 1: Patch release with 4 fixes (happy-path)

Input: *"v2.3.1 patch release. Fixed 4 bugs over the last two weeks."*

Output: notes with executive summary ("v2.3.1 fixes 1 critical + 2 major + 1 cosmetic. Weighted severity 11. Coverage +4 tests / +0.6%."); per-fix entries — Bug #4421 (critical, login silently failed after 2-min idle, auth.py:reauth_session, off-by-one in the JWT exp comparison, tests/test_auth.py::test_idle_session_reauth, SHA abc123); 3 more entries in the same shape; "Regressions NOT yet fixed" naming a deferred i18n bug targeted for v2.3.2; cross-link to v2.3.0 notes.

### Example 2: First release v0.1.0 (anti-trigger)

Input: *"We're cutting v0.1.0 — the first public release. Help me write the release notes."*

Output: skill declines to apply postmortem structure. Explains that v0.1.0 has no prior regressions to postmortem; the right artifact is feature-announcement notes covering capability list, supported platforms, install instructions, and known limitations. Hands off to a feature-announcement pattern.

## See also

- `workflow/writing-successor-primers` — pairs naturally; the primer carries founding principles, the postmortem-style notes carry the regression history
- `workflow/running-adversarial-premortem` — the prospective counterpart; premortem finds the failure modes, postmortem-style notes document the ones that escaped to production
- `security/triaging-vulnerability-findings` (planned v4-batch-1) — feeds severity classifications into Step 3 when the release is security-driven

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 under PRAGMATIC discipline as part of v2-batch-3 (research-discipline cluster)
