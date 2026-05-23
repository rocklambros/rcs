# Threat register — table template

Use this template to render the threat-modeling output. One row per (catalog-item, boundary, STRIDE-category) triple. Likelihood / Impact / Risk all use the scale named in `SKILL.md § Inputs`.

```markdown
## Threat register — <app-name> against <catalog-name> v<version>

| # | Catalog item | Boundary | STRIDE | Likelihood | Impact | Risk | Mitigation | Owner | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | LLM01: Prompt injection | User → app | T | H | M | H | Delimiter-tagged user content; system-prompt hardening; output validation before tool dispatch | ai-platform | Direct injection. Test corpus tracked in `red-team-corpus.md`. |
| 2 | LLM01: Prompt injection | Retriever → context | T, E | H | H | H | RAG allowlist (Confluence space IDs); per-document provenance tag; sandboxed tool dispatch | ai-platform | Indirect injection — highest residual risk after mitigations. |
| 3 | LLM07: Insecure plugin design | Model → tool | T, E | M | H | H | Tool-argument allowlist; per-tool schema validation; refund_order requires HITL gate | security-eng | Refund tool is the state-changing endpoint. |
| 4 | LLM08: Excessive agency | Model → tool (refund_order) | E | M | H | H | Human-in-the-loop gate for any refund > $X; per-day cap per agent identity | support-eng + security-eng | Operational + technical mitigations. |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Coverage gaps

- **Catalog items with no register row:**
  - LLM10 (Model theft): not applicable — hosted API, no model artifact accessible to user.
- **Boundaries with no catalog coverage:**
  - Model gateway → audit-log sink: no LLM Top 10 item addresses log integrity. Recommend supplementing with NIST SP 800-92 logging guidance.

### Top 3 residual risks

1. **Indirect prompt injection via RAG corpus** (row 2) — mitigations reduce but do not eliminate; ongoing red-team testing recommended.
2. **Refund tool excessive agency** (row 4) — HITL gate effective but increases support latency; review threshold quarterly.
3. **Insecure plugin design on tool dispatcher** (row 3) — argument allowlist requires per-release re-review.
```

Notes on filling this in:

- The `#` column makes rows referenceable from the executive summary.
- Risk = Likelihood × Impact, but use the same scale (do not silently switch from L/M/H to numeric).
- "Owner" is a team or role, not a person — assignment is a separate process.
- Each row's mitigation must be specific enough that an implementer can act on it. "Improve security" is not a mitigation.
- If a STRIDE category does not apply to a row, omit that letter — do not pad rows with all-letter STRIDE strings.
