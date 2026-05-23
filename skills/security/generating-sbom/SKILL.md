---
name: generating-sbom
description: >
  Generates a Software Bill of Materials (SBOM) in CycloneDX or SPDX format from
  any stack — Python, Node, Go, Java, Rust, Ruby, polyglot monorepos, container
  images. Selects the right per-ecosystem tool (syft / cyclonedx-bom / cdxgen /
  spdx-sbom-generator), invokes it, and normalizes the output. Captures direct +
  transitive dependencies with version, license, supplier, and PURL. Use when the
  user needs an SBOM for a release, a compliance ask (Executive Order 14028, EU
  CRA, FedRAMP), a vendor questionnaire, or a vulnerability-scan input. Does NOT
  cover ML-BOM 1.7 / AI-BOM (planned: writing-aibom skill); this skill is software
  components only.
version: 0.1.0
status: shipped
track: security
audience: [security-eng, devops, appsec, skill-author]
evidence:
  - quality-contract-NIST-SP-800-218
  - claude-secure-coding-rules
last-updated: 2026-05-23
---

# Generating a Software Bill of Materials (SBOM)

## When to use

Trigger this skill when the user asks for or implies one of:

- "Generate an SBOM for this repo / image / release"
- A compliance ask requires an SBOM: Executive Order 14028 (US federal), EU Cyber Resilience Act, FedRAMP, ISO 27001, SOC 2 vendor questionnaire
- A downstream consumer (security team, customer, auditor) requested CycloneDX or SPDX output
- The user wants to feed an SBOM into a vulnerability scanner (Grype, Trivy, Dependency-Track)
- A release pipeline needs SBOM attestation as part of provenance (SLSA, in-toto, sigstore)
- Mention of "PURL", "CPE", "supplier of record", "components inventory"

## When NOT to use

Skip this skill and hand off when:

- The user wants an AI-BOM / ML-BOM (CycloneDX 1.7 AI extension) — that is a different artifact covering models, datasets, prompts, and pipelines (planned skill: writing-aibom)
- The user wants to *consume* an existing SBOM for vulnerability scanning (use `security/auditing-transitive-vulnerabilities` — that walks the dependency graph)
- The user wants to *verify* an SBOM's signature / attestation (planned skill: verifying-sigstore-signatures)
- The project has not yet been built / installed (SBOM accuracy depends on a resolved dependency tree; pre-build greenfield = empty SBOM)
- The user wants a hardware BOM or a firmware BOM — those use different standards (SBoM, HBoM, FBoM); this skill is software components

## Quick start

User says: "Generate a CycloneDX SBOM for this Python + JS monorepo. We need it for our customer's compliance request."

Skill response:

1. Confirms the format (CycloneDX 1.5 JSON is the safest default unless customer specifies SPDX)
2. Detects ecosystems present (Python = `pyproject.toml` + `uv.lock`, JS = `package.json` + `pnpm-lock.yaml`)
3. Selects the per-ecosystem tool (syft as universal default, with cyclonedx-bom + cdxgen as fallbacks)
4. Invokes the tool against the install-resolved dependency tree (NOT against a fresh install — that would re-resolve and might drift)
5. Merges per-ecosystem SBOMs into a single document with one `metadata.component` per top-level project
6. Validates the output against the CycloneDX JSON schema
7. Emits the file + a summary table (components count, license distribution, suppliers, top-level vs transitive split)

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| target | repo path, container image ref, or list | yes | — | What to scan. Repo path for source SBOM, image ref (e.g., `ghcr.io/org/app:1.2.3`) for image SBOM. |
| format | "cyclonedx-json" \| "cyclonedx-xml" \| "spdx-json" \| "spdx-tag-value" | no | "cyclonedx-json" | Output format. CycloneDX JSON is most-widely consumed; SPDX is common for legal review. |
| output_path | path | no | `sbom.<ext>` | Where to write the SBOM. |
| ecosystems | list | no | (auto-detect) | Restrict to specific ecosystems: `python`, `npm`, `go`, `maven`, `cargo`, `gem`, `nuget`, `apk`, `deb`, `rpm`. |
| include_dev_deps | bool | no | false | If true, include `devDependencies` / `dev-dependencies` / test-only deps. |
| sign | "cosign" \| "none" | no | "none" | If `cosign`, sign the SBOM with cosign keyless (requires Sigstore OIDC). |

## Workflow

Copy this checklist into the response and check off items as generation progresses:

```
SBOM generation progress:
- [ ] Step 1: Detect ecosystems (lockfiles present, manifest files, container layers)
- [ ] Step 2: Select tool per ecosystem (syft default; per-ecosystem fallbacks)
- [ ] Step 3: Generate per-ecosystem SBOM(s)
- [ ] Step 4: Merge into single document with project-root metadata.component
- [ ] Step 5: Validate against schema (cyclonedx validate or pyspdxtools verify)
- [ ] Step 6: Emit summary table (components, licenses, suppliers, depth)
- [ ] Step 7: (optional) Sign with cosign
```

### Step 1: Ecosystem detection

Walk `target` and detect:

| Marker | Ecosystem |
|---|---|
| `pyproject.toml`, `requirements*.txt`, `Pipfile.lock`, `poetry.lock`, `uv.lock` | python |
| `package.json` + (`package-lock.json` \| `pnpm-lock.yaml` \| `yarn.lock`) | npm |
| `go.mod` + `go.sum` | go |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | maven |
| `Cargo.toml` + `Cargo.lock` | cargo |
| `Gemfile.lock` | gem |
| `*.csproj` + `packages.lock.json` | nuget |
| Container `apk` / `dpkg` / `rpm` databases | apk / deb / rpm |

A polyglot monorepo will trip multiple markers; produce one SBOM per ecosystem and merge.

### Step 2: Tool selection

**Default (recommended): `syft`** — covers every ecosystem above + container images, produces CycloneDX and SPDX natively.

```bash
syft <target> -o cyclonedx-json=<output_path>
syft <image>:<tag> -o spdx-json=<output_path>
```

**Per-ecosystem fallbacks** (use when syft produces incomplete or low-fidelity output):

| Ecosystem | Tool | Invocation |
|---|---|---|
| python | `cyclonedx-bom` | `cyclonedx-py environment -o sbom.json` |
| npm | `@cyclonedx/cdxgen` | `cdxgen -t npm -o sbom.json` |
| go | `cyclonedx-gomod` | `cyclonedx-gomod app -json -output sbom.json` |
| maven | `cyclonedx-maven-plugin` | `mvn cyclonedx:makeAggregateBom` |
| cargo | `cargo-cyclonedx` | `cargo cyclonedx --format json` |

### Step 3: Generate

For source SBOM, generate against the *resolved* dependency tree. Do NOT run `npm install` / `pip install` fresh — that re-resolves and may drift from what is actually committed in the lockfile. Use existing lockfiles as the source of truth.

For image SBOM, scan the image layers directly with `syft <image-ref>`.

### Step 4: Merge

If multiple per-ecosystem SBOMs exist, merge them with `cyclonedx merge`:

```bash
cyclonedx merge --input-files py-sbom.json js-sbom.json --output-file merged-sbom.json
```

Set the top-level `metadata.component` to the project root with `type: application` and a PURL like `pkg:generic/<project-name>@<version>`.

### Step 5: Validate

```bash
cyclonedx validate --input-file sbom.json --fail-on-errors
```

For SPDX:

```bash
pyspdxtools -i sbom.spdx.json
```

A valid SBOM is a hard requirement for downstream consumers; an invalid SBOM is worse than no SBOM (downstream tools may produce silently wrong results).

### Step 6: Summary table

Emit a counts summary alongside the file:

| Metric | Value |
|---|---|
| Total components | N |
| Direct dependencies | N |
| Transitive dependencies | N |
| Distinct licenses | N (with license-name distribution: MIT N, Apache-2.0 N, ...) |
| Components with NO license | N (compliance red flag) |
| Components with unknown supplier | N |

### Step 7: Sign (optional)

```bash
cosign sign-blob --yes sbom.json --output-signature sbom.json.sig --output-certificate sbom.json.crt
```

Cosign keyless uses Sigstore OIDC (GitHub / Google / Microsoft); no long-lived keys to manage. The signature + certificate land alongside the SBOM in the release artifact.

## Outputs

1. **SBOM file** at `output_path` in the requested format
2. **Summary table** — components / licenses / suppliers / depth metrics
3. **Validation result** — schema-validation pass / fail
4. **Signature + certificate** (if `sign: cosign`)
5. **Recommended downstream steps** — feed into Grype / Trivy / Dependency-Track for vulnerability scan (cross-reference `security/auditing-transitive-vulnerabilities`)

## Failure modes

- **Pre-build SBOM** — generating an SBOM before `npm install` / `pip install` has resolved a lockfile produces an SBOM of declared (not resolved) deps, missing transitive entries. Caught by: Step 3 requires lockfile presence; warns if no lockfile detected.
- **Polyglot under-coverage** — running `cyclonedx-py` on a Python + JS monorepo captures only Python and silently misses the JS half. Caught by: Step 1 detects ALL ecosystems and Step 2 requires one tool per ecosystem (or syft for full coverage).
- **License-missing silence** — components with no declared license are common in private / internal packages. Emitting an SBOM without flagging this hides a real compliance risk. Caught by: Step 6 summary explicitly counts "no-license" components.
- **Invalid schema** — many SBOMs in the wild fail validation (missing `bomFormat`, wrong `specVersion`, missing required `metadata`). Caught by: Step 5 schema validation is mandatory; the skill refuses to declare success on an invalid SBOM.
- **Drift between lockfile and SBOM** — generating SBOM after `npm install` re-resolves and may pull newer versions than the committed lockfile. Caught by: Step 3 reads from the lockfile, never re-resolves.
- **Conflating SBOM with AI-BOM** — for ML projects, the user often wants the AI-BOM (models, datasets, prompts) as well. Caught by: "When NOT to use" hands off to writing-aibom (planned); this skill is software components only.

## References

- `reference/tool-selection-matrix.md` — per-ecosystem tool selection plus fallback rules
- `reference/sbom-fields.md` — minimum required CycloneDX + SPDX fields for a complete SBOM
- [CycloneDX 1.5 specification](https://cyclonedx.org/docs/1.5/json/)
- [SPDX 2.3 specification](https://spdx.github.io/spdx-spec/v2.3/)
- [NTIA Minimum Elements for an SBOM](https://www.ntia.gov/files/ntia/publications/sbom_minimum_elements_report.pdf)
- [Executive Order 14028 SBOM guidance](https://www.cisa.gov/sbom)

## Examples

### Example 1: Mixed Python + JS monorepo (happy-path)

Input: "Generate a CycloneDX SBOM for this repo. It has a Python backend (`pyproject.toml` + `uv.lock`) and a JS frontend (`frontend/package.json` + `frontend/pnpm-lock.yaml`). We need it for our customer's compliance request."

Output: Skill detects two ecosystems (python, npm). Uses `syft` for full coverage. Generates `sbom.cdx.json` with 312 components (47 Python direct, 142 Python transitive, 18 JS direct, 105 JS transitive). Validates against CycloneDX 1.5 schema (pass). Emits summary: 312 components, 14 distinct licenses (MIT 198, Apache-2.0 64, BSD-3-Clause 28, ISC 12, unknown 10), 10 components with no license declared. Recommends following up on the 10 no-license components and feeding the SBOM into `security/auditing-transitive-vulnerabilities` for vuln-scan.

### Example 2: Container image with unknown licenses in transitive deps (edge-case)

Input: "Generate an SBOM for `ghcr.io/our-org/payment-service:v1.4.2`."

Output: Skill runs `syft ghcr.io/our-org/payment-service:v1.4.2 -o cyclonedx-json=sbom.json`. Captures 487 components: 47 from `apk` (Alpine base), 230 from Python `site-packages`, 210 from a vendored JS bundle. Validation passes. Summary flags 67 components with no declared license (mostly inside the vendored JS bundle). Recommends: (a) replace the vendored bundle with a proper `package.json`-managed dependency tree so licenses surface, (b) re-run SBOM generation, (c) feed into Trivy for vulnerability scanning.

### Example 3: Pre-build greenfield project (anti-trigger)

Input: "I just started a new Python project. I have a `pyproject.toml` but I haven't run `uv sync` yet. Generate an SBOM."

Output: Skill does NOT generate an SBOM from the unresolved `pyproject.toml`. Explains that an SBOM requires a resolved dependency tree (lockfile or installed environment). Without resolution, transitive deps are unknown and the SBOM would be misleading. Recommends: (a) run `uv lock` to produce `uv.lock`, (b) re-run this skill. Cross-references `workflow/pinning-reproducible-environments` for the initial lock setup.

## See also

- `security/auditing-transitive-vulnerabilities` — the natural downstream consumer of the SBOM (vuln-scan via Grype / Trivy / Dependency-Track)
- `security/auditing-pinned-dependencies` — verifies the lockfile this skill reads is itself pinned correctly
- `workflow/pinning-reproducible-environments` — establishes the lockfile that this skill depends on
- `security/auditing-mcp-server-pre-trust` — an MCP-specific subset of supply-chain audit

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from RCS spec (v4-batch-1, Σ 12); cross-referenced against NTIA SBOM minimum elements, EO 14028 guidance, and the CycloneDX/SPDX specs
