# SBOM minimum-required fields

Per NTIA Minimum Elements and CycloneDX 1.5 / SPDX 2.3, these fields MUST be present for a complete SBOM. The skill's Step 5 validation enforces this.

## NTIA minimum elements (baseline)

| Field | CycloneDX path | SPDX path |
|---|---|---|
| Supplier | `components[*].supplier.name` | `Package.supplier` |
| Component name | `components[*].name` | `Package.name` |
| Version | `components[*].version` | `Package.versionInfo` |
| Other unique identifier (PURL or CPE) | `components[*].purl` or `components[*].cpe` | `Package.externalRefs[*]` |
| Dependency relationship | `dependencies[*]` | `Relationship` (DEPENDS_ON / CONTAINS) |
| SBOM author | `metadata.authors[*].name` | `CreationInfo.Creator` |
| Timestamp | `metadata.timestamp` | `CreationInfo.Created` |

A component missing any of these is a partial entry and the skill flags it.

## CycloneDX 1.5 required fields

| Field | Required | Notes |
|---|---|---|
| `bomFormat` | yes | Must be `"CycloneDX"` |
| `specVersion` | yes | Must be `"1.5"` (or current) |
| `serialNumber` | no but recommended | URN-format unique id (`urn:uuid:...`) for re-identification |
| `metadata.timestamp` | yes | ISO 8601 datetime |
| `metadata.tools[*]` | recommended | The tool that produced this SBOM |
| `metadata.component` | recommended | The top-level project this SBOM describes |
| `components[*].type` | yes | `application` / `framework` / `library` / `container` / `operating-system` / `device` / `firmware` / `file` |
| `components[*].name` | yes | |
| `components[*].version` | yes (effectively) | |
| `components[*].bom-ref` | yes | Internal-to-this-document unique id for the component |
| `components[*].purl` | recommended | Package URL — the standard cross-tool identifier |
| `components[*].licenses[*]` | recommended | License declaration |
| `components[*].hashes[*]` | recommended | Content hashes for integrity verification |
| `dependencies[*].ref` | recommended | bom-ref of a component |
| `dependencies[*].dependsOn[*]` | recommended | bom-refs of dependencies |

## SPDX 2.3 required fields

| Field | Required | Notes |
|---|---|---|
| `SPDXVersion` | yes | `SPDX-2.3` |
| `DataLicense` | yes | Typically `CC0-1.0` for the SBOM metadata itself |
| `SPDXID` | yes | `SPDXRef-DOCUMENT` for the doc; `SPDXRef-<id>` for each Package |
| `DocumentName` | yes | |
| `DocumentNamespace` | yes | A globally unique URI |
| `CreationInfo.Creator` | yes | At least one Creator |
| `CreationInfo.Created` | yes | ISO 8601 datetime |
| `Package.SPDXID` | yes | Unique within doc |
| `Package.name` | yes | |
| `Package.downloadLocation` | yes | URL or `NOASSERTION` |
| `Package.filesAnalyzed` | yes | true/false |
| `Package.licenseConcluded` | yes | License conclusion or `NOASSERTION` |
| `Package.licenseDeclared` | yes | Declared license or `NOASSERTION` |
| `Package.copyrightText` | yes | Copyright text or `NOASSERTION` |
| `Relationship` | recommended | DEPENDS_ON / CONTAINS / DESCRIBES |

## PURL — the cross-tool identifier

Package URL (PURL) is the standard scheme that lets downstream tools (vuln scanners, license tools) match components across ecosystems. Examples:

- `pkg:pypi/requests@2.32.0`
- `pkg:npm/express@4.21.0`
- `pkg:golang/github.com/gin-gonic/gin@v1.9.1`
- `pkg:maven/org.apache.commons/commons-lang3@3.14.0`
- `pkg:cargo/serde@1.0.193`
- `pkg:gem/rails@7.1.2`
- `pkg:nuget/Newtonsoft.Json@13.0.3`
- `pkg:apk/alpine/openssl@3.1.4-r1?distro=alpine-3.19`
- `pkg:deb/debian/libc6@2.36-9?distro=debian-12`

A component WITHOUT a PURL (or equivalent CPE) is hard to match against vulnerability databases. The skill flags components with no `purl` and no `cpe`.

## License values

- `NOASSERTION` — supplier did not assert a license. NOT the same as "no license". Flag and follow up.
- `NONE` — supplier explicitly asserted no license. All-rights-reserved by default; compliance red flag for redistribution.
- Otherwise SPDX-license-identifier (`MIT`, `Apache-2.0`, `BSD-3-Clause`, etc.).

A component declared with NOASSERTION or NONE should NOT be silently distributed; surface it in the summary table.
