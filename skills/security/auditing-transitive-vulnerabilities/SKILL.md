---
name: auditing-transitive-vulnerabilities
description: >
  Audits a dependency graph for transitive vulnerabilities — vulnerabilities buried
  N levels deep that direct-dep scanners miss. Walks the dep graph (from lockfile
  or SBOM), enriches each CVE with EPSS exploit-probability, runs a reachability
  check (is the vulnerable symbol actually called from this project's code?), and
  ranks by exploitability x reachability. Use when a direct-dependency scan came
  back clean but a downstream scanner flagged something, when an upstream advisory
  mentions a package the user did not install directly, when preparing a fix-or-
  suppress decision for a "false-positive looking" transitive finding, or when
  needing to know whether a 10-level-deep CVE actually matters for this codebase.
version: 0.1.0
status: shipped
track: security
audience: [security-eng, appsec, devops, skill-author]
evidence:
  - quality-contract-NIST-SP-800-218
  - claude-secure-coding-rules
last-updated: 2026-05-23
---

# Auditing Transitive Vulnerabilities

## When to use

Trigger this skill when the user asks for or implies one of:

- A direct-dependency scan (npm audit, pip-audit, govulncheck) came back clean but a deeper scan (Snyk, Trivy, Grype, Dependency-Track) flagged something
- An upstream advisory mentions a package the user did not install directly (transitive)
- A CVE landed in the news and the user wants to know "are we exposed?" without manually walking the dep tree
- A vendor questionnaire asks "do you have any unpatched critical CVEs in your transitive dependencies?"
- The user has an SBOM (from `security/generating-sbom`) and wants to feed it through a vuln scanner
- The phrase "reachability", "exploitable path", or "we use this package but not THAT function" appears

## When NOT to use

Skip this skill and hand off when:

- The vulnerability is in a direct dependency the user just installed — use the direct-dep scanner output and standard upgrade path
- The user has no lockfile and no SBOM — generate an SBOM first (use `security/generating-sbom`); transitive audit needs a resolved graph
- The user wants to *triage* multi-tool SAST findings — different skill (`security/triaging-vulnerability-findings`); this skill is about dep-graph CVEs, not source-code SAST
- The user wants to verify SBOM signatures / attestations (planned: verifying-sigstore-signatures)
- The vulnerability is a runtime observation (EDR alert, IDS hit) — that is IR, not pre-merge audit

## Quick start

User says: "We have a CycloneDX SBOM for our payment-service. We need to know which transitive vulnerabilities actually matter. Run a real reachability-aware audit."

Skill response:

1. Validates the SBOM (CycloneDX 1.5 or SPDX 2.3 schema check)
2. Runs a vulnerability scan against the SBOM (`grype sbom:./sbom.json -o json`)
3. For each CVE, walks the dependency graph to determine the path from the project root to the vulnerable package (`A -> B -> C -> vulnerable-D`)
4. Enriches each CVE with EPSS exploit-probability (from FIRST EPSS API)
5. Runs a reachability check: does this project's source code actually call the vulnerable symbol, or is the vulnerable code dead in this context?
6. Ranks by `(CVSS severity x EPSS x reachability)` and outputs a triage table
7. Recommends remediation per finding (upgrade path, alternative package, suppress-with-rationale)

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| input | path | yes | — | Path to SBOM (CycloneDX or SPDX JSON) OR lockfile (`package-lock.json`, `uv.lock`, `go.sum`, etc.). |
| repo_root | path | no | `.` | Repository root for reachability analysis. |
| scanner | "grype" \| "trivy" \| "osv-scanner" | no | "grype" | Vulnerability scanner. Grype is the default; osv-scanner is the OSS-native alternative. |
| epss_lookup | "online" \| "offline" \| "skip" | no | "online" | Query EPSS API for each CVE. Offline expects `repo_root/.epss.csv`. |
| reachability | "callgraph" \| "import-only" \| "skip" | no | "import-only" | `callgraph` runs static call-graph reachability (slow, accurate). `import-only` checks whether the vulnerable package is imported anywhere (fast, less accurate). `skip` assumes reachable. |
| severity_threshold | "low" \| "medium" \| "high" \| "critical" | no | "medium" | Findings below threshold are summarized as counts. |

## Workflow

Copy this checklist into the response and check off items as the audit progresses:

```
Transitive vuln audit progress:
- [ ] Step 1: Validate input (SBOM schema or lockfile presence)
- [ ] Step 2: Run scanner (grype / trivy / osv-scanner) -> raw CVE list
- [ ] Step 3: Build dep-path for each CVE (project root -> ... -> vulnerable package)
- [ ] Step 4: EPSS enrichment for each CVE
- [ ] Step 5: Reachability check (callgraph or import-only)
- [ ] Step 6: Rank by severity x EPSS x reachability
- [ ] Step 7: Per-finding remediation (upgrade / alternative / suppress)
- [ ] Step 8: Emit audit report + remediation playbook
```

### Step 1: Validate input

- If input is an SBOM file: validate schema. Reject if invalid (an invalid SBOM produces silently wrong scanner output).
- If input is a lockfile: confirm lockfile + manifest both present and in sync (otherwise re-generate SBOM first via `security/generating-sbom`).

### Step 2: Scan

```bash
# Grype against SBOM
grype sbom:./sbom.cdx.json -o json --file vulns.json

# Trivy against SBOM
trivy sbom ./sbom.cdx.json --format json --output vulns.json

# OSV-Scanner against lockfile or SBOM
osv-scanner --lockfile=./uv.lock --format=json --output=vulns.json
osv-scanner --sbom=./sbom.cdx.json --format=json --output=vulns.json
```

Each scanner reports a `matches` array (Grype) or `Results` (Trivy) or `results` (OSV). Normalize to a common shape: `[{cve, package, version, severity, fixed_in, depth}]`.

### Step 3: Dep-path resolution

For each CVE, compute the path from project root to the vulnerable package:

- npm: walk `package-lock.json` `packages` tree
- pip / uv / poetry: walk lockfile dep graph
- Go: parse `go mod graph` output
- Maven: parse `mvn dependency:tree` output
- Cargo: parse `cargo tree` output

Result: `myapp -> express@4.21.0 -> body-parser@1.20.1 -> qs@6.11.0  (vulnerable)`.

Depth matters — a CVE at depth 6 is less likely to be reachable than a CVE at depth 1.

### Step 4: EPSS enrichment

For each CVE, look up EPSS probability:

- `online`: `https://api.first.org/data/v1/epss?cve=CVE-XXXX-NNNN`
- `offline`: read `repo_root/.epss.csv`

Record `epss_probability` (0..1) and `epss_percentile` per CVE.

EPSS is a 30-day exploit-likelihood signal, NOT a severity score. Use it to RANK findings of similar CVSS, not as a sole driver.

### Step 5: Reachability

**Modes:**

- **`callgraph`** (slow, accurate): build a static call graph from the project's source code; check whether any path from a project entry point reaches a symbol exported by the vulnerable package. Tools: `pyright` + custom walk for Python; `madge` / `dependency-cruiser` for JS; `go build -tags=...` analysis for Go; `jdeps` for Java.
- **`import-only`** (fast, conservative): grep / AST-walk the source for `import <vulnerable-package>` (or language-equivalent). If imported anywhere, treat as reachable.
- **`skip`**: assume reachable (overstates risk; use when reachability tools unavailable).

For each finding, record `reachability: reachable | likely-unreachable | dead`.

**Important caveat**: reachability of an upstream symbol does NOT guarantee exploitability — a project may import a package only for a utility function and never trigger the vulnerable code path. Callgraph analysis is necessary but not sufficient. Document this in the output.

### Step 6: Rank

`priority = severity_weight x reachability_weight x (1 + epss_probability) / log10(depth + 1)`

Where:

- severity_weight: critical=10, high=5, medium=2, low=1
- reachability_weight: reachable=1.0, likely-unreachable=0.3, dead=0.1
- depth: dependency depth (1 = direct, N = N levels of transitive)

Sort descending. Cap enumeration at 50 findings; tail summarized by package.

### Step 7: Per-finding remediation

For each top-N finding, recommend one of:

- **Upgrade direct dep**: if the vulnerable transitive can be lifted by upgrading a direct dep (e.g., `express` 4.21.0 -> 4.21.2 brings in patched `qs`)
- **Override** (npm `overrides`, yarn `resolutions`, pip `--upgrade-strategy eager`, Maven `<dependencyManagement>`): force a higher version of the transitive without touching direct deps
- **Replace**: swap the direct dep for an alternative whose transitive tree does not include the vulnerable package
- **Suppress with rationale**: if `reachability = dead` AND no fix available AND a documented rationale exists (in `.snyk` or `cve-suppressions.yaml` with date + reviewer + expiry)

The skill REFUSES silent suppression (no rationale, no expiry).

### Step 8: Report

Emit:

1. Counts summary (`X critical, Y high, Z medium`)
2. Ranked top-50 table (Rule · CVE · Package · Version · Depth · Severity · EPSS · Reachability · Priority · Remediation)
3. Per-finding remediation playbook (one paragraph per finding)
4. Suppression block (if any) — each suppression with rationale + expiry + reviewer
5. PR comment markdown ready to paste

## Outputs

1. **Audit report** markdown — counts, ranked table, remediation playbook, suppressions
2. **Machine-readable summary** at `audit-results.json` — for CI integration
3. **PR comment block** — ready to paste via `gh pr comment`
4. **Override / resolution snippets** — copy-paste blocks to add to `package.json` / `pyproject.toml` / etc. to force the patched transitive version

## Failure modes

- **Direct-dep blindness** — running `npm audit` or `pip-audit` against the manifest catches only direct deps, not transitive ones. Caught by: this skill scans against the resolved SBOM / lockfile, not the manifest.
- **Depth blindness** — treating a depth-1 CVE the same as a depth-10 CVE. Caught by: priority formula divides by `log10(depth + 1)`; depth-10 findings rank lower absent strong reachability evidence.
- **Reachability over-trust** — declaring a CVE "unreachable" because no static path reaches the vulnerable symbol, while runtime reflection / dynamic dispatch could still trigger it. Caught by: callgraph mode is documented as "necessary but not sufficient"; the report records reachability with explicit confidence, not a binary safe / unsafe.
- **Stale EPSS** — using EPSS values from a year ago; EPSS changes daily. Caught by: `online` mode fetches at audit time; `offline` mode records the CSV date and warns if older than 30 days.
- **Suppression rot** — a vendor `.snyk` ignore from 2 years ago that nobody reviewed since the upstream patched the CVE. Caught by: suppressions require an expiry date; the skill flags expired suppressions on each run.
- **Override silently breaking downstream** — forcing a higher version of `qs` via `overrides` can break `body-parser` in unexpected ways. Caught by: remediation playbook recommends running the test suite after applying any override; never blindly auto-applied.

## References

- `reference/scanner-output-normalization.md` — Grype / Trivy / OSV-Scanner output -> common shape
- `reference/reachability-methods.md` — per-language callgraph tools and import-only patterns
- `reference/remediation-patterns.md` — upgrade / override / replace / suppress decision tree
- [FIRST EPSS](https://www.first.org/epss/) — Exploit Prediction Scoring System
- [OSV.dev](https://osv.dev/) — Open Source Vulnerability database
- [GitHub Advisory Database](https://github.com/advisories)
- [Anchore Grype](https://github.com/anchore/grype)

## Examples

### Example 1: 10-level transitive CVE (happy-path)

Input: "Here is the CycloneDX SBOM for `payment-service`. Audit it for transitive vulnerabilities."

Output: Skill validates SBOM (pass). Runs `grype sbom:./sbom.cdx.json -o json`, gets 47 raw CVEs. Builds dep-paths: 5 direct, 18 at depth 2-3, 24 at depth 4+. Enriches EPSS for all 47. Reachability analysis (import-only) finds 19 reachable (i.e., the vulnerable package is imported somewhere in src/), 28 unreachable. Ranks: top finding is a critical SSRF in `urllib3` at depth 3 (CVSS 9.1, EPSS 0.85, reachable), patched in 2.2.2. Recommends bumping `requests` (direct dep) to 2.32.0 which pulls in `urllib3 >= 2.2.2`. Tail of 28 unreachable findings summarized by package family; no immediate action, re-audit if reachability changes.

### Example 2: CVE in unreachable code (edge-case)

Input: "Grype says we have CVE-2024-XXXXX in `lodash.template` at depth 4. Severity high. Is this actually a problem?"

Output: Skill walks dep-path: `myapp -> some-tool@1.2.3 -> sub-tool@0.5.0 -> lodash.template@4.5.0 (vulnerable)`. Runs reachability check. Determines `lodash.template` is imported by `sub-tool` only for a build-time helper not exposed at runtime. Reports: `reachability: likely-unreachable`, `confidence: medium` (static analysis cannot rule out dynamic dispatch). Priority is downgraded (high severity x 0.3 reachability x 0.05 EPSS = low priority). Recommendation: do NOT prioritize a fix this sprint; add a documented suppression with 90-day expiry; revisit when callgraph analysis confidence improves OR when a patched version exists at the same dep depth. Refuses to declare the CVE "false positive" without expiry.

### Example 3: Direct-deps-only flat repo (anti-trigger)

Input: "I only use 3 direct npm packages: react, react-dom, and lodash. No transitive concerns, right? Audit me."

Output: Skill clarifies that even 3 direct packages have transitive deps (lodash has ~0, react has ~10, react-dom has ~50+). Runs the audit anyway because transitive exposure is independent of direct-dep count. Notes that if the SBOM truly shows only 3 components (i.e., depth = 0), the skill's value is reduced and `npm audit` against direct deps suffices. Hands off to direct-dep audit if SBOM confirms no transitive deps; otherwise proceeds with the full pipeline.

## See also

- `security/generating-sbom` — the SBOM that this audit consumes
- `security/triaging-vulnerability-findings` — for SAST/DAST findings (this skill is for SCA / dep-graph CVEs)
- `security/auditing-pinned-dependencies` — verifies the lockfile that this audit's SBOM was generated from
- `workflow/pinning-reproducible-environments` — establishes the lockfile that anchors transitive depth

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from RCS spec (v4-batch-1, Σ 13); cross-referenced against OSV.dev, FIRST EPSS, and the NIST SP 800-218 SSDF PW.4 (re-use third-party components with attention to known vulnerabilities)
