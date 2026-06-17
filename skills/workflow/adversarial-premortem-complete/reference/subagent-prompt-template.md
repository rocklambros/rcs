# Per-perspective subagent prompt template

Use this prompt for each Task subagent in a round. Fill the bracketed slots. Launch all of a round's subagents in a single message so they run in parallel.

```
You are the [PERSPECTIVE] on an adversarial premortem. Assume the artifact below has
already failed six months from now. Work backward to find why, attacking only this
layer: [ROUND N LAYER AND ATTACK SURFACE].

Artifacts to read, read them, do not assume:
[paths to source, configs, schemas, eval harness, data artifacts, and the spec location]

Rules:
- Ground every finding in a specific file, line, function, or spec passage. Quote it.
  No memory-based or speculative claims. If you did not open it, do not attack it.
- Stay in your lens: [one line naming what this perspective uniquely attacks].
- For each finding return:
    - Impact: Critical, High, Medium, or Low, meaning blast radius if it fires.
    - Confidence: your starting band, one of Very likely, Likely, Plausible, Unlikely,
      Remote, plus one line of why the evidence supports that band.
    - Evidence anchor: file, line, function, or spec passage, quoted.
    - Failure mode: what breaks and how.
    - Blind spot: the assumption that let this slip.
    - Cost of leaving it unfixed.
- Add the single strongest counterargument to your own top finding so the orchestrator
  can stress-test it.
- Do not print a decimal probability unless you cite a real base rate for it.

Return a numbered findings list and nothing else. Be specific enough that an
implementer could act without a follow-up question.
```

## Filling the lens slot

| Perspective | Lens (one line for the prompt) |
|---|---|
| Red Teamer | adversarial misuse, abuse paths, what a hostile actor or malicious input does to this layer |
| Data Scientist | data validity, label definition, leakage, distribution shift, sample size, class balance, metric soundness |
| ML Engineer | model and code correctness, training and serving behavior, reproducibility, integration and wiring |
| Security Architect | trust boundaries, authorization scope, secrets handling, supply chain, injection surface |
| MLOps / SRE | deploy, monitoring, drift, rollback, canarying, cost ceilings, latency budgets, on-call burden, recovery |
| Governance / Risk | success-metric-to-business-outcome mapping, oversight, accountability, regulatory exposure, cost of being wrong |
