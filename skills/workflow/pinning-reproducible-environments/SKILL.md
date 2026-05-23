---
name: pinning-reproducible-environments
description: >
  Pins a project's environment for reproducibility across Python (uv.lock /
  poetry.lock / requirements.lock), Node (package-lock.json / pnpm-lock.yaml),
  R (renv.lock), and system-level (Devcontainer / Dockerfile with base-image
  digest pinning). Walks the per-ecosystem pin pattern, requires committing the
  lockfile, requires pinning the language runtime version, and recommends a
  weekly CI drift check that re-locks and diffs. Use when starting a new
  project, when a "works on my machine but not in CI" symptom appears, when
  onboarding a teammate, or when reproducibility is required for a paper,
  regulatory submission, or audit trail.
version: 0.1.0
status: shipped
track: workflow
audience: [data-scientist, ml-engineer, security-eng, devops]
evidence:
  - RCS
  - jetson-runbook
  - claude-secure-coding-rules
last-updated: 2026-05-23
---

# Pinning Reproducible Environments

## When to use

Trigger this skill when the user asks for or implies one of:

- Starting a new Python / Node / R project and asking about dependency management
- A "works on my machine but not in CI" or "same Dockerfile, different results" symptom
- Onboarding a teammate and worrying about environment drift
- Reproducibility requirements for a paper, regulatory submission, or compliance audit
- Phrases like "pin my deps", "lock my environment", "why does CI break when local works?", "what version of X are we on?"
- The harness QC.1 / NIST SP 800-218 pinned-dependencies discipline

## When NOT to use

Skip the full pinning machinery when:

- A throwaway exploratory notebook on the user's laptop with no plan to ship or share results — friction outweighs benefit
- Hot-reload library development where the user *intentionally* floats deps to test downstream consumers against the local source
- The repo is already pinned with current best practices and the user only wants a one-off bump → use `auditing-pinned-dependencies` instead

## Quick start

User says: "I'm starting a new Python ML project. How do I set up reproducible deps?"

Skill response: specifies `uv init` (or `poetry init`), `uv lock` (or `poetry lock`) producing a committed lockfile, a `.python-version` file pinning the runtime, and a weekly CI drift check. Names the base-image digest pinning pattern if Docker is in play.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| ecosystem | "python" \| "node" \| "r" \| "docker" \| "multi" | yes | — | Which ecosystem to pin. "multi" walks every ecosystem present in the project. |
| project_root | path | no | cwd | Project root; the skill reads/writes the lockfile and runtime-version files here. |
| ci_drift_check | bool | no | true | Whether to add a weekly CI job that re-locks and diffs. |
| pin_runtime_version | bool | no | true | Whether to pin the language runtime (Python `.python-version`, Node `.nvmrc`, R `renv` Python config). |
| pin_base_image_digest | bool | no | true | Whether to require `FROM image@sha256:...` (Docker only). |

## Workflow

Copy this checklist into the response and check off items as the pinning progresses:

```
Pin progress:
- [ ] Step 1: Identify every ecosystem present (Python, Node, R, Docker, system)
- [ ] Step 2: Per ecosystem — install with the lock-producing command
- [ ] Step 3: Commit the lockfile (uv.lock, poetry.lock, package-lock.json, pnpm-lock.yaml, renv.lock)
- [ ] Step 4: Pin the language runtime (.python-version, .nvmrc, renv Python config)
- [ ] Step 5: Pin base-image digest (FROM image@sha256:...) — Docker only
- [ ] Step 6: Switch CI to lockfile-strict install (npm ci, uv sync --frozen, pip install --require-hashes)
- [ ] Step 7: Add a weekly CI drift-check job that re-locks and opens a PR on diff
```

### Step 2 detail — per-ecosystem install commands

| Ecosystem | Tool | Install command (produces lock) | Strict-install command (for CI) |
|---|---|---|---|
| Python (modern) | uv | `uv add <pkg>` → updates `uv.lock` | `uv sync --frozen` |
| Python (poetry) | poetry | `poetry add <pkg>` → updates `poetry.lock` | `poetry install --no-update` |
| Python (pip + pip-tools) | pip-compile | `pip-compile --generate-hashes` → `requirements.txt` (with hashes) | `pip install --require-hashes -r requirements.txt` |
| Node | npm | `npm install <pkg>` → updates `package-lock.json` | `npm ci` |
| Node | pnpm | `pnpm add <pkg>` → updates `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` |
| R | renv | `renv::install("<pkg>")` → updates `renv.lock` | `renv::restore()` |

### Step 4 detail — runtime-version pinning

- **Python:** `.python-version` file containing the exact version (e.g. `3.13.0`) at the repo root, AND `requires-python = "==3.13.*"` in `pyproject.toml`
- **Node:** `.nvmrc` containing the major-minor (e.g. `20.10.0`), AND `"engines": {"node": "20.10.0"}` in `package.json`
- **R:** `renv` records the R version in `renv.lock`; ensure the `R_VERSION` matches the user's CI runtime image

### Step 5 detail — Docker base-image digest pinning

```dockerfile
# ❌ Floating tag — same Dockerfile, different image content next week
FROM python:3.13-slim

# ✅ Digest-pinned — bit-identical image guaranteed
FROM python:3.13-slim@sha256:abcdef0123456789...
```

The harness QC.4b / base-image-drift incident: same Dockerfile yields different model outputs when the `python:3.13-slim` tag is re-tagged at the registry. The digest is the only pin that holds.

### Step 7 detail — CI drift check

A weekly GitHub Actions job (or equivalent) that:

1. Checks out main
2. Runs `uv lock --upgrade` (or `npm update`, `renv::update()`, etc.) in a scratch directory
3. Diffs the new lockfile against the committed one
4. If different, opens a PR with the diff and a summary of what changed

This keeps the lockfile from rotting silently while preserving review of every upgrade.

## Outputs

The skill produces:

1. A list of files created or modified — lockfile, runtime-version file, `pyproject.toml` / `package.json` edits, `Dockerfile` digest line, CI workflow
2. The exact pinned install command for each ecosystem
3. The CI workflow YAML for the weekly drift check
4. A one-line per-ecosystem verification command (`uv lock --check`, `npm ci --dry-run`, `renv::status()`)

## Failure modes

- **Floating-tag base image** — `FROM python:3.13-slim` resolves to whichever image the registry happens to serve at pull time. Caught by: Step 5 (`@sha256:...` digest).
- **Lockfile-not-committed** — developer runs `uv lock` locally but `.gitignore`s the lock file. CI installs fresh and drifts. Caught by: Step 3 (explicit commit requirement) plus Step 6 (`--frozen` / `npm ci` refuses to run without a committed lockfile).
- **Runtime-version drift** — `pyproject.toml` allows `>=3.10`, local has 3.13, CI image has 3.11. Caught by: Step 4 (exact-pin in `.python-version` and `requires-python`).
- **Silent lockfile rot** — lockfile committed but never updated; deps go a year stale with un-patched CVEs. Caught by: Step 7 (weekly drift-check PR).
- **`pip install` without lockfile** — `pip install -r requirements.txt` against an unpinned `requirements.txt`. Caught by: Step 2 (use `pip-compile --generate-hashes` then `pip install --require-hashes`).

## References

- `reference/per-ecosystem-pin-commands.md` — exact commands per ecosystem, copy-pasteable
- `reference/ci-drift-check.yml` — example GitHub Actions workflow for the weekly drift check
- [NIST SP 800-218](https://csrc.nist.gov/publications/detail/sp/800-218/final) — Secure Software Development Framework (pinned-dependencies discipline)
- [reproducible-builds.org](https://reproducible-builds.org/) — broader reproducible-build context

## Examples

### Example 1: New Python ML project (happy-path)

Input: "I'm starting a new Python ML project. How do I set up reproducible deps?"

Output: Skill recommends `uv init`, `uv add <deps>` to populate `uv.lock`, commits `uv.lock` and `pyproject.toml`, adds a `.python-version` file pinning `3.13.0`, sets `requires-python = "==3.13.*"` in `pyproject.toml`, switches CI to `uv sync --frozen`, and adds the weekly drift-check workflow. Names the harness QC.1 / NIST SP 800-218 mapping.

### Example 2: Same Dockerfile, different outputs (edge-case)

Input: "My teammate's Docker container has the same Dockerfile as mine but the model produces different outputs. We checked deps, they look the same. What's going on?"

Output: Skill identifies base-image drift — `FROM python:3.13-slim` is a floating tag that can be re-tagged at the registry without warning, so the same Dockerfile pulls different image content across builds. Recommends pinning to `FROM python:3.13-slim@sha256:<digest>` and rebuilding both containers from the digest-pinned line. Cites the harness QC.4b base-image-drift pattern.

### Example 3: Throwaway notebook (anti-trigger)

Input: "I'm just experimenting in a Jupyter notebook on my laptop for an afternoon. Should I set up uv lock and all that?"

Output: Skill explicitly says no — for a throwaway exploratory notebook with no plan to ship or share, the pinning machinery is overhead. Suggests using a system Python or a quick virtualenv with no lockfile. Notes that if the experiment turns into a real project the user should revisit and run this skill then.

## See also

- `security/auditing-pinned-dependencies` — audits an *existing* repo's install commands for unpinned patterns; this skill *sets up* pinning from scratch
- `workflow/auditing-data-quality` — pair with this skill at project bootstrap to also pin the data side of reproducibility
- `claude-code-meta/auditing-claude-md-hierarchy` — analogous discipline for the Claude Code session's prefix (planned)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored from Rock's harness QC.1 / NIST SP 800-218 discipline; cross-referenced with `claude-secure-coding-rules` and `jetson-runbook` base-image patterns
