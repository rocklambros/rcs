# Scanner output normalization

Each vulnerability scanner emits a slightly different JSON shape. This reference maps Grype / Trivy / OSV-Scanner output to a common shape for the audit pipeline's ranking step.

## Common normalized shape

```json
{
  "cve": "CVE-2024-XXXXX",
  "package": "urllib3",
  "version_installed": "2.0.4",
  "ecosystem": "pypi",
  "severity": "high",
  "cvss_v3_score": 7.5,
  "fixed_in": "2.2.2",
  "depth": 3,
  "dep_path": ["payment-service", "requests@2.31.0", "urllib3@2.0.4"],
  "scanner_source": "grype"
}
```

## Grype output

```json
{
  "matches": [
    {
      "vulnerability": {
        "id": "CVE-2024-XXXXX",
        "severity": "High",
        "cvss": [{"metrics": {"baseScore": 7.5}}],
        "fix": {"versions": ["2.2.2"], "state": "fixed"}
      },
      "artifact": {
        "name": "urllib3",
        "version": "2.0.4",
        "type": "python",
        "purl": "pkg:pypi/urllib3@2.0.4"
      }
    }
  ]
}
```

Normalization:

- `cve` <- `matches[*].vulnerability.id`
- `package` <- `matches[*].artifact.name`
- `version_installed` <- `matches[*].artifact.version`
- `severity` <- `matches[*].vulnerability.severity` (lowercased)
- `cvss_v3_score` <- `matches[*].vulnerability.cvss[?].metrics.baseScore` (first v3 entry)
- `fixed_in` <- `matches[*].vulnerability.fix.versions[0]`
- `ecosystem` <- inferred from PURL prefix

## Trivy output

```json
{
  "Results": [
    {
      "Target": "Pipfile.lock",
      "Vulnerabilities": [
        {
          "VulnerabilityID": "CVE-2024-XXXXX",
          "PkgName": "urllib3",
          "InstalledVersion": "2.0.4",
          "FixedVersion": "2.2.2",
          "Severity": "HIGH",
          "CVSS": {"nvd": {"V3Score": 7.5}}
        }
      ]
    }
  ]
}
```

Normalization:

- `cve` <- `Vulnerabilities[*].VulnerabilityID`
- `package` <- `Vulnerabilities[*].PkgName`
- `version_installed` <- `Vulnerabilities[*].InstalledVersion`
- `severity` <- `Vulnerabilities[*].Severity` (lowercased)
- `cvss_v3_score` <- `Vulnerabilities[*].CVSS.nvd.V3Score` (fallback to redhat, ghsa, etc.)
- `fixed_in` <- `Vulnerabilities[*].FixedVersion`

## OSV-Scanner output

```json
{
  "results": [
    {
      "source": {"path": "uv.lock"},
      "packages": [
        {
          "package": {"name": "urllib3", "version": "2.0.4", "ecosystem": "PyPI"},
          "vulnerabilities": [
            {
              "id": "GHSA-XXXX-YYYY-ZZZZ",
              "aliases": ["CVE-2024-XXXXX"],
              "severity": [{"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}],
              "database_specific": {"severity": "HIGH"},
              "affected": [{"ranges": [{"events": [{"fixed": "2.2.2"}]}]}]
            }
          ]
        }
      ]
    }
  ]
}
```

Normalization:

- `cve` <- `aliases[?startsWith=CVE-]` (fallback to GHSA id if no CVE)
- `package` <- `package.name`
- `version_installed` <- `package.version`
- `ecosystem` <- `package.ecosystem` (lowercased: PyPI -> pypi)
- `severity` <- `database_specific.severity` (lowercased)
- `cvss_v3_score` <- parse from `severity[*].score` CVSS vector
- `fixed_in` <- `vulnerabilities[*].affected[*].ranges[*].events[?fixed]`

## Depth + dep_path computation

After normalization, walk the lockfile or SBOM dependency graph to compute the path:

- npm (`package-lock.json`): the `packages` object has parent pointers; BFS from project root
- pip / uv / poetry: walk lockfile's `dependencies` table
- Go: parse `go mod graph` (each line is `A -> B`)
- Maven: parse `mvn dependency:tree -DoutputType=text`
- Cargo: parse `cargo tree --format json`

If the package appears at multiple depths, record the SHORTEST path (worst-case from a reachability standpoint).

## Severity normalization

Lowercase, then map:

| Scanner | Original | Normalized |
|---|---|---|
| Grype | `Critical` | `critical` |
| Grype | `High` | `high` |
| Grype | `Medium` | `medium` |
| Grype | `Low` | `low` |
| Grype | `Negligible` | `info` |
| Trivy | `CRITICAL` | `critical` |
| Trivy | `HIGH` | `high` |
| OSV | `database_specific.severity == "CRITICAL"` | `critical` |
| Any | missing severity | infer from `cvss_v3_score` (>=9 critical, 7-8.9 high, 4-6.9 medium, <4 low) |
