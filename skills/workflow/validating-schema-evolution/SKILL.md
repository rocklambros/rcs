---
name: validating-schema-evolution
description: >
  Validates schema changes between dataset / table / API revisions — diffs old
  vs new schema, classifies each change as breaking (column drop, type change,
  non-null added without default, primary-key change), non-breaking (column add
  with default, type widening), or ambiguous (rename), and produces a migration
  script scaffold per breaking change. Use whenever a dataset's schema is
  about to change, whenever a downstream consumer reports unexpected nulls or
  type errors after an upstream refresh, or whenever an API version bump is
  being reviewed for backwards compatibility.
version: 0.1.0
status: shipped
track: workflow
audience: [data-engineer, data-scientist, backend-engineer]
evidence:
  - genai_agentic_incidents
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
last-updated: 2026-05-23
---

# Validating Schema Evolution

## When to use

Trigger this skill when the user asks for or implies one of:

- A dataset's schema is about to change (column added, renamed, dropped, retyped) and downstream pipelines may break
- A downstream consumer just started failing after an upstream refresh and the user suspects a schema-drift cause
- An API version bump is being reviewed for backwards-compatibility before release
- A migration script needs to be written to move a production table from schema vN to schema vN+1
- A column type is being widened (int → bigint, varchar(50) → varchar(255)) or narrowed (the reverse)
- A "rename" change needs to be classified — is it a true rename (data preserved) or a drop-and-add (data lost)?

## When NOT to use

Skip this skill and hand off when:

- The store is schema-less (MongoDB document bag, key-value blob storage) where there is no enforced schema to diff
- The change is a pure data refresh (same schema, new rows) — no schema evolution to validate
- The user is designing a brand-new schema from scratch with no predecessor (different skill: schema design)
- The change is a column-DESCRIPTION update (comment / doc) with no structural impact

## Quick start

User says: "We're renaming `customer_email` to `email_address` in our users table. Is that safe?"

Skill response: classifies "rename" as AMBIGUOUS — the surface name change is non-breaking IF data is preserved and downstream code is updated, but a naive `DROP customer_email; ADD email_address` is data-destroying. Recommends the safe two-step pattern (add new + backfill + dual-write + flip readers + drop old) and produces a migration script scaffold.

Schema diff output format:

```
Schema diff: users v3 → v4

BREAKING:
- DROP column `legacy_id` (int)               severity: blocking; downstream consumers count: 4

NON-BREAKING:
+ ADD column `created_at` (timestamp, default NOW())

AMBIGUOUS (operator confirmation required):
~ RENAME `customer_email` → `email_address`   severity: warn; default to data-preserving rename, NOT drop-and-add

Migration script scaffold: see `migrate_users_v3_to_v4.sql`
```

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| old_schema | path \| string | yes | — | The old schema: SQL `CREATE TABLE`, Pydantic / dataclass model, Avro / JSON Schema, Parquet metadata, OpenAPI spec. |
| new_schema | path \| string | yes | — | The new schema in the same format. |
| consumers | list | no | inferred | Downstream consumers that depend on this schema. Inferred via grep if a repo path is provided. |
| store | "postgres" \| "mysql" \| "sqlite" \| "bigquery" \| "snowflake" \| "parquet" \| "api" | no | postgres | Which store the migration script should target. Drives the SQL dialect. |
| allow_breaking | bool | no | false | If true, the skill produces a destructive migration. If false (default), breaking changes are flagged and the script refuses to drop. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as the validation progresses:

```
Schema-evolution validation progress:
- [ ] Parse old and new schemas into a common representation (column name, type, nullability, default, constraints)
- [ ] Diff columns: dropped, added, renamed (heuristic), retyped, nullability-changed, default-changed
- [ ] Classify each change as breaking / non-breaking / ambiguous
- [ ] For each breaking change, identify the downstream consumers affected
- [ ] Produce a migration-script scaffold with safe two-step patterns for ambiguous changes
- [ ] If consumers exist: produce a deprecation notice template
```

### Step 1: Parse schemas

Read both schemas. For each column, capture: `name`, `type`, `nullable`, `default`, `primary_key`, `unique`, `foreign_key`. If the schema format is loose (JSON Schema, Parquet metadata), be explicit about which signals are available.

### Step 2: Diff and classify

See `reference/change-classification.md` for the full rule table. Summary:

| Change | Classification | Rationale |
|---|---|---|
| ADD column nullable / with default | non-breaking | Old code keeps working |
| ADD column NOT NULL no default | breaking | Existing rows fail constraint |
| DROP column | breaking | Readers of the column break |
| RENAME column | ambiguous | Safe IF data-preserving + dual-name window + reader update; unsafe if naively drop-and-add |
| Type WIDEN (int → bigint, varchar(50) → varchar(255)) | non-breaking | Old values still fit |
| Type NARROW (bigint → int, varchar(255) → varchar(50)) | breaking | Existing values may overflow / truncate |
| Type CHANGE (int → varchar) | breaking | Casts may fail; downstream code may rely on type |
| Nullability ADD (column → NOT NULL) | breaking | Existing nulls violate constraint |
| Nullability DROP (column → nullable) | non-breaking | Old code still gets non-null in practice |
| Default ADD | non-breaking | Old code still supplies values |
| Default DROP | breaking-warn | INSERTs without the column may now fail |
| Default CHANGE | warn | Quiet behavior change |
| Primary-key CHANGE | breaking | Foreign-key references break; identity semantics change |

### Step 3: Identify rename candidates

A rename is NOT a directly-encoded operation in most schema formats — it appears as `DROP column X; ADD column Y`. The skill must heuristically identify renames by inspecting:

- Same column position
- Compatible types
- Similar names (Levenshtein distance, prefix/suffix match)
- Comment / description preservation
- An explicit `RENAME` annotation in the migration metadata (if present)

When a candidate rename is found, report it as AMBIGUOUS and ask the operator to confirm before generating SQL.

### Step 4: Identify affected consumers

If a repository path is provided, `grep -r "old_column_name"` across:

- Application code (`.py`, `.ts`, `.go`, `.rb`)
- SQL files (`*.sql`)
- ORM models (Django, SQLAlchemy, Prisma, Sequelize)
- Dashboard / report configs (Looker, Tableau, Metabase YAML)
- DBT model files (`models/**/*.sql`, `models/**/*.yml`)

Each occurrence is a consumer that must be updated before the breaking change ships.

### Step 5: Produce migration script

See `reference/migration-patterns.md` for the per-store SQL patterns. For ambiguous renames, default to the safe two-step:

1. Add new column
2. Backfill new from old
3. Dual-write window (writers update both; readers prefer new, fall back to old)
4. Flip readers to new only
5. Drop old column

For breaking changes when `allow_breaking: false`, the script REFUSES to drop and prints a deprecation-notice template instead.

## Outputs

A markdown validation report with:

1. **Diff summary** — counts of breaking / non-breaking / ambiguous changes
2. **Per-change findings** — name, classification, severity, rationale, suggested fix
3. **Affected consumers** — file:line references for every breaking column
4. **Migration script scaffold** — store-appropriate SQL with safe defaults
5. **Deprecation notice template** — for consumers that need advance warning

## Failure modes

Known pitfalls in schema-evolution validation:

- **Naive drop-and-add masquerading as rename** — `DROP customer_email; ADD email_address` looks like a rename but loses all data. Caught by: Step 3 explicitly flags rename candidates as AMBIGUOUS and requires operator confirmation.
- **NOT-NULL added without default** — existing rows violate the constraint and the migration fails mid-flight, sometimes after partial commits. Caught by: Step 2 classifies as breaking; recommended pattern is "add nullable + backfill + add NOT-NULL constraint".
- **Type narrowing silently truncates** — bigint → int causes values > 2^31 to overflow on next write. Caught by: Step 2 classifies as breaking; recommended pattern is "scan max value before narrowing".
- **Primary-key change breaks FK references** — changing the PK column or its type silently breaks every foreign key that references it. Caught by: Step 2 PK changes are always breaking; the script also enumerates inbound FKs.
- **Default change is invisible to readers but changes new-row behavior** — a column's default goes from `0` to `NULL`; downstream readers seeing "no value supplied" now get NULL where they used to get 0. Caught by: Step 2 default-CHANGE is a warn-level finding with explicit "quiet behavior change" note.
- **Floating semantic-version comparison** — comparing `schema_version` strings via lexicographic order ("v10" < "v9"). Caught by: parse schema versions as SemVer tuples, not strings (covered in `reference/migration-patterns.md`).

## References

- `reference/change-classification.md` — full diff rule table with rationales
- `reference/migration-patterns.md` — store-specific SQL migration patterns (Postgres, MySQL, BigQuery, Snowflake, Parquet via Arrow)
- [Postgres ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) — upstream reference for locking semantics of each change
- [Avro schema evolution rules](https://avro.apache.org/docs/current/specification/#schema-resolution) — formal compatibility rules; useful as a model

## Examples

### Example 1: Column rename audit (happy-path)

Input: "We're renaming `customer_email` to `email_address` on a 50M-row users table. Here are the old and new CREATE TABLE statements. Is the change safe?"

Output: Skill parses both schemas, identifies the same-position + compatible-type + similar-name pattern as an AMBIGUOUS rename candidate. Refuses to generate a one-shot `DROP customer_email; ADD email_address` (data-destroying). Produces the safe five-step pattern as a migration script: (1) ADD `email_address` NULL, (2) UPDATE backfill from `customer_email`, (3) dual-write trigger or app-layer code change, (4) flip readers, (5) DROP `customer_email`. Names the lock-acquisition window for each step on a 50M-row table and recommends running steps 1, 2, 5 in `ONLINE` mode where the store supports it.

### Example 2: NOT NULL added to existing column (edge-case)

Input: "I want to add `NOT NULL` to the `signup_source` column. The table has 1.2M rows and an unknown fraction have NULL. What's the safe migration?"

Output: Skill flags as BREAKING. Recommends the three-step pattern: (1) backfill NULLs with a sentinel value (`'unknown'` or `'__legacy__'`) via batched `UPDATE WHERE signup_source IS NULL`, (2) `ALTER COLUMN signup_source SET DEFAULT 'unknown'`, (3) `ALTER COLUMN signup_source SET NOT NULL` (which scans the table — propose running in a maintenance window OR using `pg_repack` / `gh-ost` for online execution). Refuses to emit step (3) before step (1) completes.

### Example 3: Schema-less store (anti-trigger)

Input: "Our MongoDB collection stores user events as free-form documents. We want to start including a `device_id` field on new events. Validate the schema evolution."

Output: Skill explains that MongoDB without enforced schema validation has no schema diff to perform; the "evolution" is purely a writer-side convention. Recommends instead: (a) enable MongoDB `$jsonSchema` validation on the collection (turning it into a checked schema, which would make this skill applicable going forward), or (b) use application-level Pydantic / Zod models and version them. Does NOT produce a SQL migration script. Hands off.

## See also

- `workflow/auditing-source-provenance` — pairs with this skill; provenance plus schema-version lets you reconstruct which rows used which schema
- `workflow/deduplicating-records` — dedupe across schema versions is its own problem class; the column-set must be reconciled first
- `ml-datasci/generating-data-dictionary` — the per-column reference that schema-diff consumes; useful to regenerate after every migration
- `workflow/pinning-reproducible-environments` — pinning the migration-tool version (Alembic, Flyway) is the environment-side counterpart to schema versioning

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from genai_agentic_incidents CHANGELOG.md schema migrations, DU-MSDSAI-4432-* notebook column-rename patterns
