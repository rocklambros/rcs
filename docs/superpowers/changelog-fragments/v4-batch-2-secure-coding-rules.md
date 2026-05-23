### v4 Batch 2: secure-coding rule application — 2026-05-23

Skills shipped:
- `security/applying-secure-coding-rules` v0.1.0 — applies a user-supplied corpus (semgrep / SARIF / markdown / YAML / `claude-secure-coding-rules`-style repo) to a target project, surfacing applicable findings, skipped rules with reasons, and conflicts; refuses to fabricate rules from training memory when no corpus is supplied (Σ 15, status: drafting)

Eval methodology: PRAGMATIC Sonnet-only in-session validation. Three subagent dispatches against the three eval scenarios (happy-path, edge-case, anti-trigger).

Eval results (intent-based scoring):
- 01-python-fastapi-langchain-happy-path: 0/3 (threshold 3/3 — FAIL)
- 02-polyglot-partial-coverage-edge-case: 2/3 (threshold 3/3 — FAIL; passed gap-identification + tfsec/Checkov recommendation rubric items)
- 03-no-corpus-anti-trigger: 3/3 (threshold ≥2/3 — PASS, clean refusal of fabrication with all five accepted corpus formats and the four-part rationale enumerated)

Notes:
- Status demoted to `drafting` per PRAGMATIC step 6 because two scenarios failed materially.
- Root cause analysis: the validating Sonnet subagent had filesystem tool access and interpreted the SKILL.md Step 1 ("Verify a rule corpus is supplied — if not, STOP and request one") as "verify the corpus exists on disk." When the eval scenarios described corpus paths (e.g., `~/rules/`) and target paths (e.g., `./app/`) that did not physically exist on the validating machine, the subagent refused to proceed instead of producing illustrative output. The skill's anti-fabrication discipline (the most important behavior) works correctly — anti-trigger scored 3/3.
- Follow-up options for promotion to `shipped`:
  1. Clarify in SKILL.md Step 1 that user-described corpus/target inputs should be accepted at face value for hypothetical/illustrative runs (skill-content fix).
  2. Revise the eval scenarios to inline corpus content directly in the `query` string so the rule-application machinery runs against real (eval-provided) files (eval-design fix).
  3. Run the full 3-model validation (Haiku + Sonnet + Opus) with a richer scenario harness once option 1 or 2 is in.
- Anti-fabrication discipline is the most important property of this skill and is empirically validated.

Full 3-model validation deferred to a future re-run.
