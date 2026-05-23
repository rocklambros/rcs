# Tool selection matrix

Per-ecosystem SBOM generators. The default for any stack is **syft** (one tool covers everything). The per-ecosystem entries below are the higher-fidelity fallbacks when syft output is incomplete.

## Universal default

| Tool | Coverage | Output formats | Notes |
|---|---|---|---|
| `syft` (anchore) | Python, npm, Go, Maven, Cargo, Gem, NuGet, apk, deb, rpm, container images | CycloneDX (JSON / XML), SPDX (JSON / tag-value), Syft-native | The pragmatic default. Some ecosystems have higher-fidelity dedicated tools, but syft's coverage of polyglot monorepos and container images is best-in-class. |

```bash
# repo SBOM
syft <repo-path> -o cyclonedx-json=sbom.cdx.json

# image SBOM
syft <image-ref> -o cyclonedx-json=sbom.cdx.json

# SPDX output
syft <target> -o spdx-json=sbom.spdx.json
```

## Per-ecosystem fallbacks

### Python

| Tool | Invocation | Coverage |
|---|---|---|
| `cyclonedx-bom` | `cyclonedx-py environment -o sbom.json` | Captures installed environment |
| `cyclonedx-bom` (poetry mode) | `cyclonedx-py poetry -o sbom.json` | Reads `poetry.lock` directly |
| `cyclonedx-bom` (requirements mode) | `cyclonedx-py requirements -i requirements.txt -o sbom.json` | Reads `requirements.txt` (pinned only) |
| `pip-audit --format cyclonedx-json` | `pip-audit -f cyclonedx-json -o sbom.json` | Includes vuln data inline |

### JavaScript / Node

| Tool | Invocation | Coverage |
|---|---|---|
| `@cyclonedx/cdxgen` | `cdxgen -t npm -o sbom.json` | Reads `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` |
| `@cyclonedx/bom` (older) | `cyclonedx-bom -o sbom.json` | Direct deps from `package.json` |

### Go

| Tool | Invocation | Coverage |
|---|---|---|
| `cyclonedx-gomod` | `cyclonedx-gomod app -json -output sbom.json` | Reads `go.mod` + `go.sum` |
| `cyclonedx-gomod mod` | `cyclonedx-gomod mod -json -output sbom.json` | Module-mode (library) |

### Java / Maven

| Tool | Invocation | Coverage |
|---|---|---|
| `cyclonedx-maven-plugin` | `mvn org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom` | Multi-module aggregate |
| `cyclonedx-gradle-plugin` | `gradle cyclonedxBom` | Gradle projects |

### Rust / Cargo

| Tool | Invocation | Coverage |
|---|---|---|
| `cargo-cyclonedx` | `cargo cyclonedx --format json` | Reads `Cargo.lock` |

### Ruby

| Tool | Invocation | Coverage |
|---|---|---|
| `cyclonedx-ruby` | `cyclonedx-ruby --path Gemfile.lock --output sbom.json` | Reads `Gemfile.lock` |

### Container images

`syft` covers this best. For dedicated workflows, `tern` and `trivy` also produce SBOMs:

```bash
trivy image --format cyclonedx --output sbom.json <image-ref>
```

## SBOM merging

For polyglot monorepos, generate per-ecosystem SBOMs and merge:

```bash
cyclonedx merge --input-files py-sbom.json js-sbom.json --output-file merged-sbom.json
```

Set the merged SBOM's `metadata.component` to the project root with type `application` and a PURL like `pkg:generic/<project-name>@<version>`.

## Selection algorithm

1. If the target is a container image -> `syft`.
2. If the target is a polyglot repo (multiple ecosystems) -> `syft` first; supplement with per-ecosystem tools only if syft misses something.
3. If the target is a single-ecosystem repo and the user wants highest fidelity -> use the per-ecosystem tool from the table above.
4. If the output format is SPDX -> any of the above can produce SPDX; `syft -o spdx-json` is the simplest.
