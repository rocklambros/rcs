# Cosign verify recipes

Each recipe assumes the trust-policy variables `SUBJECT_REGEXP` and `OIDC_ISSUER` are exported in the operator's shell. Substitute or template before running.

## OCI containers (most common)

### Signature only (Build L2 minimum)

```bash
cosign verify \
  --certificate-identity-regexp "$SUBJECT_REGEXP" \
  --certificate-oidc-issuer "$OIDC_ISSUER" \
  "ghcr.io/example/repo@sha256:DIGEST"
```

### Signature + SLSA provenance attestation (Build L2/L3 typical)

```bash
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp "$SUBJECT_REGEXP" \
  --certificate-oidc-issuer "$OIDC_ISSUER" \
  "ghcr.io/example/repo@sha256:DIGEST" \
  | jq -r '.payload' | base64 -d | jq '.subject, .predicate'
```

The `jq` decode is the part operators forget. The DSSE envelope wraps the predicate in base64; without decoding, you cannot inspect the `subject.digest` for digest-mismatch detection (Check 3 failure mode).

### Offline verify against a cached bundle

```bash
cosign verify \
  --offline \
  --bundle ./artifact.bundle \
  --certificate-identity-regexp "$SUBJECT_REGEXP" \
  --certificate-oidc-issuer "$OIDC_ISSUER" \
  "ghcr.io/example/repo@sha256:DIGEST"
```

Bundle generation happens at sign time and ships alongside the artifact. Required for air-gapped verification.

## Python wheels (PEP 740 attestations)

```bash
# Inspect the attestation alongside the .whl
python -m pip download --no-deps "package==VERSION" -d ./dl
cosign verify-blob-attestation \
  --type "https://docs.pypi.org/attestations/publish/v1" \
  --certificate-identity-regexp "$SUBJECT_REGEXP" \
  --certificate-oidc-issuer "$OIDC_ISSUER" \
  --signature ./dl/package-VERSION-*.whl.publish.attestation \
  ./dl/package-VERSION-*.whl
```

PyPI's PEP 740 attestations are Sigstore-native as of 2024. `cosign verify-blob-attestation` is the right verb (not `verify` — wheels are blobs, not OCI).

## npm packages (npm provenance, public registry)

```bash
npm audit signatures --json
```

For per-package detail:

```bash
npm view PACKAGE@VERSION --json | jq '.dist.attestations'
```

The npm provenance attestations are SLSA L3 when built by a supported CI provider (GitHub Actions, GitLab CI). `npm audit signatures` is the operator-facing verification command; cosign is not the primary interface here, though the underlying attestations are Sigstore.

## Generic blob

```bash
cosign verify-blob \
  --certificate-identity-regexp "$SUBJECT_REGEXP" \
  --certificate-oidc-issuer "$OIDC_ISSUER" \
  --signature ./artifact.sig \
  --certificate ./artifact.pem \
  ./artifact
```

With a bundle:

```bash
cosign verify-blob \
  --bundle ./artifact.bundle \
  --certificate-identity-regexp "$SUBJECT_REGEXP" \
  --certificate-oidc-issuer "$OIDC_ISSUER" \
  ./artifact
```

## Common mistakes

- **Tag instead of digest**: `cosign verify ghcr.io/example/repo:latest` is meaningless — verify the digest.
- **Missing `--certificate-identity-regexp`**: cosign defaults to no identity check; a passing verify with no identity check tells you only that the signature is valid for *some* identity, not the expected one.
- **Wrong predicate type**: a `--type slsaprovenance` flag verifies SLSA provenance only. If the operator wants to verify an SBOM attestation, `--type cyclonedx` or `--type spdx` instead.
- **Forgetting to decode the DSSE envelope**: `cosign verify-attestation` prints the wrapped envelope; the `subject.digest` inside the decoded predicate is where digest-mismatch attacks hide.
