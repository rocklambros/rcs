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
