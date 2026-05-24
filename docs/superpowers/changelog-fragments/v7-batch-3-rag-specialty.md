### v7-batch-3: rag-specialty — 2026-05-23

Skills shipped:

- `ml-datasci/auditing-chunking-strategy` v0.1.0 — chunk_size × overlap sweep against a held-out QA set with source-span attribution, scored by answer-coverage@k (not bare recall@k), with splitter comparison at the best cell and a documented config comment to lock the choice (Σ 13, status: shipped)
- `ml-datasci/auditing-embedding-drift` v0.1.0 — per-dim Jensen-Shannon divergence + centroid cosine distance + intra-cohort distance shift between baseline and comparison cohorts, with bootstrap 95% CIs and attribution to new content categories, upstream-data shift, or provider-side model re-versioning (Σ 11, status: shipped)
- `ml-datasci/building-rag-eval-set` v0.1.0 — three-split RAG eval set (calibration + never-viewed held-out test + adversarial) with source-doc + source-span attribution on every non-absent-topic row, human-review gate on every Q-A (including LLM-drafted candidates), and dataset hash + SemVer locking (Σ 12, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Each skill ran 3 scenarios (happy-path, edge-case, anti-trigger), one Sonnet subagent per scenario, judged by intent against the 3 rubric items per scenario. Full 3-model validation deferred to a future re-run.

Eval results:

- auditing-chunking-strategy: happy 3/3, edge 3/3, anti 3/3
- auditing-embedding-drift: happy 3/3, edge 3/3, anti 3/3
- building-rag-eval-set: happy 3/3, edge 3/3, anti 3/3

All three skills passed all Sonnet thresholds and ship with status: shipped.

Notes: The three skills are siblings of one another (each skill's "See also" cross-links the other two). Together they cover the three RAG-specialty disciplines surfaced by the v7 plan's rag-specialty cluster — chunking sweep + splitter selection (auditing-chunking-strategy), longitudinal drift quantification with attribution (auditing-embedding-drift), and the from-scratch eval-set construction that the other two depend on as their measurement input (building-rag-eval-set). auditing-chunking-strategy and auditing-embedding-drift both reference building-rag-eval-set as the prerequisite when no eval set yet exists.
