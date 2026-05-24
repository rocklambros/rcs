# Chunk-size × overlap sweep grids per corpus shape

Default sweep grids the `auditing-chunking-strategy` skill uses, tuned to the document structure of the corpus. All sizes are in **tokens** (encoded with the same tokenizer as the embedding model — `tiktoken` for OpenAI, `voyage-tokenizer` for Voyage, etc.). Overlap is a fraction of `chunk_size`.

## Long-form prose (legal, regulatory, scientific, books)

Corpus p90 length is usually > 5,000 tokens. Answers commonly span 2-3 paragraphs.

| chunk_size (tokens) | overlap fractions to sweep |
|---|---|
| 400 | 0.10, 0.25, 0.50 |
| 800 | 0.10, 0.25, 0.50 |
| 1200 | 0.10, 0.25 |
| 2000 | 0.10, 0.25 |

Skip `chunk_size=200` for this shape — too small for prose answers; recall@k climbs but answer-coverage collapses.

Skip `overlap=0` for this shape — boundary failures dominate without overlap.

## Code / docstring corpora

Corpus is structured (functions, classes). The right splitter is AST-aware, not size-based.

| chunk_size (tokens) | overlap fractions to sweep |
|---|---|
| 200 | 0.0, 0.10 |
| 400 | 0.0, 0.10 |
| 800 | 0.0, 0.10 |

Force splitter comparison: `fixed-token`, `code-block` (AST-aware via `tree-sitter` or framework equivalent), `function`. AST-aware almost always wins on code.

Skip large overlaps — code blocks have natural boundaries; overlap mainly bloats embedding cost.

## Customer-support FAQ / knowledge-base Q-A pairs

Corpus is one self-contained Q-A per document; chunking is largely cosmetic.

| chunk_size (tokens) | overlap fractions to sweep |
|---|---|
| 512 | 0.0 |
| 1024 | 0.0 |

Recommendation almost always: drop chunking entirely OR pin a size that captures the p99 Q-A length with overlap=0.

## Structured documents (tables, forms, contracts with numbered sections)

Section markers (Roman numerals, numbered clauses, table boundaries) are stronger signals than token count.

| chunk_size (tokens) | overlap fractions to sweep |
|---|---|
| 800 | 0.10, 0.25 |
| 1200 | 0.10, 0.25 |

Force splitter comparison: `fixed-token`, `paragraph`, `section-aware` (custom regex on the numbering pattern). Section-aware usually wins.

## Chat / dialogue logs

Turn boundaries are the structural signal.

| chunk_size (tokens) | overlap fractions to sweep |
|---|---|
| 400 | 0.0, 0.25 |
| 800 | 0.0, 0.25 |

Force splitter comparison: `fixed-token`, `turn-aware` (split on speaker change). Turn-aware almost always wins.

## Cost reference

For each cell, the embedding-pass cost is approximately:

```
cost = total_corpus_tokens * (1 + overlap_fraction) / chunk_size * cost_per_chunk_embedded
```

A 1M-token corpus at `chunk_size=800, overlap=0.25` produces 1562 chunks; at `text-embedding-3-large` ($0.13/1M input tokens) the pass costs ~$0.16. The 20-cell default grid sweep is ~$3.20 per 1M corpus tokens. Trim the grid if cost is the constraint; do NOT trim if quality is.

## What this grid will NOT find

- Embedding-model selection: hold embedding model fixed during the chunking sweep; vary it in a separate `selecting-embedding-model` audit
- Reranker effects: a reranker can rescue some boundary failures; the chunking sweep should run WITHOUT the reranker so the chunking signal is clean
- Hybrid retrieval (BM25 + vector): same — sweep chunking with vector-only retrieval; layer hybrid on top after the chunking decision is locked
