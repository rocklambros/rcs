# Remediation patterns

Per-finding, the audit recommends one of four actions: **upgrade direct dep**, **override transitive**, **replace direct dep**, or **suppress with rationale + expiry**. This reference details each path.

## Decision tree

```
Is there a fixed version of the vulnerable package?
├─ NO -> Suppress (with expiry + reviewer) OR find a replacement
└─ YES
   |
   Can a direct-dep upgrade pull in the patched transitive version?
   ├─ YES -> Upgrade direct dep (preferred — least risk)
   └─ NO
      |
      Does the ecosystem support transitive overrides?
      ├─ YES -> Override transitive (npm/yarn/pnpm/maven/gradle/uv) AND run the test suite
      └─ NO -> Replace the direct dep (or accept risk via suppress-with-rationale)
```

## 1. Upgrade direct dep

Preferred. Bumps a direct dep to a version that pulls in the patched transitive automatically.

```bash
# npm
npm install express@4.21.2  # if 4.21.2 brings in patched qs

# pip / uv
uv add "requests>=2.32.0"   # if 2.32.0 pulls in patched urllib3

# go
go get github.com/foo/bar@v1.5.0
go mod tidy
```

Verify with the scanner:

```bash
grype sbom:./sbom.cdx.json -o json | jq '.matches[] | select(.vulnerability.id == "CVE-...")'
```

## 2. Override transitive (when direct-dep upgrade is impossible)

Forces a higher version of the transitive without touching direct deps. Useful when the direct dep cannot be upgraded (breaks API).

### npm: `overrides`

```json
{
  "overrides": {
    "qs": "6.13.0"
  }
}
```

### pnpm: `pnpm.overrides`

```json
{
  "pnpm": {
    "overrides": {
      "qs": "6.13.0"
    }
  }
}
```

### yarn: `resolutions`

```json
{
  "resolutions": {
    "qs": "6.13.0"
  }
}
```

### pip / uv: constrained requirements

```toml
# pyproject.toml
[project]
dependencies = [
  "requests",
  "urllib3>=2.2.2"  # transitive override via direct pin
]
```

### Maven: `<dependencyManagement>`

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.example</groupId>
      <artifactId>vulnerable-dep</artifactId>
      <version>1.5.0</version>
    </dependency>
  </dependencies>
</dependencyManagement>
```

### Gradle: `resolutionStrategy.force`

```groovy
configurations.all {
  resolutionStrategy {
    force 'org.example:vulnerable-dep:1.5.0'
  }
}
```

### Go: `replace` directive in `go.mod`

```go
replace github.com/foo/bar => github.com/foo/bar v1.5.0
```

### Caveat — test after every override

Overrides can break the direct dep that bundled the transitive — the direct dep may have been pinning the OLD transitive for a reason (API breakage). Always run the full test suite (unit + integration + e2e) after applying an override. If tests fail, fall back to "replace direct dep" or suppress-with-rationale.

## 3. Replace direct dep

Swap the direct dep for an alternative whose transitive tree does not include the vulnerable package.

- Find candidates: search package registries, GitHub topics, OSS Index
- Evaluate alternatives for: maintenance status, license, transitive tree, ecosystem support
- Migrate the codebase (often largest engineering cost)

This is the most disruptive remediation; reserve for cases where upgrade and override both fail.

## 4. Suppress with rationale + expiry

When NO fix is available AND reachability is `likely-unreachable` AND the user has determined the risk is acceptable, suppress with rationale.

### `.snyk` ignore (works for Snyk-scanned projects)

```yaml
ignore:
  SNYK-PYTHON-LODASHTEMPLATE-XXX:
    - "*":
        reason: "lodash.template only used at build time, not reachable at runtime. Reviewed by alice@example.com 2026-05-23."
        expires: 2026-08-23T00:00:00Z
```

### `cve-suppressions.yaml` (custom; works across scanners)

```yaml
suppressions:
  - cve: CVE-2024-XXXXX
    package: lodash.template
    rationale: "Used only at build time; runtime reachability ruled out via callgraph (high confidence)"
    reviewer: alice@example.com
    expires: 2026-08-23
    re_review_after: 2026-08-23
    references:
      - https://github.com/our-org/our-repo/pull/4567
```

The audit reads this file on each run and flags any expired suppressions.

### What's NOT allowed

- Silent suppression (no rationale)
- Suppression with no expiry (rots forever)
- Suppression without a reviewer name (no accountability)
- Suppression based on "vendor said it's fine" without a checkable upstream issue link

## Verification after remediation

Every remediation should be verified by re-running the audit:

```bash
# Regenerate SBOM after dep changes
syft <repo> -o cyclonedx-json=sbom.cdx.json

# Re-scan
grype sbom:./sbom.cdx.json -o json --file vulns.json

# Diff against pre-remediation vulns
diff <(jq -S . vulns.json.before) <(jq -S . vulns.json) > remediation-diff.txt
```

Findings should drop. If a finding remains after an upgrade, the upgrade did not actually lift the patched transitive — re-investigate the dep-path.
