# Schema-change Classification Rules

Full rule table for diffing old → new schema and labelling each change. The skill consumes this table to produce its findings.

## Decision priority

Every column-level change is processed in this order, and only the first matching rule applies:

1. Primary-key change (column or type) → BREAKING
2. Column DROP (no rename pair) → BREAKING
3. Rename candidate (DROP+ADD with same position + compatible type + similar name) → AMBIGUOUS
4. Type CHANGE
5. Nullability CHANGE
6. Default CHANGE
7. Constraint CHANGE (unique / check / FK)
8. Column ADD

## Per-rule table

| Rule | Direction | Classification | Why |
|---|---|---|---|
| PK column DROP | n/a | BREAKING | Identity semantics change; inbound FKs break |
| PK type CHANGE | n/a | BREAKING | Inbound FK type mismatch; index rebuild required |
| PK column ADD (composite) | n/a | BREAKING | Existing rows must satisfy new uniqueness; backfill required |
| Column DROP | n/a | BREAKING | All readers of the column break |
| Column DROP + Column ADD at same position with similar name | n/a | AMBIGUOUS | Likely intentional rename; confirm before generating destructive SQL |
| Column ADD nullable | n/a | NON-BREAKING | Old code keeps working (column is invisible to old reads) |
| Column ADD NOT NULL with default | n/a | NON-BREAKING | Existing rows get the default; new INSERTs that omit the column also get the default |
| Column ADD NOT NULL no default | n/a | BREAKING | Existing rows fail; migration must backfill OR add a default temporarily |
| Type WIDEN (int → bigint, varchar(N) → varchar(M>N), float → double) | wider | NON-BREAKING | Old values fit; old readers may need cast updates but reads succeed |
| Type NARROW (bigint → int, varchar(N) → varchar(M<N)) | narrower | BREAKING | Existing values may overflow / truncate; pre-flight scan required |
| Type CHANGE (int → varchar, varchar → int) | cross-family | BREAKING | Casts may fail; downstream code may rely on type semantics |
| Nullability ADD (nullable → NOT NULL) | tighten | BREAKING | Existing NULL rows violate; backfill required |
| Nullability DROP (NOT NULL → nullable) | loosen | NON-BREAKING | Old code that assumed non-null may fail; warn-level |
| Default ADD | n/a | NON-BREAKING | INSERTs that omit the column now succeed |
| Default DROP | n/a | BREAKING-WARN | INSERTs that omitted the column now fail; producer code must supply explicitly |
| Default CHANGE | n/a | WARN | Quiet behavior change for new INSERTs that omit the column |
| Unique constraint ADD | n/a | BREAKING (if data violates) | Existing duplicates fail; pre-flight scan required |
| Unique constraint DROP | n/a | NON-BREAKING | Strictly relaxing |
| Check constraint ADD | n/a | BREAKING (if data violates) | Pre-flight scan required |
| Check constraint DROP | n/a | NON-BREAKING | Strictly relaxing |
| FK ADD | n/a | BREAKING (if data violates) | Existing rows referencing non-existent parents fail; pre-flight scan required |
| FK DROP | n/a | NON-BREAKING | Strictly relaxing |

## Rename heuristic

A `DROP X; ADD Y` pair in the same migration is a rename CANDIDATE if all of:

- Same ordinal position (or both at the end if appended)
- Compatible types (varchar↔varchar; int↔bigint; etc.)
- Name similarity: Levenshtein ≤ 3, OR shared prefix ≥ 4 chars, OR shared suffix ≥ 4 chars, OR semantic synonyms (`email` ↔ `email_address`, `user_id` ↔ `customer_id` is NOT a synonym pair)
- Description / comment preserved (if the schema format carries comments)

When all four are true, classify as AMBIGUOUS — REFUSE to emit destructive SQL until the operator confirms intent.

## Sentinel-aware rules

If the schema has columns named `is_deleted`, `deleted_at`, or `tombstone`, treat row deletes as soft-deletes; do not include hard-DELETE in any migration script unless explicitly requested.

If the schema uses Avro / Protobuf, defer to the format's own compatibility rules (BACKWARD / FORWARD / FULL) — they are stricter than this table in some cases.

## Version-tuple comparison

Compare schema versions as SemVer tuples, never as strings:

```python
def parse_version(v: str) -> tuple[int, int, int]:
    parts = v.lstrip("v").split(".")
    return tuple(int(p) for p in parts[:3])
```

`v10 > v9` lexicographically is False; SemVer-parsed comparison gives True.
