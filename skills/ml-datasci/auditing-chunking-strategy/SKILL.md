---
name: auditing-chunking-strategy
description: >
  Audits a RAG pipeline's document-chunking strategy: chunk size, overlap, and
  splitter type (fixed-token, sentence, paragraph, semantic, structure-aware).
  Walks a chunk-size × overlap sweep against a held-out QA set, surfaces
  boundary-failure examples where the answer spans two chunks, and recommends a
  splitter that matches the document structure (legal contracts and long-form
  prose need different splitters than code or FAQ pairs). Use when retrieval
  recall is dropping on long documents, when chunks visibly cut answers in half,
  when chunk_size and overlap were copied from a tutorial without a sweep, or
  when migrating from a default fixed-token splitter to something
  structure-aware. Refuses to engage when the pipeline retrieves full documents
  (no chunking) or when the corpus is one-paragraph-per-doc (chunking is
  pre-empted by document structure).
version: 0.1.0
status: shipped
track: ml-datasci
audience: [ml-engineer, data-scientist, ai-security]
evidence:
  - ai_security_framework_crosswalk
  - multiturn-injection-detection
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Auditing a RAG Chunking Strategy

## When to use

Trigger this skill when the user:

- Reports that RAG retrieval recall is degrading on long documents (legal, regulatory, scientific) but works fine on short docs
- Shows a chunk that visibly cuts an answer in half (the answer's subject is in chunk N, the predicate is in chunk N+1)
- Set `chunk_size` and `chunk_overlap` from a tutorial / framework default without sweeping for their corpus
- Is migrating from a fixed-token splitter (e.g., `RecursiveCharacterTextSplitter`) to something structure-aware (semantic, paragraph, sentence, or AST/section-aware)
- Asks "what chunk size should I use" — the answer is a sweep, not a number
- Reports that retrieval looks fine on single-fact queries but fails on multi-fact or synthesis queries (a boundary symptom)
- Is auditing an inherited RAG pipeline and the chunking config has no comment explaining the choice

## When NOT to use

Skip and hand off when:

- The pipeline retrieves whole documents (no chunking happens) — the relevant audit is corpus size, not chunking
- The corpus is structurally one-paragraph-per-document (customer-support FAQs, knowledge-base Q-A pairs) — the document IS the chunk; no splitter decision to audit
- The user is debugging the retrieval-vs-generation split (use `evaluating-rag-retrieval` to separate retrieval failures from generation failures first; come back here if retrieval is the problem)
- The user is asking about embedding-model selection (use `selecting-embedding-model`) — embedding model and chunking are separate axes
- The user is asking about embedding drift over time (use `auditing-embedding-drift`)
- The user is building a brand-new RAG eval set (use `building-rag-eval-set` first — without an eval set, no sweep can be scored)

## Quick start

User: *"My legal-doc RAG is missing answers that span across paragraphs. Chunk size is 512 tokens, overlap is 50. Audit it."*

Skill walks the 6-step workflow: (1) inventory current config + corpus stats, (2) build or reuse a held-out QA eval set, (3) run the chunk-size × overlap sweep grid from `reference/chunk-sweep-grid.md`, (4) score each cell with recall@k on the eval set, (5) collect boundary-failure examples by querying for facts the splitter cut, (6) recommend a splitter matched to the corpus structure (here: paragraph-aware or semantic, NOT fixed-token).

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| corpus_sample | list[document] | yes | — | Representative documents from the corpus. Minimum 20 documents covering the length distribution. |
| current_config | object | no | null | The current `{chunk_size, chunk_overlap, splitter}` — needed to compare against the sweep. Null = greenfield audit. |
| eval_qa_set | list[{query, answer, source_span}] | yes | — | Held-out queries with ground-truth answers and the source span the answer comes from. Minimum 30 queries. If absent, hand off to `building-rag-eval-set` before proceeding. |
| embedding_model | string | yes | — | Model ID with revision pin. Determines the token budget for `chunk_size` and the cost of the sweep. |
| chunk_size_grid | list[int] | no | [200, 400, 800, 1200, 2000] | Token sizes to sweep. Override for non-text corpora (e.g., code chunks may want smaller). |
| overlap_grid | list[float] | no | [0.0, 0.10, 0.25, 0.50] | Overlap fractions (of `chunk_size`) to sweep. |
| splitter_candidates | list[string] | no | ["fixed-token", "sentence", "paragraph", "semantic"] | Splitter strategies to compare at the best `(chunk_size, overlap)` cell. |
| top_k | int | no | 5 | Retrieval depth for recall@k scoring. |

## Workflow

Copy this checklist into the response and check off each step as the audit lands:

```
Audit progress:
- [ ] 1. Inventory: read current chunking config + corpus length distribution
- [ ] 2. Verify eval QA set exists; if missing, hand off to building-rag-eval-set
- [ ] 3. Run chunk_size × overlap sweep across the grid; embed + index each cell
- [ ] 4. Score each cell: recall@k, answer-coverage (does the retrieved chunk contain the source_span?), boundary-failure rate
- [ ] 5. Collect boundary-failure examples for the current config + the best-cell config (qualitative review)
- [ ] 6. Recommend final {chunk_size, chunk_overlap, splitter} with evidence (sweep table + boundary examples + cost/latency)
```

### Step 1 — Inventory

Capture:

- Current `chunk_size`, `chunk_overlap`, splitter class (LangChain `RecursiveCharacterTextSplitter`, `SemanticChunker`, custom)
- Corpus token-length distribution: min / p50 / p90 / p99 / max via `tiktoken` (encoding matched to the embedding model)
- Document structure: are there headings? section markers? code blocks? tables? footnotes?
- Embedding model's max input tokens (e.g., `text-embedding-3-large` = 8191; `voyage-3` = 32000)

The corpus's p90 token length and the embedding model's max input together bound the chunk-size grid.

### Step 2 — Eval QA set

The sweep cannot be scored without a held-out QA set with source-span attribution. Each QA row needs:

- `query`: a question a real user would ask
- `answer`: the ground-truth answer
- `source_doc_id`: which document contains the answer
- `source_span`: the character or token range inside the source doc where the answer lives

Without `source_span`, you can compute end-to-end answer accuracy but cannot separately measure whether the RIGHT CHUNK was retrieved. That separation is what makes a chunking sweep meaningful. If the user doesn't have one, refuse to proceed and hand off to `building-rag-eval-set`.

### Step 3 — Run the sweep

For each `(chunk_size, overlap)` cell in the grid:

1. Re-chunk the corpus with that config
2. Embed all chunks with the (fixed) embedding model
3. Index into a vector store (in-memory for the audit; production store is out of scope)
4. For each query in the eval set, retrieve `top_k` chunks

Recommended grid is at `reference/chunk-sweep-grid.md`. For a 1000-document corpus + 100-query eval set with `text-embedding-3-large` API, the full default grid (5 sizes × 4 overlaps = 20 cells) typically costs $10-30 and takes 30-60 minutes wall time. Note the cost up front so the user can decide whether to trim the grid.

### Step 4 — Score each cell

For each cell, compute:

| Metric | Definition | Why it matters |
|---|---|---|
| `recall@k` | Fraction of queries where the source_doc was in the top-k retrieved | Coarse retrieval signal; doesn't care about chunk boundaries |
| `answer-coverage@k` | Fraction of queries where a retrieved chunk contains the full source_span | The boundary-sensitive metric — answers cut across chunks fail this |
| `boundary-failure-rate` | Fraction of queries where the source_span is split across two retrieved chunks | Direct measurement of the failure mode this skill targets |
| `avg-chunks-per-doc` | Mean number of chunks per document at this config | Cost proxy (more chunks = more embeddings = more $) |

Report all four per cell. `answer-coverage@k` is the metric to optimize — it is the one that correlates with downstream answer quality, not bare `recall@k`.

### Step 5 — Boundary-failure examples

For 5-10 failing queries (where the current config got `answer-coverage@k = 0`), show:

- The query
- The retrieved chunks
- The actual source_span — highlight where it was cut
- The same query under the best-cell config — does it now succeed?

Qualitative review by the user is the gate before recommending a change. A sweep table without examples is unconvincing.

### Step 6 — Recommend

The recommendation has three parts:

1. **`chunk_size` + `overlap`**: pick the cell with highest `answer-coverage@k` within an acceptable cost envelope (don't pick `chunk_size=200, overlap=0.50` if it 3x's the embedding bill for a 2-point coverage gain)
2. **Splitter**: re-run only the best `(chunk_size, overlap)` cell across `splitter_candidates`. Recommend the structure-aware splitter that wins.
3. **Document the choice in the chunking-config file** with a comment citing the audit date and the best-cell `answer-coverage@k` value, so a future maintainer doesn't silently re-tune away from it.

## Outputs

A markdown audit report containing:

- Corpus length distribution table
- Current-config baseline scores (4 metrics at the current cell)
- Full sweep table (one row per cell, four metric columns)
- Splitter comparison table at the best cell (one row per splitter)
- 5-10 boundary-failure examples (current config vs recommended config)
- Final recommendation: `chunk_size`, `chunk_overlap`, splitter, with cost estimate
- Migration snippet: the new `text_splitter = ...(chunk_size=X, chunk_overlap=Y, ...)` line + a comment line citing the audit

## Failure modes

Known pitfalls and how this skill catches them:

- **Sweeping without an eval set** — produces a sweep table with no way to pick a winner. Caught by step 2 refusing to proceed without a QA set with source spans; hand off to `building-rag-eval-set`.
- **Optimizing bare `recall@k`** — a smaller chunk size always raises recall@k because more chunks per doc means higher chance the doc is in top-k; but the answer may be in a DIFFERENT chunk than the retrieved one. Caught by step 4 reporting `answer-coverage@k` as the primary metric, not `recall@k`.
- **Fixed-token splitter on structured documents** — cuts mid-sentence, mid-table, mid-code-block. Caught by step 6 forcing a splitter comparison at the best cell, not only a size/overlap sweep.
- **Over-overlapping** — 50% overlap doubles the embedding cost and only marginally helps coverage. Caught by step 6 weighing cost against coverage gain.
- **Re-sweeping every 3 months without need** — the optimum drifts only when the corpus structure shifts. Caught by step 6 recommending a documented config comment so the maintainer knows what is locked in and why; cross-link to `auditing-embedding-drift` for the real continuous-monitoring concern.
- **No boundary-failure examples in the report** — a numeric table is unconvincing. Caught by step 5 requiring qualitative examples before any recommendation.

## References

- `reference/chunk-sweep-grid.md` — recommended sweep grids per corpus shape (long-form prose, code, structured docs, FAQ)
- `reference/splitter-cheatsheet.md` — when to use fixed-token vs sentence vs paragraph vs semantic vs AST-aware
- [LangChain text-splitter docs](https://python.langchain.com/docs/concepts/text_splitters/) — splitter API reference (one-level link; the implementation details belong to the framework)
- [LlamaIndex node-parser docs](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/) — alternative framework reference

## Examples

### Example 1: Legal-doc RAG missing cross-paragraph answers (happy-path)

Input: *"My RAG over a 5,000-document legal corpus uses RecursiveCharacterTextSplitter with chunk_size=512, overlap=50. Recent QA spot-checks show it misses answers that span multiple paragraphs. Audit it."*

Output: Skill walks all 6 steps. Inventory: corpus p90 = 12,400 tokens, embedding model `text-embedding-3-large` (max 8191 tokens). Sweep at chunk_size ∈ {400, 800, 1200, 2000}, overlap ∈ {0.10, 0.25, 0.50}. Current cell answer-coverage@5 = 0.62. Best cell: `chunk_size=1200, overlap=0.25` with answer-coverage@5 = 0.81. Splitter comparison at the best cell: paragraph-aware beats fixed-token by 6 points. Recommendation: `chunk_size=1200, chunk_overlap=0.25, splitter=ParagraphSplitter`. Shows 6 boundary-failure examples where the original 512-token chunk cut a clause mid-sentence; the new config retrieves the full paragraph containing the answer.

### Example 2: Pipeline retrieves whole documents (anti-trigger)

Input: *"My RAG over 800 product-spec PDFs retrieves the full PDF for each query and lets the LLM read it. Audit the chunking strategy."*

Output: Skill declines. Explains that the pipeline has no chunking step to audit — the document IS the unit. Notes that full-doc retrieval works for small corpora and large-context models but breaks at scale. Suggests the relevant audits are: prompt token budget (`auditing-prompt-token-budget`), inference latency budget (`auditing-inference-latency-budget`), and whether to introduce chunking + this audit once the corpus crosses the context window.

### Example 3: Tutorial defaults on customer-support FAQ (edge-case)

Input: *"My RAG over 12,000 customer-support Q-A pairs uses chunk_size=1000, overlap=200 from the LangChain quickstart. Audit it."*

Output: Skill flags that an FAQ corpus is structurally one-Q-A-per-document — the chunking config is largely cosmetic because each Q-A is already a self-contained unit. Inventory check: corpus p90 = 180 tokens (well under 1000). Confirms that any chunk_size ≥ 200 produces effectively one-chunk-per-Q-A. Recommendation: drop the chunking layer entirely OR pin `chunk_size=512, overlap=0` and note in a comment that the splitter is a no-op for this corpus shape. Cross-links to `building-rag-eval-set` if no eval QA set exists yet to validate the no-op claim.

## See also

- `ml-datasci/evaluating-rag-retrieval` — separate retrieval failures from generation failures BEFORE auditing chunking
- `ml-datasci/auditing-embedding-drift` — the continuous-monitoring concern (drift over time), sibling to this one-shot audit
- `ml-datasci/building-rag-eval-set` — the prerequisite eval-set construction skill
- `ml-datasci/selecting-embedding-model` — the orthogonal axis (embedding model vs chunking config)
- `ml-datasci/auditing-prompt-token-budget` — for full-doc-retrieval pipelines

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
