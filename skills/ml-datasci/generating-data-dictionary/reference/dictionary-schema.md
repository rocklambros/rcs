# Data-dictionary JSON Schema

The machine-readable output format. Validates with any JSON Schema Draft 2020-12 validator.

## Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RCS data dictionary",
  "type": "object",
  "required": ["dataset", "row_count", "columns", "generated_at"],
  "properties": {
    "dataset": {
      "type": "string",
      "description": "Identifier for the dataset (path, URL, or name)."
    },
    "row_count": {
      "type": "integer",
      "minimum": 0
    },
    "sample_size": {
      "type": "integer",
      "description": "If the dictionary was generated from a sample, this is the sample size. Equal to row_count for full scans."
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "generator_version": {
      "type": "string",
      "description": "Version of the skill that generated this dictionary (e.g., generating-data-dictionary@0.1.0)."
    },
    "columns": {
      "type": "array",
      "items": { "$ref": "#/$defs/column" }
    },
    "issues": {
      "type": "array",
      "items": { "$ref": "#/$defs/issue" }
    }
  },
  "$defs": {
    "column": {
      "type": "object",
      "required": ["name", "dtype", "null_pct", "unique_count", "semantic_class", "role"],
      "properties": {
        "name": { "type": "string" },
        "dtype": { "type": "string" },
        "null_count": { "type": "integer", "minimum": 0 },
        "null_pct": { "type": "number", "minimum": 0, "maximum": 100 },
        "unique_count": { "type": "integer", "minimum": 0 },
        "semantic_class": {
          "type": "string",
          "enum": ["id", "boolean", "categorical", "ordinal", "continuous", "datetime", "text"]
        },
        "role": {
          "type": "string",
          "enum": ["identifier", "feature", "target", "temporal", "pii", "leakage-risk", "unknown"]
        },
        "range_numeric": {
          "type": "object",
          "properties": {
            "min": { "type": ["number", "null"] },
            "max": { "type": ["number", "null"] },
            "mean": { "type": ["number", "null"] },
            "median": { "type": ["number", "null"] },
            "std": { "type": ["number", "null"] }
          }
        },
        "top_values": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["value", "count", "pct"],
            "properties": {
              "value": {},
              "count": { "type": "integer" },
              "pct": { "type": "number" }
            }
          }
        },
        "range_datetime": {
          "type": "object",
          "properties": {
            "min": { "type": ["string", "null"], "format": "date-time" },
            "max": { "type": ["string", "null"], "format": "date-time" }
          }
        },
        "sample_values": {
          "type": "array",
          "items": {}
        },
        "notes": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "issue": {
      "type": "object",
      "required": ["column", "severity", "kind", "message"],
      "properties": {
        "column": { "type": "string" },
        "severity": { "enum": ["blocking", "warn", "info"] },
        "kind": {
          "type": "string",
          "description": "Short identifier: 'range-implausible', 'cardinality-alarm', 'sentinel-pattern', 'mixed-types', 'pii-shape', 'constant', etc."
        },
        "message": { "type": "string" }
      }
    }
  }
}
```

## Example output

```json
{
  "dataset": "data/patients_2026.csv",
  "row_count": 50000,
  "sample_size": 50000,
  "generated_at": "2026-05-23T14:32:00Z",
  "generator_version": "generating-data-dictionary@0.1.0",
  "columns": [
    {
      "name": "patient_id",
      "dtype": "int64",
      "null_count": 0,
      "null_pct": 0.0,
      "unique_count": 50000,
      "semantic_class": "id",
      "role": "identifier",
      "range_numeric": { "min": 100001, "max": 150000 },
      "sample_values": [100001, 123456, 149999],
      "notes": ["unique count equals row count; do not use as feature"]
    },
    {
      "name": "age",
      "dtype": "int64",
      "null_count": 100,
      "null_pct": 0.2,
      "unique_count": 102,
      "semantic_class": "continuous",
      "role": "feature",
      "range_numeric": { "min": 0, "max": 250, "mean": 54.2, "median": 53, "std": 18.1 },
      "sample_values": [45, 67, 23],
      "notes": ["max value 250 is implausible; likely data-entry error or sentinel"]
    }
  ],
  "issues": [
    {
      "column": "age",
      "severity": "warn",
      "kind": "range-implausible",
      "message": "max=250 exceeds plausible human age; investigate before modeling"
    }
  ]
}
```

## Round-trippable

A dictionary emitted by this skill can be re-loaded, mutated (e.g., a human adds Notes), and re-emitted without information loss. Downstream tools can rely on the schema.
