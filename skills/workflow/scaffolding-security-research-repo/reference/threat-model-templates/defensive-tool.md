<!-- THREAT-MODEL.md — defensive-tool variant. -->
<!-- Used by scaffolding-security-research-repo when project_kind=defensive-tool. -->

# Threat Model — `<project_name>`

> **Status:** Starter template. Fill in every `<!-- TODO -->` block before
> publishing v0.2 or later. A threat-model document with TODO blocks intact
> is not a threat model; it is a placeholder.

## Assets

What does this tool protect, generate, or operate on?

<!-- TODO: enumerate assets (data, models, credentials, runtime state). -->

## Trust boundaries

Where does input cross a trust boundary?

<!-- TODO: list every boundary (network, IPC, filesystem, model invocation). -->

## Adversary model

Who is the assumed adversary?

- Capability: <!-- TODO: e.g., remote unauthenticated / authenticated user / insider -->
- Knowledge: <!-- TODO: e.g., black-box / source-available / white-box -->
- Persistence: <!-- TODO: e.g., one-shot / sustained -->

## STRIDE walk

| Boundary | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|---|---|---|---|---|---|---|
| <!-- TODO --> | | | | | | |

## Mitigations

For each threat above, what mitigates it?

<!-- TODO: per-threat mitigation table. -->

## Residual risk

What does the tool NOT defend against?

<!-- TODO: explicit out-of-scope list. -->

## Detection

If a mitigation fails, how would we detect the failure?

<!-- TODO: detection / observability plan. -->
