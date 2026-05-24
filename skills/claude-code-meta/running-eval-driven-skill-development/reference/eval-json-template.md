# Eval JSON template

Copy-paste this template for each of the three required eval files per skill. Save as `evals/01-<happy>.json`, `evals/02-<edge>.json`, `evals/03-<anti>.json` under the skill directory.

## Schema

```json
{
  "skill": "<gerund-form-slug>",
  "scenario_id": "0[1-3]-<short-descriptive>",
  "scenario_kind": "happy-path | edge-case | anti-trigger",
  "query": "<verbatim user prompt — what a real user would type>",
  "files": [],
  "expected_behavior": [
    "<rubric item 1 — third-person checkable assertion>",
    "<rubric item 2 — third-person checkable assertion>",
    "<rubric item 3 — third-person checkable assertion>"
  ]
}
```

## Field semantics

| Field | Type | Notes |
|---|---|---|
| `skill` | string | The skill slug; matches the directory name and frontmatter `name`. |
| `scenario_id` | string | `0[1-3]-<short-descriptive>`; matches the eval filename stem. |
| `scenario_kind` | enum | One of `happy-path`, `edge-case`, `anti-trigger`. Exactly one of each per skill. |
| `query` | string | The verbatim user prompt. Write it as a user would type it — including conversational slack and missing context — not as a polished prompt-engineering example. |
| `files` | list[string] | Optional file paths (relative to skill dir) the candidate model should reference. Empty list if none. |
| `expected_behavior` | list[string] | Exactly 3 rubric items. Each must be a third-person checkable assertion. |

## Three example evals

### 01-happy-path

```json
{
  "skill": "auditing-graphql-nullability",
  "scenario_id": "01-mixed-nullability-realistic",
  "scenario_kind": "happy-path",
  "query": "Here is our customer-API GraphQL schema. Some fields are nullable, some aren't, and our product manager is asking which ones we should tighten up. Audit it.",
  "files": ["reference/example-customer-api.graphql"],
  "expected_behavior": [
    "Identifies at least one nullable field where non-null would be safer (e.g., a primary identifier or required relationship)",
    "Distinguishes legitimately-nullable fields (e.g., optional metadata) from over-permissive ones",
    "Recommends a migration path that preserves backward compatibility (deprecate + introduce non-null replacement) rather than a breaking change"
  ]
}
```

### 02-edge-case

```json
{
  "skill": "auditing-graphql-nullability",
  "scenario_id": "02-load-bearing-nullable",
  "scenario_kind": "edge-case",
  "query": "Our `User.email` field is nullable. Should we tighten it to non-null?",
  "files": [],
  "expected_behavior": [
    "Asks for context on WHY email is nullable (anonymized users? OAuth-only accounts? pre-verification state?) before recommending non-null",
    "Names at least one legitimate case where nullable email is correct (e.g., social-login users without verified email)",
    "Does NOT recommend non-null without surfacing the context-dependent tradeoffs"
  ]
}
```

### 03-anti-trigger

```json
{
  "skill": "auditing-graphql-nullability",
  "scenario_id": "03-rest-openapi-not-graphql",
  "scenario_kind": "anti-trigger",
  "query": "Here is our REST API's OpenAPI spec. Audit the nullability of the response fields.",
  "files": ["reference/example-rest-openapi.yaml"],
  "expected_behavior": [
    "Identifies the artifact as OpenAPI / REST, NOT GraphQL",
    "Declines to engage the GraphQL-specific workflow and explains the schemas are not equivalent",
    "Recommends an OpenAPI-specific nullability skill or general schema-design skill instead"
  ]
}
```

## Validation tips

- Read each rubric item aloud and ask: *"Could a judge mark this pass / fail without subjective interpretation?"* If no, rewrite.
- Avoid rubric items that require the response to use a specific exact phrase. Match intent, not phrasing.
- For anti-trigger scenarios, ensure the query has surface features that make the wrong skill look applicable; otherwise the test is too easy.
