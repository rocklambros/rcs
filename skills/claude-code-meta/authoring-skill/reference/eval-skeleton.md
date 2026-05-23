# Eval skeleton

Three scenarios per skill, one JSON file each, under `evals/`. Exactly 3 rubric items per scenario.

## 01-happy-path

```json
{
  "skill": "<slug>",
  "scenario_id": "01-<short-descriptive>",
  "scenario_kind": "happy-path",
  "query": "<verbatim user prompt — the canonical positive case>",
  "files": [],
  "expected_behavior": [
    "<Third-person assertion about the response — checkable 0/1>",
    "<Second assertion — falsifiable>",
    "<Third assertion — names a concrete artifact the response should contain>"
  ]
}
```

## 02-edge-case

```json
{
  "skill": "<slug>",
  "scenario_id": "02-<short-descriptive>",
  "scenario_kind": "edge-case",
  "query": "<query that hits a known assumption violation, ambiguity, missing data, or edge condition>",
  "files": [],
  "expected_behavior": [
    "<Asserts the response identifies the edge case rather than blindly applying the happy path>",
    "<Asserts the response chooses the correct alternative (different method, hand-off, etc.)>",
    "<Asserts the response cites the specific signal that drove the alternative choice>"
  ]
}
```

## 03-anti-trigger

```json
{
  "skill": "<slug>",
  "scenario_id": "03-<short-descriptive>",
  "scenario_kind": "anti-trigger",
  "query": "<query that should NOT engage this skill — adjacent topic, different concept, out of scope>",
  "files": [],
  "expected_behavior": [
    "<Asserts the response does NOT engage the skill's workflow>",
    "<Asserts the response explains why this skill doesn't apply>",
    "<Asserts the response hands off to the correct alternative (named skill, different tool, different category of work)>"
  ]
}
```

## Rubric writing rules

| Rule | Why |
|---|---|
| Each rubric item is a third-person assertion about the response | Lets a judge model score 0/1 mechanically |
| Each rubric item is falsifiable | "The response is helpful" is unjudgeable; "The response names Wilcoxon signed-rank" is judgeable |
| Don't restate the query in the rubric | The rubric scores what the response did, not what the query said |
| Anti-trigger rubrics include a "does NOT" item | The whole point is verifying the skill DOESN'T fire |
| Exactly 3 items | Matches the v1 pass-threshold math; v2+ may extend to 5 with reweighted thresholds |

## Pass thresholds (Sonnet-only PRAGMATIC)

| Scenario | Threshold |
|---|---|
| happy-path | 3/3 |
| edge-case | 3/3 |
| anti-trigger | ≥ 2/3 |

For full 3-model thresholds (Haiku / Sonnet / Opus), see `docs/eval-protocol.md` in the RCS root.
