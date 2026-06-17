---
name: auditing-pinned-dependencies
description: >
  Audits a repository's install commands and CI for unpinned dependency installs.
  Greps for npx -y, @latest, pip install without ==, unpinned uvx --from git+,
  and curl|sh patterns across READMEs, Dockerfiles, GitHub Actions workflows,
  package.json scripts, pyproject.toml, requirements files, pre-commit configs,
  and mcp.json. Use when reviewing a new repo before adoption, evaluating an MCP
  server's install command, hardening an existing project against supply-chain
  attacks, or auditing CI pipelines for drift risk. Produces a per-file findings
  list with line numbers, suggested pinned forms, and remediation snippets.
version: 0.1.0
status: shipped
track: security
audience: [security-eng, devops, skill-author]
evidence:
  - quality-contract-NIST-SP-800-218
  - PreToolUse-supply-chain-bash-checks
last-updated: 2026-05-23
---

# Auditing Pinned Dependencies

## When to use

Trigger this skill when the user asks for or implies one of:

- Reviewing a new repository before adopting it into the team's stack or a Claude Code harness
- Evaluating an MCP server install command (`npx -y …`, `uvx --from git+…`) before adding to `mcp.json`
- Hardening an existing project against supply-chain attacks (PyPI takeovers, npm typosquatting, malicious tag-republishing)
- Auditing CI workflows for drift — same `main` branch builds fine today, breaks tomorrow because an unpinned dep silently bumped
- Reviewing a Dockerfile / Containerfile that uses base images without digest pinning

## When NOT to use

Skip this skill and hand off when:

- The repo is a brand-new project bootstrap scenario where the user explicitly wants the latest version on first install (e.g., `npm create vite@latest`)
- The repo is a throwaway prototype / personal scratch project where pinning friction outweighs benefit
- The user wants help WRITING a pinned install command (different skill: scaffolding install commands)
- The MCP server itself needs a full six-check audit, not just version pinning (use `security/auditing-mcp-server-pre-trust` instead — this skill is the dep-pinning slice)

## Quick start

User says: "Here is our team's Dockerfile. Audit the install commands for pinning issues."

Skill response: walks every install / RUN / FROM line. Per finding: file path · line number · current command · suggested pinned form · remediation snippet. Produces a verdict table with severity. Recommends `npm ci` over `npm install`, `pip install --require-hashes` where lockfile hashes are present, and `FROM image@sha256:…` for base images.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| target | repo path or file path | yes | — | The repository root or specific file to audit. |
| scan_files | list of strings | no | (default set) | Defaults: `README*.md`, `Dockerfile`, `Containerfile`, `.github/workflows/*.yml`, `package.json`, `pyproject.toml`, `requirements*.txt`, `Pipfile`, `pre-commit-config.yaml`, `mcp.json`, `.mcp.json`. |
| severity_threshold | "low" \| "medium" \| "high" | no | "medium" | Findings below this threshold are summarized as counts, not enumerated. |
| include_create_scaffolders | bool | no | false | If true, also flag `npm create *@latest`, `cargo generate`, etc. By default these are excluded as legitimate one-shot scaffolds. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as the audit progresses:

```
Dep-pinning audit progress:
- [ ] Scan README + install docs for curl|sh and npx -y patterns
- [ ] Scan Dockerfile / Containerfile for FROM without @sha256 and RUN install commands
- [ ] Scan .github/workflows/*.yml for action versions and install steps
- [ ] Scan package.json scripts + dependencies for unpinned ranges (^, ~, *, latest)
- [ ] Scan pyproject.toml / requirements files for unpinned specifiers
- [ ] Scan mcp.json / .mcp.json for unpinned MCP install commands
- [ ] Produce per-file findings with line numbers + suggested pinned form
- [ ] Final verdict: pass / pass-with-warnings / fail
```

### Step 1: Blocking patterns (must-fix)

See `reference/unpinned-install-patterns.md` for the complete pattern catalog. Top items:

- `npx -y <pkg>` (no version) — pin to `npx -y <pkg>@<version>` or save the script and review
- `npm install <pkg>` without `@<version>` — pin to `<pkg>@1.2.3` or use `npm ci` against a committed lockfile
- `pip install <pkg>` without `==<version>` — pin to `<pkg>==1.2.3` or use `-r requirements.lock`
- `uvx --from git+<url>` without `#<ref>` or `@<sha>` — pin the git ref (`#v1.2.3` or `@<sha>`); HEAD of default branch can change
- `@latest` anywhere
- `curl … | sh`, `wget … | bash`, `iwr … | iex` — save the script to disk, review, then run

### Step 2: Acceptable forms

- `<pkg>@1.2.3` (npm)
- `<pkg>==1.2.3` (pip)
- `git+<url>@<sha>` or `git+<url>#<tag>`
- `pip install -r requirements.lock` (lockfile-pinned)
- `npm ci` (enforces `package-lock.json`)
- `pip install --require-hashes -r requirements.txt` (hash-enforced)

### Step 3: Defense-in-depth recommendations (warnings, not blocking)

- `FROM python:3.13` → `FROM python:3.13.1-slim@sha256:…` (digest-pinned base image)
- GitHub Actions `uses: actions/checkout@v4` → `uses: actions/checkout@<sha>` (SHA-pinned actions)
- `npm install` in CI → `npm ci` (enforces lockfile)
- `pip install` in CI → `pip install --require-hashes -r requirements.txt`

### Step 4: Produce findings table

Per finding:

```
| File | Line | Current | Suggested | Severity | Remediation |
|------|------|---------|-----------|----------|-------------|
| Dockerfile | 12 | RUN npm install express | RUN npm install express@4.21.0 | High | Pin or use `npm ci` against lockfile |
```

## Outputs

A markdown audit report:

1. **Repo identity** — name + commit SHA + audit date
2. **Per-file findings table** — File · Line · Current · Suggested · Severity · Remediation
3. **Counts summary** — high / medium / low / informational findings
4. **Final verdict** — pass / pass-with-warnings / fail (any high-severity = fail)
5. **Recommended next steps** — specific commands to run (`npm ci`, `uv lock`, `pip-compile --generate-hashes`)

## Failure modes

Known pitfalls in dep-pinning audits and how this skill catches them:

- **Audit theater** — running grep without inspecting context, producing false positives on every range specifier. Caught by: severity threshold + scaffolder exclusion + acceptable-forms list to suppress noise.
- **Scaffolder false positive** — flagging `npm create vite@latest` for a brand-new project as a pinning violation. Caught by: `include_create_scaffolders: false` default + explicit "Acceptable scaffolder" carve-out.
- **Git+ HEAD trap** — accepting `uvx --from git+https://github.com/foo/bar.git` as pinned because it specifies a URL. Caught by: explicit Step 1 rule that git+ without `#<ref>` or `@<sha>` is unpinned (resolves to HEAD of default branch, which moves).
- **Lockfile-without-enforcement** — committing `package-lock.json` but CI uses `npm install` (which ignores the lockfile). Caught by: Step 3 recommendation to switch CI to `npm ci`.
- **Range specifier ambiguity** — `^1.2.3` and `~1.2.3` are pinned RANGES, not exact pins. Caught by: severity-medium finding with explanation that ranges allow silent minor/patch bumps.

## References

- `reference/unpinned-install-patterns.md` — complete catalog of blocking patterns + acceptable forms + per-ecosystem notes
- `reference/audit-report-template.md` — markdown template for the per-file findings table
- [NIST SP 800-218 SSDF](https://csrc.nist.gov/Projects/ssdf) — Secure Software Development Framework, basis for the pinning requirement
- [OpenSSF Scorecard](https://github.com/ossf/scorecard) — automated check for pinned dependencies

## Examples

### Example 1: Mixed Dockerfile audit (happy-path)

Input: "Here is our team's Dockerfile. Audit the install commands." [Dockerfile content with mixed pinned and unpinned RUN statements]

Output: Skill walks each RUN line. Flags `RUN npm install express` (line 12) as high-severity — suggests `RUN npm install express@4.21.0` or switch to `npm ci`. Flags `RUN pip install requests` (line 18) — suggests `requests==2.32.0`. Does NOT flag `RUN apt-get install -y curl=7.88.1-10` (line 8) as it is properly version-pinned. Produces the findings table with 2 high, 0 medium, 1 informational.

### Example 2: `uvx --from git+` without ref (edge-case)

Input: "We use `uvx --from git+https://github.com/anthropic/somelib.git` to install our internal CLI. Is that pinned?"

Output: Skill identifies the install as UNPINNED. Explains that git+ without `#<tag>` or `@<sha>` resolves to HEAD of the default branch, which can change without notice. Recommends pinning to a specific tag (`#v1.2.3`) or commit SHA (`@<sha>`). Notes that for security-sensitive contexts, SHA pinning is preferred because tags can be re-pointed by the repo maintainer.

### Example 3: Project scaffold (anti-trigger)

Input: "I just ran `npm create vite@latest my-app -- --template react`. Should I have pinned it?"

Output: Skill does NOT flag the `create-vite` invocation as a pinning failure. Explains that `npm create *@latest` is a one-shot scaffolder, not a runtime dependency. Recommends instead that the user pin the resulting RUNTIME dependencies in the new project's `package.json` — including running `npm install` once and committing the resulting `package-lock.json` for CI to consume via `npm ci`.

## See also

- `security/auditing-mcp-server-pre-trust` — broader six-check MCP audit; this skill is the version-pin slice
- `workflow/pinning-reproducible-environments` — the proactive companion: build a project that pins from day one
- `workflow/auditing-source-provenance` — pairs naturally; provenance.json captures the pinned versions that this audit verified

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from Rock's harness `foundation/00-quality-contract.md` QC.1 (NIST SP 800-218 pinning requirement) and the `PreToolUse-supply-chain-bash-checks.py` hook patterns
