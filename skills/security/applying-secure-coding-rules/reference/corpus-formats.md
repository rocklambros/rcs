# Corpus formats — per-format indexing recipe

This skill accepts five corpus shapes. Each has a different indexing recipe.

## semgrep rule pack

**Detection:** directory containing `.yaml` files whose top-level key is `rules:`.

**Per-rule schema (semgrep):**

```yaml
rules:
  - id: <rule-id>
    pattern: <pattern>
    message: <human-readable description>
    severity: ERROR | WARNING | INFO
    languages: [python | javascript | typescript | go | ...]
    metadata:
      category: security
      cwe: CWE-79
      framework: <optional framework hint>
      applies_to: <optional, custom>
```

**Indexing steps:**

1. Walk the directory, parse every `*.yaml` / `*.yml` file
2. Extract `rules:` arrays from each
3. For each rule, capture: `id`, `message`, `severity`, `languages`, `metadata.framework` (if present), `metadata.applies_to` (if present)
4. If `applies_to` is missing, fall back to `languages` as the applicability hint
5. Pattern hints — scan the `pattern:` text for framework imports (e.g., `from fastapi import` → FastAPI; `import langchain` → LangChain) to infer additional applicability tags

**Application:** run `semgrep --config <rule-file> <target> --json` for the applicable subset. Parse the resulting findings array.

## SARIF rule pack

**Detection:** `.sarif` file whose top-level structure has `runs[].tool.driver.rules[]`.

**Per-rule schema (SARIF):**

```json
{
  "id": "<rule-id>",
  "name": "<rule-name>",
  "shortDescription": {"text": "..."},
  "fullDescription": {"text": "..."},
  "defaultConfiguration": {"level": "error|warning|note"},
  "properties": {
    "tags": ["security", "python", "fastapi"],
    "precision": "high|medium|low"
  }
}
```

**Indexing steps:**

1. Parse the SARIF JSON
2. Extract `runs[].tool.driver.rules[]`
3. For each rule, capture: `id`, `name`, `shortDescription.text`, `defaultConfiguration.level`, `properties.tags`
4. Use `properties.tags` as the applicability hint (tag values like `python`, `fastapi`, `langchain` indicate stack)

**Application:** if the user already ran the SARIF-emitting tool against the target, parse `runs[].results[]` for matches. Otherwise, ask the user to run the tool and provide the output SARIF.

## Markdown rule sheets (claude-secure-coding-rules style)

**Detection:** directory containing per-rule markdown files with YAML frontmatter.

**Per-rule frontmatter schema:**

```yaml
---
id: SC-FA-002
title: FastAPI route accepts dict from body without Pydantic model
severity: medium
category: input-validation
applies_to:
  language: python
  framework: fastapi
pattern: |
  Function decorated with @app.post / @app.put / @app.patch / @app.delete
  taking a parameter typed as `dict` (not a Pydantic BaseModel).
fix: Replace `body: dict` with a Pydantic BaseModel.
---
```

The markdown body explains rationale, examples, and references.

**Indexing steps:**

1. Walk the directory, parse every `*.md` file's frontmatter
2. Capture: `id`, `title`, `severity`, `category`, `applies_to`, `pattern` (human-readable), `fix`
3. If a rule lacks `applies_to`, mark its applicability as "unknown — review pattern"

**Application:** rules without machine-checkable patterns are surfaced as "human-review-required" findings against files matching the `applies_to` scope. For rules with grep-able or AST-walkable patterns described in the body, apply them manually.

## YAML rule pack

**Detection:** single `rules.yaml` (or similar) at the corpus root with a top-level `rules:` list whose items match the markdown frontmatter schema above.

**Indexing steps:** parse the YAML, treat the `rules:` list as a flat array of rule objects with the same schema as the markdown frontmatter.

**Application:** same as markdown rule sheets.

## claude-secure-coding-rules convention

**Detection:** repository whose README references the `claude-secure-coding-rules` convention or whose layout matches:

```
rules/
  README.md
  python/
    fastapi/
      SC-FA-001.md
      SC-FA-002.md
    flask/
      ...
    langchain/
      ...
  javascript/
    react/
      ...
    nextjs/
      ...
```

**Indexing steps:**

1. Read the README to learn convention specifics (rule-id prefix, severity scale, applies_to schema)
2. Walk `rules/<language>/<framework>/*.md` — each file is one rule in markdown-rule-sheet format
3. Treat the directory path as additional applies_to context (e.g., `rules/python/fastapi/` implies `applies_to: {language: python, framework: fastapi}`)

**Application:** same as markdown rule sheets.

## Corpus revision capture

For ANY corpus format, capture and record in the report header:

- Corpus path or URL
- Corpus revision: git commit SHA (`git -C <corpus> rev-parse HEAD`), file mtime, or a pack version string
- Number of rules indexed

Without this metadata, the audit is not reproducible.
