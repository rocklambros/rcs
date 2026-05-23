# Judge prompts for faithfulness and answer relevance

LLM-as-judge scoring is required for the generation-stage metrics. These prompt patterns minimize the common biases.

## Judge-model selection rules

1. **Use a model distinct from the generator.** If GPT-4 generated the answer, do not also use GPT-4 as the judge. Same-family bias inflates faithfulness scores by ~10-20 points in published evaluations.
2. **Pin the judge model version.** A floating "gpt-4o-latest" judge breaks longitudinal comparisons silently.
3. **Use the strongest available judge.** Generation-stage scoring quality is bounded above by judge quality.
4. **Document the judge in the report.** Every metric tied to a judge gets a judge-model footnote.

## Faithfulness prompt

Asks: does every factual claim in the generated answer derive from the retrieved context?

```
You are evaluating a generated answer for faithfulness to a retrieved context.

QUESTION:
{question}

RETRIEVED CONTEXT (the only sources the generator was supposed to use):
{retrieved_chunks}

GENERATED ANSWER:
{generated_answer}

Decompose the generated answer into atomic factual claims (one fact per line).
For each claim, decide whether it is fully supported by the retrieved context.

Output JSON:
{
  "claims": [
    {"claim": "...", "supported": true|false, "evidence": "<verbatim quote from context, or null if unsupported>"}
  ],
  "faithfulness_score": <count of supported claims / total claims>
}
```

## Answer-relevance prompt

Asks: does the answer address the question, or does it restate context tangentially?

```
You are evaluating whether a generated answer is relevant to a question.

QUESTION:
{question}

GENERATED ANSWER:
{generated_answer}

Score on a 0-1 scale:
- 1.0: directly and fully answers the question
- 0.5: partially answers (addresses the topic but misses the specific ask)
- 0.0: does not answer (tangential, refusal, or restates context without addressing the question)

Output JSON:
{
  "score": <0.0 | 0.5 | 1.0>,
  "rationale": "<one sentence>"
}
```

## Context-utilization prompt

Asks: of the retrieved chunks, how many were actually used by the generation?

```
You are evaluating how much of the retrieved context contributed to the generated answer.

RETRIEVED CHUNKS:
{enumerated_chunks}

GENERATED ANSWER:
{generated_answer}

For each chunk, decide whether the answer used information from it (cited, paraphrased, or relied on).

Output JSON:
{
  "chunk_usage": [
    {"chunk_index": 0, "used": true|false}
  ],
  "utilization_score": <count of used chunks / total chunks>
}
```

## Sanity checks for judge output

- Reject judge responses that are not parseable JSON; re-prompt or skip
- Spot-check 10% of judge verdicts by human review per eval run; investigate disagreements
- Track judge-model self-consistency: re-run a 20-question subsample with `temperature = 0` twice and compare; agreement below 90% means the prompt is too ambiguous

## Cohen's κ for judge agreement

When two independent judges score the same set, report Cohen's κ. κ below 0.6 means the judge disagreement is large enough that the metric is not meaningful; tighten the prompts or pick a stronger judge.
