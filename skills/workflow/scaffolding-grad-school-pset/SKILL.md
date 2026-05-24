---
name: scaffolding-grad-school-pset
description: >
  Scaffolds a graduate-school statistics or quantitative-methods problem set as a
  Jupyter notebook or RMarkdown document with the statistical-discipline cell
  ordering baked in: data audit cell → assumption-check cell → test cell → effect-size
  and confidence-interval cell → interpretation cell → conclusion cell. The structure
  forces the author to check assumptions BEFORE running a test and to report effect
  sizes alongside p-values, addressing the two most-flagged categories in graduate
  pset grading rubrics. Use when starting a new graded statistics problem set
  (frequentist or Bayesian), a quantitative-methods assignment, or a take-home
  data-analysis exam. Refuses to engage on research notebooks (different intent),
  programming-only problem sets without a statistical-inference component, or
  one-shot quick-look queries that do not warrant the full pset structure.
version: 0.1.0
status: shipped
track: workflow
audience: [stats-student, instructor, data-scientist]
evidence:
  - DU-MSDSAI-4441-Final
  - DU-MSDSAI-4441-weekly-psets
last-updated: 2026-05-23
---

# Scaffolding a Graduate-School Problem Set

## When to use

Trigger this skill when:

- The user is starting a new graduate-school statistics or quantitative-methods problem set
- The user is writing a take-home data-analysis exam
- The user says "I have a stats homework" / "weekly pset" / "Bayesian assignment" / "quant methods take-home"
- The artifact will be graded by an instructor against a rubric that includes assumption-checking and effect-size reporting (the two most-flagged categories in graduate-program rubrics, per the evidence)
- The user is migrating from a single-cell exploratory notebook to a structured graded artifact

## When NOT to use

Skip this skill (different intent or overkill) when:

- The user is writing a research notebook for original work — use `workflow/scaffolding-ml-research-notebook` (planned) instead. Research notebooks emphasize exploration and provenance; psets emphasize discipline and graded structure.
- The pset is programming-only with no statistical inference (e.g., a data-structures pset) — there is nothing to assumption-check
- The user wants a one-shot quick-look query ("what's the mean of this column?") that does not warrant a full pset scaffold
- The instructor has provided a strict template that this scaffold would conflict with — use the instructor's template

## Quick start

User says: "I have a graduate stats pset due Friday. It asks me to compare blood-pressure change between two treatment groups, then to fit a regression of change on baseline plus group. Scaffold the notebook."

Skill response: produces a Jupyter notebook (`.ipynb`) or RMarkdown (`.Rmd`) skeleton with the canonical 6-section cell ordering — (1) header + seed + imports, (2) data load + audit, (3) assumption checks per planned test, (4) tests + estimates, (5) effect sizes + 95% CIs, (6) interpretation + conclusion. Each section has placeholder cells with TODO comments referencing the specific question parts.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| pset_brief | string or file path | yes | — | The pset prompt — questions to answer, data described, methods expected. |
| stack | "jupyter-python" \| "jupyter-r" \| "rmarkdown" \| "quarto" | no | "jupyter-python" | Notebook stack. RMarkdown / Quarto for R-centric programs. |
| course_level | "undergrad" \| "masters" \| "phd-qualifying" | no | "masters" | Depth of assumption checks and effect-size reporting expected. PhD-qualifying adds power analysis + sensitivity sections. |
| frequentist_or_bayesian | "frequentist" \| "bayesian" \| "both" | no | "frequentist" | Affects test-section and diagnostics-section content. Bayesian adds R-hat / ESS / posterior-predictive cells. |

## Workflow

Copy this checklist into the response and check items as the scaffold is generated:

```
Pset scaffold:
- [ ] Step 1: Parse pset_brief — extract question count, data description, planned tests
- [ ] Step 2: Choose stack (default jupyter-python) and create the notebook file
- [ ] Step 3: Section 1 — header (course / pset / author / date), seed call, imports
- [ ] Step 4: Section 2 — data audit cells (per-column type / null / range / cardinality)
- [ ] Step 5: Section 3 — assumption-check cells per planned test (Normality, equal variance, expected counts, residual diagnostics)
- [ ] Step 6: Section 4 — test cells per question part with TODO placeholder for the actual test call
- [ ] Step 7: Section 5 — effect-size + 95% CI cells per test
- [ ] Step 8: Section 6 — interpretation + conclusion cells with direction sentence per question
- [ ] Step 9: Add markdown cells between sections explaining the discipline (for the grader)
```

### Step 1: Parse the pset brief

From the brief, extract:

- How many questions / parts? (e.g., "Q1a, Q1b, Q2") — each gets its own subsection in Sections 4 and 5
- What data is provided? (columns, types, sample size)
- What tests are implied by the questions? (two-sample comparison → t / Wilcoxon; regression → OLS / GLM; categorical → chi-squared / Fisher / McNemar)

### Step 2: Choose the stack and create the file

| Stack | File extension | When |
|---|---|---|
| jupyter-python | `.ipynb` | Most US grad programs; Python-centric courses |
| jupyter-r | `.ipynb` (R kernel) | Programs that use Python notebook UX with R kernel |
| rmarkdown | `.Rmd` | R-centric biostatistics / public-health programs |
| quarto | `.qmd` | Newer programs using Quarto across Python and R |

### Step 3: Section 1 — header + seed + imports

Header markdown cell:

```markdown
# <Course code> — Pset <N>: <title>
**Author:** <name> · **Date:** <YYYY-MM-DD> · **Stack:** <stack>
```

Seed code cell (Python example; use the analog for R / Bayesian):

```python
import os
os.environ["PYTHONHASHSEED"] = "42"
import random
import numpy as np
random.seed(42)
np.random.seed(42)
# Add torch / jax / tf seed calls if used
```

(See `workflow/enforcing-seed-hygiene` for the full multi-library seed pattern.)

Imports cell: pandas / numpy / scipy.stats / statsmodels / matplotlib for frequentist Python; pymc / arviz for Bayesian; tidyverse / lme4 / brms for R.

### Step 4: Section 2 — data audit

For each dataset loaded, generate one cell that produces a per-column report (type, null count, null %, min, max, mean, SD, unique values, sample values). See `workflow/auditing-data-quality` for the full audit pattern. Why this matters for psets: the most-common pset failure mode is running a test on data with silent quality issues (a 99th-percentile outlier, a sentinel `-999` masquerading as a value, a string-typed numeric column).

### Step 5: Section 3 — assumption checks per planned test

For each test the brief implies, scaffold an assumption-check cell BEFORE the test cell. The check cell determines whether the test is appropriate.

| Test | Assumption check | Cell content |
|---|---|---|
| Two-sample t | Normality per group + equal variance | Shapiro per group, Levene, QQ-plot |
| Paired t | Normality of differences | Shapiro on differences, QQ-plot |
| Wilcoxon signed-rank | Symmetry of differences (mild) | Boxplot or histogram of differences |
| Chi-squared 2x2 | Expected counts ≥ 5 | Print expected-counts table |
| OLS regression | Linearity + homoscedasticity + residual Normality + leverage | Residuals-vs-fitted, QQ-plot of residuals, Cook's D |
| Bayesian (MCMC) | Convergence (R-hat, ESS, divergences) | `az.summary()` + traceplot + R-hat |

See `ml-datasci/checking-test-assumptions` for the full per-test pattern.

### Step 6: Section 4 — test cells per question part

For each question part, scaffold a test cell with the planned test call commented as TODO. Cross-reference back to the assumption-check section.

### Step 7: Section 5 — effect sizes + 95% CIs

For each test in Section 4, add an effect-size cell. The metric depends on the test family (see `ml-datasci/reporting-effect-sizes`):

| Test family | Effect size | 95% CI |
|---|---|---|
| Parametric two-group | Cohen's d | Bootstrap or analytic |
| Paired parametric | Cohen's dz | Bootstrap or analytic |
| Non-parametric two-group | Cliff's δ | Bootstrap |
| Categorical 2x2 | Odds ratio or risk difference | Analytic |
| Regression | Adjusted R² + per-coefficient CI | Analytic |
| Bayesian | Posterior mean + 95% credible interval | Posterior quantiles |

### Step 8: Section 6 — interpretation + conclusion

Per question part, write a markdown interpretation cell with the canonical sentence template:

> The <test> showed <metric> = <value> [95% CI: <low>, <high>], direction: <which group higher>, n = <sample size>. <Plain-English interpretation tied to the question.>

### Step 9: Inter-section markdown for the grader

Between sections, add brief markdown explaining WHY the structure is in that order. Graders score discipline; making the discipline visible earns rubric points.

## Outputs

A notebook file at the user-chosen path (default `pset-<N>-<short-title>.ipynb` or `.Rmd`) with:

- 6 sections in the canonical order
- One cell or cell-group per section
- TODO markers for the per-question content the user must fill in
- Markdown explanations between sections so the grader sees the discipline

## Failure modes

- **Test-before-assumption-check ordering** — running a parametric test without first verifying Normality / equal variance, then citing p-value as evidence. Caught by: Section 3 is REQUIRED before Section 4; cell ordering is enforced by the scaffold.
- **Bare p-value reporting** — reporting "p < 0.05 so significant" without effect size + 95% CI. Caught by: Section 5 is REQUIRED after Section 4.
- **Missing direction sentence** — saying "groups differ" without naming WHICH group is higher. Caught by: Section 6's canonical sentence template forces a direction phrase.
- **Hidden outlier driving the result** — a single 99th-percentile value flipping the test verdict, not surfaced. Caught by: Section 2's per-column audit + Section 3's residual / leverage diagnostics.
- **Frequentist scaffold applied to a Bayesian pset** — running Shapiro-Wilk on a Bayesian assignment. Caught by: `frequentist_or_bayesian` argument switches Section 3 content to R-hat / ESS / posterior-predictive diagnostics.

## References

- `reference/pset-template.ipynb.md` — full markdown rendering of the scaffold for jupyter-python
- `reference/section-cookbook.md` — copy-paste cell snippets per section per stack
- `workflow/enforcing-seed-hygiene` — first-cell seed discipline
- `workflow/auditing-data-quality` — per-column audit pattern used in Section 2
- `ml-datasci/checking-test-assumptions` — assumption-check menu used in Section 3
- `ml-datasci/reporting-effect-sizes` — effect-size selector used in Section 5

## Examples

### Example 1: Weekly DU-MSDSAI-style pset (happy-path)

Input: "Pset 4 — compare blood-pressure change between treatment and control (n=30 per group). Then fit a regression of change on baseline plus group. Scaffold the notebook for me."

Output: Skill produces a `.ipynb` with 6 sections. Section 3 contains Shapiro-per-group + Levene for the two-sample test AND residual diagnostics (residuals-vs-fitted, QQ-plot of residuals, Cook's D) for the regression. Section 5 contains Cohen's d + 95% CI for the two-sample test and adjusted R² + per-coefficient 95% CI for the regression. Section 6 has direction-sentence templates for both.

### Example 2: Programming-only pset (anti-trigger)

Input: "Pset 2 — implement quicksort and merge sort in Python, then benchmark them on arrays of size 10, 100, 1000, 10000. Scaffold the notebook."

Output: Skill declines to engage the full pset scaffold. Explains that this is a programming / algorithms pset with no statistical-inference component — there is nothing to assumption-check, no effect sizes to report. Suggests a simpler notebook with implementation cells + benchmark cells + a single timing-comparison chart.

### Example 3: Bayesian pset (edge-case)

Input: "Bayesian methods pset — fit a hierarchical normal model with PyMC for student test scores nested in schools. Diagnose convergence and report posterior estimates with uncertainty."

Output: Skill produces a scaffold with `frequentist_or_bayesian = "bayesian"`. Section 3 replaces Shapiro / Levene with R-hat / ESS / divergences via `az.summary()` + traceplots. Section 5 replaces Cohen's d / Cliff's δ with posterior mean + 95% credible interval per parameter. Section 6's canonical sentence template substitutes "95% credible interval" for "95% CI" and notes the Bayesian-vs-frequentist interpretation difference.

## See also

- `workflow/scaffolding-ml-research-notebook` (planned) — research-notebook variant; emphasizes exploration and provenance rather than graded discipline
- `workflow/enforcing-seed-hygiene` — seed-discipline component used in Section 1
- `ml-datasci/reporting-effect-sizes` — effect-size discipline component used in Section 5
- `ml-datasci/checking-test-assumptions` — assumption-check discipline component used in Section 3

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
