# Migration Patterns by Store

Safe migration scaffolds per change type and per store. Always pair with a rollback plan and a backup.

## Postgres

### Safe rename (5-step)

```sql
-- Step 1: add new column
ALTER TABLE users ADD COLUMN email_address varchar(255);

-- Step 2: backfill in batches (avoid long-running UPDATE)
UPDATE users SET email_address = customer_email WHERE id IN (
  SELECT id FROM users WHERE email_address IS NULL LIMIT 10000
);
-- Repeat until 0 rows updated.

-- Step 3: dual-write window (trigger OR app-layer code)
CREATE OR REPLACE FUNCTION sync_email() RETURNS trigger AS $$
BEGIN
  IF NEW.email_address IS DISTINCT FROM NEW.customer_email THEN
    NEW.customer_email := NEW.email_address;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_email_trigger BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION sync_email();

-- Step 4: flip all readers in application code; verify with telemetry

-- Step 5: drop old column
DROP TRIGGER sync_email_trigger ON users;
DROP FUNCTION sync_email();
ALTER TABLE users DROP COLUMN customer_email;
```

### Safe NOT-NULL add (3-step)

```sql
-- Step 1: backfill NULLs in batches
UPDATE users SET signup_source = 'unknown' WHERE id IN (
  SELECT id FROM users WHERE signup_source IS NULL LIMIT 10000
);
-- Repeat until 0 rows updated.

-- Step 2: set default (so future INSERTs that omit work)
ALTER TABLE users ALTER COLUMN signup_source SET DEFAULT 'unknown';

-- Step 3: add the NOT NULL constraint (scans the table — for large tables
-- consider pg_repack or pt-online-schema-change)
ALTER TABLE users ALTER COLUMN signup_source SET NOT NULL;
```

### Type widening (online)

```sql
-- bigint widening from int — safe, fast, no rewrite on modern Postgres
ALTER TABLE orders ALTER COLUMN customer_id TYPE bigint;
```

### Type narrowing (PRE-FLIGHT REQUIRED)

```sql
-- BEFORE narrowing, scan max value:
SELECT max(customer_id), max(length(notes)) FROM orders;
-- If max fits in the narrow type, proceed; otherwise refuse.

ALTER TABLE orders ALTER COLUMN notes TYPE varchar(50);
```

## MySQL

Same patterns as Postgres but note:

- `ALTER TABLE` is a full rebuild for many operations; use `pt-online-schema-change` or `gh-ost` for large tables
- `DEFAULT` is required when adding NOT NULL columns to existing tables in strict mode

## BigQuery

- Cannot DROP columns without rewriting the table; use `SELECT * EXCEPT(col)` into a new table OR mark the column unused
- No NOT NULL enforcement on most operations — schema is advisory; downstream consumers must enforce
- `ALTER TABLE ADD COLUMN` is online and free

## Snowflake

- `ALTER TABLE` is metadata-only for most operations
- Zero-copy clone makes the safe-rename pattern cheap (clone → mutate → swap)

## Parquet (Arrow)

Parquet files are immutable; "schema evolution" is read-side reconciliation:

```python
import pyarrow.parquet as pq
import pyarrow as pa

# Read old + new files and unify schemas
old = pq.read_table("data/old.parquet")
new = pq.read_table("data/new.parquet")

unified_schema = pa.unify_schemas([old.schema, new.schema])
combined = pa.concat_tables(
    [old.cast(unified_schema), new.cast(unified_schema)]
)
```

The unify_schemas call follows Arrow's compatibility rules — incompatible changes raise; widen-compatible changes proceed.

## API versioning

For OpenAPI / GraphQL / gRPC schemas:

- BREAKING changes → bump major version, expose both versions in parallel for a deprecation window (e.g., 90 days)
- NON-BREAKING changes → bump minor version, no parallel exposure needed
- DEPRECATE old fields with `deprecated: true` annotation before removing

Deprecation notice template (for consumers):

```
Schema migration notice — <service> v<old> → v<new>

Effective date: <YYYY-MM-DD>
Deprecation window: <N> days

Breaking changes:
- DROP field `<name>` (consumer count: <N>) — migrate to `<new-name>` by <date>
- ...

Action required by your service:
1. Update calls to use the new field names
2. Test against v<new> before the cutoff date
3. Contact <owner> if your service cannot migrate by the deadline
```

## Rollback plan

Every migration script must be paired with a rollback. For BREAKING changes, the rollback is not always automatic:

- Column DROP → rollback requires a backup of the dropped data
- Type CHANGE → rollback requires reverse cast (may lose precision)
- Rename → rollback is the reverse 5-step

Plan and document the rollback BEFORE running the forward migration.
