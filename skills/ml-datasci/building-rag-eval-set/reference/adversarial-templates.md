# Adversarial Q-A templates

Templates for drafting the adversarial split. The adversarial set stress-tests retrieval and generation. Failures here are expected and informative, not blocking.

## 1. Absent-topic (the answer is NOT in the corpus)

Tests whether the system refuses to fabricate an answer when retrieval returns irrelevant chunks. A RAG system that hallucinates a confident answer here is broken; a RAG system that says "I don't have information about that" is healthy.

Templates:

- "What is the company's policy on [topic that is plausibly HR-adjacent but not covered]?"
- "How does [product feature that doesn't exist] work?"
- "Who is the manager of [a person not in the org chart]?"
- "When was [an event that didn't happen] scheduled?"

Calibration tip: include 2-3 absent-topic queries about subtly out-of-corpus topics (e.g., similar to a covered topic but with one specific detail not in any source) — these are the hardest because retrieval will return near-misses that look relevant.

Expected answer in the Q-A row: an explicit refusal pattern (e.g., "Based on the provided documents, I cannot find information about X.").

## 2. Multi-hop synthesis across many documents

Tests whether retrieval surfaces multiple relevant docs AND whether the generator can combine them coherently.

Templates:

- "Compare the [policy/feature/process] in [document A] with [document B]."
- "Calculate the total [metric] across [region 1], [region 2], and [region 3] from the [data source documents]."
- "List all employees mentioned in both [report 1] and [report 2]."
- "What changes were introduced between [policy version N-1] and [policy version N]?"

These require:

- Retrieval to return 2+ correct documents (not just top-1)
- Generation to synthesize without losing facts from any of them

The `source_spans` field on these rows should contain entries from MULTIPLE `source_doc_id` values.

## 3. Distractor-rich queries

Tests whether retrieval can pick the RIGHT chunk when many chunks look superficially relevant.

Templates:

- Use a query containing terms that appear in many irrelevant chunks (e.g., "parental leave" when most chunks discuss "leave" in some form)
- Include numeric ranges that overlap across multiple chunks (e.g., "employees over 5 years" when seniority thresholds appear in many policies)
- Reference a concept by a synonym not used in the source doc (e.g., query says "vacation," source says "PTO")

The ground-truth `source_doc_id` is one specific document; the test is whether retrieval surfaces THAT document over the look-alikes.

## 4. Ambiguous queries (calibration only, not held-out)

Tests how the system handles genuinely ambiguous questions where multiple defensible answers exist.

Templates:

- "What is the leave policy?" (multiple leave types exist)
- "How much PTO do I get?" (depends on tenure, role, region)
- "Is remote work allowed?" (depends on role and team)

For these, mark `ambiguity_flag=true`. The acceptable answer set is broader — the test is whether the system asks for clarification or surfaces ALL the candidate answers, not whether it picks one.

These belong in calibration, NOT held-out test. Ambiguous-query scoring is unreliable for headline test metrics; it's useful for prompt-tuning during dev.

## 5. Temporal / version-sensitive queries

Tests whether the system retrieves the CURRENT version of a document when older versions also exist in the corpus.

Templates:

- "What is the current [policy/spec/rate]?"
- "What's the latest [version/revision] of [document]?"

The `source_doc_id` should be the latest version; the failure mode is retrieving an older version that contains different content.

## Coverage targets

For a 30-row adversarial split (default), recommended distribution:

| Template | Count |
|---|---|
| Absent-topic | 12 |
| Multi-hop synthesis | 8 |
| Distractor-rich | 6 |
| Temporal | 4 |

Ambiguous queries go in calibration, not adversarial.

## What adversarial is NOT for

- Replacing the held-out test set (adversarial is for stress; held-out is for honest end-of-cycle measurement)
- Tuning retrieval thresholds (use calibration for that)
- Publishing as a "the model passed our adversarial tests" claim without context — adversarial failures are expected; the headline number is the held-out test result, with adversarial as supporting context
