# RCS — Rock's Claude Skills: Public Skills Repo Design

**Date:** 2026-05-22
**Status:** Draft — pending user review
**Owner:** Rock Lambros (klambros / RockCyber)
**Scope:** v1 (initial public release) — 18 catalog-free, methodology-first skills across 5 audience tracks. Full ~80-skill universe is the planning horizon; v2+ ships incrementally.

---

## 1. Identity and positioning

**Repo name:** `RCS` (Rock's Claude Skills).

**Elevator pitch (for the root README):**

> Production-quality Claude Code skills for AI security researchers, data scientists, and ML engineers. Every skill encodes a discipline that would otherwise be rebuilt from scratch each project — statistical-test selection, leakage firewalls, seed hygiene, MCP pre-trust audits, adversarial premortems. Catalog-free by design: no bundled framework controls, no ISO mirrors, no drift to maintain. Methodology only.

**Non-goals (v1):**

- **No framework catalogs.** No bundled NIST CSF / MITRE ATT&CK / OWASP / ISO / EU AI Act / CMMC / PCI DSS / control mappings. Deferred to a later release as a separate sub-project with its own acquisition + refresh + licensing plan per framework.
- **No project-output replicators.** Skills are reusable workflow disciplines. A skill that "does the framework crosswalk for you" or "builds the incident corpus for you" is out of scope. The corresponding work already lives in dedicated repos (`ai-security-framework-crosswalk`, `genai_agentic_incidents`, `TRACT`, etc.).
- **No plugin manifest in v1.** Distribution is flat clone-and-symlink. A Claude Code plugin wrapper can be layered on later without restructuring the skills.
- **No ACS / AgBOM / AI-BOM skills in v1.** Excluded per user direction (in-flight personal work).
- **No AI authorship attribution.** Per global CLAUDE.md: never credit Claude or any AI in commit messages, PR descriptions, code comments, file headers, changelogs, or documentation. Git author/committer is the human. Enforced deterministically by the existing `~/.claude/hooks/PreToolUse-no-ai-attribution.sh`.

## 2. Audience and audience routing

Two primary audiences plus three secondary:

| Audience | Primary track | Description |
|---|---|---|
| Security engineers, CISOs, AI red-teamers, GRC engineers | `security/` | Day-job audience. Threat modeling, vuln triage, MCP pre-trust, pen-test discipline. |
| Data scientists, ML engineers, stats students, applied ML | `ml-datasci/` | Grad-school + applied-ML audience. Stats test selection, classifier eval, regression diagnostics, baseline models, train/test split discipline. |
| Researchers, both audiences with cross-cutting hygiene needs | `workflow/` | Seed hygiene, dedup discipline, temporal-field validation, reproducibility, adversarial premortems, context-window pressure. |
| Instructors, TAs, course-prep | `teaching/` | Pedagogy patterns, rubric writing, pset walkthroughs. v1 ships no skills here; structure pre-allocated. |
| Claude Code skill / plugin / hook / MCP authors | `claude-code-meta/` | Meta — how to write skills, plugins, hooks, rules; how to audit CLAUDE.md hierarchies. |

Audience routing happens at three layers (see § 7 Documentation contract): root README, track READMEs, and `description` fields in skill frontmatter.

## 3. Architectural constraints (settled during brainstorming)

| # | Constraint | Source |
|---|---|---|
| C1 | Skills are **capabilities** (reusable workflow disciplines), not **outputs** (project replicators). | User feedback |
| C2 | No framework catalogs in v1. Methodology-only or catalog-as-input. | User decision |
| C3 | Flat skills repo, clone-and-symlink install. No plugin manifest in v1. | User decision |
| C4 | Audience-track top-level organization (5 tracks, not 3 or 4). | User decision |
| C5 | Filesystem ships only built skills. Planned skills enumerated in track README, no stub SKILL.md files. | User decision |
| C6 | Comprehensive documentation required at all three layers (root, track, per-skill). Lint-enforced. | User decision |
| C7 | v1 ships 18 highest-Σ skills (Σ ≥ 17 from the ROI scorecard). | User decision |
| C8 | Eval-driven development per Anthropic best-practices: ≥3 evals per skill before body. | Anthropic doc |
| C9 | Anthropic frontmatter rules: `name` ≤ 64 chars / lowercase-kebab / no reserved words; `description` third-person, ≤ 1024 chars. | Anthropic doc |
| C10 | SKILL.md body ≤ 500 lines; bundled reference files for longer content. | Anthropic doc |
| C11 | Reference links one level deep from SKILL.md. | Anthropic doc |
| C12 | No AI attribution anywhere. | User CLAUDE.md |

## 4. Directory layout

```
RCS/
├── README.md                              # Root: positioning + audience routing + install + catalog + license
├── LICENSE                                # MIT (override during user review if desired)
├── CONTRIBUTING.md                        # How to add a skill (evals first), no-AI-attribution
├── CHANGELOG.md                           # Per-skill SemVer + repo-level batch tags
├── .gitignore
│
├── docs/
│   ├── conventions.md                     # Frontmatter spec, status semantics, naming rules
│   ├── eval-protocol.md                   # Eval JSON schema, harness, model coverage, thresholds
│   └── governance.md                      # Versioning, deprecation policy, contribution SLAs
│
├── tools/
│   ├── lint-frontmatter.py                # YAML + name/desc Anthropic-spec validation
│   ├── lint-skill-md.py                   # Required H2 section validation
│   ├── lint-links.py                      # One-level-deep reference check
│   └── run-evals.py                       # Eval harness across Haiku / Sonnet / Opus
│
├── skills/
│   ├── README.md                          # Cross-track skill index by Σ rank
│   │
│   ├── security/
│   │   ├── README.md                      # Track narrative + shipped + planned tables
│   │   ├── auditing-mcp-server-pre-trust/
│   │   └── auditing-pinned-dependencies/
│   │
│   ├── ml-datasci/
│   │   ├── README.md
│   │   ├── auditing-train-test-split/
│   │   ├── building-baseline-models/
│   │   ├── checking-test-assumptions/
│   │   ├── evaluating-binary-classifiers/
│   │   ├── evaluating-regression-models/
│   │   ├── reporting-effect-sizes/
│   │   └── selecting-statistical-test/
│   │
│   ├── workflow/
│   │   ├── README.md
│   │   ├── auditing-context-window-pressure/
│   │   ├── auditing-data-quality/
│   │   ├── deduplicating-records/
│   │   ├── enforcing-seed-hygiene/
│   │   ├── pinning-reproducible-environments/
│   │   ├── running-adversarial-premortem/
│   │   └── validating-temporal-fields/
│   │
│   ├── teaching/
│   │   └── README.md                      # No v1 skills; narrative + planned table only
│   │
│   └── claude-code-meta/
│       ├── README.md
│       ├── auditing-claude-md-hierarchy/
│       └── writing-claude-code-skill/
│
└── .github/
    └── workflows/
        ├── frontmatter-lint.yml           # On every PR — runs lint-frontmatter.py + lint-skill-md.py
        ├── link-check.yml                 # On every PR — runs lint-links.py
        └── eval-suite.yml                 # On-PR (changed skills) + nightly (full sweep)
```

**v1 track counts:** security=2, ml-datasci=7, workflow=7, teaching=0, claude-code-meta=2. Total = 18.

## 5. Per-skill directory anatomy

Each skill directory matches the Anthropic best-practices doc structure:

```
skills/<track>/<skill-name>/
├── SKILL.md                # Body ≤ 500 lines; gerund-form name; third-person description
├── reference/              # Bundled reference docs (loaded on-demand; no startup token cost)
│   └── <topic>.md          # e.g. test-decision-tree.md, effect-size-rubric.md
├── scripts/                # Executable utilities (forward slashes; explicit error handling)
│   └── <utility>.py
├── evals/                  # ≥3 eval scenarios (Anthropic checklist requirement)
│   ├── 01-<happy-path>.json
│   ├── 02-<edge-case>.json
│   └── 03-<anti-trigger>.json
└── tests/                  # pytest unit tests for scripts
    └── test_<utility>.py
```

`reference/`, `scripts/`, and `tests/` are optional per-skill (omit if the skill is methodology-only with no executable code). `evals/` is mandatory for `status: shipped`.

## 6. Frontmatter specification

Anthropic-required fields (validated by `tools/lint-frontmatter.py`):

- `name` — gerund-form, lowercase-kebab, ≤ 64 chars, must not contain "anthropic" or "claude" as reserved words
- `description` — third-person ("Walks a decision tree...", NOT "I can help..." or "You can use this..."), ≤ 1024 chars, includes both what the skill does AND when to trigger it

Custom RCS metadata (extends the schema without breaking Anthropic compatibility):

- `version` — SemVer per skill (`MAJOR.MINOR.PATCH`)
- `status` — `shipped` | `drafting` | `planned`
- `track` — `security` | `ml-datasci` | `workflow` | `teaching` | `claude-code-meta`
- `audience` — list of audience tags: `security-eng`, `ai-security`, `data-scientist`, `ml-engineer`, `stats-student`, `instructor`, `skill-author`
- `evidence` — list of repo names where the gap appeared (provenance trail)
- `last-updated` — ISO date

Example:

```yaml
---
name: selecting-statistical-test
description: >
  Walks a decision tree from data characteristics (sample count, paired-vs-independent,
  measurement scale, distributional assumptions) to a recommended statistical test
  (t / Welch / Wilcoxon / Mann-Whitney / Sign / paired-t / Fisher / chi-squared).
  Use when the user has a hypothesis to test, has data in hand, and needs to commit
  to a test before running it.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer, stats-student, instructor]
evidence:
  - DU-MSDSAI-4441-Final
  - DU-MSDSAI-4441-Week8-GDPSurveyInference
  - llm-safety-alignment-study
last-updated: 2026-05-22
---
```

**Status semantics:**

- `shipped` — SKILL.md body complete, ≥ 3 evals passing on Haiku / Sonnet / Opus, all required H2 sections present, scripts (if any) pass tests
- `drafting` — body exists but evals incomplete or failing on one model; visible to readers, not recommended for auto-invocation
- `planned` — listed only in track README; no directory or SKILL.md exists in the filesystem

## 7. Documentation contract

Three documentation layers. All lint-enforced.

### Layer 1 — Root `README.md` required sections

1. Repo name + "Rock's Claude Skills" expansion + elevator pitch
2. **Audience routing block**: "If you're a security engineer, start with X · If you're a data scientist, start with Y · If you're a stats student, start with Z · If you author Claude Code skills, start with W"
3. **Install** — clone-and-symlink instructions for Claude Code (`~/.claude/skills/`), Copilot CLI, Gemini CLI, Anthropic API
4. **Full skill catalog table**: *name · track · what · when · options · status · Σ*
5. **Quick start** — link a beginner-friendly skill walkthrough
6. **Governance summary** — license, contribution rules, no-AI-attribution, versioning
7. **Acknowledgments** — Anthropic skills best-practices, related skill collections
8. **Disclaimer**

### Layer 2 — Track `README.md` required sections (one per track)

1. **Track narrative** — 1-2 paragraphs: audience, problem space, what this track solves
2. **Shipped-skills table** — *name · what · when · options · status · Σ*
3. **Planned-skills table** — status: planned, with target Σ + rationale + sibling-track cross-references
4. **Cross-track references** — "If you use this track you probably also want X from workflow/"
5. **Track-specific conventions** if any (e.g., security track may require additional safety disclaimers)

### Layer 3 — Per-skill `SKILL.md` required H2 sections (in order)

1. `## When to use` — explicit triggers: user requests, keywords, situations
2. `## When NOT to use` — anti-triggers: when Claude should skip or hand off
3. `## Quick start` — minimum-viable runnable example
4. `## Inputs / Arguments / Flags` — every parameter (name, type, required/optional, default, allowed values, example)
5. `## Workflow` — numbered steps; checklist if multi-step (per best-practices doc)
6. `## Outputs` — what the skill produces (format, location, conventions)
7. `## Failure modes` — known pitfalls + how the skill catches them
8. `## References` — bundled `reference/` files + external authoritative links (one level deep)
9. `## Examples` — ≥ 2 real input/output pairs
10. `## See also` — sibling skills (one level deep)
11. `## Status & version` — restates status + SemVer + last-updated

Enforcement: `tools/lint-skill-md.py` validates required H2 sections; CI blocks PR without them.

## 8. Eval-driven development

Per Anthropic best-practices doc: *evals before docs*.

**Per-skill eval requirements** (CI gate for `status: shipped`):

- **Exactly 3 scenarios per skill** in v1, distributed across: 1 happy-path · 1 edge-case (assumption violation, missing data, ambiguity) · 1 anti-trigger (skill should refuse or hand off). v2+ may add more.
- **Exactly 3 expected_behavior rubric items per scenario** in v1 (matches Anthropic doc minimum; keeps pass-threshold math clean). v2+ may extend to 5 with reweighted thresholds.
- **JSON schema**:

  ```json
  {
    "skill": "<skill-name>",
    "scenario_id": "01-<descriptive>",
    "query": "<user prompt to test>",
    "files": ["<optional file paths>"],
    "expected_behavior": [
      "Checkable rubric item 1",
      "Checkable rubric item 2",
      "Checkable rubric item 3",
      "Checkable rubric item 4",
      "Checkable rubric item 5"
    ]
  }
  ```

- **Model coverage:** Haiku 4.5, Sonnet 4.6, Opus 4.7
- **Pass thresholds** (with 3 rubric items per scenario):
  - Haiku 4.5: ≥ 2 of 3 rubric items pass on each scenario; all 3 scenarios required
  - Sonnet 4.6: 3 of 3 on happy-path AND edge-case; ≥ 2 of 3 on anti-trigger
  - Opus 4.7: 3 of 3 on all 3 scenarios

**Harness (`tools/run-evals.py`):**

- Reads eval JSONs from `skills/<track>/<skill>/evals/`
- Runs each scenario against each target model via Anthropic SDK
- Judges with Sonnet 4.6 using a structured judge prompt that scores each `expected_behavior` item 0/1 with rationale
- Writes `skills/<track>/<skill>/evals/results-<model>-<date>.json`
- Outputs CI-friendly summary table

**CI gate (`eval-suite.yml`):**

- On PR with skill changes: run evals for the changed skill across all 3 models; block merge if thresholds not met
- Nightly: full sweep across all `status: shipped` skills; failures filed as issues with the result JSON attached

## 9. License, governance, CI

**License:** MIT (default). Override during user review if Apache 2.0 or other is preferred. MIT chosen because skill-sharing repos in the Claude Code ecosystem (`obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`, the official Anthropic skills) trend permissive, and the lower legal friction encourages adoption.

**CONTRIBUTING.md** required content:

- Eval-first workflow (write evals before SKILL.md body)
- Frontmatter spec + naming convention (gerund, lowercase-kebab)
- Layer-3 required H2 sections
- No AI attribution in commits / PRs / code / docs / file headers
- PR template: links to evals, links to track README update, status declared

**Versioning:**

- Each skill has its own SemVer in frontmatter
- Repo-level tags mark batch releases (`v1`, `v1.1`, etc.)
- Breaking changes to a skill's interface (frontmatter `name` change, removed required args, removed required H2) bump MAJOR
- New optional args, new examples, refined wording bump MINOR
- Typos, lint fixes, eval rubric clarifications bump PATCH

**Deprecation policy:**

- Skill moves to `status: deprecated` with a 90-day notice in CHANGELOG
- SKILL.md gets an `## Old patterns` block linking to the replacement (per best-practices doc pattern)
- After 90 days, the skill is removed from the catalog table; the directory may remain with a tombstone SKILL.md pointing to the replacement

**CI workflows:**

| Workflow | Trigger | Action |
|---|---|---|
| `frontmatter-lint.yml` | Every PR | Run `tools/lint-frontmatter.py` + `tools/lint-skill-md.py` on changed files |
| `link-check.yml` | Every PR | Run `tools/lint-links.py` — verify one-level-deep references resolve |
| `eval-suite.yml` | On PR (changed skills) + nightly (full sweep) | Run `tools/run-evals.py` — block merge if thresholds not met |

## 10. v1 ship batch — build order

Phase plan. Each phase is a coherent PR batch.

### Phase 0 — Bootstrap

No skills yet. Ships:

- Repo skeleton with directory tree from § 4
- Root `README.md` with placeholder catalog table
- `LICENSE` (MIT)
- `CONTRIBUTING.md`
- `CHANGELOG.md` (empty)
- `docs/conventions.md`, `docs/eval-protocol.md`, `docs/governance.md`
- `tools/lint-frontmatter.py`, `tools/lint-skill-md.py`, `tools/lint-links.py`, `tools/run-evals.py`
- `.github/workflows/*.yml`
- All 5 track `README.md` files with planned-skills tables populated from the full ~80 universe

### Phase 1 — Free ships (migrate existing local skills; criterion is "already-authored" not Σ)

- `workflow/running-adversarial-premortem` ← extract from `~/.claude/skills/adversarial-premortem.skill` (ZIP-encoded), reformat to Layer-3 contract, add 3 evals (ATACE math-flags as happy-path)
- `security/auditing-mcp-server-pre-trust` ← migrate from `~/.claude/skills/mcp-server-pre-trust-audit/`, rename to gerund slug, reformat, add 3 evals (license-check / egress-check / secret-handling-check)

### Phase 2 — Highest-Σ low-effort batch (Σ ≥ 19, methodology-only)

- `workflow/enforcing-seed-hygiene` (Σ 20)
- `workflow/validating-temporal-fields` (Σ 19)
- `security/auditing-pinned-dependencies` (Σ 19)
- `ml-datasci/reporting-effect-sizes` (Σ 19)

### Phase 3 — Stats discipline cluster (cross-reference, build together)

- `ml-datasci/selecting-statistical-test` (Σ 18)
- `ml-datasci/checking-test-assumptions` (Σ 18)
- `ml-datasci/auditing-train-test-split` (Σ 18)

### Phase 4 — ML eval cluster

- `ml-datasci/evaluating-binary-classifiers` (Σ 19)
- `ml-datasci/building-baseline-models` (Σ 17)
- `ml-datasci/evaluating-regression-models` (Σ 17)

### Phase 5 — Data + workflow hygiene

- `workflow/deduplicating-records` (Σ 18)
- `workflow/pinning-reproducible-environments` (Σ 17)
- `workflow/auditing-data-quality` (Σ 17)

### Phase 6 — Claude-Code meta + context discipline

- `claude-code-meta/writing-claude-code-skill` (Σ 18)
- `claude-code-meta/auditing-claude-md-hierarchy` (Σ 18)
- `workflow/auditing-context-window-pressure` (Σ 17)

**Total: 18 skills across 6 build phases + bootstrap.**

## 11. Migration plan for existing local skills

The user's harness currently contains three skills in `~/.claude/skills/`:

| Skill | Migration plan |
|---|---|
| `adversarial-premortem.skill` (ZIP-encoded) | Unzip → extract SKILL.md → reformat to Layer-3 contract → add `## When NOT to use`, `## Inputs / Arguments / Flags`, `## Failure modes` if missing → write 3 evals (ATACE math-flags as happy-path scenario) → ship to `workflow/running-adversarial-premortem/`. Keep the harness internal copy in `~/.claude/skills/` as the canonical local copy; the public version is a polished export. |
| `mcp-server-pre-trust-audit/` | Read existing SKILL.md → reformat to Layer-3 contract → add missing required sections → rename slug `mcp-server-pre-trust-audit` → `auditing-mcp-server-pre-trust` (enforce gerund convention) → write 3 evals (license / egress / secret-handling) → ship to `security/auditing-mcp-server-pre-trust/`. |
| `seed-evaluation/` | **Not migrating** to public. Harness-internal: applies the foundation/03 two-stage methodology for adopting external tools into the user's Mac harness. Stays in `~/.claude/skills/`. |

## 12. Open questions / risks

1. **License default.** MIT defaulted; user may want Apache 2.0 or other. Override during user review.
2. **Eval harness model availability.** Eval gate requires Anthropic API key with access to Haiku 4.5 / Sonnet 4.6 / Opus 4.7 in CI. Subscription-only access through Claude Code CLI is not sufficient for the CI harness. If any model is unavailable, `eval-suite.yml` needs a documented fallback (skip-and-warn vs hard-fail) so private forks without full API access can still contribute. Recommend hard-fail in the main repo, skip-and-warn opt-in for forks.
3. **Eval judge bias.** Sonnet 4.6 judging Sonnet 4.6 output is a known source of bias. Mitigation: judge prompt is strict and rubric-based; consider rotating judge model across runs in v2.
4. **`docs/superpowers/specs/` location.** This spec lives in the `RCS/docs/superpowers/specs/` path per the brainstorming skill default. If the user prefers a different convention (e.g., `RCS/docs/specs/` without the `superpowers/` segment), rename before commit.
5. **No-AI-attribution enforcement in the public repo.** Local hook enforces during authoring. External contributors won't have the hook. Mitigation: CONTRIBUTING.md states the rule explicitly + PR template checkbox + maintainer review.
6. **Reference link integrity at one level deep.** `lint-links.py` must catch transitive references (per best-practices: "Keep references one level deep from SKILL.md") — write the check carefully.
7. **Frontmatter custom fields and Anthropic compatibility.** Anthropic spec only validates `name` and `description`. Custom fields (`status`, `track`, `audience`, `evidence`, `last-updated`, `version`) are tolerated but unused by the Anthropic runtime. Verify with a test skill loaded into Claude Code before Phase 1 ships.
8. **Teaching track empty in v1.** Risk that the track looks abandoned. Mitigation: track README narrative + planned-skills table makes it clear it's pre-allocated. Consider shipping 1 teaching skill in v1.1 to demonstrate the track.

---

**Next step:** spec self-review (placeholders, contradictions, ambiguity, scope), then user review gate, then invoke `writing-plans` for the implementation plan.
