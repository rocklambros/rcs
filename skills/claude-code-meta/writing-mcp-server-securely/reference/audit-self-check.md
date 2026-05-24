# Pre-publish self-audit checklist

Run this against your own MCP repo BEFORE publishing. Mirrors the consumer's `auditing-mcp-server-pre-trust` six-check audit.

## Check 1 — License

- [ ] `LICENSE` file exists at repo root
- [ ] License is an SPDX identifier (MIT, Apache-2.0, BSD-3-Clause, etc.)
- [ ] License declared in package metadata (`pyproject.toml [project].license`, `package.json "license"`) — matches the LICENSE file content

**Fail if any item is missing.**

## Check 2 — Source review

- [ ] No `eval()`, `exec()`, `Function()`, `new Function()` in any source file
- [ ] No dynamic `import()` with user-controlled strings
- [ ] No base64-encoded blobs that get decoded at runtime
- [ ] No obfuscation; published source is human-readable
- [ ] No `subprocess.run(..., shell=True)` with unescaped user input
- [ ] Source files are linted clean by your language's standard linter

**Fail if any check finds a hit.**

## Check 3 — Network egress

- [ ] README has a "Network egress" section listing every outbound endpoint
- [ ] Every endpoint has: target URL, auth method, why the call exists
- [ ] Every endpoint is overridable via env var (consumer can point at proxy or restrict)
- [ ] No telemetry endpoint that fires by default (must be opt-in)
- [ ] Source grep for `http://`, `https://`, `requests.`, `httpx.`, `fetch(` matches the documented set

**Fail if README and source don't match.**

## Check 4 — Version pin

- [ ] Lockfile committed (`uv.lock`, `package-lock.json`, `Cargo.lock`, `go.sum`)
- [ ] Release tagged with SemVer (e.g., `v0.1.0`)
- [ ] README install command pins to a specific version or SHA
- [ ] No `@latest`, `@main`, `@master`, `*` in any dependency spec or install command
- [ ] CI workflow uses `npm ci` (not `npm install`), `uv sync --frozen` (not `uv sync`), `pip install --require-hashes`

**Fail if any unpinned form is found.**

## Check 5 — Secret handling

- [ ] All secrets loaded from env vars; no config files committed with secrets
- [ ] Source grep for the secret name shows: read once, never logged, never printed, never in `repr()` / `__repr__`
- [ ] Test asserting that secret does not appear in tool results or error messages
- [ ] OAuth flows (if any) use least-privilege scopes
- [ ] Callback URL (if OAuth) is localhost or a verified domain

**Fail if a secret appears in any log, error, or result.**

## Check 6 — Tool subset

- [ ] `tools/list` returns a fixed, build-time-known list
- [ ] Every tool has a JSON Schema input contract with explicit `type` / `properties` / `required`
- [ ] No tool dispatches on an opcode argument
- [ ] No tool runs `eval` / `exec` on a string argument
- [ ] Read-only and write tools are separated so consumers can enable read-only subset

**Fail if a tool can do more than its description claims.**

## Final pre-publish gate

If ALL six checks pass:

1. Tag the release with the SemVer version
2. Update CHANGELOG.md
3. Publish to PyPI / npm / GitHub release
4. Update marketplace.json entry (if applicable)

If ANY check fails:

- Fix before publishing
- Do not publish "for now"; consumers may install the broken version before the fix lands

## On version bumps

Re-run this checklist on every release, even PATCH bumps. Upstream dependency updates can silently change egress behavior, secret handling, or license terms. The republish itself does not earn trust — the re-audit does.
