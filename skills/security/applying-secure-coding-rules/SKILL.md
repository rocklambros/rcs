---
name: applying-secure-coding-rules
description: >
  Applies a user-supplied corpus of secure-coding rules (semgrep packs, SARIF
  rule packs, markdown rule sheets, custom YAML, or the user's
  claude-secure-coding-rules-style repo) to a specific project. Detects the
  project's language, framework, and AI/ML stack; selects the subset of corpus
  rules that apply; flags rules whose preconditions are unmet; produces a
  per-finding report with file + line + rule id + recommended fix. Refuses to
  fabricate rules from memory when no corpus is supplied. Use when reviewing a
  Python+FastAPI+LangChain or similar AI/ML app against a known rule corpus,
  hardening a polyglot repo with partial rule coverage, or surfacing which
  corpus rules apply to which files in the project.
version: 0.1.0
status: drafting
track: security
audience: [security-eng, ml-engineer, backend-dev, skill-author]
evidence:
  - claude-secure-coding-rules
  - quality-contract-NIST-SP-800-218
last-updated: 2026-05-23
---

# Applying Secure-Coding Rules

## When to use

Trigger this skill when the user asks for or implies one of:

- Reviewing a project against a specific, user-supplied secure-coding rule corpus (semgrep rule pack, SARIF rule pack, markdown/YAML rule sheets, or a `claude-secure-coding-rules`-style repository)
- Hardening a Python+FastAPI+LangChain (or similar AI/ML) application against the rules a security team has codified
- Auditing which corpus rules apply to which files in a polyglot repository (Python backend + TypeScript frontend + Terraform infra)
- Producing a per-finding report (file · line · rule id · recommended fix) instead of fabricating "best practices" from training memory
- Asking which corpus rules' preconditions are NOT met (so the user understands what was skipped and why)

## When NOT to use

Skip this skill and hand off when:

- **No rule corpus is supplied.** This skill does NOT invent rules from training memory. Decline and ask the user to point at a rule pack, repository, or markdown file. (Anti-trigger; see Examples → Example 3.)
- The user wants a generic OWASP Top 10 walkthrough or compliance-control mapping → use `security/threat-modeling-llm-app` (planned) or a framework-catalog skill (not yet shipped — RCS v1 has no bundled catalogs)
- The user wants dependency-pinning audit specifically → use `security/auditing-pinned-dependencies`
- The user wants supply-chain provenance verification → use `security/auditing-mcp-server-pre-trust` or a future `security/auditing-source-provenance` skill
- The user wants to write NEW rules → that is rule authoring, a different concern; this skill applies an existing corpus

## Quick start

User: *"Here is our team's `claude-secure-coding-rules` repo at `~/rules/`. Apply it to the FastAPI app at `./app/`."*

Skill response:

1. Detect stack of `./app/` (Python 3.13, FastAPI, LangChain, SQLAlchemy)
2. Index the corpus at `~/rules/` (read README + per-rule files; bucket by language + framework + topic)
3. Select applicable rules: intersection of `(detected_stack, corpus_rule.applies_to)`
4. Surface each applicable rule with: rule id · rule title · matching file/line citations in `./app/` · recommended fix
5. List rules SKIPPED with reason (preconditions unmet — e.g., rule applies to Flask, project uses FastAPI)
6. Final report: applicable-rule findings table + skipped-rule summary + open questions

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| corpus | path or URL | yes | — | Path to the rule corpus (directory, repo, single markdown/YAML file, semgrep pack, or SARIF rule pack). No corpus = decline. |
| target | repo path or directory | yes | — | The project to apply rules against. |
| corpus_format | string | no | auto-detect | One of: `semgrep`, `sarif-rules`, `markdown-rule-sheets`, `yaml-rule-pack`, `claude-secure-coding-rules`. Auto-detected from corpus structure when omitted. |
| stack_overrides | mapping | no | — | Override detected stack (e.g., `{ "framework": "FastAPI", "ml_stack": "LangChain+OpenAI" }`) when auto-detection misses or is ambiguous. |
| severity_floor | "info" \| "low" \| "medium" \| "high" \| "critical" | no | "medium" | Findings below this severity are summarized as counts, not enumerated. |
| include_skipped_rules | bool | no | true | If true, the report explicitly lists rules whose preconditions were not met and why. Recommended to leave on for transparency. |
| output_format | "markdown" \| "json" \| "sarif" | no | "markdown" | Findings report format. SARIF output is for re-ingestion into security tooling. |

## Workflow

Copy this checklist into the response and check items off as the application progresses:

```
Secure-coding-rule application progress:
- [ ] Verify a rule corpus is supplied — if not, STOP and request one
- [ ] Identify corpus format (semgrep / SARIF / markdown / YAML / custom repo)
- [ ] Index the corpus: enumerate rules, capture per-rule applies_to metadata
- [ ] Detect the target project's stack (language, framework, AI/ML stack, runtime)
- [ ] Compute applicable_rules = corpus_rules ∩ detected_stack
- [ ] Compute skipped_rules = corpus_rules \ applicable_rules, with reason per rule
- [ ] Apply each applicable rule: locate matches (file + line) in the target
- [ ] Produce findings table: rule_id · title · file · line · severity · fix
- [ ] Produce skipped-rules summary: rule_id · reason
- [ ] List open questions / preconditions the user must resolve
```

### Step 1: Refuse fabrication

If the user has NOT supplied a corpus, this skill refuses to proceed with rules invented from memory. Output:

> *"This skill applies a user-supplied corpus of secure-coding rules. No corpus was provided. Please point at a rule pack (semgrep, SARIF), a rule repository (e.g., `claude-secure-coding-rules`), a markdown rule sheet, or a YAML rule file. I will not fabricate rules from training memory because the resulting recommendations would be unverifiable and may conflict with your team's policy."*

This refusal is non-negotiable — see `reference/no-corpus-no-rules.md` for the rationale.

### Step 2: Index the corpus

See `reference/corpus-formats.md` for the full per-format indexing recipe. Top accepted formats:

- **semgrep pack** — a directory of `.yaml` files each containing `rules:` with `id`, `pattern`, `message`, `severity`, `languages`, and (optionally) `metadata.framework` / `metadata.applies_to`
- **SARIF rule pack** — a `.sarif` file with `runs[].tool.driver.rules[]`; each rule has `id`, `name`, `shortDescription`, `defaultConfiguration.level`, and `properties` (use `properties.tags` for stack hints)
- **markdown rule sheets** — one rule per markdown file in a directory; conventional frontmatter (`id`, `applies_to`, `severity`, `category`) — used by `claude-secure-coding-rules`
- **YAML rule pack** — single `rules.yaml` with a list of rule objects matching the markdown frontmatter schema
- **claude-secure-coding-rules** — a repository following the `claude-secure-coding-rules` convention; index per its README

When `applies_to` metadata is absent from a rule, treat the rule's `languages` / file glob as the applicability hint (e.g., a semgrep rule with `languages: [python]` is Python-applicable; a rule pattern matching `from fastapi import` is FastAPI-applicable).

### Step 3: Detect the target stack

See `reference/stack-detection-cheatsheet.md` for fingerprints. Minimum stack dimensions to resolve:

- **Language(s)** — file extension dominance + lockfile presence
- **Framework** — characteristic imports / config files (FastAPI: `from fastapi import` + `uvicorn` in deps; Flask: `from flask import` + `app.py`; Django: `manage.py` + `settings.py`)
- **AI/ML stack** — `langchain` / `langchain-core` / `langchain-openai` in deps; `openai`, `anthropic`, `cohere` clients; vector DB clients (`chromadb`, `qdrant-client`, `weaviate-client`, `pgvector`); RAG indicators (loaders, splitters, retrievers)
- **Runtime / deployment** — `Dockerfile`, `docker-compose.yml`, `serverless.yml`, k8s manifests
- **Data layer** — ORM (SQLAlchemy, Django ORM, Prisma), raw SQL drivers, NoSQL clients

Output a stack manifest at the top of the report so the user can verify or correct it via `stack_overrides`.

### Step 4: Intersection — applicable vs skipped

For each corpus rule:

- If `rule.applies_to` intersects `detected_stack` → applicable
- If `rule.applies_to` does NOT intersect → skipped (record the reason: "rule applies to Flask, project uses FastAPI")
- If `rule.applies_to` is missing AND the rule's pattern is stack-agnostic → applicable
- If `rule.applies_to` is missing AND the pattern requires a framework not detected → skipped with low confidence (note in report)

Document EVERY skipped rule with reason. Silent skipping is the failure mode this skill exists to prevent.

### Step 5: Apply applicable rules

For each applicable rule, locate matches in the target:

- **semgrep rules** — run `semgrep --config <rule-file> <target>` and parse JSON output
- **SARIF rules** — if the user has run the tool already, parse the SARIF results JSON; if not, ask the user to run the tool and provide results
- **markdown / YAML rules** — apply the rule's pattern manually (grep / AST walk per the rule's recipe); if the rule lacks a machine-checkable pattern, surface it as a "human-review-required" finding for the relevant files

For each match, capture: rule_id · rule title · file · line · severity · suggested fix · rule-pack source.

### Step 6: Produce the report

See `reference/rule-application-report-template.md` for the markdown template. Three required sections:

1. **Stack manifest** — what was detected, what to override if wrong
2. **Findings** — applicable-rule matches table, sortable by severity
3. **Skipped rules** — per-rule reason (so the user knows what was NOT checked and why)

## Outputs

A markdown report (or JSON / SARIF if requested):

1. **Run identity** — corpus path + corpus format + corpus revision (commit SHA or version), target path + commit SHA, run date
2. **Stack manifest** — detected language(s) · framework(s) · AI/ML stack · runtime · data layer
3. **Findings table** — `| Rule id | Title | File | Line | Severity | Fix |`
4. **Skipped-rules table** — `| Rule id | Reason skipped |`
5. **Counts summary** — critical / high / medium / low / informational findings
6. **Open questions** — preconditions the user must resolve (e.g., "Rule SC-007 applies if the app accepts file uploads — does it?")
7. **Next steps** — concrete commands (e.g., `semgrep --config <selected-subset> .`) the user can run to re-verify

## Failure modes

Known pitfalls in applying a rule corpus and how this skill catches them:

- **No-corpus fabrication.** Without an explicit corpus, the temptation is to "just apply OWASP Top 10 from memory." Caught by Step 1's explicit refusal. The user is told what kinds of corpora are accepted and asked to provide one.
- **Silent skipping.** A rule designed for Flask is silently dropped on a FastAPI project; the user does not know coverage gaps exist. Caught by `include_skipped_rules: true` default — every skipped rule is listed with reason.
- **Stack misdetection.** Auto-detection misses a sub-framework (e.g., LangChain agents present but only `langchain-core` in deps). Caught by surfacing the detected stack at the top of the report so the user can correct via `stack_overrides`.
- **Over-application of generic rules.** A rule with no `applies_to` and a stack-agnostic pattern (e.g., "do not hardcode secrets") is correctly applied everywhere, but a rule with no `applies_to` and a framework-specific pattern is harder to judge — caught by marking such rules as "applied with low confidence; review needed."
- **Corpus drift.** The corpus moves (commit SHA changes) between runs but the report does not reflect it; later you cannot reproduce the audit. Caught by recording the corpus's commit SHA or version in the report header.
- **Rule-pattern false-positive cascade.** Running `semgrep` with the full pack on a large repo produces hundreds of low-severity hits that drown the high-severity ones. Caught by `severity_floor` default of `medium` and explicit counts summary for the suppressed lower-severity findings.
- **Conflicting rules.** Two rules in the corpus give contradictory guidance (e.g., one requires bcrypt cost ≥ 12, another requires argon2id). Caught by surfacing both in the findings, flagging the conflict, and asking the user which policy is authoritative — do NOT silently pick one.

## References

- `reference/corpus-formats.md` — per-format indexing recipe (semgrep, SARIF, markdown rule sheets, YAML, claude-secure-coding-rules)
- `reference/stack-detection-cheatsheet.md` — fingerprints for Python / FastAPI / Flask / Django / LangChain / OpenAI client / vector DB clients / Dockerfile / SQLAlchemy / Prisma
- `reference/rule-application-report-template.md` — markdown template for the report
- `reference/no-corpus-no-rules.md` — rationale for the no-fabrication refusal
- [SARIF 2.1.0 specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html) — for ingesting external tool outputs
- [semgrep rules format](https://semgrep.dev/docs/writing-rules/rule-syntax/) — for the most common corpus shape

## Examples

### Example 1: Python + FastAPI + LangChain against a claude-secure-coding-rules-style corpus (happy-path)

Input: *"Apply our `claude-secure-coding-rules` repo (at `~/rules/`) to the FastAPI+LangChain app at `./app/`. Use markdown rule sheets."*

Output:

```
Stack manifest:
- Language: Python 3.13
- Framework: FastAPI 0.115
- AI/ML stack: LangChain 0.3 + langchain-openai
- Data layer: SQLAlchemy 2.0 (PostgreSQL)
- Runtime: Dockerfile (python:3.13-slim, NOT digest-pinned — see SC-D-002)

Applicable rules: 14 of 47 corpus rules
Findings (high+ only, 6 shown):
| Rule id | Title | File | Line | Severity | Fix |
|---|---|---|---|---|---|
| SC-P-014 | Bare `eval()` / `exec()` forbidden | app/utils/parser.py | 42 | High | Replace with ast.literal_eval or explicit parser |
| SC-LC-003 | LangChain LLM call without `max_tokens` cap | app/chains/qa.py | 17 | High | Pass max_tokens explicitly to prevent runaway cost |
| SC-LC-007 | RAG retriever returns raw user prompt as metadata | app/retrievers/rag.py | 88 | High | Strip user_prompt from metadata before logging |
| SC-FA-002 | FastAPI route accepts dict from body without Pydantic model | app/routes/admin.py | 31 | Medium | Replace `body: dict` with Pydantic BaseModel |
| SC-FA-009 | `Depends()` for auth missing on /admin/* router | app/routes/admin.py | 7 | High | Add Depends(get_current_admin) at router level |
| SC-D-002 | Base image not digest-pinned | Dockerfile | 1 | Medium | `FROM python:3.13-slim@sha256:<digest>` |

Skipped rules: 33 (with reasons)
- SC-F-001..018 (Flask-specific) — project uses FastAPI, not Flask
- SC-JS-001..009 (JavaScript/Node) — no JS in project
- SC-DJ-001..006 (Django-specific) — project uses FastAPI, not Django

Open questions:
- Does `/admin/users/{id}/export` route accept file uploads? Rule SC-FA-022 (upload size cap) applies only if so.
- Is `OPENAI_API_KEY` rotated automatically? Rule SC-LC-011 (key rotation cadence) requires confirmation.
```

### Example 2: Polyglot project with partial corpus coverage (edge-case)

Input: *"Our corpus only covers Python and JS. The project is Python (backend) + TypeScript (frontend) + Terraform (infra). Apply what applies and tell us the gaps."*

Output:

```
Stack manifest:
- Languages: Python 3.13 (backend), TypeScript 5.4 (frontend), HCL/Terraform (infra)
- Frameworks: FastAPI (backend), Next.js (frontend)
- AI/ML: none detected
- Runtime: Dockerfile, terraform/aws/*.tf

Corpus coverage:
- Python rules: applied (29 applicable, 12 findings)
- TypeScript/JS rules: applied (18 applicable, 7 findings, mostly Next.js)
- Terraform: NO corpus coverage — gap

Skipped (incl. uncovered): the entire terraform/ directory has no rules applied. Recommend adding:
- A Terraform-specific rule pack (e.g., tfsec / Checkov rules) to the corpus
- Or marking infra/ as out-of-scope explicitly so the gap is documented

Findings (high+ only):
| Rule id | Title | File | Line | Severity | Fix |
|---|---|---|---|---|---|
| SC-P-014 | Bare eval forbidden | backend/utils.py | 21 | High | Replace with ast.literal_eval |
| SC-JS-007 | dangerouslySetInnerHTML on user input | frontend/Comment.tsx | 34 | High | Sanitize with DOMPurify or use plain text |
| ... (10 more) |

Open questions:
- Does the corpus author plan to add Terraform rules, or should infra/ be excluded from scope?
- Should TypeScript files under frontend/.next/ be excluded? (Build artifacts — usually yes.)
```

### Example 3: No corpus provided (anti-trigger)

Input: *"Audit my Python app for secure coding issues."*

Output:

> *"This skill applies a user-supplied corpus of secure-coding rules. I have not been pointed at a corpus. Please provide one of: a semgrep rule pack directory, a SARIF rule pack file, a markdown rule sheets repository (e.g., your `claude-secure-coding-rules` repo), or a YAML rule pack file. I will not fabricate rules from training memory because the resulting recommendations would be unverifiable and may conflict with your team's policy.*
>
> *If you do not yet have a corpus, here are the lightweight starting options: (1) adopt `claude-secure-coding-rules` from your team, (2) pull a published semgrep rule pack such as `p/python` or `p/security-audit`, or (3) export the rules from a SAST tool you already trust to SARIF. Once you have a corpus, re-invoke this skill with `corpus=<path>` and `target=<repo>`."*

The skill does NOT produce a generic OWASP Top 10 walkthrough, does NOT invent rules, and does NOT pick a default corpus on the user's behalf.

## See also

- `security/auditing-pinned-dependencies` — applies the dep-pinning slice; pairs with this skill on supply-chain hardening
- `security/auditing-mcp-server-pre-trust` — six-check audit for MCP servers before adopting them; complementary to corpus-based code rules
- `workflow/pinning-reproducible-environments` — proactive companion: build a project that pins from day one
- `security/threat-modeling-llm-app` (planned) — pairs with this skill when the target is an LLM/agent application

## Status & version

- Status: drafting
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: RCS v4 batch 2 — codifies the user-supplied-corpus pattern from Rock's `claude-secure-coding-rules` workflow, with explicit anti-fabrication discipline aligned to QC.1 (NIST SP 800-218) of the harness Quality Contract
- Drafting reason: PRAGMATIC Sonnet-only eval validation hit the anti-trigger threshold cleanly (3/3, no-corpus refusal) but the happy-path and edge-case scenarios scored 0/3 and 2/3 respectively because the validating subagent over-applied Step 1's "verify a rule corpus is supplied" to mean "verify on disk" and refused to produce illustrative output when the described corpus/target paths were not physically present. Follow-up needed: either (a) clarify in Step 1 that user-described corpus/target inputs should be accepted at face value for hypothetical/illustrative runs, or (b) revise the eval scenarios to inline corpus content so the rule-application machinery runs against real files.
