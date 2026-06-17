---
name: verifying-sigstore-signatures
description: >
  Verifies a signed artifact (container image, Python wheel, npm tarball, generic blob)
  against Sigstore — cosign signature, optional in-toto attestation, SLSA Build level —
  and emits a per-check verdict (identity, signature, attestation, provenance level)
  with the artifact's effective trust level. Use when an operator is about to pull a
  container into production, when a CI pipeline needs an admission-control gate on
  signed artifacts, when a supply-chain advisory requires re-verifying every artifact
  a service depends on, or when a regulator asks for documented provenance on deployed
  software. Refuses to engage on ecosystems with no Sigstore signatures (the answer is
  "use the ecosystem's native trust model", not "fabricate a cosign verdict") and on
  requests where no trust policy is declared — the verdict requires the policy as input.
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - devops
  - sre
  - compliance-eng
evidence:
  - slsa-framework
  - sigstore-cosign-spec
last-updated: 2026-05-23
---

# Verifying Sigstore Signatures

## When to use

Trigger this skill when the user asks for or implies one of:

- A container image is about to be pulled into production and the operator needs to verify it is signed by the expected publisher
- A CI pipeline needs an admission-control gate on signed artifacts (block deploy if signature or provenance is missing)
- A supply-chain attack notification (CVE, vendor advisory, ecosystem-wide compromise) requires re-verifying every artifact a service depends on
- A regulator, customer, or internal compliance review is asking for provenance evidence on deployed software (FedRAMP, EU CRA, NIST SP 800-218 task PO.3, SLSA conformance attestation)
- Phrases like "verify this image is signed", "cosign verify failed, why?", "what SLSA level is this artifact?", "validate the attestation on this wheel", "sigstore check on our base image"

## When NOT to use

Skip this skill and hand off when:

- The artifact's ecosystem has no signing infrastructure in production use (rare in 2026, but: small private registries, legacy ecosystems). The answer is "publish unsigned, document the risk, accept the residual exposure", not a verdict.
- The signature exists but the operator has no trust policy declaring which subject identities and which OIDC issuers are acceptable. The skill needs the policy as an input — a verdict on "trusted by whom?" is undefined without it. Hand off to `security/writing-deny-allow-rules` or the operator's policy authoring workflow to write the policy first.
- The request is about *creating* signatures (signing during build) rather than verifying them downstream. Use the build-pipeline / signing workflow (cosign sign, attestations generation), not this skill.
- The request is about TLS certificate validation, package signature (apt / yum / brew) outside Sigstore, or PGP/GPG — those are adjacent but distinct trust models. This skill is Sigstore-specific.

## Quick start

User says: "We're about to deploy `ghcr.io/example/api-server@sha256:abc123...` to prod. The image was built by our GitHub Actions workflow at `.github/workflows/build.yml`. Our trust policy says only signers with subject prefix `https://github.com/example/api-server/.github/workflows/` and issuer `https://token.actions.githubusercontent.com` are acceptable, and we require SLSA Build L3 minimum. Verify it."

Skill response: walks the four-check verification (identity, signature, attestation, SLSA level), runs the cosign + in-toto commands inline, reads the Rekor inclusion proof timestamp, parses the SLSA provenance predicate from the in-toto envelope, maps the predicate fields to the SLSA Build level criteria, and emits a per-check verdict with an overall trust verdict (`verified`, `verified-with-warnings`, `failed`).

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| artifact_ref | string | yes | — | The artifact reference. For containers: `registry/repo@sha256:digest` (digest, not tag). For wheels/tarballs: file path or URL. The digest form is required for container verification — tag-only references are inherently spoofable. |
| trust_policy | object | yes | — | Allowed signer subjects (exact or prefix), allowed OIDC issuers, minimum SLSA level. Without this, the verdict is undefined. |
| ecosystem | string | yes | — | One of `oci-container`, `python-wheel`, `npm-package`, `generic-blob`. Determines which cosign sub-command and which attestation format to expect. |
| require_attestation | bool | no | true | Whether a signature alone is sufficient (`false`) or a SLSA provenance attestation is also required (`true`). Production deploys typically require `true`. |
| rekor_url | string | no | "https://rekor.sigstore.dev" | The transparency log URL. Private Sigstore deployments override this. |
| offline_verify | bool | no | false | Verify against a previously cached Rekor inclusion proof without contacting the public log (air-gapped operation). |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as each check completes:

```
Sigstore signature verification (artifact: <ref>):
- [ ] Check 1: Identity — signer subject + OIDC issuer match trust policy
- [ ] Check 2: Signature — cosign verify succeeds; Rekor inclusion proof present and valid
- [ ] Check 3: Attestation — in-toto envelope present (if required); predicate type expected
- [ ] Check 4: Provenance level — SLSA Build level meets policy minimum
- [ ] Overall verdict: verified | verified-with-warnings | failed
```

### Check 1: Identity

- Extract the signer subject (e.g., `https://github.com/example/api-server/.github/workflows/build.yml@refs/heads/main`) and OIDC issuer (e.g., `https://token.actions.githubusercontent.com`) from the certificate.
- Compare against the trust policy's allowed subjects (exact match or prefix) and allowed issuers.
- A signer subject from an unexpected workflow path is a Check 1 failure. A signer subject from a workflow PR branch when the policy only allows main is a Check 1 failure.
- Capture: subject string, issuer string, certificate validity window.

### Check 2: Signature

- Run `cosign verify --certificate-identity-regexp <policy-pattern> --certificate-oidc-issuer <policy-issuer> <artifact_ref>` (or the equivalent for the artifact ecosystem).
- A non-zero exit code is a Check 2 failure. Common causes: digest mismatch, signature does not match the artifact's content, certificate expired or revoked, Rekor entry missing.
- Verify the Rekor inclusion proof is present in the cosign output and timestamps land before the artifact deploy window. A signature created after deploy is a Check 2 failure (suggests a backfilled attack).
- Offline mode: verify against a cached Rekor inclusion proof bundle stored at sign time.

### Check 3: Attestation

- If `require_attestation: true`, run `cosign verify-attestation --type slsaprovenance <artifact_ref>`.
- A missing attestation when required is a Check 3 failure.
- Verify the predicate type is `https://slsa.dev/provenance/v1` (or the version your trust policy accepts). A wrong predicate type means the attestation is not a SLSA provenance attestation — it might be a CycloneDX SBOM attestation or something else — and Check 4 cannot proceed.
- Capture the predicate's `builder.id` (the build platform), `buildType`, and `invocation.configSource` for the SLSA level mapping.

### Check 4: Provenance level (SLSA mapping)

Map the predicate fields to a SLSA Build level. The SLSA spec uses Build L0–L3; L4 was retired in SLSA v1.0 (the historical "L4" criteria now distribute across L3 and a separate Source track). Per SLSA v1.0:

- **Build L0**: no provenance claim. Predicate absent or unverifiable.
- **Build L1**: provenance exists but is not signed or is signed by the producer themselves. Useful for auditability, not for tampering resistance.
- **Build L2**: provenance is signed by a hosted build platform (e.g., GitHub Actions OIDC token, GCP Cloud Build), is generated by the platform (not the user), and references the source.
- **Build L3**: as L2 + the build platform isolates the build environment such that runtime injection of provenance content is infeasible. Examples: GitHub Actions reusable workflows that pin to specific SHA-256, SLSA-conformant GitHub Actions builder, GoReleaser w/ Sigstore.

If `builder.id` is the same identity as the artifact publisher (self-signed by user), it is L1 at best. If `builder.id` is a hosted build platform OIDC identity AND the predicate is signed by that platform's OIDC certificate, L2 is achievable. L3 additionally requires the build platform's documented isolation guarantees.

Compare the achieved level to the trust policy's minimum and emit pass / fail.

### Overall verdict

- **Verified**: all four checks pass; the artifact meets policy.
- **Verified-with-warnings**: Checks 1, 2, and (if required) 3 pass; Check 4 achieves a SLSA level below policy minimum but the operator has documented an exception. Used only with an explicit recorded exception.
- **Failed**: any required check fails. Do not deploy.

## Outputs

A two-part deliverable:

1. **Verdict report (markdown)** — artifact ref, trust policy summary, per-check table (Check · Verdict · Evidence · Notes), overall verdict, and a one-line recommendation (deploy / deploy-with-exception / block).
2. **Reproduction commands** — the exact cosign + (if applicable) in-toto commands the operator can paste to reproduce the verdict. The commands include the policy parameters used so the verdict is auditable.

If the verdict is `failed`, the report also includes the root-cause classification (identity mismatch, signature invalid, attestation missing, provenance level insufficient, Rekor entry missing) and the remediation path (re-build, rotate signing identity, adopt a SLSA-conformant builder, etc.).

## Failure modes

- **Tag-based verification on a container** — verifying `repo:latest` instead of `repo@sha256:digest` is a verification fiction; a registry can serve different content under the same tag after the fact. Caught by: `artifact_ref` accepts only digest form for containers; tag-only inputs are rejected at the input validation step.
- **Self-signed provenance claimed as L2/L3** — the producer signs their own provenance with their own key and claims SLSA L2. Caught by: Check 4 explicitly requires `builder.id` to be a hosted platform OIDC identity, not the same identity as the publisher, to map above L1.
- **Attestation present, provenance broken** — an in-toto envelope is attached but the predicate is for a different artifact (digest mismatch inside the predicate). Caught by: Check 3 verifies the predicate's `subject.digest` matches the verified artifact digest.
- **Trust policy missing from the request** — without a declared trust policy, the verdict has no defined meaning. Caught by: `trust_policy` is a required input; if absent, the skill refuses to issue a verdict and asks for the policy or hands off to the policy-authoring workflow.
- **Old verdict treated as current** — a verdict from last month is not a verdict for today's deploy if Rekor or the upstream signer's certificate has changed. Caught by: every verdict report timestamps the run and recommends re-verification at deploy time, not just at build time.
- **Confusing Sigstore with TLS certificate validation** — operators sometimes assume "the image came from HTTPS, that's signed". TLS validates transport, not artifact provenance. Caught by: the skill's "When NOT to use" section explicitly excludes TLS validation.

## References

- `reference/cosign-verify-recipes.md` — copy-paste cosign verify commands per ecosystem (oci, python, npm, generic blob), with the policy-flag set
- `reference/slsa-level-mapping.md` — the SLSA Build level criteria checklist mapped to predicate fields
- [SLSA v1.0 specification](https://slsa.dev/spec/v1.0/)
- [Sigstore cosign documentation](https://docs.sigstore.dev/cosign/overview)
- [Rekor transparency log](https://docs.sigstore.dev/rekor/overview)
- [in-toto attestation specification](https://github.com/in-toto/attestation)

## Examples

### Example 1: GitHub Actions container with cosign keyless + SLSA L3 attestation (happy-path)

Input: "Verify `ghcr.io/example/api-server@sha256:abc...` for prod deploy. Trust policy: subject prefix `https://github.com/example/api-server/.github/workflows/`, issuer `https://token.actions.githubusercontent.com`, minimum SLSA Build L3."

Output: Skill runs the four checks. Check 1: cert subject matches the policy prefix and is from main (not a PR) ✓. Check 2: `cosign verify --certificate-identity-regexp` returns OK with a Rekor inclusion proof dated 12 hours before deploy ✓. Check 3: `cosign verify-attestation --type slsaprovenance` returns OK; predicate type is `https://slsa.dev/provenance/v1` ✓. Check 4: `builder.id` is the SLSA-conformant GitHub Actions builder reusable workflow, isolation criteria satisfied, mapped to Build L3 ✓. Overall: verified. Reproduction commands included.

### Example 2: Attestation present but provenance digest mismatch (edge-case)

Input: "Verify `ghcr.io/example/svc@sha256:abc...`. Trust policy: any subject under `https://github.com/example/`, minimum L2. Cosign verify passes, but something feels off — attestation is attached."

Output: Skill runs the checks. Check 1 ✓ (subject under example org). Check 2 ✓ (cosign verify OK, Rekor entry present). Check 3 FAIL — the in-toto envelope's `subject.digest` references a different digest than the artifact being verified. The predicate is for a different image; the attestation was attached to the wrong artifact. Overall: failed. Root cause: provenance broken (digest mismatch inside the predicate). Remediation: re-run the build pipeline so the attestation is generated for the actual artifact digest, or investigate whether an attacker swapped the attached envelope.

### Example 3: No Sigstore in the ecosystem (anti-trigger)

Input: "We need to verify the signatures on the deb packages our internal apt repo serves. Walk us through cosign."

Output: Skill returns a redirect, not a verdict. Explains that apt packages use the apt-secure / GPG trust model, not Sigstore — `cosign verify` is the wrong tool. Recommends `apt-key` / `gpg --verify` against the publisher's signing key (or migrating the apt repo to a Sigstore-fronted artifact store if the operator wants to consolidate trust models, which is a separate workstream). Does not produce a Sigstore verdict for an artifact that has no Sigstore signature.

## See also

- `security/auditing-pinned-dependencies` — pairs with this skill: pin the digest, then verify the signature on the pinned digest
- `security/generating-sbom` (planned) — the in-toto envelope often carries SBOM attestations alongside provenance; verifying both is a related workflow
- `security/auditing-transitive-vulnerabilities` (planned) — verifying signatures on transitive dependencies, not just the top-level artifact
- `security/writing-deny-allow-rules` — the trust policy this skill consumes is itself a deny/allow rule artifact

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored in RCS v7-batch-5 per PRAGMATIC discipline; Sonnet-only in-session eval validation
