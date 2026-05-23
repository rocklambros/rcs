# RCS Phase 0 + Phase 1 — Bootstrap and Free-Ship Migrations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a publishable Claude Code skills repo with full bootstrap (tooling, lint, docs contract, CI, all 5 track READMEs) plus 2 migrated free-ship skills (`workflow/running-adversarial-premortem`, `security/auditing-mcp-server-pre-trust`) that exercise the entire eval-gated documentation pipeline end-to-end.

**Architecture:** Flat clone-and-symlink skills repo, audience-track top-level organization (5 tracks), MIT license, Python tooling (uv + pytest), GitHub Actions CI gating frontmatter / link / eval checks. Per-skill anatomy follows Anthropic best-practices doc (SKILL.md + reference/ + scripts/ + evals/ + tests/). Three documentation layers (root README, track README, per-skill SKILL.md) lint-enforced. Eval-driven development per Anthropic guidance — 3 scenarios × 3 rubric items per skill, judged by Sonnet 4.6 against Haiku 4.5 / Sonnet 4.6 / Opus 4.7 completions.

**Tech Stack:** Python 3.13, uv (package management), pytest (testing), Anthropic Python SDK (eval harness), PyYAML (frontmatter parsing), markdown-it-py (link extraction), GitHub Actions (CI). No Claude Code plugin manifest in v1.

**Spec:** `docs/superpowers/specs/2026-05-22-rcs-public-skills-repo-design.md`

---

## File Structure

Phase 0 + Phase 1 will create or modify these files:

```
RCS/
├── README.md                                            # Phase 0 Task 3 / Phase 1 Task 32 (update catalog)
├── LICENSE                                              # Phase 0 Task 2 (MIT)
├── CONTRIBUTING.md                                      # Phase 0 Task 4
├── CHANGELOG.md                                         # Phase 0 Task 5 / Phase 1 Task 33
├── .gitignore                                           # Phase 0 Task 1
├── pyproject.toml                                       # Phase 0 Task 1 (uv init)
├── docs/
│   ├── conventions.md                                   # Phase 0 Task 6
│   ├── eval-protocol.md                                 # Phase 0 Task 7
│   ├── governance.md                                    # Phase 0 Task 8
│   ├── specs/2026-05-22-rcs-public-skills-repo-design.md   # already exists
│   └── plans/2026-05-22-rcs-phase-0-and-1-...md         # this file
├── tools/
│   ├── __init__.py                                      # Phase 0 Task 9
│   ├── lint_frontmatter.py                              # Phase 0 Task 9
│   ├── lint_skill_md.py                                 # Phase 0 Task 10
│   ├── lint_links.py                                    # Phase 0 Task 11
│   ├── run_evals.py                                     # Phase 0 Task 12
│   └── tests/
│       ├── __init__.py                                  # Phase 0 Task 9
│       ├── test_lint_frontmatter.py                     # Phase 0 Task 9
│       ├── test_lint_skill_md.py                        # Phase 0 Task 10
│       ├── test_lint_links.py                           # Phase 0 Task 11
│       └── test_run_evals.py                            # Phase 0 Task 12
├── skills/
│   ├── README.md                                        # Phase 0 Task 16 / Phase 1 Task 32
│   ├── security/
│   │   ├── README.md                                    # Phase 0 Task 17 / Phase 1 Task 31
│   │   └── auditing-mcp-server-pre-trust/               # Phase 1 Tasks 27-31
│   │       ├── SKILL.md
│   │       └── evals/
│   │           ├── 01-happy-path.json
│   │           ├── 02-edge-case-no-license.json
│   │           └── 03-anti-trigger.json
│   ├── ml-datasci/README.md                             # Phase 0 Task 18
│   ├── workflow/
│   │   ├── README.md                                    # Phase 0 Task 19 / Phase 1 Task 26
│   │   └── running-adversarial-premortem/               # Phase 1 Tasks 22-26
│   │       ├── SKILL.md
│   │       └── evals/
│   │           ├── 01-happy-path.json
│   │           ├── 02-edge-case-too-large.json
│   │           └── 03-anti-trigger.json
│   ├── teaching/README.md                               # Phase 0 Task 20
│   └── claude-code-meta/README.md                       # Phase 0 Task 21
└── .github/
    └── workflows/
        ├── frontmatter-lint.yml                         # Phase 0 Task 13
        ├── link-check.yml                               # Phase 0 Task 14
        └── eval-suite.yml                               # Phase 0 Task 15
```

**Per-file responsibility:**

| File | Responsibility |
|---|---|
| `README.md` | Repo positioning, audience routing, install, full skill catalog, governance summary |
| `LICENSE` | MIT license text |
| `CONTRIBUTING.md` | Eval-first workflow, frontmatter spec, naming convention, no-AI-attribution rule |
| `CHANGELOG.md` | Per-skill SemVer + repo-level batch tags |
| `pyproject.toml` | Python tooling deps (anthropic, pyyaml, markdown-it-py, pytest, click) |
| `docs/conventions.md` | Frontmatter spec, status semantics, naming rules |
| `docs/eval-protocol.md` | Eval JSON schema, harness, model coverage, pass thresholds |
| `docs/governance.md` | Versioning, deprecation policy, contribution SLAs |
| `tools/lint_frontmatter.py` | Validates Anthropic-required name/description rules + custom RCS fields |
| `tools/lint_skill_md.py` | Validates required H2 sections in SKILL.md per Layer-3 contract |
| `tools/lint_links.py` | Verifies cross-file refs are one level deep (Anthropic best-practices rule) |
| `tools/run_evals.py` | Eval harness: runs scenarios across 3 models, judges with Sonnet 4.6 |
| `skills/<track>/README.md` | Track narrative, shipped table, planned-skills table, cross-track refs |
| `skills/<track>/<skill>/SKILL.md` | Anthropic frontmatter + Layer-3 H2 sections |
| `skills/<track>/<skill>/evals/0[1-3]-*.json` | Eval scenarios (happy / edge / anti-trigger) |
| `.github/workflows/frontmatter-lint.yml` | CI: every PR runs lint_frontmatter + lint_skill_md |
| `.github/workflows/link-check.yml` | CI: every PR runs lint_links |
| `.github/workflows/eval-suite.yml` | CI: on-PR (changed skills) + nightly (full sweep) |

---

# Phase 0 — Bootstrap (Tasks 1–21)

### Task 1: Initialize repo skeleton with uv + .gitignore

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`

- [ ] **Step 1: Verify cwd is the RCS repo root**

```bash
pwd
```

Expected output ends with `/RCS`. If not, `cd /Users/klambros/github_projects/RCS` first.

- [ ] **Step 2: Initialize uv project**

```bash
uv init --no-readme --no-pin-python --bare
```

Expected: creates `pyproject.toml` only (no source dir, no Python pin since we want flexible Python ≥3.11).

- [ ] **Step 3: Set Python version requirement and project metadata in pyproject.toml**

Edit `pyproject.toml` to be exactly:

```toml
[project]
name = "rcs-tools"
version = "0.1.0"
description = "Tooling for Rock's Claude Skills (RCS) — lint and eval harness"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.40.0",
    "pyyaml>=6.0",
    "markdown-it-py>=3.0.0",
    "click>=8.1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-mock>=3.12",
]

[tool.pytest.ini_options]
testpaths = ["tools/tests"]
pythonpath = ["."]
```

- [ ] **Step 4: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
.uv/
.pytest_cache/
*.egg-info/

# Eval results (regenerated per run; not committed)
skills/**/evals/results-*.json

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
```

- [ ] **Step 5: Install deps and verify**

```bash
uv sync
uv run python -c "import anthropic, yaml, markdown_it, click; print('deps OK')"
```

Expected: `deps OK`

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .gitignore uv.lock
git commit -m "Initialize Python tooling project (uv + pyproject)"
```

---

### Task 2: Write LICENSE (MIT)

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Write the MIT license file**

```
MIT License

Copyright (c) 2026 Rock Lambros (RockCyber, LLC)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Commit**

```bash
git add LICENSE
git commit -m "Add MIT license"
```

---

### Task 3: Write initial root README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write the root README**

The README contains the elevator pitch, audience routing block, install instructions, a placeholder catalog table (filled in Phase 1 Task 32 with the 2 shipped skills), and governance summary.

```markdown
# Rock's Claude Skills (RCS)

Production-quality Claude Code skills for AI security researchers, data scientists, and ML engineers. Every skill encodes a discipline that would otherwise be rebuilt from scratch each project — statistical-test selection, leakage firewalls, seed hygiene, MCP pre-trust audits, adversarial premortems. Catalog-free by design: no bundled framework controls, no ISO mirrors, no drift to maintain. Methodology only.

## Audience routing

- **Security engineer or AI red-teamer?** Start with `skills/security/`.
- **Data scientist, ML engineer, or stats student?** Start with `skills/ml-datasci/`.
- **Researcher working across both?** Start with `skills/workflow/` (cross-cutting hygiene).
- **Instructor or TA?** Start with `skills/teaching/` (pedagogy patterns).
- **Claude Code skill author?** Start with `skills/claude-code-meta/`.

## Install

### Claude Code

Clone and symlink each skill you want into `~/.claude/skills/`:

```bash
git clone https://github.com/rockcyber/rcs.git
cd rcs
for skill in skills/*/*/; do
  name=$(basename "$skill")
  ln -s "$(pwd)/$skill" "$HOME/.claude/skills/$name"
done
```

### Copilot CLI, Gemini CLI, Anthropic API

The `skills/<track>/<name>/SKILL.md` files follow the Anthropic Skills format and work in any host that supports the spec. Symlink or copy the directories into your tool's skill discovery path. For the Anthropic API, upload via the SDK per the Skills guide.

## Skill catalog

_Catalog populated in Phase 1. Two skills planned for first release:_

| Skill | Track | Status |
|---|---|---|
| `running-adversarial-premortem` | workflow | planned |
| `auditing-mcp-server-pre-trust` | security | planned |

## Governance

- **License:** MIT (see `LICENSE`)
- **Contributing:** See `CONTRIBUTING.md` — eval-first workflow, gerund naming, no AI attribution
- **Versioning:** SemVer per skill (`frontmatter.version`) + loose repo-level batch tags (`v1`, `v1.1`, ...)
- **Documentation contract:** See `docs/conventions.md`

## Acknowledgments

Skill design follows the [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) document and the patterns demonstrated by the official `anthropics/claude-code` skills, `obra/superpowers`, and `affaan-m/everything-claude-code` repos.

## Disclaimer

Skills are tooling, not advice. They encode disciplines and decision trees observed in real research and engineering practice. Verify outputs against authoritative sources before relying on them in regulated or safety-critical contexts.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "Add root README with audience routing and install instructions"
```

---

### Task 4: Write CONTRIBUTING.md

**Files:**
- Create: `CONTRIBUTING.md`

- [ ] **Step 1: Write CONTRIBUTING.md**

```markdown
# Contributing to RCS

## What we accept

Skills that match the RCS positioning:

- **Catalog-free**: no bundled framework controls (NIST / MITRE / OWASP / ISO / EU AI Act / CMMC / PCI). Methodology-only or catalog-as-input.
- **Capability, not output**: reusable workflow disciplines, not skills that replicate a finished project's output.
- **Real evidence**: the gap the skill closes must have appeared in 2+ real-world contexts.

If your skill doesn't fit, propose a separate sibling repo or open an issue to discuss.

## Workflow

### 1. Open an issue first

Describe the gap (which workflow you keep redoing) and propose the skill name (gerund-form, lowercase-kebab, ≤ 64 chars).

### 2. Write evals before the skill body

Per the [Anthropic best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), evals come first. For each new skill, create:

- `skills/<track>/<skill>/evals/01-happy-path.json` — typical use case
- `skills/<track>/<skill>/evals/02-edge-case.json` — assumption violation, missing data, or ambiguity
- `skills/<track>/<skill>/evals/03-anti-trigger.json` — skill should refuse or hand off

Each scenario has exactly 3 checkable `expected_behavior` rubric items in v1.

### 3. Write SKILL.md against the Layer-3 documentation contract

Required H2 sections in this order: `When to use`, `When NOT to use`, `Quick start`, `Inputs / Arguments / Flags`, `Workflow`, `Outputs`, `Failure modes`, `References`, `Examples`, `See also`, `Status & version`. See `docs/conventions.md`.

Body ≤ 500 lines. Longer content goes in `reference/` files (loaded on-demand, no startup token cost).

### 4. Run lint locally

```bash
uv run python -m tools.lint_frontmatter skills/<track>/<skill>/SKILL.md
uv run python -m tools.lint_skill_md skills/<track>/<skill>/SKILL.md
uv run python -m tools.lint_links skills/<track>/<skill>/
```

### 5. Run evals locally

You need `ANTHROPIC_API_KEY` set with access to Haiku 4.5, Sonnet 4.6, and Opus 4.7.

```bash
uv run python -m tools.run_evals skills/<track>/<skill>/
```

Pass thresholds (per `docs/eval-protocol.md`):

- Haiku 4.5: ≥ 2 of 3 rubric items on each scenario, all 3 scenarios
- Sonnet 4.6: 3 of 3 on happy-path AND edge-case; ≥ 2 of 3 on anti-trigger
- Opus 4.7: 3 of 3 on all 3 scenarios

### 6. Update track README + root README catalog

Add a row to the track's shipped-skills table and to the root catalog.

### 7. Submit PR

CI will run frontmatter lint, link check, and eval suite. The PR is blocked until all three pass.

## No AI attribution

Do not credit Claude, GPT, or any AI as an author or contributor — in commits, PR descriptions, code comments, file headers, changelogs, or documentation. No `Co-Authored-By: Claude`, no "Generated with AI" lines, no robot emoji. Git author and committer stay the human. PRs that include AI attribution will be asked to amend.

## Naming convention

Skill slugs are gerund-form, lowercase-kebab, ≤ 64 characters, no `anthropic` or `claude` as reserved words. Examples: `selecting-statistical-test`, `enforcing-seed-hygiene`, `auditing-mcp-server-pre-trust`.

## License

By contributing, you agree your contribution is licensed under the MIT license that covers this repo.
```

- [ ] **Step 2: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "Add CONTRIBUTING.md with eval-first workflow and no-AI-attribution rule"
```

---

### Task 5: Write CHANGELOG.md

**Files:**
- Create: `CHANGELOG.md`

- [ ] **Step 1: Write CHANGELOG.md with v0 / Unreleased placeholder**

```markdown
# Changelog

All notable changes to RCS are documented here. Per-skill changes use the skill's SemVer; repo-level batch tags mark release groupings.

## [Unreleased]

### Added (Phase 0 — Bootstrap)

- Repo skeleton, root README, LICENSE (MIT), CONTRIBUTING.md
- `docs/conventions.md`, `docs/eval-protocol.md`, `docs/governance.md`
- `tools/lint_frontmatter.py`, `tools/lint_skill_md.py`, `tools/lint_links.py`, `tools/run_evals.py`
- `.github/workflows/frontmatter-lint.yml`, `link-check.yml`, `eval-suite.yml`
- All 5 track READMEs with planned-skills tables populated from the full ~80-skill universe

### Added (Phase 1 — Free ships)

- `workflow/running-adversarial-premortem` v0.1.0 — migrated from harness
- `security/auditing-mcp-server-pre-trust` v0.1.0 — migrated from harness
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "Add CHANGELOG.md with Phase 0 and Phase 1 unreleased entries"
```

---

### Task 6: Write docs/conventions.md

**Files:**
- Create: `docs/conventions.md`

- [ ] **Step 1: Write conventions doc**

```markdown
# RCS Conventions

This document defines the frontmatter spec, status semantics, naming rules, and Layer-3 SKILL.md required sections that every RCS skill must satisfy. Lint-enforced via `tools/lint_frontmatter.py` and `tools/lint_skill_md.py`.

## Naming

- Skill slugs are **gerund-form** (verb + -ing): `selecting-...`, `enforcing-...`, `auditing-...`, `evaluating-...`, `building-...`, `writing-...`, `running-...`, `scaffolding-...`, `validating-...`, `deduplicating-...`, `tuning-...`.
- Lowercase-kebab. ≤ 64 characters. No `anthropic` or `claude` reserved words. No XML tags.
- The slug is the directory name AND the frontmatter `name` field.

## Frontmatter (YAML)

### Required (Anthropic spec)

```yaml
name: <gerund-form-slug>
description: >
  <Third-person, ≤ 1024 chars, includes WHAT the skill does and WHEN to trigger it.>
```

**Third-person rule**: write "Walks a decision tree..." NOT "I can help you..." or "You can use this..." (per Anthropic best-practices doc; the description is injected into the system prompt and POV inconsistency causes discovery problems).

### RCS custom fields (don't break Anthropic schema)

```yaml
version: 0.1.0                       # SemVer per skill
status: shipped                       # shipped | drafting | planned
track: ml-datasci                     # security | ml-datasci | workflow | teaching | claude-code-meta
audience:                             # list of tags
  - data-scientist
  - ml-engineer
  - stats-student
  - instructor
evidence:                             # repos where the gap appeared (provenance)
  - DU-MSDSAI-4441-Final
  - llm-safety-alignment-study
last-updated: 2026-05-22              # ISO date
```

## Status semantics

| Status | Filesystem | Required for | Auto-invocable |
|---|---|---|---|
| `shipped` | Full SKILL.md + 3 passing evals + Layer-3 H2 sections | Production use | Yes |
| `drafting` | SKILL.md exists, evals incomplete or failing on one model | Public review | No |
| `planned` | NO directory; listed only in track README | Roadmap visibility | No |

## SKILL.md Layer-3 contract — required H2 sections in order

1. `## When to use` — explicit triggers (user requests, keywords, situations)
2. `## When NOT to use` — anti-triggers (when Claude should skip or hand off)
3. `## Quick start` — minimum-viable runnable example
4. `## Inputs / Arguments / Flags` — every parameter (name, type, required/optional, default, allowed values, example)
5. `## Workflow` — numbered steps; checklist if multi-step (per Anthropic best-practices)
6. `## Outputs` — what the skill produces (format, location, conventions)
7. `## Failure modes` — known pitfalls + how the skill catches them
8. `## References` — bundled `reference/` files + external links (one level deep)
9. `## Examples` — ≥ 2 real input/output pairs
10. `## See also` — sibling skills (one level deep links)
11. `## Status & version` — restates status + SemVer + last-updated

Body ≤ 500 lines. Longer content goes in `reference/` (no startup token cost; loaded on-demand).

## File path rules

- Forward slashes only (Unix-style, works on all platforms).
- Reference links one level deep from SKILL.md — Claude may partially read transitively-linked files, missing content.
- Bundle large reference material in `reference/`; bundle scripts in `scripts/`.

## Eval requirements (see `eval-protocol.md` for details)

- Exactly 3 scenarios per skill in v1: happy-path, edge-case, anti-trigger.
- Exactly 3 rubric items per scenario.
- Sonnet 4.6 judges Haiku/Sonnet/Opus completions against the rubric.
```

- [ ] **Step 2: Commit**

```bash
git add docs/conventions.md
git commit -m "Add conventions doc: frontmatter spec, naming, status, Layer-3 contract"
```

---

### Task 7: Write docs/eval-protocol.md

**Files:**
- Create: `docs/eval-protocol.md`

- [ ] **Step 1: Write eval protocol doc**

```markdown
# RCS Eval Protocol

Eval-driven development per the [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) guidance: *evals before docs*.

## Per-skill requirements

| Item | v1 requirement |
|---|---|
| Scenarios per skill | Exactly 3 |
| Scenario coverage | 1 happy-path + 1 edge-case + 1 anti-trigger |
| Rubric items per scenario | Exactly 3 |
| Model coverage | Haiku 4.5, Sonnet 4.6, Opus 4.7 |
| Judge model | Sonnet 4.6 (rotate in v2 to reduce same-family bias) |

## Eval JSON schema

Each eval file at `skills/<track>/<skill>/evals/0[1-3]-<scenario-id>.json`:

```json
{
  "skill": "selecting-statistical-test",
  "scenario_id": "01-paired-non-normal-small-n",
  "scenario_kind": "happy-path",
  "query": "I have before/after measurements for 18 subjects. Shapiro-Wilk p=0.003 on the differences. Which test should I use?",
  "files": [],
  "expected_behavior": [
    "Identifies the design as paired (within-subject before/after)",
    "Recommends Wilcoxon signed-rank, NOT paired t-test",
    "Names the Shapiro-Wilk p-value as the gating assumption check"
  ]
}
```

Field semantics:

- `skill` — the skill slug (matches the directory name)
- `scenario_id` — `0[1-3]-<short-descriptive>`; matches the filename stem
- `scenario_kind` — `happy-path` | `edge-case` | `anti-trigger`
- `query` — verbatim user prompt
- `files` — optional list of file paths Claude should reference (relative to skill dir)
- `expected_behavior` — exactly 3 checkable rubric items, written as third-person assertions about the response

## Judge prompt structure

The judge (Sonnet 4.6) receives:

1. The skill's SKILL.md body
2. The eval `query` (and `files` if present)
3. The candidate model's completion
4. The 3 rubric items

For each rubric item, the judge returns `pass: true|false` with a one-sentence rationale. The judge prompt enforces strict literal interpretation — partial credit is `false`.

## Pass thresholds (with 3 rubric items per scenario)

| Model | Happy-path | Edge-case | Anti-trigger |
|---|---|---|---|
| Haiku 4.5 | ≥ 2 of 3 | ≥ 2 of 3 | ≥ 2 of 3 |
| Sonnet 4.6 | 3 of 3 | 3 of 3 | ≥ 2 of 3 |
| Opus 4.7 | 3 of 3 | 3 of 3 | 3 of 3 |

A skill earns `status: shipped` only when ALL pass thresholds are met across ALL 3 scenarios.

## CI gating

`.github/workflows/eval-suite.yml`:

- On PR with skill changes: run evals for the changed skill across all 3 models; block merge if thresholds not met
- Nightly: full sweep across all `status: shipped` skills; failures filed as GitHub issues with result JSONs attached
- Public forks without `ANTHROPIC_API_KEY` skip-and-warn (documented opt-out); main repo hard-fails

## Local execution

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run python -m tools.run_evals skills/<track>/<skill>/
```

Output: `skills/<track>/<skill>/evals/results-<model>-<YYYY-MM-DD>.json` (gitignored).

## Result JSON schema

```json
{
  "skill": "selecting-statistical-test",
  "model": "claude-haiku-4-5-20251001",
  "run_date": "2026-05-22T14:32:00Z",
  "scenarios": [
    {
      "scenario_id": "01-paired-non-normal-small-n",
      "completion": "<full response text>",
      "rubric_results": [
        {"item": "Identifies the design as paired...", "pass": true, "rationale": "..."},
        {"item": "Recommends Wilcoxon...", "pass": true, "rationale": "..."},
        {"item": "Names Shapiro-Wilk...", "pass": false, "rationale": "..."}
      ],
      "score": "2/3"
    }
  ],
  "passed_threshold": false
}
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/eval-protocol.md
git commit -m "Add eval-protocol.md: schema, thresholds, judge, CI gating"
```

---

### Task 8: Write docs/governance.md

**Files:**
- Create: `docs/governance.md`

- [ ] **Step 1: Write governance doc**

```markdown
# RCS Governance

## Versioning

Each skill has its own SemVer in `frontmatter.version`:

- **MAJOR** (`1.x.x` → `2.0.0`): breaking change — frontmatter `name` change, removed required argument, removed required H2 section, behavior change that would break an existing eval scenario.
- **MINOR** (`x.1.x` → `x.2.0`): new optional argument, new examples, refined wording, additional reference files, new scenario added to evals.
- **PATCH** (`x.x.1` → `x.x.2`): typos, lint fixes, eval rubric clarifications that don't change pass/fail behavior.

Repo-level tags are loose: `v1`, `v1.1`, `v2` mark batch releases that correspond to spec phases. They are NOT SemVer at the repo level.

## Deprecation policy

A skill moves to `status: deprecated` with a 90-day notice in `CHANGELOG.md`. The SKILL.md gets an `## Old patterns` block (per Anthropic best-practices) linking to the replacement. After 90 days, the skill is removed from catalog tables; the directory may remain with a tombstone SKILL.md pointing to the replacement.

## PR review SLAs

- Acknowledge within 7 days
- Initial review within 14 days
- Merge or rejection decision within 30 days

PRs that don't meet the documentation contract or eval thresholds get a checklist of what's missing; the contributor revises.

## No AI attribution — maintainer responsibilities

Per CONTRIBUTING.md, no AI attribution is permitted anywhere in the repo. Maintainers reviewing PRs must:

1. Check commit messages for `Co-Authored-By:` lines crediting AI; ask contributor to amend
2. Check PR description for "generated with" / "AI-assisted" language; ask contributor to remove
3. Check new files for AI-attribution comments

## Code of conduct

Contributors are expected to engage respectfully. Disagreement on technical merit is welcome; ad hominem is not. Maintainers may close issues and PRs that violate this norm without further discussion.
```

- [ ] **Step 2: Commit**

```bash
git add docs/governance.md
git commit -m "Add governance.md: versioning, deprecation, PR SLAs"
```

---

### Task 9: Create lint_frontmatter.py with TDD

**Files:**
- Create: `tools/__init__.py` (empty)
- Create: `tools/tests/__init__.py` (empty)
- Create: `tools/tests/test_lint_frontmatter.py`
- Create: `tools/lint_frontmatter.py`

- [ ] **Step 1: Create empty package init files**

```bash
touch tools/__init__.py tools/tests/__init__.py
```

- [ ] **Step 2: Write failing tests in tools/tests/test_lint_frontmatter.py**

```python
"""Tests for lint_frontmatter.

The linter parses YAML frontmatter from a SKILL.md path and validates
Anthropic-required fields (name, description) plus RCS custom fields
(version, status, track, audience, evidence, last-updated).
"""
import pytest
from pathlib import Path
from tools.lint_frontmatter import lint_frontmatter, LintError


def write_skill_md(tmp_path: Path, frontmatter: str, body: str = "# Title\n\nbody") -> Path:
    """Helper: write a SKILL.md with the given frontmatter and body."""
    p = tmp_path / "SKILL.md"
    p.write_text(f"---\n{frontmatter}\n---\n\n{body}\n")
    return p


def test_valid_frontmatter_passes(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: selecting-statistical-test
description: >
  Walks a decision tree from data characteristics to a recommended test.
  Use when the user has a hypothesis and data and needs to commit to a test.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, stats-student]
evidence: [DU-MSDSAI-4441-Final]
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert errors == []


def test_missing_name_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("name" in e.message for e in errors)


def test_name_over_64_chars_fails(tmp_path):
    long_name = "x" * 65
    p = write_skill_md(tmp_path, frontmatter=f"""\
name: {long_name}
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("64 characters" in e.message for e in errors)


def test_name_with_reserved_word_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: anthropic-helper
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("reserved" in e.message.lower() for e in errors)


def test_name_with_uppercase_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: SelectingTest
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("lowercase" in e.message.lower() for e in errors)


def test_description_over_1024_chars_fails(tmp_path):
    long_desc = "x" * 1025
    p = write_skill_md(tmp_path, frontmatter=f"""\
name: a-skill
description: {long_desc}
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("1024 characters" in e.message for e in errors)


def test_description_first_person_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: a-skill
description: I can help you process spreadsheets.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("third-person" in e.message.lower() for e in errors)


def test_invalid_status_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: a-skill
description: A description.
version: 0.1.0
status: maybe-someday
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("status" in e.message for e in errors)


def test_invalid_track_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: a-skill
description: A description.
version: 0.1.0
status: shipped
track: random-track
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("track" in e.message for e in errors)


def test_missing_version_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: a-skill
description: A description.
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("version" in e.message for e in errors)


def test_no_frontmatter_fails(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("# No frontmatter here\n\nbody\n")
    errors = lint_frontmatter(p)
    assert any("frontmatter" in e.message.lower() for e in errors)
```

- [ ] **Step 3: Run tests and verify they fail (module not implemented yet)**

```bash
uv run pytest tools/tests/test_lint_frontmatter.py -v
```

Expected: ImportError on `tools.lint_frontmatter` (module doesn't exist).

- [ ] **Step 4: Implement tools/lint_frontmatter.py**

```python
"""Lint Anthropic-required + RCS-custom frontmatter fields in a SKILL.md."""
from __future__ import annotations
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click
import yaml


RESERVED_NAME_WORDS = {"anthropic", "claude"}
VALID_STATUSES = {"shipped", "drafting", "planned", "deprecated"}
VALID_TRACKS = {"security", "ml-datasci", "workflow", "teaching", "claude-code-meta"}
FIRST_PERSON_PATTERN = re.compile(
    r"\b(I |I'll |I can |I will |you can |you'll |we |we'll )",
    re.IGNORECASE,
)


@dataclass
class LintError:
    message: str
    line: Optional[int] = None

    def format(self, path: Path) -> str:
        loc = f"{path}:{self.line}" if self.line else str(path)
        return f"{loc}: {self.message}"


def parse_frontmatter(text: str) -> tuple[Optional[dict], list[LintError]]:
    """Extract YAML frontmatter block. Returns (data, errors)."""
    if not text.startswith("---\n"):
        return None, [LintError("file does not start with '---' frontmatter delimiter")]
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, [LintError("frontmatter block not closed (missing trailing '---')")]
    fm_block = text[4:end]
    try:
        data = yaml.safe_load(fm_block)
    except yaml.YAMLError as e:
        return None, [LintError(f"YAML parse error in frontmatter: {e}")]
    if not isinstance(data, dict):
        return None, [LintError("frontmatter must be a YAML mapping")]
    return data, []


def lint_frontmatter(path: Path) -> list[LintError]:
    """Return a list of LintErrors. Empty list = pass."""
    text = path.read_text()
    data, errs = parse_frontmatter(text)
    if data is None:
        return errs
    errors: list[LintError] = []

    # name
    name = data.get("name")
    if not name:
        errors.append(LintError("missing required field 'name'"))
    else:
        if not isinstance(name, str):
            errors.append(LintError("'name' must be a string"))
        else:
            if len(name) > 64:
                errors.append(LintError(f"'name' is {len(name)} chars; must be ≤ 64 characters"))
            if name != name.lower():
                errors.append(LintError("'name' must be lowercase (lowercase-kebab)"))
            if not re.fullmatch(r"[a-z0-9-]+", name):
                errors.append(LintError("'name' must contain only lowercase letters, digits, hyphens"))
            for reserved in RESERVED_NAME_WORDS:
                if reserved in name.lower():
                    errors.append(LintError(f"'name' contains reserved word '{reserved}'"))

    # description
    desc = data.get("description")
    if not desc:
        errors.append(LintError("missing required field 'description'"))
    elif not isinstance(desc, str):
        errors.append(LintError("'description' must be a string"))
    else:
        if len(desc) > 1024:
            errors.append(LintError(f"'description' is {len(desc)} chars; must be ≤ 1024 characters"))
        if FIRST_PERSON_PATTERN.search(desc):
            errors.append(LintError(
                "'description' contains first/second-person language; must be third-person "
                "(write 'Walks a decision tree...', not first or second person)"
            ))

    # version
    version = data.get("version")
    if not version:
        errors.append(LintError("missing required field 'version'"))
    elif not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(LintError(f"'version' must be SemVer (e.g. '0.1.0'); got {version!r}"))

    # status
    status = data.get("status")
    if not status:
        errors.append(LintError("missing required field 'status'"))
    elif status not in VALID_STATUSES:
        errors.append(LintError(
            f"'status' must be one of {sorted(VALID_STATUSES)}; got {status!r}"
        ))

    # track
    track = data.get("track")
    if not track:
        errors.append(LintError("missing required field 'track'"))
    elif track not in VALID_TRACKS:
        errors.append(LintError(
            f"'track' must be one of {sorted(VALID_TRACKS)}; got {track!r}"
        ))

    # audience
    audience = data.get("audience")
    if audience is None:
        errors.append(LintError("missing required field 'audience'"))
    elif not isinstance(audience, list) or not all(isinstance(a, str) for a in audience):
        errors.append(LintError("'audience' must be a list of strings"))

    # evidence
    evidence = data.get("evidence")
    if evidence is None:
        errors.append(LintError("missing required field 'evidence'"))
    elif not isinstance(evidence, list) or not all(isinstance(e, str) for e in evidence):
        errors.append(LintError("'evidence' must be a list of strings"))

    # last-updated
    last_updated = data.get("last-updated")
    if not last_updated:
        errors.append(LintError("missing required field 'last-updated'"))
    elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(last_updated)):
        errors.append(LintError(
            f"'last-updated' must be ISO date YYYY-MM-DD; got {last_updated!r}"
        ))

    return errors


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
def main(paths: tuple[Path, ...]) -> None:
    """Lint frontmatter for one or more SKILL.md files."""
    if not paths:
        click.echo("usage: lint_frontmatter <SKILL.md>...", err=True)
        sys.exit(2)
    total = 0
    for path in paths:
        errors = lint_frontmatter(path)
        for err in errors:
            click.echo(err.format(path), err=True)
            total += 1
    if total:
        click.echo(f"\n{total} frontmatter error(s) across {len(paths)} file(s)", err=True)
        sys.exit(1)
    click.echo(f"OK ({len(paths)} file(s))")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tools/tests/test_lint_frontmatter.py -v
```

Expected: all 11 tests PASS.

- [ ] **Step 6: Smoke-test the CLI on the existing spec markdown**

```bash
uv run python -m tools.lint_frontmatter docs/superpowers/specs/2026-05-22-rcs-public-skills-repo-design.md || true
```

Expected: fails because the spec is not a SKILL.md and has no frontmatter — confirms the linter rejects non-skill content.

- [ ] **Step 7: Commit**

```bash
git add tools/__init__.py tools/tests/__init__.py tools/tests/test_lint_frontmatter.py tools/lint_frontmatter.py
git commit -m "Add lint_frontmatter tool with 11 unit tests covering all validation rules"
```

---

### Task 10: Create lint_skill_md.py with TDD

**Files:**
- Create: `tools/tests/test_lint_skill_md.py`
- Create: `tools/lint_skill_md.py`

- [ ] **Step 1: Write failing tests in tools/tests/test_lint_skill_md.py**

```python
"""Tests for lint_skill_md.

Validates that a SKILL.md body contains the required H2 sections per the
Layer-3 documentation contract: When to use, When NOT to use, Quick start,
Inputs / Arguments / Flags, Workflow, Outputs, Failure modes, References,
Examples, See also, Status & version. Order matters.
"""
from pathlib import Path
from tools.lint_skill_md import lint_skill_md


REQUIRED_SECTIONS = [
    "When to use",
    "When NOT to use",
    "Quick start",
    "Inputs / Arguments / Flags",
    "Workflow",
    "Outputs",
    "Failure modes",
    "References",
    "Examples",
    "See also",
    "Status & version",
]


def make_skill(tmp_path: Path, sections: list[str]) -> Path:
    """Helper: build a minimal SKILL.md with frontmatter and given H2 sections."""
    body = "\n\n".join(f"## {s}\n\ncontent for {s}" for s in sections)
    text = f"""---
name: a-skill
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22
---

# Title

{body}
"""
    p = tmp_path / "SKILL.md"
    p.write_text(text)
    return p


def test_all_required_sections_in_order_passes(tmp_path):
    p = make_skill(tmp_path, REQUIRED_SECTIONS)
    errors = lint_skill_md(p)
    assert errors == []


def test_missing_section_fails(tmp_path):
    p = make_skill(tmp_path, [s for s in REQUIRED_SECTIONS if s != "Failure modes"])
    errors = lint_skill_md(p)
    assert any("Failure modes" in e.message for e in errors)


def test_section_out_of_order_fails(tmp_path):
    out_of_order = REQUIRED_SECTIONS.copy()
    out_of_order[0], out_of_order[2] = out_of_order[2], out_of_order[0]
    p = make_skill(tmp_path, out_of_order)
    errors = lint_skill_md(p)
    assert any("order" in e.message.lower() for e in errors)


def test_body_over_500_lines_fails(tmp_path):
    huge = ["body line"] * 600
    text = f"""---
name: a-skill
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22
---

# Title

""" + "\n".join(huge)
    p = tmp_path / "SKILL.md"
    p.write_text(text)
    errors = lint_skill_md(p)
    assert any("500 lines" in e.message for e in errors)


def test_extra_section_allowed(tmp_path):
    sections = REQUIRED_SECTIONS + ["Bonus section"]
    p = make_skill(tmp_path, sections)
    errors = lint_skill_md(p)
    assert errors == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tools/tests/test_lint_skill_md.py -v
```

Expected: ImportError on `tools.lint_skill_md`.

- [ ] **Step 3: Implement tools/lint_skill_md.py**

```python
"""Lint SKILL.md body for required Layer-3 H2 sections and length cap."""
from __future__ import annotations
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click


REQUIRED_SECTIONS_IN_ORDER = [
    "When to use",
    "When NOT to use",
    "Quick start",
    "Inputs / Arguments / Flags",
    "Workflow",
    "Outputs",
    "Failure modes",
    "References",
    "Examples",
    "See also",
    "Status & version",
]
MAX_BODY_LINES = 500
H2_PATTERN = re.compile(r"^## (.+?)\s*$", re.MULTILINE)


@dataclass
class LintError:
    message: str
    line: Optional[int] = None

    def format(self, path: Path) -> str:
        loc = f"{path}:{self.line}" if self.line else str(path)
        return f"{loc}: {self.message}"


def split_frontmatter_and_body(text: str) -> tuple[str, str]:
    """Return (frontmatter_block, body). Body excludes frontmatter."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end < 0:
        return "", text
    return text[4:end], text[end + 5 :]


def lint_skill_md(path: Path) -> list[LintError]:
    text = path.read_text()
    _, body = split_frontmatter_and_body(text)
    errors: list[LintError] = []

    body_line_count = len(body.splitlines())
    if body_line_count > MAX_BODY_LINES:
        errors.append(LintError(
            f"body is {body_line_count} lines; must be ≤ {MAX_BODY_LINES} lines "
            f"(move long content to reference/ files)"
        ))

    found = H2_PATTERN.findall(body)

    for required in REQUIRED_SECTIONS_IN_ORDER:
        if required not in found:
            errors.append(LintError(f"missing required H2 section: '## {required}'"))

    required_indices = [
        (s, found.index(s)) for s in REQUIRED_SECTIONS_IN_ORDER if s in found
    ]
    for i in range(1, len(required_indices)):
        prev_name, prev_idx = required_indices[i - 1]
        curr_name, curr_idx = required_indices[i]
        if curr_idx < prev_idx:
            errors.append(LintError(
                f"section '## {curr_name}' appears before '## {prev_name}' but "
                f"must appear after it (required order: {REQUIRED_SECTIONS_IN_ORDER})"
            ))
            break

    return errors


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
def main(paths: tuple[Path, ...]) -> None:
    if not paths:
        click.echo("usage: lint_skill_md <SKILL.md>...", err=True)
        sys.exit(2)
    total = 0
    for path in paths:
        errors = lint_skill_md(path)
        for err in errors:
            click.echo(err.format(path), err=True)
            total += 1
    if total:
        click.echo(f"\n{total} SKILL.md body error(s) across {len(paths)} file(s)", err=True)
        sys.exit(1)
    click.echo(f"OK ({len(paths)} file(s))")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tools/tests/test_lint_skill_md.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/tests/test_lint_skill_md.py tools/lint_skill_md.py
git commit -m "Add lint_skill_md tool with 5 unit tests for Layer-3 H2 section contract"
```

---

### Task 11: Create lint_links.py with TDD

**Files:**
- Create: `tools/tests/test_lint_links.py`
- Create: `tools/lint_links.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for lint_links.

Validates that markdown links from SKILL.md to bundled reference files
do not go more than one level deep (per Anthropic best-practices doc:
'Claude may partially read files when they're referenced from other
referenced files').
"""
from pathlib import Path
from tools.lint_links import lint_links


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_skill_with_direct_reference_passes(tmp_path):
    skill = tmp_path / "skills/workflow/example/SKILL.md"
    write_file(skill, "# Skill\n\nSee [reference/topic.md](reference/topic.md).")
    write_file(tmp_path / "skills/workflow/example/reference/topic.md", "# Topic")
    errors = lint_links(skill.parent)
    assert errors == []


def test_skill_with_two_level_deep_reference_fails(tmp_path):
    """SKILL.md links to advanced.md which links to details.md — fails."""
    skill = tmp_path / "skills/workflow/example/SKILL.md"
    write_file(skill, "# Skill\n\nSee [reference/advanced.md](reference/advanced.md).")
    write_file(
        tmp_path / "skills/workflow/example/reference/advanced.md",
        "# Advanced\n\nSee [details.md](details.md) for more.",
    )
    write_file(tmp_path / "skills/workflow/example/reference/details.md", "# Details")
    errors = lint_links(skill.parent)
    assert any("one level deep" in e.message.lower() or "two-level" in e.message.lower() for e in errors)


def test_skill_with_broken_reference_fails(tmp_path):
    skill = tmp_path / "skills/workflow/example/SKILL.md"
    write_file(skill, "# Skill\n\nSee [reference/missing.md](reference/missing.md).")
    errors = lint_links(skill.parent)
    assert any("broken" in e.message.lower() or "not found" in e.message.lower() for e in errors)


def test_external_url_ignored(tmp_path):
    skill = tmp_path / "skills/workflow/example/SKILL.md"
    write_file(skill, "# Skill\n\nSee [Anthropic](https://platform.claude.com/docs/).")
    errors = lint_links(skill.parent)
    assert errors == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tools/tests/test_lint_links.py -v
```

Expected: ImportError on `tools.lint_links`.

- [ ] **Step 3: Implement tools/lint_links.py**

```python
"""Lint that SKILL.md references stay one level deep per Anthropic best-practices."""
from __future__ import annotations
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import click


MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass
class LintError:
    message: str
    line: Optional[int] = None

    def format(self, path: Path) -> str:
        loc = f"{path}:{self.line}" if self.line else str(path)
        return f"{loc}: {self.message}"


def extract_local_links(text: str, base_dir: Path) -> list[tuple[str, Path]]:
    """Return list of (display_text, resolved_path) for non-URL markdown links."""
    out: list[tuple[str, Path]] = []
    for match in MARKDOWN_LINK.finditer(text):
        display, target = match.group(1), match.group(2)
        parsed = urlparse(target)
        if parsed.scheme in ("http", "https", "mailto"):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path:
            continue
        resolved = (base_dir / target_path).resolve()
        out.append((display, resolved))
    return out


def lint_links(skill_dir: Path) -> list[LintError]:
    """Lint a single skill directory (containing SKILL.md and reference/)."""
    errors: list[LintError] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(LintError(f"SKILL.md not found in {skill_dir}"))
        return errors

    skill_links = extract_local_links(skill_md.read_text(), skill_dir)
    level_one_files: set[Path] = set()
    for display, target in skill_links:
        if not target.exists():
            errors.append(LintError(f"broken reference: SKILL.md → {target}", None))
            continue
        if not target.is_relative_to(skill_dir.resolve()):
            errors.append(LintError(
                f"reference escapes skill directory: SKILL.md → {target}"
            ))
            continue
        if target.suffix == ".md":
            level_one_files.add(target)

    for ref_file in level_one_files:
        sub_links = extract_local_links(ref_file.read_text(), ref_file.parent)
        for display, target in sub_links:
            if target.exists() and target.suffix == ".md" and target.is_relative_to(skill_dir.resolve()):
                if target.resolve() in {skill_md.resolve(), ref_file.resolve()}:
                    continue
                errors.append(LintError(
                    f"two-level-deep reference: SKILL.md → {ref_file.name} → {target.name}; "
                    f"links must be one level deep from SKILL.md"
                ))

    return errors


@click.command()
@click.argument("skill_dirs", nargs=-1, type=click.Path(exists=True, file_okay=False, path_type=Path))
def main(skill_dirs: tuple[Path, ...]) -> None:
    if not skill_dirs:
        click.echo("usage: lint_links <skill-directory>...", err=True)
        sys.exit(2)
    total = 0
    for d in skill_dirs:
        errors = lint_links(d)
        for err in errors:
            click.echo(err.format(d), err=True)
            total += 1
    if total:
        click.echo(f"\n{total} link error(s) across {len(skill_dirs)} skill(s)", err=True)
        sys.exit(1)
    click.echo(f"OK ({len(skill_dirs)} skill(s))")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tools/tests/test_lint_links.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/tests/test_lint_links.py tools/lint_links.py
git commit -m "Add lint_links tool enforcing one-level-deep reference rule"
```

---

### Task 12: Create run_evals.py with TDD (mocked Anthropic client)

**Files:**
- Create: `tools/tests/test_run_evals.py`
- Create: `tools/run_evals.py`

- [ ] **Step 1: Write failing tests with mocked Anthropic client**

```python
"""Tests for run_evals.

Verifies the eval harness parses scenario JSONs, dispatches to a mocked
Anthropic client, judges completions with a mocked judge, and applies
pass thresholds per docs/eval-protocol.md.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.run_evals import (
    EvalScenario,
    JudgeResult,
    load_scenarios,
    judge_response,
    check_threshold,
)


def write_scenario(tmp_path: Path, filename: str, payload: dict) -> Path:
    p = tmp_path / filename
    p.write_text(json.dumps(payload))
    return p


def test_load_scenarios_returns_three(tmp_path):
    evals_dir = tmp_path / "evals"
    evals_dir.mkdir()
    for i, kind in enumerate(["happy-path", "edge-case", "anti-trigger"], start=1):
        write_scenario(evals_dir, f"0{i}-{kind}.json", {
            "skill": "a-skill",
            "scenario_id": f"0{i}-{kind}",
            "scenario_kind": kind,
            "query": "test query",
            "files": [],
            "expected_behavior": ["item 1", "item 2", "item 3"],
        })
    scenarios = load_scenarios(evals_dir)
    assert len(scenarios) == 3
    assert {s.scenario_kind for s in scenarios} == {"happy-path", "edge-case", "anti-trigger"}


def test_judge_response_parses_strict_json(tmp_path):
    """judge_response uses a mocked Anthropic client; verifies it parses
    the expected JSON-formatted judge output."""
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=json.dumps({
            "results": [
                {"item": "item 1", "pass": True, "rationale": "yes"},
                {"item": "item 2", "pass": False, "rationale": "no"},
                {"item": "item 3", "pass": True, "rationale": "yes"},
            ]
        }))]
    )
    scenario = EvalScenario(
        skill="a-skill",
        scenario_id="01-happy-path",
        scenario_kind="happy-path",
        query="q",
        files=[],
        expected_behavior=["item 1", "item 2", "item 3"],
    )
    result = judge_response(
        scenario=scenario,
        skill_body="# Skill",
        completion="some response",
        judge_client=mock_client,
    )
    assert isinstance(result, JudgeResult)
    assert result.score == "2/3"


def test_threshold_haiku_happy_path_passes_2_of_3():
    assert check_threshold(model="claude-haiku-4-5-20251001", scenario_kind="happy-path", passed=2, total=3) is True


def test_threshold_haiku_happy_path_fails_1_of_3():
    assert check_threshold(model="claude-haiku-4-5-20251001", scenario_kind="happy-path", passed=1, total=3) is False


def test_threshold_sonnet_happy_path_requires_3_of_3():
    assert check_threshold(model="claude-sonnet-4-6", scenario_kind="happy-path", passed=2, total=3) is False
    assert check_threshold(model="claude-sonnet-4-6", scenario_kind="happy-path", passed=3, total=3) is True


def test_threshold_sonnet_anti_trigger_allows_2_of_3():
    assert check_threshold(model="claude-sonnet-4-6", scenario_kind="anti-trigger", passed=2, total=3) is True


def test_threshold_opus_requires_3_of_3_everywhere():
    for kind in ["happy-path", "edge-case", "anti-trigger"]:
        assert check_threshold(model="claude-opus-4-7", scenario_kind=kind, passed=2, total=3) is False
        assert check_threshold(model="claude-opus-4-7", scenario_kind=kind, passed=3, total=3) is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tools/tests/test_run_evals.py -v
```

Expected: ImportError on `tools.run_evals`.

- [ ] **Step 3: Implement tools/run_evals.py**

```python
"""Eval harness: run scenarios against models, judge completions, apply thresholds."""
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click


TARGET_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-7",
]
JUDGE_MODEL = "claude-sonnet-4-6"

THRESHOLDS: dict[tuple[str, str], int] = {
    ("claude-haiku-4-5-20251001", "happy-path"): 2,
    ("claude-haiku-4-5-20251001", "edge-case"): 2,
    ("claude-haiku-4-5-20251001", "anti-trigger"): 2,
    ("claude-sonnet-4-6", "happy-path"): 3,
    ("claude-sonnet-4-6", "edge-case"): 3,
    ("claude-sonnet-4-6", "anti-trigger"): 2,
    ("claude-opus-4-7", "happy-path"): 3,
    ("claude-opus-4-7", "edge-case"): 3,
    ("claude-opus-4-7", "anti-trigger"): 3,
}

JUDGE_SYSTEM = """You are a strict literal evaluator. Given a skill's SKILL.md, a user query, the candidate model's response, and a list of rubric items, return a JSON object scoring each rubric item.

Each rubric item is scored independently. Partial credit is FALSE. The output MUST be valid JSON matching this schema:

{
  "results": [
    {"item": "<rubric item verbatim>", "pass": true|false, "rationale": "<one sentence>"},
    ...
  ]
}

Do not include any text outside the JSON object."""


@dataclass
class EvalScenario:
    skill: str
    scenario_id: str
    scenario_kind: str
    query: str
    files: list[str]
    expected_behavior: list[str]

    @classmethod
    def from_dict(cls, d: dict) -> "EvalScenario":
        return cls(
            skill=d["skill"],
            scenario_id=d["scenario_id"],
            scenario_kind=d["scenario_kind"],
            query=d["query"],
            files=d.get("files", []),
            expected_behavior=d["expected_behavior"],
        )


@dataclass
class RubricItemResult:
    item: str
    pass_: bool
    rationale: str


@dataclass
class JudgeResult:
    scenario_id: str
    completion: str
    rubric_results: list[RubricItemResult]
    score: str

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.rubric_results if r.pass_)


def load_scenarios(evals_dir: Path) -> list[EvalScenario]:
    scenarios: list[EvalScenario] = []
    for path in sorted(evals_dir.glob("0[1-3]-*.json")):
        data = json.loads(path.read_text())
        scenarios.append(EvalScenario.from_dict(data))
    return scenarios


def judge_response(
    scenario: EvalScenario,
    skill_body: str,
    completion: str,
    judge_client,
) -> JudgeResult:
    rubric_block = "\n".join(f"- {item}" for item in scenario.expected_behavior)
    judge_user = (
        f"SKILL.md body:\n{skill_body}\n\n"
        f"User query: {scenario.query}\n\n"
        f"Candidate model response:\n{completion}\n\n"
        f"Rubric items to score (each independent):\n{rubric_block}"
    )
    resp = judge_client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=2000,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": judge_user}],
    )
    raw = resp.content[0].text
    parsed = json.loads(raw)
    results = [
        RubricItemResult(item=r["item"], pass_=r["pass"], rationale=r["rationale"])
        for r in parsed["results"]
    ]
    passed = sum(1 for r in results if r.pass_)
    return JudgeResult(
        scenario_id=scenario.scenario_id,
        completion=completion,
        rubric_results=results,
        score=f"{passed}/{len(results)}",
    )


def check_threshold(model: str, scenario_kind: str, passed: int, total: int) -> bool:
    if total != 3:
        return False
    required = THRESHOLDS.get((model, scenario_kind))
    if required is None:
        return False
    return passed >= required


def run_skill_evals(skill_dir: Path, anthropic_client) -> dict:
    skill_body = (skill_dir / "SKILL.md").read_text()
    scenarios = load_scenarios(skill_dir / "evals")
    if len(scenarios) != 3:
        raise ValueError(
            f"{skill_dir} has {len(scenarios)} eval scenarios; v1 requires exactly 3"
        )

    summary = {
        "skill_dir": str(skill_dir),
        "run_date": datetime.now(timezone.utc).isoformat(),
        "models": {},
    }

    for model in TARGET_MODELS:
        model_results = []
        all_passed = True
        for scenario in scenarios:
            resp = anthropic_client.messages.create(
                model=model,
                max_tokens=4000,
                system=skill_body,
                messages=[{"role": "user", "content": scenario.query}],
            )
            completion = resp.content[0].text
            judge_result = judge_response(scenario, skill_body, completion, anthropic_client)
            scenario_passed = check_threshold(
                model, scenario.scenario_kind, judge_result.passed_count, len(scenario.expected_behavior)
            )
            if not scenario_passed:
                all_passed = False
            model_results.append({
                "scenario_id": scenario.scenario_id,
                "scenario_kind": scenario.scenario_kind,
                "score": judge_result.score,
                "passed_threshold": scenario_passed,
                "rubric_results": [asdict(r) for r in judge_result.rubric_results],
            })
        summary["models"][model] = {
            "all_passed": all_passed,
            "scenarios": model_results,
        }

    return summary


@click.command()
@click.argument("skill_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def main(skill_dir: Path) -> None:
    """Run evals for one skill directory across all 3 target models."""
    try:
        from anthropic import Anthropic
    except ImportError:
        click.echo("anthropic SDK not installed; run 'uv sync'", err=True)
        sys.exit(2)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        click.echo("ANTHROPIC_API_KEY not set; exporting required for eval runs", err=True)
        sys.exit(2)
    client = Anthropic()
    summary = run_skill_evals(skill_dir, client)
    run_date = summary["run_date"][:10]
    for model, model_summary in summary["models"].items():
        out = skill_dir / "evals" / f"results-{model}-{run_date}.json"
        out.write_text(json.dumps(model_summary, indent=2))
    overall_passed = all(m["all_passed"] for m in summary["models"].values())
    for model, m in summary["models"].items():
        status = "PASS" if m["all_passed"] else "FAIL"
        click.echo(f"  {model}: {status}")
    if not overall_passed:
        click.echo("\nOne or more models failed pass thresholds.", err=True)
        sys.exit(1)
    click.echo("\nAll thresholds met.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tools/tests/test_run_evals.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/tests/test_run_evals.py tools/run_evals.py
git commit -m "Add run_evals harness with 7 unit tests for loading, judging, thresholds"
```

---

### Task 13: Write .github/workflows/frontmatter-lint.yml

**Files:**
- Create: `.github/workflows/frontmatter-lint.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: Frontmatter and SKILL.md lint

on:
  pull_request:
    paths:
      - 'skills/**/SKILL.md'
      - 'tools/lint_frontmatter.py'
      - 'tools/lint_skill_md.py'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Sync dependencies
        run: uv sync
      - name: Find changed SKILL.md files
        id: skills
        run: |
          changed=$(git diff --name-only origin/${{ github.base_ref }}...HEAD -- 'skills/**/SKILL.md' || true)
          if [ -z "$changed" ]; then
            echo "No SKILL.md changes; running on all SKILL.md files instead."
            changed=$(find skills -name SKILL.md)
          fi
          echo "files<<EOF" >> $GITHUB_OUTPUT
          echo "$changed" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      - name: Lint frontmatter
        run: |
          echo "${{ steps.skills.outputs.files }}" | xargs uv run python -m tools.lint_frontmatter
      - name: Lint SKILL.md body
        run: |
          echo "${{ steps.skills.outputs.files }}" | xargs uv run python -m tools.lint_skill_md
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/frontmatter-lint.yml
git commit -m "Add frontmatter-lint workflow"
```

---

### Task 14: Write .github/workflows/link-check.yml

**Files:**
- Create: `.github/workflows/link-check.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: Skill link integrity check

on:
  pull_request:
    paths:
      - 'skills/**'
      - 'tools/lint_links.py'

jobs:
  links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Sync dependencies
        run: uv sync
      - name: Find changed skill directories
        id: dirs
        run: |
          changed_dirs=$(git diff --name-only origin/${{ github.base_ref }}...HEAD -- 'skills/**' \
            | awk -F/ '{ if (NF >= 3) print $1"/"$2"/"$3 }' | sort -u || true)
          if [ -z "$changed_dirs" ]; then
            changed_dirs=$(find skills -mindepth 2 -maxdepth 2 -type d)
          fi
          echo "dirs<<EOF" >> $GITHUB_OUTPUT
          echo "$changed_dirs" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      - name: Lint links
        run: |
          while read -r dir; do
            [ -z "$dir" ] && continue
            [ -f "$dir/SKILL.md" ] || continue
            uv run python -m tools.lint_links "$dir"
          done <<< "${{ steps.dirs.outputs.dirs }}"
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/link-check.yml
git commit -m "Add link-check workflow"
```

---

### Task 15: Write .github/workflows/eval-suite.yml

**Files:**
- Create: `.github/workflows/eval-suite.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: Skill eval suite

on:
  pull_request:
    paths:
      - 'skills/**'
  schedule:
    - cron: '0 6 * * *'

jobs:
  evals:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - name: Fail if API key missing (main repo only)
        if: github.repository == 'rockcyber/rcs' && env.ANTHROPIC_API_KEY == ''
        run: |
          echo "::error::ANTHROPIC_API_KEY secret not set in main repo"
          exit 1
      - name: Skip if API key missing (forks)
        if: github.repository != 'rockcyber/rcs' && env.ANTHROPIC_API_KEY == ''
        run: |
          echo "::warning::ANTHROPIC_API_KEY not set in fork; skipping eval suite"
          exit 0
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Sync dependencies
        run: uv sync
      - name: Determine target skills
        id: targets
        run: |
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            changed_dirs=$(git diff --name-only origin/${{ github.base_ref }}...HEAD -- 'skills/**' \
              | awk -F/ '{ if (NF >= 3) print $1"/"$2"/"$3 }' | sort -u || true)
          else
            changed_dirs=$(find skills -mindepth 2 -maxdepth 2 -type d)
          fi
          echo "dirs<<EOF" >> $GITHUB_OUTPUT
          echo "$changed_dirs" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      - name: Run eval suite
        run: |
          failed=0
          while read -r dir; do
            [ -z "$dir" ] && continue
            [ -f "$dir/SKILL.md" ] || continue
            [ -d "$dir/evals" ] || continue
            echo "::group::$dir"
            uv run python -m tools.run_evals "$dir" || failed=1
            echo "::endgroup::"
          done <<< "${{ steps.targets.outputs.dirs }}"
          exit $failed
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/eval-suite.yml
git commit -m "Add eval-suite workflow (PR and nightly, with fork skip-and-warn)"
```

---

### Task 16: Write skills/README.md (cross-track index)

**Files:**
- Create: `skills/README.md`

- [ ] **Step 1: Write the cross-track skill index**

```markdown
# RCS Skills — Cross-Track Index

All RCS skills, organized first by audience track and then by ROI rank (Σ score from the v1 brainstorm).

## By track

- **[security/](security/)** — Security engineers, AI red-teamers, GRC, vuln triage, MCP pre-trust, pen-test discipline.
- **[ml-datasci/](ml-datasci/)** — Data scientists, ML engineers, stats students, applied ML.
- **[workflow/](workflow/)** — Cross-cutting hygiene and research discipline for both audiences.
- **[teaching/](teaching/)** — Pedagogy patterns, rubrics, pset walkthroughs (no v1 skills; structure pre-allocated).
- **[claude-code-meta/](claude-code-meta/)** — Skill / plugin / hook / MCP / rule authoring meta.

## Status legend

- ✅ **shipped** — body + 3 passing evals + Layer-3 H2 sections; auto-invocable
- 🔨 **drafting** — visible to readers but not yet eval-validated; not auto-invocable
- 📝 **planned** — listed only; no directory yet

See `docs/conventions.md` for full status semantics.
```

- [ ] **Step 2: Commit**

```bash
git add skills/README.md
git commit -m "Add skills/README.md cross-track index"
```

---

### Task 17: Write skills/security/README.md with planned-skills table

**Files:**
- Create: `skills/security/README.md`

- [ ] **Step 1: Write the security track README**

```markdown
# Security Track

For security engineers, AI red-teamers, CISOs, GRC engineers, and AI security researchers.

This track encodes day-job disciplines: MCP pre-trust auditing, vulnerability triage, threat modeling (methodology-only — bring your own catalog), pen-test scaffolding, supply-chain hygiene, and adversarial-ML eval harnesses.

## Shipped skills

_Populated in Phase 1._

| Skill | What it does | When to use | Σ |
|---|---|---|---|

## Planned skills

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-mcp-server-pre-trust` | Six-check audit (license, source, network egress, version pin, secret handling, tool subset) before registering an MCP server | 18 | 📝 planned (Phase 1) |
| `auditing-pinned-dependencies` | Greps for unpinned installs, flags supply-chain risk | 19 | 📝 planned (Phase 2) |
| `threat-modeling-llm-app` | Walks an LLM app through STRIDE-style threats; user supplies the checklist as input | 13 | 📝 planned |
| `threat-modeling-agentic-systems` | MAESTRO/STRIDE walk for an agent design; user supplies the catalog | 11 | 📝 planned |
| `triaging-vulnerability-findings` | SARIF processing: dedupe → EPSS-enrich → blast-radius → suppress with pragma | 14 | 📝 planned |
| `applying-secure-coding-rules` | Surfaces secure-coding rules per language + framework + AI/ML stack | 15 | 📝 planned |
| `scaffolding-CTF-engagement` | Engagement scope, rules of engagement, finding template, severity rubric | 10 | 📝 planned |
| `writing-pentest-finding` | CVSS scoring walk, repro steps, remediation pattern | 11 | 📝 planned |
| `running-cloud-IR-runbook` | Triage → evidence collection → comms → lessons-learned | 10 | 📝 planned |
| `writing-vdp-and-coordinated-disclosure` | Vulnerability disclosure policy template + coordinated-disclosure timeline | 12 | 📝 planned |
| `scaffolding-security-research-repo` | SECURITY.md, threat-model.md template, gitleaks/semgrep pre-commit, VDP, license | 13 | 📝 planned |
| `generating-sbom` | CycloneDX/SPDX SBOM from any stack | 12 | 📝 planned |
| `auditing-transitive-vulnerabilities` | Dependency graph walk, EPSS scoring | 13 | 📝 planned |
| `verifying-sigstore-signatures` | Cosign verification, in-toto policy check | 10 | 📝 planned |
| `scaffolding-red-team-engagement` | RoE, scope, kill-switch, logging template for AI red-team | 12 | 📝 planned |
| `running-prompt-injection-eval` | Generic harness; corpus is user-supplied | 13 | 📝 planned |
| `running-multiturn-attack-suite` | Multi-turn prompt-injection eval harness | 12 | 📝 planned |
| `running-encoded-payload-suite` | Base64 / ROT13 / unicode / zero-width payload harness | 12 | 📝 planned |
| `evaluating-jailbreak-judge-agreement` | Cohen's κ between LLM judges on jailbreak outcomes | 13 | 📝 planned |
| `running-adversarial-perturbation-suite` | FGSM / PGD / AutoAttack for vision/tabular | 8 | 📝 planned |
| `auditing-rlhf-reward-hacking` | Reward-model probing for goodharting | 7 | 📝 planned |
| `scrubbing-PII-with-policy` | PII detection + redaction with user-supplied policy | 12 | 📝 planned |
| `verifying-training-data-erasure` | DSR-proof workflow for AI: dataset → embeddings → fine-tune | 10 | 📝 planned |
| `interpreting-vendor-questionnaire-skeptically` | Skeptical pass over vendor security questionnaires | 9 | 📝 planned |
| `scaffolding-ai-policy-doc` | AI use policy template | 10 | 📝 planned |

## Cross-track references

- Most security work pairs with `workflow/` for cross-cutting hygiene (seed, dedup, reproducibility).
- For Claude Code skill / MCP / hook authoring, see `claude-code-meta/`.

## Track-specific conventions

- Security skills MUST disclaim that they are tooling, not professional advice (per repo-wide disclaimer in root README; restate per skill).
- Skills that touch credentials, secrets, or supply-chain artifacts MUST document the exact files they read and write in the `## Outputs` section.
```

- [ ] **Step 2: Commit**

```bash
git add skills/security/README.md
git commit -m "Add security track README with planned-skills table"
```

---

### Task 18: Write skills/ml-datasci/README.md

**Files:**
- Create: `skills/ml-datasci/README.md`

- [ ] **Step 1: Write the ml-datasci track README**

```markdown
# ML / Data Science Track

For data scientists, ML engineers, applied-ML practitioners, and stats students.

This track encodes disciplines that recur across model-building work: statistical-test selection from data characteristics, classifier and regression evaluation, calibration, leakage firewalls, baseline-model discipline, regression diagnostics, fine-tuning audits, and RAG retrieval evaluation.

## Shipped skills

_Populated in Phase 2._

| Skill | What it does | When to use | Σ |
|---|---|---|---|

## Planned skills

### Statistical / mathematical reasoning

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `selecting-statistical-test` | Decision tree from data characteristics → recommends t / Welch / Wilcoxon / Mann-Whitney / Sign / paired-t / Fisher / χ², names the gating assumption | 18 | 📝 planned (Phase 3) |
| `checking-test-assumptions` | Shapiro / Levene / QQ / residual diagnostics → pass/fail per assumption with evidence | 18 | 📝 planned (Phase 3) |
| `reporting-effect-sizes` | Cohen's d / Cliff's δ / R² + 95% CI + direction; refuses bare p-value | 19 | 📝 planned (Phase 2) |
| `interpreting-conflicting-tests` | Assumption-status table to commit to a winner when t / Wilcoxon disagree | 16 | 📝 planned |
| `analyzing-regression-diagnostics` | Linearity / residual normality / homoscedasticity / leverage / Cook's D | 14 | 📝 planned |
| `running-power-analysis` | Sample-size + MDE + effect-size sanity check before running the study | 13 | 📝 planned |
| `running-bayesian-workflow` | Priors → posterior-predictive → R-hat/ESS → divergence check | 10 | 📝 planned |
| `building-conformal-prediction-set` | Split-conformal calibration, coverage check | 11 | 📝 planned |
| `analyzing-causal-DAG` | Confounder checklist, do-calculus walk | 9 | 📝 planned |

### ML / DL hygiene

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-train-test-split` | Leakage detection, stratification check, group-aware verification, temporal split for time series | 18 | 📝 planned (Phase 3) |
| `building-baseline-models` | Dummy / LogReg / RF before fancy model | 17 | 📝 planned (Phase 4) |
| `evaluating-binary-classifiers` | ROC + PR + calibration + CM + threshold sweep + class-imbalance + bootstrap CI from (y_true, y_proba) | 19 | 📝 planned (Phase 4) |
| `evaluating-regression-models` | RMSE / MAE / R² / residual plots + cross-validation | 17 | 📝 planned (Phase 4) |
| `evaluating-multiclass-classifiers` | Macro/micro F1, per-class PR, confusion matrix, top-k | 16 | 📝 planned |
| `tuning-classification-threshold` | Domain-aware threshold sweep (FN-cost » FP-cost in security) | 16 | 📝 planned |
| `running-chollet-ratio-check` | Samples-to-mean-seq-length → BoW vs LSTM vs Transformer recommendation | 16 | 📝 planned |
| `enforcing-leakage-firewall` | LOFO / hub-firewall / group-leakage check | 14 | 📝 planned |
| `comparing-models-fairly` | McNemar / paired-folds tests | 14 | 📝 planned |
| `auditing-deep-learning-overfit` | Train/val gap, learning curves, weight-norm growth | 12 | 📝 planned |
| `writing-model-cards` | AIBOM-compatible model card from fitted model + eval results | 13 | 📝 planned |
| `generating-shap-explanations` | SHAP / LIME / IG / permutation-importance scaffolding | 11 | 📝 planned |
| `auditing-model-fairness` | Eq-opp / dem-parity / calibration-within-group + intersectional | 12 | 📝 planned |

### RAG / fine-tuning / MLOps

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `evaluating-rag-retrieval` | recall@k / MRR / nDCG / faithfulness / answer-relevance | 14 | 📝 planned |
| `auditing-chunking-strategy` | Chunk-size + overlap + boundary-aware splits | 13 | 📝 planned |
| `auditing-embedding-drift` | KL/cosine drift between embedding distributions over time | 11 | 📝 planned |
| `building-rag-eval-set` | Golden Q/A + held-out + adversarial set | 12 | 📝 planned |
| `selecting-embedding-model` | Intrinsic vs extrinsic comparison | 13 | 📝 planned |
| `evaluating-OOD-detection` | Mahalanobis / energy / max-softmax-prob | 9 | 📝 planned |
| `auditing-sft-dataset` | PII / dup / leakage / format / chat-template | 11 | 📝 planned |
| `running-eval-before-after-finetune` | Paired McNemar / regression on perplexity | 12 | 📝 planned |
| `writing-finetune-spec-sheet` | Base model + data + recipe + eval | 10 | 📝 planned |
| `scaffolding-pytorch-training-loop` | Seed / AMP / grad-clip / lr-sched / early-stop / resume | 12 | 📝 planned |
| `running-hyperparameter-sweep` | Seed-stratified optuna/ray-tune | 12 | 📝 planned |
| `packaging-model-for-deployment` | Signature + schema + smoke test | 12 | 📝 planned |
| `building-canary-rollout` | Traffic-split policy + rollback | 9 | 📝 planned |
| `monitoring-data-drift` | PSI / KL / KS per feature | 11 | 📝 planned |
| `monitoring-prediction-drift` | Calibration-over-time, score-distribution shift | 11 | 📝 planned |
| `auditing-inference-latency-budget` | P50/P95/P99 budget vs SLO | 10 | 📝 planned |
| `building-rollback-plan` | Versioned rollback + smoke tests | 10 | 📝 planned |

### Synthetic data + privacy

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-synthetic-data-utility` | Downstream-task fidelity | 11 | 📝 planned |
| `auditing-synthetic-data-leakage` | Membership-inference | 10 | 📝 planned |
| `applying-differential-privacy` | ε/δ budget tracking | 8 | 📝 planned |
| `building-data-dictionary-with-consent-class` | Per-field consent class for DSR readiness | 11 | 📝 planned |
| `generating-data-dictionary` | Per-field type / range / null / semantic class | 15 | 📝 planned |

### Performance / cost (LLM apps)

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `profiling-llm-cost` | Per-call token cost rollup | 14 | 📝 planned |
| `auditing-prompt-token-budget` | Detect prompt bloat | 16 | 📝 planned |
| `recommending-model-tier` | Haiku / Sonnet / Opus selection per task | 14 | 📝 planned |

### Scaffolding

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `scaffolding-ml-research-notebook` | uv/poetry + src/ + data/raw immutable + tests/ + claudedocs/ + seed util + pre-commit | 15 | 📝 planned |
| `scaffolding-grad-school-pset` | Jupyter/RMarkdown template with stats discipline baked in | 12 | 📝 planned |
| `scaffolding-llm-eval-harness` | model_id + dataset_hash + prompt_version + judge_model + results.jsonl | 14 | 📝 planned |

## Cross-track references

- For seed hygiene, train/test split discipline, and reproducibility, see `workflow/`.
- For research discipline (premortems, pre-registration), see `workflow/`.
- For teaching variations of these skills (rubrics, walkthroughs), see `teaching/` (planned).
```

- [ ] **Step 2: Commit**

```bash
git add skills/ml-datasci/README.md
git commit -m "Add ml-datasci track README with planned-skills table"
```

---

### Task 19: Write skills/workflow/README.md

**Files:**
- Create: `skills/workflow/README.md`

- [ ] **Step 1: Write the workflow track README**

```markdown
# Workflow Track

Cross-cutting research and engineering hygiene. Applies to both security and ml-datasci audiences.

## Shipped skills

_Populated in Phase 1._

| Skill | What it does | When to use | Σ |
|---|---|---|---|

## Planned skills

### Notebook + reproducibility

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `enforcing-seed-hygiene` | First-cell gate + CI check: every notebook starts with explicit seed call | 20 | 📝 planned (Phase 2) |
| `pinning-reproducible-environments` | uv lock / devcontainer / version-pin enforcement | 17 | 📝 planned (Phase 5) |
| `auditing-data-quality` | Nulls / ranges / types / semantic class | 17 | 📝 planned (Phase 5) |
| `auditing-notebook-narrative` | Diff rendered figures against in-narrative claims | 13 | 📝 planned |
| `building-deterministic-data-pipelines` | LF endings, sorted JSON keys, content-hash snapshots, provenance.json | 15 | 📝 planned |
| `auditing-jupyter-execution-order` | Cells-out-of-order detection | 16 | 📝 planned |

### Data engineering

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `deduplicating-records` | Multi-key dedup with index-refresh after merge, transitive collapse, ID-format normalization | 18 | 📝 planned (Phase 5) |
| `validating-temporal-fields` | Reject future dates, repair year-fallback, separate event-date from disclosure-date | 19 | 📝 planned (Phase 2) |
| `validating-schema-evolution` | Schema-diff + breaking-change classification | 13 | 📝 planned |
| `auditing-source-provenance` | provenance.json: source repo + commit SHA + pull date + adapter version | 16 | 📝 planned |

### Research discipline

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `running-adversarial-premortem` | Multi-subagent premortem: location + concern + strongest-counter + stops-mattering-if | 17 | 📝 planned (Phase 1 — migrate from harness) |
| `pre-registering-eval-study` | Lock + hypothesis + stopping rules + falsification criteria | 16 | 📝 planned |
| `writing-successor-primers` | "If you have to pick this up cold" template | 15 | 📝 planned |
| `writing-release-notes-as-postmortem` | Regression → root cause → test added to prevent recurrence | 15 | 📝 planned |
| `auditing-mathematical-claims` | Per-claim: location, concern, strongest-counter, stops-mattering-if (ATACE math-flags template) | 13 | 📝 planned |

### Context discipline

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-context-window-pressure` | CLAUDE.md hierarchy under 400 lines, cache-warm hygiene, drift detection | 17 | 📝 planned (Phase 6) |

## Cross-track references

- Pairs with everything. If you're shipping a skill in `security/` or `ml-datasci/`, you almost certainly want one of these too.
- For Claude Code authoring discipline (skill / plugin / hook), see `claude-code-meta/`.
```

- [ ] **Step 2: Commit**

```bash
git add skills/workflow/README.md
git commit -m "Add workflow track README with planned-skills table"
```

---

### Task 20: Write skills/teaching/README.md

**Files:**
- Create: `skills/teaching/README.md`

- [ ] **Step 1: Write the teaching track README**

```markdown
# Teaching Track

For instructors, TAs, course-prep workflows. Pedagogy patterns and grading discipline.

This track ships **no skills in v1**. The structure is pre-allocated; v2+ will populate it.

## Shipped skills

_None in v1._

## Planned skills

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `explaining-statistical-concept` | Socratic, audience-tier (high-school / undergrad / grad / practitioner) | 9 | 📝 planned |
| `writing-graded-rubric` | Criterion-referenced rubric with proficiency bands | 7 | 📝 planned |
| `writing-pset-walkthrough` | "What it's asking / Why this works / What the result tells us / Gotcha" template | 11 | 📝 planned |
| `diffing-instructor-vs-student-solution` | Side-by-side diff with feedback on common errors | 11 | 📝 planned |
| `writing-onboarding-guide` | Multi-audience onboarding (engineer / scientist / executive) | 12 | 📝 planned |

## Cross-track references

- Most teaching skills wrap a corresponding `ml-datasci/` or `workflow/` skill — e.g., `explaining-statistical-concept` for `selecting-statistical-test`. Build the wrapped skill first.
```

- [ ] **Step 2: Commit**

```bash
git add skills/teaching/README.md
git commit -m "Add teaching track README (no v1 skills; structure pre-allocated)"
```

---

### Task 21: Write skills/claude-code-meta/README.md

**Files:**
- Create: `skills/claude-code-meta/README.md`

- [ ] **Step 1: Write the claude-code-meta track README**

```markdown
# Claude Code Meta Track

For Claude Code skill / plugin / hook / MCP / rule authors. Meta-skills that encode how to build the kinds of things this repo itself ships.

## Shipped skills

_Populated in Phase 6._

| Skill | What it does | When to use | Σ |
|---|---|---|---|

## Planned skills

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `writing-claude-code-skill` | Walks the Anthropic best-practices checklist; eval-first workflow; Layer-3 H2 contract | 18 | 📝 planned (Phase 6) |
| `auditing-claude-md-hierarchy` | Size check (≤ 400 lines), cache hygiene (no timestamps), drift detection | 18 | 📝 planned (Phase 6) |
| `writing-claude-code-plugin` | marketplace.json + commands + agents + hooks + lifecycle | 11 | 📝 planned |
| `writing-mcp-server-securely` | Six-check audit baked into the authoring workflow | 14 | 📝 planned |
| `writing-claude-code-hook` | PreToolUse / PostToolUse / Stop / SessionStart patterns with security review | 12 | 📝 planned |
| `writing-deny-allow-rules` | `.claude/rules/*.md` allow/deny rule authoring with glob path matching | 13 | 📝 planned |
| `writing-decision-trees-as-skills` | Meta: convert "given data shape X, do Y" expertise into a deterministic walk | 13 | 📝 planned |
| `running-eval-driven-skill-development` | Per Anthropic best-practices: write 3 evals BEFORE the SKILL.md body | 13 | 📝 planned |

## Cross-track references

- Skill-authoring discipline pairs with `workflow/auditing-context-window-pressure` (cache hygiene) and `workflow/running-adversarial-premortem` (premortem your skill before shipping).
- For security-critical skills (MCP servers, hooks that wield permissions), see `security/auditing-mcp-server-pre-trust`.
```

- [ ] **Step 2: Commit**

```bash
git add skills/claude-code-meta/README.md
git commit -m "Add claude-code-meta track README with planned-skills table"
```

---

# Phase 1 — Free-Ship Migrations (Tasks 22–33)

### Task 22: Extract adversarial-premortem ZIP content and inspect

**Files:**
- Read: `/Users/klambros/.claude/skills/adversarial-premortem.skill`
- Create: `/tmp/adversarial-premortem-extracted/` (scratch)

- [ ] **Step 1: Inspect the .skill file (it's a ZIP)**

```bash
file /Users/klambros/.claude/skills/adversarial-premortem.skill
```

Expected: identifies as Zip archive data.

- [ ] **Step 2: Extract to scratch directory**

```bash
mkdir -p /tmp/adversarial-premortem-extracted
cd /tmp/adversarial-premortem-extracted && unzip -o /Users/klambros/.claude/skills/adversarial-premortem.skill
```

Expected: extracts `adversarial-premortem/SKILL.md`.

- [ ] **Step 3: Read the extracted SKILL.md**

```bash
cat /tmp/adversarial-premortem-extracted/adversarial-premortem/SKILL.md | head -100
```

Capture the existing structure: frontmatter, main body, any subdirectories. This is the source content for migration.

- [ ] **Step 4: Note the gaps against Layer-3 contract**

Compare existing sections against required H2 list (When to use / When NOT / Quick start / Inputs / Workflow / Outputs / Failure modes / References / Examples / See also / Status & version). Note which sections need to be authored anew (likely most of them — original was harness-internal).

This step is inspection only; no file changes yet.

---

### Task 23: Author skills/workflow/running-adversarial-premortem/SKILL.md

**Files:**
- Create: `skills/workflow/running-adversarial-premortem/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/workflow/running-adversarial-premortem/evals
```

- [ ] **Step 2: Write SKILL.md with frontmatter and all 11 required H2 sections**

```markdown
---
name: running-adversarial-premortem
description: >
  Runs a structured multi-round adversarial premortem on a spec, plan, design, paper,
  proof, or codebase. Assumes the artifact has already failed six months out, works
  backward to identify causes, scores each surviving failure mode with a calibrated
  confidence band, and emits a prioritized remediation plan. Use when the cost of
  being wrong is high — AI security designs, ML system architecture, mathematical
  proofs, agentic-system designs, or any high-stakes plan where surfacing failure
  modes you would otherwise miss is the goal.
version: 0.1.0
status: shipped
track: workflow
audience: [security-eng, ai-security, ml-engineer, data-scientist, skill-author]
evidence:
  - ATACE
  - incident-rank-validation
  - TRACT
last-updated: 2026-05-22
---

# Running an Adversarial Premortem

## When to use

Trigger this skill when the user asks for or implies one of:

- A premortem, devil's-advocate review, or red-team pass on a spec, plan, design, paper, proof, or codebase
- A check on a mathematical or empirical claim where the cost of being wrong is high (research papers, regulatory submissions, safety arguments)
- A failure-mode analysis for an AI / ML / agentic / MLOps / security-sensitive design
- Phrases like "what would go wrong with...", "stress-test this plan", "what am I missing?", "argue against this"

## When NOT to use

Skip this skill and hand off to a different one when:

- The user wants a simple code review for bugs → use a debugging or code-review pattern
- The user wants a brainstorm for new ideas → use brainstorming (this skill is the inverse: it assumes the idea exists and stress-tests it)
- The artifact has not been written yet → run brainstorming or planning first, then return for premortem
- The artifact is a small bug fix or one-line change where premortem overhead exceeds blast radius

## Quick start

User says: "I just finished my paper claiming that all transformer attention heads are equivalent for short sequences. Can you premortem the math claims?"

Skill response: structured premortem report covering (1) the strongest counter-argument to the main claim, (2) per-claim audit table with location + concern + strongest-counter + stops-mattering-if, (3) prioritized remediation list, (4) confidence bands.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| artifact | file path or pasted text | yes | — | The spec, paper, plan, code, or proof to premortem. |
| scope_hint | string | no | "full artifact" | Narrow the premortem to a section, claim, or component if the artifact is too large to cover in one pass. |
| confidence_format | "calibrated" \| "binary" \| "qualitative" | no | "calibrated" | Output format for confidence per failure mode. |
| stop_after_rounds | integer | no | 3 | Cap on premortem rounds (each round may surface new failure modes; diminishing returns past 3). |

## Workflow

Copy this checklist into the response and check off items as the premortem progresses:

```
Premortem progress:
- [ ] Round 1: Assume failure → enumerate top-level failure modes
- [ ] Round 2: For each failure mode, work backward to root causes
- [ ] Round 3: Score each surviving failure mode (severity × likelihood × detectability)
- [ ] For each high-priority failure mode, write: location · concern · strongest-counter · stops-mattering-if
- [ ] Prioritized remediation plan
```

### Round 1: Assume failure

The artifact has already failed six months from now. Independently of the artifact's claims, ask: what is the most likely way this failed?

Generate 5–10 top-level failure modes. Categories to seed (use as appropriate):

- **Premise failure** — the claim is wrong; the data don't support it; the proof is flawed
- **Methodology failure** — the experimental design is wrong; the eval is biased; the dedupe is broken
- **Implementation failure** — code does not match design; off-by-one; race condition; memory leak
- **Operational failure** — the system is deployed wrong; monitoring is missing; rollback is impossible
- **Reception failure** — the audience misinterprets the result; the title oversells; the limitations are buried
- **Defense-in-depth-creates-false-confidence failure** — multiple layers of "safety" mask the actual brittle component

### Round 2: Backward chain to root cause

For each top-level failure mode, ask "why did this fail?" and write the strongest version of the answer. Repeat 3–5 times to reach a root cause.

### Round 3: Score and triage

For each surviving failure mode, produce:

```
Failure mode: <short name>
Location: <file:line / section / claim>
Concern: <one paragraph; the strongest version of the worry>
Strongest counter: <the most generous defense of the artifact>
Stops mattering if: <falsifiable stopping condition — what would have to be true to stop worrying>
Severity: 1–5 (1 = mildly embarrassing; 5 = retraction / safety incident)
Likelihood: 1–5 (calibrated)
Detectability: 1–5 (1 = invisible until a postmortem; 5 = caught by existing CI)
Priority = Severity × Likelihood / Detectability
```

### Remediation

Sort by priority descending. For the top half:

- Specific fix proposal
- What the fix costs (effort, schedule, scope reduction)
- What the fix does NOT solve

## Outputs

A markdown report with the following structure:

1. **Executive summary** (3 sentences max): the single highest-priority concern and recommended next step
2. **Per-claim audit table** (one row per failure mode): Location · Concern · Strongest counter · Stops mattering if · Severity · Likelihood · Detectability · Priority
3. **Prioritized remediation list** (top-half failure modes only)
4. **Calibrated confidence**: the premortem itself has limitations; state them

## Failure modes

Known pitfalls in running premortems and how this skill catches them:

- **Premortem theater** — going through the motions without genuine adversarial engagement. Caught by: requiring the "strongest counter" field (forces engagement with the artifact's defense).
- **Defense-in-depth false confidence** — listing many low-priority concerns masks one high-priority one. Caught by: explicit prioritization formula + remediation list limited to top-half.
- **Stops-mattering-if omission** — concerns that have no falsifiable stop condition are worry, not analysis. Caught by: required "stops mattering if" field per failure mode.
- **Scope overflow** — running premortem on a 10K-line spec produces noise. Caught by: `scope_hint` argument + Round 1 categorical seeding.

## References

- `reference/premortem-template.md` — the per-claim table template
- `reference/seed-failure-categories.md` — expanded category descriptions
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — for workflow-checklist pattern
- [Klein 2007 *Performing a Project Premortem*, Harvard Business Review](https://hbr.org/2007/09/performing-a-project-premortem) — origin of the premortem method

## Examples

### Example 1: Mathematical paper premortem (happy-path)

Input: "I just finished my paper claiming that all transformer attention heads are equivalent for short sequences. Can you premortem the math claims?"

Output: Skill produces a per-claim audit table — Theorem 1 (claim "equivalent" under specific norm; counter: "equivalent" is used loosely on a 6-element finite set, true isomorphism would require demonstrating bijection of operations not just sets), Theorem 2 (polynomial bound vs claimed exponential), Lemma 1 (dilution vs steering conflation). Emits stops-mattering-if conditions per claim.

### Example 2: Anti-trigger (simple bug review)

Input: "Just review my code for off-by-one errors in this loop."

Output: Skill refuses to engage premortem. Explains that premortem is for high-stakes designs with multiple plausible failure modes; for a single-bug code review, debugging or code-review patterns are the right tool. Hands off.

## See also

- `workflow/pre-registering-eval-study` — the prospective version of this skill
- `workflow/auditing-mathematical-claims` — narrower variant focused on proof claims
- `workflow/writing-successor-primers` — pairs well after premortem identifies areas a successor needs to know

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-22
- Provenance: migrated from `~/.claude/skills/adversarial-premortem.skill` (zip-encoded); reformatted to Layer-3 contract
```

- [ ] **Step 3: Create the two reference files mentioned in `## References`**

Write `skills/workflow/running-adversarial-premortem/reference/premortem-template.md`:

```markdown
# Premortem per-claim audit template

| Field | Value |
|---|---|
| Failure mode | <short name> |
| Location | <file:line / section / claim> |
| Concern | <one paragraph; strongest version of the worry> |
| Strongest counter | <most generous defense of the artifact> |
| Stops mattering if | <falsifiable stopping condition> |
| Severity (1–5) | |
| Likelihood (1–5) | |
| Detectability (1–5) | |
| Priority | Severity × Likelihood / Detectability |
```

Write `skills/workflow/running-adversarial-premortem/reference/seed-failure-categories.md`:

```markdown
# Seed failure categories

Use these as starting points for Round 1. Skip any that obviously do not apply.

## Premise failure

The claim is wrong; the data don't support it; the proof is flawed. Examples: regression coefficient is significant but wrong direction; classifier accuracy was inflated by leakage; theorem assumes a property the system lacks.

## Methodology failure

The experimental design is wrong; the eval is biased; the dedupe is broken. Examples: train/test contamination; judge model rates its own output favorably; corpus dedup did not refresh indices after merge.

## Implementation failure

Code does not match design; off-by-one; race condition; memory leak. Examples: schema enforced in docs but not in code; concurrent writers can corrupt state; long-running job times out at exactly the wrong moment.

## Operational failure

System is deployed wrong; monitoring is missing; rollback is impossible. Examples: rollback procedure never tested; canary traffic split is 0%; metric is collected but not alerted on.

## Reception failure

Audience misinterprets the result; title oversells; limitations are buried. Examples: paper title implies general claim but methods section limits to one dataset; risk score is reported but uncertainty band is hidden in an appendix.

## Defense-in-depth-creates-false-confidence failure

Multiple layers of "safety" mask the actual brittle component. Examples: input validation + rate limiting + WAF — all happen to be misconfigured because they were copied from a different system; multiple eval gates all judge the same property in correlated ways.
```

- [ ] **Step 4: Lint frontmatter and SKILL.md**

```bash
uv run python -m tools.lint_frontmatter skills/workflow/running-adversarial-premortem/SKILL.md
uv run python -m tools.lint_skill_md skills/workflow/running-adversarial-premortem/SKILL.md
uv run python -m tools.lint_links skills/workflow/running-adversarial-premortem/
```

Expected: all three commands output `OK (1 file(s))`. Fix any reported errors.

- [ ] **Step 5: Commit**

```bash
git add skills/workflow/running-adversarial-premortem/
git commit -m "Add workflow/running-adversarial-premortem skill (migrated from harness)"
```

---

### Task 24: Write 3 evals for running-adversarial-premortem

**Files:**
- Create: `skills/workflow/running-adversarial-premortem/evals/01-paper-math-claims.json`
- Create: `skills/workflow/running-adversarial-premortem/evals/02-too-large-artifact.json`
- Create: `skills/workflow/running-adversarial-premortem/evals/03-simple-bug-review.json`

- [ ] **Step 1: Write happy-path scenario**

```json
{
  "skill": "running-adversarial-premortem",
  "scenario_id": "01-paper-math-claims",
  "scenario_kind": "happy-path",
  "query": "I just finished a paper claiming that all transformer attention heads are equivalent for short sequences (length ≤ 8). Theorem 1 proves this by showing isomorphism. Theorem 2 derives a polynomial bound on the equivalence gap. Can you premortem the math claims?",
  "files": [],
  "expected_behavior": [
    "Produces a per-claim audit table that has at least one row per theorem with the columns Location, Concern, Strongest counter, and Stops-mattering-if",
    "Names at least one specific concern about the use of 'isomorphism' on a small finite set (6 or 8 elements) — that demonstrating bijection of operations is required, not just bijection of sets",
    "Provides a prioritized remediation list ordered by severity × likelihood / detectability, NOT alphabetically or by appearance order"
  ]
}
```

- [ ] **Step 2: Write edge-case scenario**

```json
{
  "skill": "running-adversarial-premortem",
  "scenario_id": "02-too-large-artifact",
  "scenario_kind": "edge-case",
  "query": "Here is our company's 14,000-line agent-platform architecture spec. Please run a full premortem.",
  "files": [],
  "expected_behavior": [
    "Refuses to premortem the entire 14,000-line spec in one pass; explains that scope overflow produces noise",
    "Asks the user for a scope_hint to narrow the premortem to one component, section, or claim",
    "Suggests using the seed failure categories (premise / methodology / implementation / operational / reception / defense-in-depth) to choose where to focus the first round"
  ]
}
```

- [ ] **Step 3: Write anti-trigger scenario**

```json
{
  "skill": "running-adversarial-premortem",
  "scenario_id": "03-simple-bug-review",
  "scenario_kind": "anti-trigger",
  "query": "Can you check my Python loop for off-by-one errors? Here it is: for i in range(len(arr)): print(arr[i+1])",
  "files": [],
  "expected_behavior": [
    "Does NOT engage the premortem workflow (does not produce a per-claim audit table or seed failure categories)",
    "Explains that premortem is for high-stakes designs with multiple plausible failure modes; a single-bug code review is the wrong tool match",
    "Hands off to a code-review or debugging approach and identifies the off-by-one (arr[i+1] reads past the end on the last iteration)"
  ]
}
```

- [ ] **Step 4: Commit**

```bash
git add skills/workflow/running-adversarial-premortem/evals/
git commit -m "Add 3 evals for running-adversarial-premortem (happy / edge / anti-trigger)"
```

---

### Task 25: Run evals for running-adversarial-premortem and iterate until pass

**Files:**
- Modify (if eval fails): `skills/workflow/running-adversarial-premortem/SKILL.md`

- [ ] **Step 1: Ensure ANTHROPIC_API_KEY is exported**

```bash
echo "${ANTHROPIC_API_KEY:0:6}..."
```

Expected: output begins with `sk-ant`. If not, `export ANTHROPIC_API_KEY=sk-ant-...` first.

- [ ] **Step 2: Run the eval suite for this skill**

```bash
uv run python -m tools.run_evals skills/workflow/running-adversarial-premortem/
```

Expected (target): all three models pass their thresholds. Console shows:

```
  claude-haiku-4-5-20251001: PASS
  claude-sonnet-4-6: PASS
  claude-opus-4-7: PASS

All thresholds met.
```

- [ ] **Step 3: If any model fails, inspect the results JSON**

```bash
ls skills/workflow/running-adversarial-premortem/evals/results-*-2026-*.json
```

Identify which rubric items failed for which scenario+model. Common causes:

- **Haiku misses the prioritization-formula requirement.** Fix: add an explicit prioritization sentence to the `## Workflow` Round 3 step.
- **Sonnet/Opus engages the anti-trigger scenario.** Fix: tighten the `## When NOT to use` block; add an example mirroring the anti-trigger query.
- **Edge-case scenario does not ask for scope_hint.** Fix: add an explicit "if artifact > N lines, ask user for scope_hint" rule to `## Workflow`.

Edit SKILL.md to address the gap, then return to Step 2 and re-run. Repeat until all thresholds met.

- [ ] **Step 4: Commit any SKILL.md changes made during iteration**

```bash
git add skills/workflow/running-adversarial-premortem/SKILL.md
git commit -m "Tighten running-adversarial-premortem to pass eval thresholds across Haiku/Sonnet/Opus"
```

(If no changes were needed, skip this step.)

---

### Task 26: Update skills/workflow/README.md to mark running-adversarial-premortem shipped

**Files:**
- Modify: `skills/workflow/README.md`

- [ ] **Step 1: Move running-adversarial-premortem from the "Planned skills" → "Research discipline" subsection to the "Shipped skills" table**

Replace the `## Shipped skills` block of `skills/workflow/README.md`:

```markdown
## Shipped skills

| Skill | What it does | When to use | Σ |
|---|---|---|---|
| [`running-adversarial-premortem`](running-adversarial-premortem/) | Multi-round adversarial premortem on a spec / plan / design / paper / proof / codebase — per-claim audit table + stops-mattering-if + prioritized remediation | When the cost of being wrong is high; AI/ML/agentic/security-sensitive designs; mathematical proofs; high-stakes plans | 17 |
```

And remove the corresponding row from the "Research discipline" planned-skills subsection.

- [ ] **Step 2: Commit**

```bash
git add skills/workflow/README.md
git commit -m "Mark running-adversarial-premortem as shipped in workflow track README"
```

---

### Task 27: Inspect existing mcp-server-pre-trust-audit skill

**Files:**
- Read: `/Users/klambros/.claude/skills/mcp-server-pre-trust-audit/SKILL.md` (and any siblings)

- [ ] **Step 1: List the existing skill directory contents**

```bash
ls -la /Users/klambros/.claude/skills/mcp-server-pre-trust-audit/
```

Expected: directory exists with SKILL.md and possibly `scripts/`, `reference/`, etc.

- [ ] **Step 2: Read the existing SKILL.md**

```bash
cat /Users/klambros/.claude/skills/mcp-server-pre-trust-audit/SKILL.md
```

Capture the six-check structure (license, source review, network egress, version pin, secret handling, tool subset) and any existing examples or reference content. This is the source content for migration.

- [ ] **Step 3: Note the gaps against Layer-3 contract**

Identify which required H2 sections are missing or under-specified. Inspection only — no file changes yet.

---

### Task 28: Author skills/security/auditing-mcp-server-pre-trust/SKILL.md

**Files:**
- Create: `skills/security/auditing-mcp-server-pre-trust/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p skills/security/auditing-mcp-server-pre-trust/evals
```

- [ ] **Step 2: Write SKILL.md with full Layer-3 contract**

```markdown
---
name: auditing-mcp-server-pre-trust
description: >
  Audits an MCP (Model Context Protocol) server against six security checks — license,
  source review, network egress, version pin, secret handling, and tool subset —
  before the server is registered into the Claude Code tool pool. Use whenever the
  user proposes adding an MCP server to ~/.claude/mcp.json, a project .mcp.json, or
  a plugin's mcpServers config. Produces a per-check verdict, a blocking-issues list,
  and a final integrate / integrate-with-constraints / reject recommendation.
version: 0.1.0
status: shipped
track: security
audience: [security-eng, ai-security, skill-author]
evidence:
  - jetson-runbook
  - RCAP
  - claude-secure-coding-rules
last-updated: 2026-05-22
---

# Auditing an MCP Server Before Pre-Trust

## When to use

Trigger this skill when the user asks for or implies one of:

- Adding a new MCP server to `~/.claude/mcp.json`, a project `.mcp.json`, or a plugin's `mcpServers` config
- Evaluating whether to install or trust a community / third-party MCP server
- Phrases like "should I add this MCP?", "is this MCP server safe?", "install <mcp-name>", "audit this MCP"

## When NOT to use

Skip this skill and hand off when:

- The user wants to *write* an MCP server, not audit an existing one → use `claude-code-meta/writing-mcp-server-securely` (planned)
- The MCP server is already registered and the question is "did it do something weird?" — that is incident-response, not pre-trust
- The user is configuring a first-party Anthropic MCP server bundled with Claude Code that has already gone through Anthropic's audit

## Quick start

User says: "I want to add the github-mcp-server from https://github.com/example/github-mcp to my Claude Code setup. Audit it."

Skill response: walks the six checks (license, source, network, version, secret, tool subset), produces a per-check verdict table, lists any blocking issues, and gives a final integrate / integrate-with-constraints / reject recommendation with rationale.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| mcp_source | URL or local path | yes | — | The MCP server source — GitHub URL, npm package name, local path, or PyPI package name. |
| install_scope | "user" \| "project" \| "plugin" | no | "user" | Where the MCP will be registered. Affects blast radius assessment. |
| permission_level | "default" \| "elevated" | no | "default" | Whether the MCP would run with default Claude Code permissions or elevated. |

## Workflow

Copy this checklist into the response and check off items as each check completes:

```
Pre-trust audit progress:
- [ ] Check 1: License — present, permissive, redistribution OK
- [ ] Check 2: Source review — last commit, contributor count, signed commits, suspicious patterns
- [ ] Check 3: Network egress — declared outbound calls, no exfiltration risks
- [ ] Check 4: Version pin — install command pins a specific version (not @latest, not unpinned)
- [ ] Check 5: Secret handling — how secrets are passed, never logged, never sent to upstream
- [ ] Check 6: Tool subset — list of tools the MCP exposes; principle of least privilege
- [ ] Final verdict: integrate / integrate-with-constraints / reject
```

### Check 1: License

- Verify a `LICENSE` file exists in the repo root or `pyproject.toml` / `package.json` declares a license
- Confirm the license is permissive enough for the user's context (MIT / Apache 2.0 / BSD typically fine; AGPL may not be)
- Flag any "no license = all rights reserved" cases as blocking

### Check 2: Source review

- Identify the latest commit date and the count of distinct contributors
- Note whether commits are signed (sigstore / GPG)
- Read source files (top file at minimum); look for: shell command execution with user-controlled input, dynamic import with user-controlled strings, telemetry endpoints, hardcoded credentials
- Flag obvious red flags (obfuscated code, base64-encoded payloads, suspicious network calls) as blocking

### Check 3: Network egress

- Read the README and source for documented outbound calls (API endpoints, telemetry, update checks)
- Compare against the MCP's stated purpose — a "filesystem tool" with HTTP calls is suspicious
- Confirm any documented endpoints are owned by the MCP author / well-known third party (GitHub API for a GitHub MCP, etc.)

### Check 4: Version pin

The install command MUST pin a specific version. Acceptable forms include npm-style `pkg@1.2.3`, pip-style `pkg==1.2.3`, or git-clone with explicit commit sha. Unpinned forms (latest, no version constraint, `npx -y`, `pip install pkg` without a constraint) are blocking.

### Check 5: Secret handling

- Identify how the MCP consumes secrets (env vars, config file, OAuth flow)
- Verify secrets are NOT logged (search for log/print calls near secret usage)
- Verify secrets are NOT included in error messages sent to a remote service
- For OAuth flows, confirm the callback URL is localhost or under the MCP author's domain

### Check 6: Tool subset

- List every tool the MCP exposes (`tools/list` output if available, or grep the source)
- Apply principle of least privilege — does this MCP need ALL these tools, or only some?
- If the MCP exposes destructive tools (file deletion, network requests, shell execution), flag for `permission_level: elevated` review

### Final verdict

- **Integrate**: all 6 checks pass; install
- **Integrate with constraints**: 4–5 checks pass; constraints required (subset of tools enabled, network egress blocked at firewall, etc.)
- **Reject**: ≥ 2 checks fail OR any single blocking issue identified

## Outputs

A markdown report:

1. **MCP identity** — name, version, source URL
2. **Per-check verdict table**: Check · Verdict (Pass / Warn / Fail) · Evidence · Notes
3. **Blocking issues list** (if any)
4. **Final recommendation** — integrate / integrate-with-constraints / reject — with rationale
5. **Install command** (if integrate or integrate-with-constraints) — exact pinned command

## Failure modes

- **Audit theater** — going through the checklist without genuine inspection. Caught by: required "Evidence" column on the verdict table (must cite specific files / lines / commits).
- **Permissive license bias** — assuming permissive license = safe code. License is necessary, not sufficient. Source review (Check 2) is separate.
- **Stale source review** — auditing one commit and integrating later versions. Caught by: Check 4 requires a specific version/sha pin AND a re-audit on version bumps.
- **Tool-subset omission** — installing an MCP and accepting all tools by default. Caught by: Check 6 requires explicit tool-subset declaration.

## References

- `reference/audit-table-template.md` — the per-check verdict table template
- `reference/red-flag-patterns.md` — specific code patterns that indicate compromise
- [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp.md)
- [MCP specification](https://modelcontextprotocol.io/)

## Examples

### Example 1: Pinned, licensed, low-privilege MCP (happy-path)

Input: "Audit github.com/anthropics/mcp-filesystem v1.2.3 for my project scope."

Output: Skill walks all six checks. License: MIT ✓. Source: 14 contributors, last commit 3 days ago, no signed commits but Anthropic ownership confirmed via GitHub org ✓. Network: no egress declared, source confirms no outbound calls ✓. Version: pinned to v1.2.3 ✓. Secrets: MCP accepts a working directory path; no secrets handled ✓. Tools: read_file, write_file, list_directory (3 tools, all expected for a filesystem MCP) ✓. Final: integrate.

### Example 2: Unknown MCP, no license (anti-trigger)

Input: "Add this random MCP I found: https://github.com/randomuser/cool-mcp"

Output: Skill begins audit, immediately fails Check 1 (no LICENSE file in repo root, no license declaration in pyproject.toml). Reports blocking issue. Final: reject. Recommends user contact the author for license clarification before re-audit.

## See also

- `security/auditing-pinned-dependencies` — broader supply-chain audit pattern
- `claude-code-meta/writing-mcp-server-securely` — the authoring side of this skill (planned)
- `workflow/running-adversarial-premortem` — for high-stakes MCP integration decisions

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-22
- Provenance: migrated from `~/.claude/skills/mcp-server-pre-trust-audit/`; reformatted to Layer-3 contract; slug renamed to enforce gerund convention
```

- [ ] **Step 3: Write the two referenced files**

`skills/security/auditing-mcp-server-pre-trust/reference/audit-table-template.md`:

```markdown
# Pre-trust audit verdict table template

| Check | Verdict | Evidence | Notes |
|---|---|---|---|
| 1. License | Pass / Warn / Fail | <file path or commit ref> | |
| 2. Source review | Pass / Warn / Fail | <commits inspected, lines reviewed> | |
| 3. Network egress | Pass / Warn / Fail | <endpoints found in source> | |
| 4. Version pin | Pass / Warn / Fail | <install command> | |
| 5. Secret handling | Pass / Warn / Fail | <how secrets flow through the code> | |
| 6. Tool subset | Pass / Warn / Fail | <tools exposed; least-privilege check> | |

Final verdict: **integrate** / **integrate-with-constraints** / **reject**
```

`skills/security/auditing-mcp-server-pre-trust/reference/red-flag-patterns.md`:

```markdown
# Red-flag patterns to look for in MCP server source review

These patterns are not automatically disqualifying, but each one warrants a deeper look and either an explicit safe-explanation or a downgraded verdict.

## Dynamic code execution with user-controlled input

Any function that takes user-provided text and runs it as code or shell — Python's dynamic-execution builtins, the Node child-process family, JavaScript's dynamic-eval family — is the highest-priority pattern to find. Confirm the source either (a) does not contain it, or (b) uses it only on inputs the MCP itself controls.

## Dynamic import with user-controlled string

Pattern where the module/library to load is determined at runtime from caller input. In Python this is `importlib.import_module(user_input)`; in Node this is requiring or importing a path that came from the request. Both can be vehicles for arbitrary-code execution.

## Hardcoded credentials in source

Strings matching API-key formats (e.g. `sk-` prefixes followed by 40+ characters, AWS `AKIA…` patterns, GitHub personal-access-token patterns). Literal `password = "…"` or `api_key = "…"` assignments. Any of these in source are blocking.

## Obfuscated payloads

Look for: long base64 literals followed by decoding-and-execution patterns; hex-encoded byte strings followed by binary execution; one-line minified JavaScript with no source map. Each is a strong indicator of intentional obfuscation.

## Suspicious telemetry

Outbound calls to free-tier analytics services with PII in the payload. Calls to non-author-owned domains for "update checks" that are not declared in the README.

## Excessive permissions

Filesystem-MCP that requires `network` permission. Read-only MCP that requires `write` permission. Single-purpose MCP that exposes ≥ 10 tools.

## Suspicious commit patterns

A single commit replacing all source with new content from a one-off contributor. Squash-merge from a fork that was not reviewed. Commits dated in the future.
```

- [ ] **Step 4: Lint**

```bash
uv run python -m tools.lint_frontmatter skills/security/auditing-mcp-server-pre-trust/SKILL.md
uv run python -m tools.lint_skill_md skills/security/auditing-mcp-server-pre-trust/SKILL.md
uv run python -m tools.lint_links skills/security/auditing-mcp-server-pre-trust/
```

Expected: all three commands output `OK (1 file(s))`.

- [ ] **Step 5: Commit**

```bash
git add skills/security/auditing-mcp-server-pre-trust/
git commit -m "Add security/auditing-mcp-server-pre-trust skill (migrated from harness)"
```

---

### Task 29: Write 3 evals for auditing-mcp-server-pre-trust

**Files:**
- Create: `skills/security/auditing-mcp-server-pre-trust/evals/01-pinned-licensed-mcp.json`
- Create: `skills/security/auditing-mcp-server-pre-trust/evals/02-no-license.json`
- Create: `skills/security/auditing-mcp-server-pre-trust/evals/03-blanket-approve.json`

- [ ] **Step 1: Write happy-path scenario**

```json
{
  "skill": "auditing-mcp-server-pre-trust",
  "scenario_id": "01-pinned-licensed-mcp",
  "scenario_kind": "happy-path",
  "query": "I want to add https://github.com/example/filesystem-mcp v1.2.3 to my Claude Code setup. The README says it exposes read_file, write_file, and list_directory tools. License is MIT. Install command they recommend is npm install filesystem-mcp@1.2.3. Audit it.",
  "files": [],
  "expected_behavior": [
    "Walks all six checks (license, source, network, version pin, secret handling, tool subset) — at minimum lists each check explicitly",
    "Identifies that the install command IS pinned (npm install filesystem-mcp@1.2.3, not unpinned), and rates Check 4 as Pass",
    "Issues a final verdict of integrate or integrate-with-constraints (not reject), with rationale tied to the six checks"
  ]
}
```

- [ ] **Step 2: Write edge-case scenario**

```json
{
  "skill": "auditing-mcp-server-pre-trust",
  "scenario_id": "02-no-license",
  "scenario_kind": "edge-case",
  "query": "Add this MCP I found: https://github.com/randomuser123/cool-mcp. I really need it for my project. The repo does not have a LICENSE file but the README is detailed.",
  "files": [],
  "expected_behavior": [
    "Identifies the missing license as a Check 1 failure / blocking issue (not merely a warning)",
    "Issues a final verdict of reject, NOT integrate-with-constraints",
    "Recommends a remediation: contact the author to add an explicit license before re-auditing"
  ]
}
```

- [ ] **Step 3: Write anti-trigger scenario**

```json
{
  "skill": "auditing-mcp-server-pre-trust",
  "scenario_id": "03-blanket-approve",
  "scenario_kind": "anti-trigger",
  "query": "Just set up Claude Code with all my standard MCPs — GitHub, Linear, Slack, Notion, and Filesystem. Use whatever versions are current.",
  "files": [],
  "expected_behavior": [
    "Does NOT blanket-approve all 5 MCPs without audit",
    "Explains that each MCP must be audited individually against the six checks before pre-trust",
    "Refuses the 'whatever versions are current' framing because it violates Check 4 (version pin); requires explicit pinned versions before proceeding"
  ]
}
```

- [ ] **Step 4: Commit**

```bash
git add skills/security/auditing-mcp-server-pre-trust/evals/
git commit -m "Add 3 evals for auditing-mcp-server-pre-trust (happy / edge / anti-trigger)"
```

---

### Task 30: Run evals for auditing-mcp-server-pre-trust and iterate until pass

**Files:**
- Modify (if eval fails): `skills/security/auditing-mcp-server-pre-trust/SKILL.md`

- [ ] **Step 1: Run the eval suite**

```bash
uv run python -m tools.run_evals skills/security/auditing-mcp-server-pre-trust/
```

Expected: all three models pass their thresholds.

- [ ] **Step 2: If any model fails, inspect results JSON**

```bash
ls skills/security/auditing-mcp-server-pre-trust/evals/results-*.json
```

Common failure causes:

- **Haiku does not list all six checks explicitly.** Fix: bold the check names in `## Workflow`; add a one-line "name each check by number" instruction to the checklist.
- **Sonnet/Opus blanket-approves in the anti-trigger.** Fix: add an explicit "## When NOT to use" item for blanket approval; add an example mirroring the anti-trigger.
- **Edge case downgrades 'reject' to 'integrate-with-constraints'.** Fix: tighten the final-verdict criteria — missing license is "≥ 2 checks fail OR any single blocking issue" → blocking by itself.

Edit SKILL.md to address gaps; re-run.

- [ ] **Step 3: Commit any SKILL.md changes**

```bash
git add skills/security/auditing-mcp-server-pre-trust/SKILL.md
git commit -m "Tighten auditing-mcp-server-pre-trust to pass eval thresholds"
```

---

### Task 31: Update skills/security/README.md to mark auditing-mcp-server-pre-trust shipped

**Files:**
- Modify: `skills/security/README.md`

- [ ] **Step 1: Replace the `## Shipped skills` block**

```markdown
## Shipped skills

| Skill | What it does | When to use | Σ |
|---|---|---|---|
| [`auditing-mcp-server-pre-trust`](auditing-mcp-server-pre-trust/) | Six-check audit (license, source, network, version pin, secret handling, tool subset) of any proposed MCP server before pre-trust | Whenever you are about to add an MCP server to your Claude Code config | 18 |
```

Remove the corresponding row from the planned-skills table (or change its status to ✅).

- [ ] **Step 2: Commit**

```bash
git add skills/security/README.md
git commit -m "Mark auditing-mcp-server-pre-trust as shipped in security track README"
```

---

### Task 32: Update root README catalog + skills/README.md

**Files:**
- Modify: `README.md`
- Modify: `skills/README.md`

- [ ] **Step 1: Replace the placeholder catalog block in root README.md with the 2 shipped skills**

```markdown
## Skill catalog

| Skill | Track | What it does | Status | Σ |
|---|---|---|---|---|
| [`running-adversarial-premortem`](skills/workflow/running-adversarial-premortem/) | workflow | Multi-round adversarial premortem on spec / plan / paper / proof / codebase | ✅ shipped | 17 |
| [`auditing-mcp-server-pre-trust`](skills/security/auditing-mcp-server-pre-trust/) | security | Six-check audit before registering an MCP server | ✅ shipped | 18 |

_2 of ~80 planned skills shipped. See each track's README for the planned-skills roadmap._
```

- [ ] **Step 2: Update skills/README.md to add a "Shipped skills" subsection above the by-track listing**

Replace the existing skills/README.md content with:

```markdown
# RCS Skills — Cross-Track Index

All RCS skills, organized first by audience track and then by ROI rank (Σ score from the v1 brainstorm).

## Shipped (v1.0.0-phase1)

| Skill | Track | Σ |
|---|---|---|
| [`running-adversarial-premortem`](workflow/running-adversarial-premortem/) | workflow | 17 |
| [`auditing-mcp-server-pre-trust`](security/auditing-mcp-server-pre-trust/) | security | 18 |

## By track

- **[security/](security/)** — Security engineers, AI red-teamers, GRC, vuln triage, MCP pre-trust, pen-test discipline.
- **[ml-datasci/](ml-datasci/)** — Data scientists, ML engineers, stats students, applied ML.
- **[workflow/](workflow/)** — Cross-cutting hygiene and research discipline for both audiences.
- **[teaching/](teaching/)** — Pedagogy patterns, rubrics, pset walkthroughs (no v1 skills; structure pre-allocated).
- **[claude-code-meta/](claude-code-meta/)** — Skill / plugin / hook / MCP / rule authoring meta.

## Status legend

- ✅ **shipped** — body + 3 passing evals + Layer-3 H2 sections; auto-invocable
- 🔨 **drafting** — visible to readers but not yet eval-validated; not auto-invocable
- 📝 **planned** — listed only; no directory yet

See `docs/conventions.md` for full status semantics.
```

- [ ] **Step 3: Commit**

```bash
git add README.md skills/README.md
git commit -m "Update root + skills indexes to list 2 shipped skills"
```

---

### Task 33: Tag the Phase 1 release

**Files:**
- (no file changes; tag operation)

- [ ] **Step 1: Verify all tests pass and all skills lint clean**

```bash
uv run pytest -v
uv run python -m tools.lint_frontmatter skills/workflow/running-adversarial-premortem/SKILL.md skills/security/auditing-mcp-server-pre-trust/SKILL.md
uv run python -m tools.lint_skill_md skills/workflow/running-adversarial-premortem/SKILL.md skills/security/auditing-mcp-server-pre-trust/SKILL.md
uv run python -m tools.lint_links skills/workflow/running-adversarial-premortem/ skills/security/auditing-mcp-server-pre-trust/
```

Expected: all four commands output success.

- [ ] **Step 2: Update CHANGELOG.md — move Unreleased → v1.0.0-phase1 entry**

Edit `CHANGELOG.md`. Replace the `## [Unreleased]` heading with `## [v1.0.0-phase1] — 2026-05-22` and start a new empty `## [Unreleased]` block above it for future work.

```markdown
# Changelog

All notable changes to RCS are documented here. Per-skill changes use the skill's SemVer; repo-level batch tags mark release groupings.

## [Unreleased]

## [v1.0.0-phase1] — 2026-05-22

### Added — Bootstrap

- Repo skeleton, root README, LICENSE (MIT), CONTRIBUTING.md
- `docs/conventions.md`, `docs/eval-protocol.md`, `docs/governance.md`
- `tools/lint_frontmatter.py`, `tools/lint_skill_md.py`, `tools/lint_links.py`, `tools/run_evals.py`
- `.github/workflows/frontmatter-lint.yml`, `link-check.yml`, `eval-suite.yml`
- All 5 track READMEs with planned-skills tables populated from the full ~80-skill universe

### Added — Free-ship skills

- `workflow/running-adversarial-premortem` v0.1.0 — migrated from `~/.claude/skills/adversarial-premortem.skill`
- `security/auditing-mcp-server-pre-trust` v0.1.0 — migrated from `~/.claude/skills/mcp-server-pre-trust-audit/`
```

- [ ] **Step 3: Commit CHANGELOG update**

```bash
git add CHANGELOG.md
git commit -m "CHANGELOG: cut v1.0.0-phase1 release"
```

- [ ] **Step 4: Create the annotated tag**

```bash
git tag -a v1.0.0-phase1 -m "v1.0.0-phase1: bootstrap + 2 free-ship migrations (running-adversarial-premortem, auditing-mcp-server-pre-trust)"
git tag -n v1.0.0-phase1
```

Expected output: tag listing with annotation.

- [ ] **Step 5: (Manual, requires user action) Push to GitHub when ready**

Pushing to a remote is reserved for the user. Document the next manual step in `CHANGELOG.md` or the PR description rather than executing it from the plan.

Recommended push commands (run manually):

```bash
git remote add origin git@github.com:rockcyber/rcs.git
git push -u origin main
git push origin v1.0.0-phase1
```

---

## Self-review

Performed against `docs/superpowers/specs/2026-05-22-rcs-public-skills-repo-design.md`.

### Spec coverage

| Spec section | Plan task(s) |
|---|---|
| § 1 Identity | Task 3 (root README) |
| § 2 Audience routing | Task 3 (root README), Tasks 17–21 (track READMEs) |
| § 3 Constraints (C1–C12) | C1 baked into all skill authoring tasks; C2 enforced by absence of catalogs; C3 by directory layout (no plugin manifest); C4 by 5-track tree; C5 by no-stub policy (Tasks 17–21); C6 by lint tools (Tasks 9–10); C7 covered in Phase 2+ plans (this plan ships 2 of 18); C8 by Tasks 24, 29; C9, C10, C11 by lint tools; C12 by Tasks 4, 8 |
| § 4 Directory layout | Task 1 (skeleton), Tasks 17–21 (track dirs), Tasks 22–31 (skill dirs) |
| § 5 Per-skill anatomy | Tasks 23, 28 (SKILL.md + reference/), Tasks 24, 29 (evals/) |
| § 6 Frontmatter spec | Task 9 (lint enforcement), Tasks 23, 28 (compliant skills) |
| § 7 Documentation contract | Task 10 (lint enforcement for Layer 3); Tasks 17–21 (Layer 2); Task 3 (Layer 1) |
| § 8 Eval-driven dev | Task 12 (harness), Tasks 24, 25, 29, 30 (evals + iterate) |
| § 9 License + governance + CI | Task 2 (LICENSE), Task 4 (CONTRIBUTING), Task 8 (governance), Tasks 13–15 (CI) |
| § 10 v1 ship batch — Phase 0 | Tasks 1–21 |
| § 10 v1 ship batch — Phase 1 | Tasks 22–33 |
| § 11 Migration plan | Tasks 22 (extract), 23, 27, 28 (reformat); seed-evaluation deferred as documented |
| § 12 Open questions | Task 12 documents the model-availability fallback; license default carried through Task 2 |

No spec section is unaddressed.

### Placeholder scan

Reviewed for "TBD", "TODO", "implement later", "add appropriate error handling", "similar to Task N". None found in this plan. All steps contain actual content.

### Type / signature consistency

- `lint_frontmatter` returns `list[LintError]`; used the same way in Task 9 implementation and CLI.
- `lint_skill_md` returns `list[LintError]`; same.
- `lint_links` returns `list[LintError]`; same.
- `EvalScenario`, `JudgeResult`, `RubricItemResult` dataclasses defined once in Task 12 and referenced consistently in tests.
- `TARGET_MODELS` list and `THRESHOLDS` dict defined once in Task 12 and referenced by `check_threshold` in tests.
- Skill slugs: `running-adversarial-premortem` and `auditing-mcp-server-pre-trust` used consistently across Tasks 22–33.

No type/signature drift identified.

### Scope check

This plan covers Phase 0 + Phase 1 of the spec (bootstrap + 2 free-ship migrations). Phases 2–6 (16 more skills) get their own follow-up plans after Phase 1 lands.
