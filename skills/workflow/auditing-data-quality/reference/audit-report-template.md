# Data-quality audit report — copy-pasteable template

Fill in the bracketed fields. Keep every section even when empty; an empty section is itself an audit signal.

---

## Audit: `<dataset_name>` — `<YYYY-MM-DD>`

**Source:** `<file path / URL / pipeline name + commit SHA>`
**Auditor:** `<name>`
**Schema version:** `<if known>`

### 1. Shape

- Rows: `<N>`
- Columns: `<M>`
- File size: `<bytes / MB / GB>`
- Memory footprint (in-memory DataFrame): `<MB / GB>`
- Change from previous audit: `<+/- N rows, +/- M columns; reason if known>`

### 2. Per-column report

| Column | dtype | null_count | null_% | distinct_count | min | max | mean | std | sample_values |
|---|---|---|---|---|---|---|---|---|---|
| `<col>` | `<type>` | `<n>` | `<%>` | `<n>` | `<v>` | `<v>` | `<v>` | `<v>` | `[v1, v2, v3]` |

### 3. Semantic class

| Column | Inferred class | Confidence | Notes |
|---|---|---|---|
| `<col>` | ID / categorical / continuous / ordinal / text / datetime / boolean | high / medium / low | `<flags, e.g. "ask user — could be ordinal">` |

### 4. Range violations

| Column | Expected range | Violation count | Sample violating values | Hypothesis |
|---|---|---|---|---|
| `<col>` | `<low, high>` | `<n>` | `[v1, v2]` | `<sentinel? data-entry error? domain extreme?>` |

### 5. Outlier report

| Column | Method | Bounds | Outlier count | Sample values | Hypothesis | Required action |
|---|---|---|---|---|---|---|
| `<col>` | IQR (Tukey 1.5×) | `[low, high]` | `<n>` | `[v1, v2, v3]` | `<sentinel / error / legit extreme>` | Confirm with data producer; do NOT auto-drop |

### 6. Cardinality alarms

| Column | Inferred class | Cardinality | Likely cause |
|---|---|---|---|
| `<col>` | categorical | `<n>` (> alarm threshold) | `<free text mislabeled / ID mislabeled / scheme drift>` |

### 7. Row-level integrity

- Exact duplicate rows: `<n>` (sample: `[idx1, idx2, ...]`)
- Same-content rows with different IDs: `<n>` (sample: `[(id_a, id_b), ...]`)
- Conflicting fact-pairs: `<n>` (sample: `[(key, attr, val_a, val_b), ...]`)

### Final verdict

- **Go** — no blocking issues; modeling may proceed
- **No-go with blockers** — listed issues must be resolved with the data producer before modeling
- **No-go** — dataset is unfit for the intended task

### Remediation list (ordered by blocker severity)

1. `<highest-severity blocker; specific action; owner>`
2. ...
