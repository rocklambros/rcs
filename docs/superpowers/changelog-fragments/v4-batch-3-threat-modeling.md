### v4-batch-3: threat modeling — 2026-05-23

Skills shipped:
- `security/threat-modeling-llm-app` v0.1.0 — STRIDE-style threat-modeling walk over LLM applications (chatbot, RAG, summarizer, content-generation pipeline) against a user-supplied catalog (OWASP LLM Top 10, MITRE ATLAS, MAESTRO, custom); inventories components and five canonical LLM-app boundaries, maps catalog items to STRIDE categories, produces an auditable register with likelihood / impact / mitigation / owner per row; methodology only, no bundled catalogs (Σ 13, status: shipped)
- `security/threat-modeling-agentic-systems` v0.1.0 — extends LLM-app threat modeling with agentic boundaries (planner↔executor, memory↔next-turn, tool-result↔next-prompt, agent↔agent, identity blast radius) and agent-concern tagging (EA / GH / MP / RL / TC / MAC); mandatory runaway-loop / blast-radius subsection and data-plane vs control-plane mitigation tagging; methodology only, no bundled catalogs (Σ 11, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 6 dispatches (3 scenarios × 2 skills); all scored 3/3 against intent for every scenario including the anti-triggers. Full 3-model (Haiku / Sonnet / Opus) validation deferred to a future re-run.

Notes: Both skills are deliberately methodology-only — they refuse to invent a catalog if the user does not supply one, per the public-skills-repo design (no bundled NIST / MITRE / OWASP / EU-AI-Act content in v1). The agentic skill cross-references the LLM-app sibling and the anti-trigger eval verifies the handoff works cleanly. No eval failures or calibration corrections; both skills retained `status: shipped`.
