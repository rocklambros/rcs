# Splitter cheatsheet

When to use which splitter, based on document structure. The chunking-strategy audit's step 6 picks one of these.

| Splitter | When it fits | When it fails |
|---|---|---|
| `fixed-token` (`RecursiveCharacterTextSplitter` defaults) | Truly unstructured prose; small corpora where the structure is noisy enough that nothing else helps | Anything structured — cuts mid-sentence, mid-table, mid-function, mid-clause |
| `sentence` (NLTK / spaCy sentence segmenter) | Short-form factual content; news; encyclopedia entries | Multi-sentence answers where one sentence depends on the previous one for context |
| `paragraph` (split on blank lines, then merge to target `chunk_size`) | Long-form prose; essays; reports; most legal documents | Documents without paragraph breaks (single-block PDFs); chat logs |
| `semantic` (LangChain `SemanticChunker`, embedding-similarity-based split points) | Mixed-topic long documents where paragraph boundaries don't match topic boundaries | Computationally expensive at index time; flaky on noisy corpora; needs careful similarity threshold |
| `section-aware` (regex on numbering / headings) | Documents with explicit numbering (legal contracts, regulations, technical specs) | Documents without consistent structure markers |
| `turn-aware` (split on speaker change) | Chat logs, dialogue transcripts, support tickets | Anything not dialogue |
| `AST-aware` (tree-sitter or language-specific) | Source code | Anything not source code |
| `markdown-aware` (split on headings + code-block awareness) | Markdown documentation, READMEs, technical writing in MD | Non-markdown content; markdown with inconsistent heading depth |

## How to pick during the audit

1. After the size+overlap sweep locks the best `(chunk_size, overlap)` cell, run that cell across the candidate splitters
2. Score each splitter on `answer-coverage@k` against the same eval QA set
3. Pick the structure-aware splitter that wins by ≥ 3 points over `fixed-token`; if the gap is < 3 points, prefer the simpler splitter (less maintenance, faster indexing)

## Frameworks

- LangChain: `langchain_text_splitters` module (RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter, SemanticChunker, CharacterTextSplitter)
- LlamaIndex: `node_parser` module (SentenceSplitter, MarkdownNodeParser, SemanticSplitterNodeParser, HierarchicalNodeParser)
- Haystack: `PreProcessor` with `split_by` parameter (word, sentence, passage)
- DIY: a 30-line paragraph splitter beats a misconfigured framework splitter every time

## Don't combine splitters

A pipeline that runs `markdown-aware` then `fixed-token` as a fallback re-introduces every boundary-failure the markdown splitter was meant to avoid. Pick one. If the corpus is heterogeneous (some MD, some plain prose), route by file extension at ingest, not at chunking.
