# Unpinned install patterns — blocking, warning, and acceptable forms

Reference catalog for the audit. Match patterns against the file content; produce findings per match.

## Blocking patterns (high severity)

| Ecosystem | Pattern | Why blocking | Suggested fix |
|---|---|---|---|
| npm | `npx -y <pkg>` (no `@<version>`) | Runs latest published version; supply-chain attack vector | `npx -y <pkg>@<version>` |
| npm | `npm install <pkg>` (no `@<version>`) | Installs latest; silent drift | `npm install <pkg>@<version>` or `npm ci` against lockfile |
| npm | `<pkg>@latest` | Explicit unpinning | `<pkg>@<version>` |
| pip | `pip install <pkg>` (no `==`) | Latest release; silent drift | `pip install <pkg>==<version>` or `-r requirements.lock` |
| pip | `pip install <pkg>>=<version>` | Floor without ceiling; can install future incompatible versions | `pip install <pkg>==<version>` |
| uv | `uvx --from git+<url>` without `#<ref>` or `@<sha>` | Resolves to HEAD of default branch; moves silently | `uvx --from git+<url>@<sha>` or `#<tag>` |
| any | `curl <url> \| sh` or `wget <url> \| bash` | Executes remote script without review; vendor compromise = code execution | Save script with `curl -o`, review, then run |
| Docker | `FROM <image>` (no `@sha256:`) | Tag can be re-pointed by registry | `FROM <image>@sha256:<digest>` |
| Docker | `RUN apt-get install -y <pkg>` (no `=<version>`) | Latest distro version | `RUN apt-get install -y <pkg>=<version>` |
| GH Actions | `uses: <action>@<branch>` | Branch ref moves | `uses: <action>@<sha>` |
| GH Actions | `uses: <action>@v1` (major-only) | Mutable major tag | `uses: <action>@v1.2.3` (immutable tag) or `@<sha>` |

## Warning patterns (medium severity)

| Pattern | Why warning | Suggested fix |
|---|---|---|
| `<pkg>^1.2.3` (npm caret) | Allows minor + patch bumps | Pin exact `<pkg>@1.2.3` or use `npm ci` against lockfile |
| `<pkg>~1.2.3` (npm tilde) | Allows patch bumps | Pin exact or use lockfile |
| `<pkg>>=1.2,<2.0` (pip range) | Allows minor bumps within range | Pin exact `<pkg>==1.2.3` |
| `npm install` in CI | Ignores lockfile; reproducibility risk | Switch to `npm ci` |
| `pip install -r requirements.txt` without hashes | No integrity check | `pip install --require-hashes -r requirements.txt` (requires hash-generated requirements file) |

## Acceptable forms (no finding)

| Pattern | Why OK |
|---|---|
| `<pkg>@1.2.3` (npm exact) | Exact version pin |
| `<pkg>==1.2.3` (pip exact) | Exact version pin |
| `git+<url>@<sha>` | Commit-SHA pin |
| `git+<url>#<tag>` | Tag pin (acceptable; SHA stronger) |
| `npm ci` (with `package-lock.json` committed) | Lockfile-enforced install |
| `pip install -r requirements.lock` | Lockfile-enforced |
| `pip install --require-hashes -r requirements.txt` | Hash-enforced |
| `uv sync` (with `uv.lock` committed) | Lockfile-enforced |
| `FROM <image>@sha256:<digest>` | Digest-pinned base image |
| `RUN apt-get install -y <pkg>=<version>` | Version-pinned apt install |
| `uses: <action>@<40-char-sha>` | SHA-pinned action |

## Scaffolder carve-out (not flagged by default)

These are one-shot project scaffolders, not runtime dependencies. Flagging them produces noise.

- `npm create <template>@latest`
- `npm init <template>`
- `pnpm create <template>`
- `yarn create <template>`
- `cargo generate`
- `dotnet new <template>`
- `npx create-react-app`, `npx create-next-app`

Recommend the user pin the RESULTING dependencies (i.e., the `package.json` the scaffolder produces) instead.

To include scaffolders in the audit anyway, set `include_create_scaffolders: true`.

## Per-ecosystem notes

### npm
- Lockfile: `package-lock.json` (npm), `pnpm-lock.yaml` (pnpm), `yarn.lock` (yarn). Commit all.
- CI: use `npm ci` / `pnpm install --frozen-lockfile` / `yarn install --frozen-lockfile`.

### pip
- Lockfile: `pip-compile --generate-hashes -o requirements.lock requirements.in` produces hash-pinned lock.
- Modern alternative: `uv` (`uv lock` → `uv.lock`) or `poetry` (`poetry lock` → `poetry.lock`).
- CI: `pip install --require-hashes -r requirements.lock` for integrity-checked install.

### Docker
- Base image digest: `docker pull <image>:<tag>` then `docker inspect --format='{{index .RepoDigests 0}}' <image>:<tag>` to retrieve the current digest.
- Multi-stage builds: pin every `FROM`, not just the final stage.

### GitHub Actions
- SHA pinning: copy the full 40-char commit SHA from the action's repo. Use Dependabot or Renovate to keep them current.
- Alternative: trust major tags only for first-party `actions/*` (still riskier than SHA).
