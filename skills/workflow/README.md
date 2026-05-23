# Workflow Track

Cross-cutting research and engineering hygiene. Applies to both security and ml-datasci audiences.

## Shipped skills

| Skill | What it does | When to use | Σ |
|---|---|---|---|
| [`running-adversarial-premortem`](running-adversarial-premortem/) | Multi-round adversarial premortem on a spec / plan / design / paper / proof / codebase — per-claim audit table + stops-mattering-if + prioritized remediation | When the cost of being wrong is high; AI/ML/agentic/security-sensitive designs; mathematical proofs; high-stakes plans | 17 |
| [`enforcing-seed-hygiene`](enforcing-seed-hygiene/) | First-cell seed gate covering Python/NumPy/PyTorch/JAX/TF/R + CPU-pin for cross-platform sampler determinism + pre-commit hook | When starting an ML/DS notebook, training script, or diagnosing run-to-run drift | 20 |
| [`validating-temporal-fields`](validating-temporal-fields/) | Reject-future + min-year-fallback + event-vs-disclosure-date separation for any temporal corpus | When ingesting incident registries, vulnerability disclosures, or news-derived corpora with year/date fields | 19 |
| [`deduplicating-records`](deduplicating-records/) | Multi-key dedup with index-refresh between passes, transitive collapse via connected-components / union-find, and ID-format normalization across sources | Ingesting a corpus from multiple sources; merging registries with different ID formats; observing duplicates after a recent merge or schema change | 18 |
| [`pinning-reproducible-environments`](pinning-reproducible-environments/) | Per-ecosystem pin pattern (uv.lock / poetry.lock / package-lock.json / pnpm-lock.yaml / renv.lock / base-image digest) + runtime-version pinning + CI strict-install + weekly drift-check | Starting a new project; "works on my machine but not in CI" symptoms; teammate onboarding; reproducibility for a paper, regulatory submission, or audit trail | 17 |
| [`auditing-data-quality`](auditing-data-quality/) | Per-column null / range / type / cardinality audit + semantic-class detection + outlier flagging (no auto-drop) + row-level integrity (duplicate rows, conflicting facts) | Receiving a new dataset; before fitting any model; when results suddenly look off; when a dataset changed shape between runs | 17 |
| [`auditing-context-window-pressure`](auditing-context-window-pressure/) | Multi-turn session pressure audit: context %, cache-hit-rate, instruction-hierarchy size, tool-result bloat, system-reminder accumulation, /compact vs /clear triage with mandatory file-offload + subagent-summary moves first | Session feels slow; prompt-cache hit rate dropped; token cost seems high; before starting a long-running multi-turn workflow | 17 |

## Planned skills

### Notebook + reproducibility

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-notebook-narrative` | Diff rendered figures against in-narrative claims | 13 | 📝 planned |
| `building-deterministic-data-pipelines` | LF endings, sorted JSON keys, content-hash snapshots, provenance.json | 15 | 📝 planned |
| `auditing-jupyter-execution-order` | Cells-out-of-order detection | 16 | 📝 planned |

### Data engineering

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `validating-schema-evolution` | Schema-diff + breaking-change classification | 13 | 📝 planned |
| `auditing-source-provenance` | provenance.json: source repo + commit SHA + pull date + adapter version | 16 | 📝 planned |

### Research discipline

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `pre-registering-eval-study` | Lock + hypothesis + stopping rules + falsification criteria | 16 | 📝 planned |
| `writing-successor-primers` | "If you have to pick this up cold" template | 15 | 📝 planned |
| `writing-release-notes-as-postmortem` | Regression → root cause → test added to prevent recurrence | 15 | 📝 planned |
| `auditing-mathematical-claims` | Per-claim: location, concern, strongest-counter, stops-mattering-if (ATACE math-flags template) | 13 | 📝 planned |

## Cross-track references

- Pairs with everything. If you're shipping a skill in `security/` or `ml-datasci/`, you almost certainly want one of these too.
- For Claude Code authoring discipline (skill / plugin / hook), see `claude-code-meta/`.
