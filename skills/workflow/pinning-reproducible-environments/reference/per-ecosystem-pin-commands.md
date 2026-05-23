# Per-ecosystem pin commands — copy-pasteable

Each ecosystem has its own canonical lockfile, its own install command for development, and its own strict-install command for CI. Read the row for your ecosystem and copy the commands as written.

## Python — uv (recommended for new projects)

```bash
# One-time setup
uv init                                     # creates pyproject.toml
echo "3.13.0" > .python-version             # pin runtime
# In pyproject.toml: requires-python = "==3.13.*"

# Add a dependency
uv add pandas numpy scikit-learn            # updates uv.lock

# Install from lockfile (dev)
uv sync

# Install from lockfile (CI — fails if lockfile is stale)
uv sync --frozen

# Files to commit
# - pyproject.toml
# - uv.lock
# - .python-version
```

## Python — poetry

```bash
# One-time setup
poetry init
echo "3.13.0" > .python-version

# Add a dependency
poetry add pandas numpy scikit-learn        # updates poetry.lock

# Install from lockfile (CI — refuses on lockfile drift)
poetry install --no-update

# Files to commit
# - pyproject.toml
# - poetry.lock
# - .python-version
```

## Python — pip + pip-tools (legacy)

```bash
# requirements.in lists top-level deps; requirements.txt is the lock
pip-compile --generate-hashes requirements.in -o requirements.txt

# Install with hash verification
pip install --require-hashes -r requirements.txt

# Files to commit
# - requirements.in
# - requirements.txt (with hashes)
```

## Node — npm

```bash
# Add a dependency
npm install express                          # updates package-lock.json

# Install from lockfile (CI — refuses if lock is out-of-date)
npm ci

# Files to commit
# - package.json
# - package-lock.json
# - .nvmrc (containing the Node version, e.g. "20.10.0")
```

## Node — pnpm

```bash
# Add a dependency
pnpm add express                             # updates pnpm-lock.yaml

# Install from lockfile (CI)
pnpm install --frozen-lockfile

# Files to commit
# - package.json
# - pnpm-lock.yaml
# - .nvmrc
```

## R — renv

```r
# One-time setup (inside R)
renv::init()                                  # creates renv.lock

# Add a dependency
renv::install("data.table")
renv::snapshot()                              # updates renv.lock

# Restore from lockfile (CI)
renv::restore()
```

```bash
# Files to commit
# - renv.lock
# - renv/activate.R
# - .Rprofile (auto-created by renv::init)
```

## Docker — base-image digest pinning

```dockerfile
# ❌ Floating — same Dockerfile yields different image content over time
FROM python:3.13-slim

# ✅ Digest-pinned — bit-identical image
FROM python:3.13-slim@sha256:abcd1234ef567890abcd1234ef567890abcd1234ef567890abcd1234ef567890

# To get the current digest for a tag
docker pull python:3.13-slim
docker inspect --format='{{index .RepoDigests 0}}' python:3.13-slim
```

When the upstream image is re-tagged, your digest-pinned `FROM` keeps building against the original image. To pick up upstream changes intentionally, run the `docker inspect` command again and update the digest in a PR.

## Devcontainer (`.devcontainer/devcontainer.json`)

```json
{
  "name": "rcs-dev",
  "image": "mcr.microsoft.com/devcontainers/python:1-3.13-bookworm@sha256:abcd...",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20.10.0"
    }
  },
  "postCreateCommand": "uv sync --frozen"
}
```

Pin the `image` to a digest just like a Dockerfile `FROM`. Pin every `features` entry's `version` field to an exact version, not `latest`.

## Verification — one-line per ecosystem

| Ecosystem | Verify lockfile is current and applied |
|---|---|
| uv | `uv lock --check` (exit 0 if lock is current) |
| poetry | `poetry check --lock` |
| pip-tools | `pip-compile --dry-run` and diff |
| npm | `npm ci --dry-run` |
| pnpm | `pnpm install --frozen-lockfile --dry-run` |
| renv | `renv::status()` |
| Docker | `docker pull <image>@sha256:<digest>` (succeeds if digest still exists) |
