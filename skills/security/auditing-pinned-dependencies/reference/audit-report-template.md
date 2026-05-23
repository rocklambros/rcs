# Audit report template

Use this template for the per-file findings output of the dep-pinning audit.

## Header

```markdown
# Dep-Pinning Audit Report

| Field | Value |
|---|---|
| Repo | `<org>/<repo>` |
| Commit SHA | `<40-char-sha>` |
| Audit date | YYYY-MM-DD |
| Auditor | <name or skill version> |
| Scan files | <count> |
| Findings | <H high> / <M medium> / <L low> / <I informational> |
| Final verdict | pass \| pass-with-warnings \| fail |
```

## Per-file findings table

```markdown
| File | Line | Current | Suggested | Severity | Remediation |
|------|------|---------|-----------|----------|-------------|
| Dockerfile | 12 | `RUN npm install express` | `RUN npm install express@4.21.0` | High | Pin exact or switch to `npm ci` against `package-lock.json` |
| Dockerfile | 3 | `FROM python:3.13-slim` | `FROM python:3.13.1-slim@sha256:abc123…` | Medium | Pin base-image digest; tags can move |
| .github/workflows/ci.yml | 18 | `uses: actions/checkout@v4` | `uses: actions/checkout@<40-char-sha>` | Medium | SHA-pin actions or rely on Dependabot to bump |
| requirements.txt | 5 | `requests>=2.30` | `requests==2.32.0` | High | Pin exact; ranges allow silent bumps |
| README.md | 42 | `curl https://example.com/install.sh \| sh` | Save to disk, review, then run | High | Remote-execute pattern; supply-chain risk |
```

## Counts summary

```markdown
## Summary

- **High** (blocking): N
- **Medium** (recommended fix): N
- **Low**: N
- **Informational**: N

**Final verdict: <pass | pass-with-warnings | fail>**

Any high-severity finding produces `fail`. Medium-only findings produce `pass-with-warnings`.
```

## Recommended next steps

```markdown
## Next steps

1. Pin the high-severity findings (see table). Run:
   - `npm install <pkg>@<version> --save-exact` for each unpinned npm dep
   - `pip-compile --generate-hashes` to produce a hash-pinned `requirements.lock`
2. Switch CI from `npm install` to `npm ci` and from `pip install` to `pip install --require-hashes -r requirements.lock`.
3. Pin base-image digests in the Dockerfile:
   ```bash
   docker pull python:3.13-slim
   docker inspect --format='{{index .RepoDigests 0}}' python:3.13-slim
   ```
4. SHA-pin GitHub Actions and enable Dependabot to bump them on a schedule.
5. Re-run this audit on the next dependency-bump PR to verify pinning held.
```

## Optional: timeline section

For repos with multiple findings, group by ecosystem and order by remediation cost:

```markdown
## Remediation timeline (suggested)

| Week | Tasks |
|---|---|
| Week 1 | Pin all high-severity findings in Dockerfile + CI |
| Week 2 | Generate lockfiles and switch CI to `npm ci` / `--require-hashes` |
| Week 3 | SHA-pin GitHub Actions; enable Dependabot |
| Week 4 | Digest-pin Docker base images; document the digest-bump process |
```
