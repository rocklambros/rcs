### v4-batch-1: AppSec triage + SBOM — 2026-05-23

Skills shipped:

- `security/triaging-vulnerability-findings` v0.1.0 — SARIF triage pipeline (parse → dedupe across tools → reachability → EPSS → rank → suppress-with-rationale → PR comment). Refuses silent suppression. (Σ 14, status: shipped)
- `security/generating-sbom` v0.1.0 — CycloneDX / SPDX SBOM generation from any stack via syft (default) + per-ecosystem fallbacks (cyclonedx-py, cdxgen, cyclonedx-gomod, etc.). Software components only — explicitly scoped to NOT cover AI-BOM (CycloneDX 1.7 AI extension), which is deferred to a planned writing-aibom skill. (Σ 12, status: shipped)
- `security/auditing-transitive-vulnerabilities` v0.1.0 — Dependency-graph CVE audit consuming SBOM or lockfile. Walks dep-path, enriches with EPSS, runs reachability check (callgraph or import-only), ranks by `severity × reachability × (1 + EPSS) / log10(depth + 1)`, and recommends upgrade / override / replace / suppress-with-rationale-and-expiry. (Σ 13, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Each of the 9 scenarios (3 skills × 3 scenarios) was dispatched to a general-purpose subagent with `model: sonnet`, system context = the SKILL.md file, user message = scenario.query. Rubric items judged against intent (not literal phrasing). All 9 scenarios passed at 3/3. Full 3-model validation (Haiku + Sonnet + Opus) deferred to a future re-run.

Notes:

- All three skills cross-reference one another: SBOM is the natural input to transitive-vuln audit; triage applies to SAST/DAST findings while transitive-vuln-audit applies to SCA findings. Together they cover the dominant appsec triage cluster.
- The `generating-sbom` skill explicitly carves out AI-BOM as out of scope; a `writing-aibom` skill is planned for a later batch when CycloneDX 1.7's AI extension matures.
- Suppression discipline is consistent across all three skills: NO silent suppression. Every suppression carries inline rationale + (for transitive-vulns) expiry + reviewer.
