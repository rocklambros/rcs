# Workflow Track

Cross-cutting research and engineering hygiene. Applies to both security and ml-datasci audiences.

## Shipped skills

_None yet. `running-adversarial-premortem` is at `status: drafting` pending eval validation; see "Drafting" section below._

## Drafting

| Skill | What it does | When to use | Σ |
|---|---|---|---|
| [`running-adversarial-premortem`](running-adversarial-premortem/) | Multi-round adversarial premortem on a spec / plan / design / paper / proof / codebase — per-claim audit table + stops-mattering-if + prioritized remediation | When the cost of being wrong is high; AI/ML/agentic/security-sensitive designs; mathematical proofs; high-stakes plans | 17 |

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
