# Pset template — full jupyter-python scaffold

Markdown rendering of the canonical 6-section jupyter-python scaffold. Save as `pset-N-short-title.ipynb` and translate to actual notebook cells (one cell per fenced block).

---

## Cell 1 — Header (markdown)

```markdown
# <COURSE-CODE> — Pset <N>: <title>

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Stack:** jupyter-python

## Questions covered
- Q1: <one-line summary>
- Q2: <one-line summary>
```

## Cell 2 — Seed (code)

```python
import os
os.environ["PYTHONHASHSEED"] = "42"
import random
import numpy as np
random.seed(42)
np.random.seed(42)
```

## Cell 3 — Imports (code)

```python
import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
```

## Cell 4 — Section 2 header (markdown)

```markdown
## Section 2 — Data audit

Per-column type / null / range / cardinality before any analysis.
Why: surfaces data-quality issues that would otherwise silently
corrupt downstream tests.
```

## Cell 5 — Data load (code)

```python
df = pd.read_csv("TODO-data.csv")
df.head()
```

## Cell 6 — Audit table (code)

```python
audit = pd.DataFrame({
    "dtype":   df.dtypes.astype(str),
    "n_null":  df.isna().sum(),
    "pct_null": (df.isna().mean() * 100).round(2),
    "n_unique": df.nunique(),
    "min":     df.select_dtypes("number").min(),
    "max":     df.select_dtypes("number").max(),
    "mean":    df.select_dtypes("number").mean().round(3),
    "std":     df.select_dtypes("number").std().round(3),
})
audit
```

## Cell 7 — Audit verdict (markdown)

```markdown
**Audit verdict:** <flag any high-null columns, suspect ranges,
sentinel values, or cardinality alarms. If clean, state so.>
```

## Cell 8 — Section 3 header (markdown)

```markdown
## Section 3 — Assumption checks

Run BEFORE the tests in Section 4. The verdicts here determine
which test variant is appropriate (e.g., pooled-t vs Welch vs
Mann-Whitney).
```

## Cell 9 — Assumption-check code per planned test

(One sub-section per planned test — see `section-cookbook.md` for snippets.)

## Cell 10 — Assumption verdicts (markdown)

```markdown
**Per-test verdicts:**

- Q1 two-sample comparison: Shapiro treatment p = <X>, Shapiro control p = <Y>,
  Levene p = <Z>. Decision: <pooled-t / Welch / Mann-Whitney>.
- Q2 regression: residuals-vs-fitted shows <linear / fanning>, QQ shows
  <Normal / heavy-tailed>, Cook's D max = <V>. Decision: <OLS / robust /
  remove influential point>.
```

## Cell 11 — Section 4 header (markdown)

```markdown
## Section 4 — Tests

One test per question part. Reference back to Section 3 verdicts
for justification.
```

## Cell 12+ — Test cells (code, one per question part)

See `section-cookbook.md` Section 4 examples.

## Cell N — Section 5 header (markdown)

```markdown
## Section 5 — Effect sizes + 95% CIs

Every test in Section 4 gets a paired effect-size + 95% CI cell here.
P-values without effect sizes are not sufficient for graduate-level
reporting.
```

## Cell N+1 — Effect-size cells (code, one per test)

See `section-cookbook.md` Section 5 examples.

## Cell M — Section 6 header (markdown)

```markdown
## Section 6 — Interpretation + conclusion

Per question part: the canonical sentence template — test, effect
size, 95% CI, direction, n, plain-English interpretation.
```

## Cell M+1 — Interpretation cells (markdown, one per question)

```markdown
**Q1.** The <test> showed <metric> = <value> [95% CI: <low>, <high>],
direction: <which group higher by how much>, n = <sample size>.
<Plain-English interpretation tied to the question's wording.>
```

## Cell Final — Conclusion (markdown)

```markdown
## Conclusion

<2-3 sentences summarizing the overall finding across all questions.
Cite the strongest effect size and any caveat (e.g., small sample,
assumption violation, unmeasured confounder).>
```
