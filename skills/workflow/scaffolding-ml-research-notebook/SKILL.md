---
name: scaffolding-ml-research-notebook
description: >
  Scaffolds a greenfield ML / data-science research project with a reproducible
  layout from the first commit: pinned environment (uv or poetry), src/ package,
  data/raw + data/processed split, tests/, claudedocs/, seed utility, pre-commit
  config, ML-specific .gitignore, and a starter notebook that imports the seed
  helper. Use whenever the user is starting a NEW ML or data-science project,
  spinning up a research notebook from scratch, or has just typed `uv init` /
  `poetry new` and wants the rest of the directory layout. Refuses to scaffold
  on top of an existing mature project (different skill — migration is a separate
  concern) and refuses for one-off throwaway exploration where the layout cost
  exceeds the benefit.
version: 0.1.0
status: shipped
track: workflow
audience: [data-scientist, ml-engineer, stats-student, instructor]
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
last-updated: 2026-05-23
---

# Scaffolding an ML / Data-Science Research Notebook

## When to use

Trigger this skill when the user:

- Is starting a brand-new ML, data-science, or stats research project from an empty directory
- Asks "how should I structure my ML project" or "what files do I need to set up before I start"
- Has run `uv init`, `poetry new`, or `mkdir my-project && cd my-project` and asks what to do next
- Wants a reproducible-from-day-one notebook (seeds set, deps pinned, data path conventions, tests scaffolded)
- Is about to paste raw CSVs into a folder and start a Jupyter session with no structure around it

## When NOT to use

Skip this skill and hand off when:

- The project already has a `pyproject.toml` + `src/` layout — the work is migration, not scaffolding (no migration skill exists yet; flag and stop)
- The work is a one-off five-minute exploratory query that will be thrown away (the layout cost exceeds the benefit; a single `analysis.ipynb` in `/tmp` is fine)
- The project is a security-research repo specifically (use `workflow/scaffolding-security-research-repo` — different deliverables: SECURITY.md, threat-model, gitleaks, VDP)
- The project is an LLM-eval harness specifically (use `workflow/scaffolding-llm-eval-harness` — different deliverables: model_id pinning, dataset_hash, results.jsonl)
- The user wants a production-deployable web service (this skill targets research / notebook workflows, not service deployment)

## Quick start

User: *"I'm starting a new project to predict customer churn. Set me up."*

Skill walks the 9-step checklist (Workflow below), produces the directory layout, writes `pyproject.toml` with pinned Python + locked dependencies, creates `src/<pkg>/seed.py` with the multi-library seed helper, scaffolds `notebooks/00-exploration.ipynb` that imports and calls the seed helper in cell 1, drops a `.pre-commit-config.yaml`, writes the data-science-specific `.gitignore` (ignore `data/raw/`, `data/processed/`, `*.ckpt`, `wandb/`, `mlruns/`, `.ipynb_checkpoints/`), and prints a one-paragraph "what's next" pointer.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| project_name | string | yes | — | The Python package / project slug (lowercase-snake or kebab). Used for `src/<pkg>/`, `pyproject.toml` name, and the repo directory. |
| package_manager | "uv" \| "poetry" \| "pip-tools" | no | "uv" | Which lockfile system to scaffold. uv is the default per Rock's preference and per QC.1. |
| python_version | string | no | "3.13" | Python version to pin in `requires-python` + `.python-version`. |
| ml_stack | "sklearn" \| "pytorch" \| "jax" \| "tensorflow" \| "none" | no | "sklearn" | Which ML library to add to deps and seed-helper coverage. Drives which seed calls land in `src/<pkg>/seed.py`. |
| include_pre_commit | bool | no | true | Whether to scaffold `.pre-commit-config.yaml` with ruff, mypy, nbstripout, and a seed-call grep gate. |
| include_tests | bool | no | true | Whether to scaffold `tests/` with a stub `test_seed.py`. |
| starter_notebook | bool | no | true | Whether to write `notebooks/00-exploration.ipynb` with cell 1 calling the seed helper. |

## Workflow

Copy this checklist into the response and check off each item as the scaffold lands:

```
Scaffold progress:
- [ ] 1. Verify empty / near-empty target directory (refuse if existing project structure detected)
- [ ] 2. Write pyproject.toml with pinned Python + ml_stack deps
- [ ] 3. Write .python-version + lock the env (`uv lock` / `poetry lock`)
- [ ] 4. Create src/<pkg>/__init__.py + src/<pkg>/seed.py (multi-library seed helper)
- [ ] 5. Create data/raw/.gitkeep + data/processed/.gitkeep + data/README.md
- [ ] 6. Create tests/test_seed.py (asserts seed helper produces deterministic output)
- [ ] 7. Create notebooks/00-exploration.ipynb (cell 1 imports + calls set_seed)
- [ ] 8. Write .gitignore (ML-specific patterns) + .pre-commit-config.yaml + claudedocs/
- [ ] 9. Print "what's next" pointer (run `uv sync`, `pre-commit install`, open notebook)
```

### Step 1 — Verify empty target

If any of these exist at the target path, **refuse and hand off**: `pyproject.toml`, `src/`, `setup.py`, `requirements.txt` already populated, `.git/` with > 0 commits other than an initial empty commit. This skill scaffolds greenfield; migration of mature projects is out of scope.

### Step 2 — pyproject.toml

Pin `requires-python = "==3.13.*"` (not `>=3.13` — see `auditing-pinned-dependencies` for why version-floor-without-ceiling is unsafe). Pin direct deps to compatible-release (`numpy~=2.1`) and let the lockfile resolve transitives. See `reference/pyproject-template.toml`.

### Step 3 — Lock + .python-version

Run `uv lock` (or `poetry lock`) and commit `uv.lock` (or `poetry.lock`). Write `.python-version` with the exact 3.13.x line `uv python pin` resolves. Cross-reference `pinning-reproducible-environments` for the broader pinning discipline.

### Step 4 — src/ layout + seed helper

`src/<pkg>/seed.py` exports `set_seed(seed: int = 42) -> None` covering Python `random`, `numpy.random`, and whichever of `torch` / `jax` / `tensorflow` matches `ml_stack`. The function must be idempotent + side-effect-only + return None. See `reference/seed-helper-template.py`.

Cross-reference `enforcing-seed-hygiene` for the broader determinism discipline (this skill scaffolds the helper; that skill explains when and where to call it).

### Step 5 — data/ layout

```
data/
  raw/           # immutable; ingested copy of the upstream dataset
    .gitkeep
  processed/     # outputs of feature pipelines; reproducible from raw + code
    .gitkeep
  README.md      # provenance: where raw came from, when, schema notes
```

Both `data/raw/` and `data/processed/` are listed in `.gitignore` — data does not live in git. The README documents source + pull-date + adapter version (cross-reference `auditing-source-provenance` planned for v2-batch-2).

### Step 6 — tests/

A stub `tests/test_seed.py` that asserts `set_seed(42)` followed by `np.random.random()` produces the same float twice across two calls. This is the smallest possible reproducibility test and a CI-runnable invariant from day one.

### Step 7 — Starter notebook

`notebooks/00-exploration.ipynb` with cell 1:

```python
from <pkg>.seed import set_seed
set_seed(42)

import pandas as pd
import numpy as np
```

This makes the right pattern frictionless: the first cell already calls the helper, so subsequent cells inherit determinism without per-cell `np.random.seed(...)` scatter.

### Step 8 — .gitignore + .pre-commit-config.yaml + claudedocs/

`.gitignore` includes ML-specific patterns: `data/raw/`, `data/processed/`, `*.ckpt`, `*.pt`, `*.h5`, `wandb/`, `mlruns/`, `.ipynb_checkpoints/`, `__pycache__/`, `.venv/`, `*.egg-info/`, `.DS_Store`, `htmlcov/`, `.coverage`, plus eval-result outputs (`evals/results-*.json`).

`.pre-commit-config.yaml` wires ruff (lint + format), mypy (optional type check on `src/`), `nbstripout` (strip notebook outputs before commit — keeps diffs reviewable + avoids leaking secrets in cell outputs), and a custom local hook that greps new `.ipynb` files for a `set_seed(` call.

`claudedocs/` is the convention for reports / analyses / Claude-generated docs (per Rock's harness `~/.claude/RULES.md` file-organization rule).

### Step 9 — What's next pointer

Print:

```
Done. Next:
  uv sync                 # install deps
  pre-commit install      # wire git hooks
  jupyter lab notebooks/  # start exploring
First commit recommended now (git add -A && git commit -m "Initial scaffold").
```

## Outputs

A populated project directory with the following files (greenfield, all new):

```
<project_name>/
  pyproject.toml
  uv.lock                       (or poetry.lock)
  .python-version
  .gitignore
  .pre-commit-config.yaml
  README.md                     (stub: 1 paragraph + Quick start)
  src/<pkg>/__init__.py
  src/<pkg>/seed.py
  tests/__init__.py
  tests/test_seed.py
  notebooks/00-exploration.ipynb
  data/raw/.gitkeep
  data/processed/.gitkeep
  data/README.md
  claudedocs/.gitkeep
```

Plus a printed "what's next" 3-line action list.

## Failure modes

Known pitfalls and how this skill catches them:

- **Scaffolding over an existing project** — would silently overwrite the user's `pyproject.toml` or worse. Caught by Step 1 (refuse if any of `pyproject.toml`, `src/`, `setup.py`, populated `requirements.txt`, or a git history > 1 commit exists).
- **Unpinned deps slipping in** — `uv init` defaults to `>=` ranges; raw `pip install pandas` produces floating versions. Caught by the pyproject template using `~=` for direct deps + committing the lockfile + cross-reference to `auditing-pinned-dependencies`.
- **Seed helper exists but no one calls it** — a `seed.py` no one imports is theater. Caught by Step 7 (starter notebook imports + calls in cell 1) + the pre-commit grep hook in Step 8.
- **Data accidentally committed to git** — fresh `git add -A` would slurp `data/raw/`. Caught by Step 8 (`.gitignore` includes `data/raw/` + `data/processed/` from day one).
- **Notebook outputs leak secrets / massive diffs** — committing notebooks with outputs is the most common diff-rot source. Caught by `nbstripout` in the pre-commit config.
- **Wrong skill engaged for a security-research repo** — would miss SECURITY.md, gitleaks, threat-model, VDP. Caught by "When NOT to use" handoff to `workflow/scaffolding-security-research-repo`.

## References

- `reference/pyproject-template.toml` — the pinned `pyproject.toml` skeleton with per-stack dependency blocks
- `reference/seed-helper-template.py` — the multi-library `set_seed` implementation
- `reference/pre-commit-template.yaml` — the `.pre-commit-config.yaml` with the seed-call grep hook
- `reference/gitignore-template` — the ML-specific `.gitignore`
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — for the workflow-checklist pattern
- [uv documentation](https://docs.astral.sh/uv/) — package manager defaults

## Examples

### Example 1: Fresh data-science project (happy-path)

Input: *"I'm starting a new project to predict customer churn from a tabular dataset. Set me up — Python 3.13, sklearn."*

Output: Skill walks the 9-step checklist, writes `pyproject.toml` with pinned `python = "==3.13.*"`, `scikit-learn~=1.5`, `pandas~=2.2`, `numpy~=2.1`, runs `uv lock`, scaffolds `src/churn/seed.py` with Python+NumPy+sklearn coverage, writes `notebooks/00-exploration.ipynb` with cell 1 calling `set_seed(42)`, drops `.gitignore` ignoring `data/raw/`, prints the 3-line next-steps pointer. User can run `uv sync && pre-commit install && jupyter lab notebooks/` and is ready to load data.

### Example 2: Existing-repo migration (edge-case anti-trigger handoff)

Input: *"I have an existing 2-year-old project with a setup.py, no lockfile, notebooks scattered in the root. Scaffold it."*

Output: Skill refuses to scaffold over the existing project. Explains that this skill targets greenfield projects only — overwriting `setup.py` or seeding a fresh `pyproject.toml` could break existing imports. Hands off: "Migration is a separate concern (no migration skill exists yet in this repo; v2 roadmap). For now, I recommend: 1) commit your current state, 2) read `pinning-reproducible-environments` for the dep-locking subset, 3) read `enforcing-seed-hygiene` for the seed-helper subset — apply incrementally instead of a bulk scaffold."

### Example 3: Throwaway query (anti-trigger)

Input: *"I'm going to compute a few quick correlation matrices on a CSV and throw the notebook away."*

Output: Skill declines to scaffold. Explains that for genuine throwaway exploration the 9-step layout overhead exceeds the benefit; a single `analysis.ipynb` in a temp directory with an inline `np.random.seed(42)` is fine. Notes that if the work turns into a real project the user should come back and scaffold properly.

## See also

- `workflow/scaffolding-security-research-repo` — sibling: greenfield for security-research projects (SECURITY.md, gitleaks, threat-model, VDP)
- `workflow/scaffolding-llm-eval-harness` — sibling: greenfield for LLM-eval pipelines (model_id, dataset_hash, results.jsonl)
- `workflow/enforcing-seed-hygiene` — the discipline this scaffold encodes for seeds
- `workflow/pinning-reproducible-environments` — the discipline this scaffold encodes for deps
- `security/auditing-pinned-dependencies` — the audit that verifies a scaffolded project stays pinned over time

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
