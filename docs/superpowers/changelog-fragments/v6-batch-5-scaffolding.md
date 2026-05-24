### v6-batch-5: scaffolding — 2026-05-23

Skills shipped:

- `workflow/scaffolding-ml-research-notebook` v0.1.0 — greenfield ML/DS project scaffold: pinned env, src/, seed helper, data/raw split, tests, pre-commit, starter notebook (Σ 15, status: shipped)
- `workflow/scaffolding-security-research-repo` v0.1.0 — greenfield security-research scaffold: SECURITY.md, VDP.md (safe-harbor), THREAT-MODEL.md template per project_kind, gitleaks + semgrep pre-commit, Apache-2.0 default license, security ISSUE_TEMPLATE (Σ 13, status: shipped)
- `workflow/scaffolding-llm-eval-harness` v0.1.0 — LLM-eval harness scaffold with the five-field result-row contract (model_id with revision pin, dataset_hash, prompt_version, judge_model, results.jsonl) (Σ 14, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Each skill ran 3 scenarios (happy-path, edge-case, anti-trigger), one Sonnet subagent per scenario, judged by intent. Full 3-model validation deferred to a future re-run.

Eval results:

- scaffolding-ml-research-notebook: happy 3/3, edge 3/3, anti 3/3
- scaffolding-security-research-repo: happy 3/3, edge 3/3, anti 3/3
- scaffolding-llm-eval-harness: happy 3/3, edge 3/3, anti 3/3

All three skills passed all thresholds and ship with status: shipped.

Notes: All 3 skills are siblings of one another (the "When NOT to use" of each links to the other two). Together they cover the three greenfield-scaffolding shapes Rock's evidence corpus has surfaced — ML/DS notebooks, security-research repos, LLM-eval harnesses.
