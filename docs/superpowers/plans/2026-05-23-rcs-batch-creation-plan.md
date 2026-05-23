# RCS Batch Skill Creation Plan

> **For agentic workers:** Invoked as `/superpowers:writing-skills create batch X at docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md using PRAGMATIC` from inside the RCS repo. Each invocation in a fresh session executes exactly one batch end-to-end without coordination with other batch sessions.

**Goal:** Parallelize authoring of the remaining 16 v1 skills across 5 independent batches, each landed via its own PR, with a single final integration step.

**Why batches:** Each batch ships 2-4 skills that touch a small set of files (mostly their own new directories plus one or two track READMEs). With proper isolation (per-batch git worktree + per-batch branch + changelog fragments instead of editing CHANGELOG.md), 5 batch sessions can run concurrently with zero merge conflicts.

---

## How to invoke

For each batch (1-5), open a new Claude Code session in the RCS repo and run:

```
/superpowers:writing-skills create batch 1 at docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md using PRAGMATIC
```

(Substitute `1` with the batch number 1-5.)

After all 5 batches' PRs have merged to main, run **Batch 6** (Integration) in a single session — also via this command:

```
/superpowers:writing-skills create batch 6 at docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md using PRAGMATIC
```

Batch 6 consolidates the changelog fragments, updates root README + skills/README.md catalogs, and tags `v1.0.0-phase2-thru-6`.

---

## PRAGMATIC discipline (explicit deviation from writing-skills Iron Law)

`PRAGMATIC` is a documented batch-authoring discipline. It replaces strict RED-GREEN-REFACTOR with a lighter flow specifically because:

1. The gap evidence for every skill in this plan is already captured in Rock's repo history + the v1 brainstorm Σ scoring (see `docs/superpowers/specs/2026-05-22-rcs-public-skills-repo-design.md`). The "baseline failure" exists empirically and is documented.
2. Phase 1 (running-adversarial-premortem, auditing-mcp-server-pre-trust) was validated using this same in-session subagent-dispatch eval flow; the methodology is proven.
3. CLAUDE.md priority order: explicit user operator instructions override skill defaults. PRAGMATIC is the operator's explicit instruction.

**PRAGMATIC steps per skill:**

1. **Read context** (each session, once):
   - `docs/superpowers/specs/2026-05-22-rcs-public-skills-repo-design.md` (spec)
   - `docs/conventions.md` (Layer-3 H2 contract, frontmatter spec, status semantics)
   - `docs/eval-protocol.md` (eval JSON schema)
   - `skills/workflow/running-adversarial-premortem/SKILL.md` (Phase 1 template — copy the layout)
   - `skills/security/auditing-mcp-server-pre-trust/SKILL.md` (Phase 1 template — copy the layout)
   - This plan's "Per-batch isolation contract" section (below)
   - This plan's section for the assigned batch
2. **Author SKILL.md** per the skill's scaffolding in the batch section. Must satisfy all 11 Layer-3 H2 sections from `docs/conventions.md`. Frontmatter `status: shipped`.
3. **Author bundled reference files** if the scaffolding calls for them (under `reference/`).
4. **Author 3 eval JSON files** under `evals/`: 01-happy-path.json, 02-edge-case.json, 03-anti-trigger.json. Per `docs/eval-protocol.md`: exactly 3 rubric items per scenario.
5. **Lint:**
   ```bash
   uv run python -m tools.lint_frontmatter skills/<track>/<skill>/SKILL.md
   uv run python -m tools.lint_skill_md skills/<track>/<skill>/SKILL.md
   uv run python -m tools.lint_links skills/<track>/<skill>/
   ```
   All must print `OK`. Fix any failures before proceeding.
6. **In-session Sonnet-only eval validation** (PRAGMATIC compromise: full 3-model would be ~36 dispatches per 4-skill batch; Sonnet-only is 12 dispatches and gives real signal):

   For each of the 3 scenarios per skill, dispatch ONE general-purpose subagent with `model: sonnet`, system context = the SKILL.md body inlined, user message = scenario.query. Capture completion. Judge each rubric item against intent (not literal phrasing). Score N/3.

   Pass thresholds (Sonnet-only):
   - happy-path: 3/3
   - edge-case: 3/3
   - anti-trigger: ≥ 2/3

   If skill passes all 3 scenarios → keep `status: shipped`.
   If any scenario fails materially → demote `status: drafting`, note the failure in the PR description.
7. **Update the track README** (and only the track README — NOT root README, NOT skills/README.md, NOT CHANGELOG.md):
   - Add row to "Shipped skills" table
   - Remove the row from "Planned skills" table
8. **Write changelog fragment** at `docs/superpowers/changelog-fragments/batch-N-<short-name>.md`:
   ```markdown
   ### Batch N: <short-name> — 2026-05-23

   Skills shipped:
   - `<track>/<slug>` v0.1.0 — <one-line description> (Σ N, status: shipped|drafting)
   - ...

   Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Full 3-model validation deferred to a future re-run.

   Notes: <any failures, deviations, calibration corrections>
   ```
9. **Commit per skill** (one commit per skill, not one combined commit) with messages:
   - `Add <track>/<skill-slug> skill (PRAGMATIC validation, status: <shipped|drafting>)`
10. **Update track README in a separate commit** with message:
   - `Move N shipped skills from Planned to Shipped in <track> track README`
11. **Commit changelog fragment** in a separate commit:
   - `Add batch-N changelog fragment`
12. **Push branch and open PR** per the "Per-batch PR template" section below.
13. **Merge** with `gh pr merge --merge --delete-branch`.

**What PRAGMATIC explicitly does NOT do:**
- No formal baseline (RED) testing. The gap is already evidenced in repo history.
- No Haiku or Opus eval dispatches (just Sonnet).
- No multi-round refactor loops on rubric mismatches. One pass.
- No edits to root `README.md`, `skills/README.md`, or `CHANGELOG.md` from inside the batch (those are integration-step edits; see Batch 6).

---

## Per-batch isolation contract

Every batch session MUST follow this isolation discipline. Violating it causes merge conflicts across the other 4 concurrent batches.

### Step 1: Create the worktree

From the RCS repo root:

```bash
git fetch origin
git worktree add ../RCS-batch-N -b feature/v1.0.0-batch-N-<short-name> origin/main
cd ../RCS-batch-N
```

Where `N` is the batch number and `<short-name>` is the batch's short name (e.g., `batch-1-high-sigma`, `batch-2-stats-discipline`, `batch-3-ml-eval`, `batch-4-data-hygiene`, `batch-5-meta`, `batch-6-integration`).

### Step 2: Sync deps

```bash
uv sync
```

### Step 3: Author skills per the PRAGMATIC steps above (steps 1-11)

### Step 4: Files this batch may touch

Whitelist (only these directories/files are in scope for batches 1-5):

- `skills/<track>/<new-skill-slug>/**` — all new skill content
- `skills/<track>/README.md` — for the batch's tracks ONLY
- `docs/superpowers/changelog-fragments/batch-N-<short-name>.md` — the batch's changelog fragment

Files the batch MUST NOT touch (batches 1-5):

- `README.md` (root) — deferred to Batch 6
- `skills/README.md` (cross-track index) — deferred to Batch 6
- `CHANGELOG.md` — deferred to Batch 6
- Other batches' track READMEs — deferred to other batches
- `pyproject.toml`, `.gitignore`, `LICENSE`, `CONTRIBUTING.md`, `docs/*.md` (conventions, eval-protocol, governance) — out of scope
- `tools/**` — out of scope
- `.github/workflows/**` — out of scope

### Step 5: Push + PR + merge

```bash
git push -u origin feature/v1.0.0-batch-N-<short-name>
gh pr create --base main --head feature/v1.0.0-batch-N-<short-name> \
  --title "v1.0.0-batch-N: <skills shipped>" \
  --body "$(cat <<'EOF'
<see PR template below>
EOF
)"
gh pr merge --merge --delete-branch
```

### Step 6: Cleanup worktree

```bash
cd ../RCS  # back to main repo
git worktree remove ../RCS-batch-N
git worktree prune
```

### Per-batch PR template

```markdown
## Summary

Batch N: <descriptive name>. Ships <count> new skills authored via PRAGMATIC discipline (writes-skills with Sonnet-only in-session eval validation, not strict 3-model RED-GREEN-REFACTOR).

### Skills shipped

- `<track>/<slug>` v0.1.0 — <one-line description> (Σ N, status: <shipped|drafting>)
- ...

### Files changed

- `skills/<track>/<slug>/` directories (new)
- `skills/<track>/README.md` (move skills from planned → shipped)
- `docs/superpowers/changelog-fragments/batch-N-<short-name>.md` (new)

### Eval results

<paste Sonnet-only eval pass/fail per scenario>

### Test plan

- [x] `uv run pytest -q` → 27/27 pass
- [x] `tools.lint_frontmatter` on each new SKILL.md → OK
- [x] `tools.lint_skill_md` on each new SKILL.md → OK
- [x] `tools.lint_links` on each new skill directory → OK
- [x] Sonnet eval pass per scenario per skill (intent-matched scoring; see Eval results)

### Integration deferred

Root README catalog, `skills/README.md` cross-track index, and `CHANGELOG.md` updates are deferred to Batch 6 (final integration). This is intentional to avoid merge conflicts across concurrent batch PRs.
```

---

## Batch 1: Phase 2 high-Σ low-effort (4 skills)

**Branch:** `feature/v1.0.0-batch-1-high-sigma`
**Short name (worktree dir):** `RCS-batch-1`
**Skills shipped:** 4
**Tracks touched (README updates):** `workflow/`, `security/`, `ml-datasci/`

### 1.1 enforcing-seed-hygiene (Σ 20)

- **Slug:** `enforcing-seed-hygiene`
- **Track:** `workflow`
- **Audience:** `[data-scientist, ml-engineer, security-eng, skill-author]`
- **Evidence:** `incident-rank-validation` (NUTS CPU-pin), `multiturn-injection-detection` (set_global_seed(42)), `llm-toxicity-visual-analysis`, `DU-MSDSAI-4432-DiabetesDiseasePrediction`, `DU-MSDSAI-4432-TitanicSurvivalClassifiers`, `DU-MSDSAI-4432-MultiModelDiseaseProg`, `DU-MSDSAI-4432-MultiModelBikeShareRegression`, `DU-MSDSAI-4432-OptimalClusteringComparison`
- **Frontmatter description:** *"Enforces deterministic seed initialization in any Jupyter notebook, Python/R script, or ML training pipeline that touches randomness. Use whenever the user is starting an ML/DS notebook, writing a training script, or asks why their results changed run-to-run. Walks the multi-library seed-set pattern (Python random, NumPy, PyTorch, JAX, TensorFlow, R), the CPU-pin pattern for NUTS/JAX determinism, and a pre-commit gate that catches missing seeds in new files."*
- **What the skill teaches:**
  - First-cell pattern: every notebook starts with a seed call covering all libraries the notebook will use
  - Multi-library cookbook: Python `random.seed(N)`, `numpy.random.seed(N)`, `torch.manual_seed(N)` + `torch.cuda.manual_seed_all(N)`, `jax.random.PRNGKey(N)`, `tf.random.set_seed(N)`, R `set.seed(N)`
  - CPU-pin determinism: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `JAX_PLATFORM_NAME=cpu` for sampler/JAX-style cross-platform determinism (cite incident-rank-validation pattern)
  - Pre-commit hook: grep new Python/R/notebook files for seed-set calls; fail the commit if absent
  - Anti-pattern: per-cell `np.random.seed(...)` calls scattered through the notebook (caught: should be one first-cell call)
- **When NOT to use:**
  - Throwaway exploratory queries that don't persist results
  - Code that legitimately wants nondeterminism (security entropy, Monte Carlo with documented run-stamps)
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I'm starting a new ML notebook to train a binary classifier on a tabular dataset. Help me set it up."* → Skill should produce/recommend a first-cell seed block covering Python/NumPy/PyTorch (or whichever lib the user mentions); should name the multi-library coverage explicitly; should NOT scatter `np.random.seed(...)` across cells. Rubric: (1) produces a first-cell seed block; (2) covers at least Python random + NumPy + whichever ML lib the user implies; (3) does NOT scatter per-cell seed calls.
  - **02-edge-case:** Query: *"My NUTS sampler results differ between my laptop and our Linux GPU server. Same seed, same code. Help."* → Skill should diagnose as a CPU-pin / platform determinism issue and recommend `OMP_NUM_THREADS=1` + CPU-pin pattern (cite the incident-rank-validation discipline). Rubric: (1) names CPU-pin / platform-determinism as the cause; (2) recommends `OMP_NUM_THREADS=1` or equivalent; (3) explains seed alone is insufficient for cross-platform.
  - **03-anti-trigger:** Query: *"Generate me a random nonce for an API request."* → Skill should NOT engage seed-hygiene workflow; nonces are security-critical and require fresh entropy. Rubric: (1) does NOT recommend a fixed seed; (2) recommends `secrets.token_bytes(...)` or `os.urandom(...)`; (3) explains why seeded RNG is wrong for cryptographic use.

### 1.2 validating-temporal-fields (Σ 19)

- **Slug:** `validating-temporal-fields`
- **Track:** `workflow`
- **Audience:** `[data-engineer, data-scientist, security-eng]`
- **Evidence:** `genai_agentic_incidents` (AIID 2027-election year-fallback bug documented in CHANGELOG.md 2.0.0)
- **Frontmatter description:** *"Validates date/time fields in incident corpora, event logs, or any temporal dataset. Catches future-dated records, max-year-fallback bugs, and event-vs-disclosure-date confusions. Use whenever ingesting a dataset with year/date fields, especially incident registries, vulnerability disclosures, or news-derived corpora where the source text may contain spurious future-year mentions (e.g., 'the 2027 election')."*
- **What the skill teaches:**
  - **Reject future-dated rows:** any `event_date > today()` is an automatic ingest error
  - **Year-fallback rule:** when a record's year cannot be determined from structured fields, fall back to the MIN plausible year (often the disclosure date), NEVER the MAX year mentioned in the text. The genai_agentic_incidents AIID bug was: text mentioned "2027 election" → max-year extractor stamped 2027 → record was future-dated.
  - **Separate event-date from disclosure-date:** maintain both. Event date is when the thing happened; disclosure date is when it was reported. They often differ; conflating them masks the year-fallback bug.
  - **Schema validation pattern:** Pydantic / Pandera / dataclass validation that runs both invariants (no-future + event ≤ disclosure)
  - **CI determinism:** the validator's "today" must come from a single source (env var, not `datetime.now()` per call) so CI runs are deterministic
- **When NOT to use:**
  - Forecasting / scheduling datasets where future dates are legitimate
  - Pure-mathematical date arithmetic outside ingest pipelines
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I'm ingesting the AIID incident corpus into our pipeline. Each record has an `incident_date` field. What validation should I add?"* → Skill should specify reject-future + min-year-fallback + event-vs-disclosure separation. Rubric: (1) recommends rejecting any future-dated rows; (2) names the min-year-fallback rule (not max); (3) recommends separating event date from disclosure date.
  - **02-edge-case:** Query: *"One of our records has incident_date = 2027-11-03 but the disclosure date is 2024-09-15. The text mentioned 'the 2027 election' as context. Is the record valid?"* → Skill should identify this as the year-fallback bug class — the 2027 was a contextual mention, not the event year; the actual event year is likely 2024. Rubric: (1) identifies the 2027 as a contextual/forecast mention, not the event; (2) recommends correcting to the disclosure year or marking incident_date as unknown; (3) cites the max-year-fallback anti-pattern.
  - **03-anti-trigger:** Query: *"Schedule a reminder for January 15, 2027 to renew the SSL cert."* → Skill should NOT engage temporal validation; future dates in scheduling are legitimate. Rubric: (1) does NOT reject the future date; (2) accepts the scheduling as valid; (3) explicitly distinguishes scheduling from ingest.

### 1.3 auditing-pinned-dependencies (Σ 19)

- **Slug:** `auditing-pinned-dependencies`
- **Track:** `security`
- **Audience:** `[security-eng, devops, skill-author]`
- **Evidence:** Rock's harness `foundation/00-quality-contract.md` QC.1 (NIST SP 800-218), `PreToolUse-supply-chain-bash-checks.py` hook
- **Frontmatter description:** *"Audits a repository's install commands and CI for unpinned dependency installs. Greps for npx -y, @latest, pip install without ==, unpinned uvx --from git+, curl|sh patterns. Use when reviewing a new repo before adoption, evaluating an MCP server's install command, hardening an existing project against supply-chain attacks, or auditing CI pipelines for drift risk."*
- **What the skill teaches:**
  - **Patterns to flag (blocking):** `npx -y <pkg>` (no version), `npm install <pkg>` without `@<version>`, `pip install <pkg>` without `==<version>`, `uvx --from git+<url>` without `#<ref>` or `@<sha>`, `@latest` anywhere, `curl ... | sh` / `wget ... | bash`
  - **Acceptable forms:** `pkg@1.2.3`, `pkg==1.2.3`, `git+url@<sha>`, `git+url#<tag>`, `pip install -r requirements.lock` (lockfile-pinned)
  - **Files to scan:** `README.md` install sections, `Dockerfile` / `Containerfile`, GitHub Actions YAML (`.github/workflows/*.yml`), `package.json` scripts, `pyproject.toml` (dependencies should pin), `requirements*.txt`, `Pipfile`, `pre-commit-config.yaml`, `mcp.json` / `.mcp.json` install commands
  - **Report format:** per-file findings with line numbers + suggested pinned form + remediation snippet
  - **Hash integrity bonus:** for npm, recommend `npm ci` over `npm install` to enforce package-lock integrity; for pip, recommend `pip install --require-hashes` if hashes are available
- **When NOT to use:**
  - Brand-new project bootstrap where you legitimately want the latest version on first install
  - Throwaway prototype / personal scratch repos
- **Eval scenarios:**
  - **01-happy-path:** Query: *"Here's our team's Dockerfile. Audit the install commands for pinning issues."* (followed by a Dockerfile with mixed pinned and unpinned installs) → Skill should flag each unpinned line with line number + suggested fix. Rubric: (1) identifies at least one unpinned install with line reference; (2) suggests a pinned form for each finding; (3) does NOT flag already-pinned lines as issues.
  - **02-edge-case:** Query: *"We use `uvx --from git+https://github.com/anthropic/somelib.git` to install our internal CLI. Is that pinned?"* → Skill should identify that git+ without `#<tag>` or `@<sha>` is unpinned (resolves to HEAD of default branch) and recommend adding `#v1.2.3` or `@<sha>`. Rubric: (1) identifies the git+ without ref as unpinned; (2) recommends adding `#<tag>` or `@<sha>` syntax; (3) explains that HEAD of default branch can change.
  - **03-anti-trigger:** Query: *"I just ran `npm create vite@latest my-app -- --template react`. Should I have pinned it?"* → Skill should NOT flag first-time scaffolding `create-*` invocations on a brand-new project as pinning violations (different from runtime dependencies). Rubric: (1) does NOT flag the create-vite invocation as a pinning failure; (2) explains create-* scaffolders are one-shot, not runtime deps; (3) recommends the user pin the project's RESULTING dependencies in package.json instead.

### 1.4 reporting-effect-sizes (Σ 19)

- **Slug:** `reporting-effect-sizes`
- **Track:** `ml-datasci`
- **Audience:** `[data-scientist, stats-student, instructor, ml-engineer]`
- **Evidence:** `DU-MSDSAI-4441-Final/GRADING_ISSUES.md` (#4 and #6), every DU-MSDSAI-4441 weekly pset, `llm-safety-alignment-study`
- **Frontmatter description:** *"Reports statistical results with effect sizes + 95% CI + direction, refuses to report bare p-values as 'significant'. Use whenever a user reports a t-test, regression, chi-squared, McNemar, or any hypothesis test result; the user is writing up a stats homework / paper / report; or the user says 'p < 0.05 so X is true'. Selects the appropriate effect-size metric per test (Cohen's d for parametric two-group, Cliff's δ for non-parametric, odds ratio for categorical, partial η² for ANOVA, R²-adjusted for regression)."*
- **What the skill teaches:**
  - **Metric per test family:**
    - Parametric two-group (t-test): Cohen's d with 95% CI
    - Non-parametric two-group (Wilcoxon/Mann-Whitney): Cliff's δ with 95% CI
    - Paired (paired t / signed-rank): Cohen's dz with 95% CI
    - Categorical 2x2 (chi-squared / Fisher / McNemar): odds ratio with 95% CI, or risk difference
    - ANOVA / regression: partial η² or R²-adjusted with 95% CI
  - **Required report sentence:** "<metric> = <value> [95% CI: <low>, <high>], direction: <which group higher>, n = <sample size>."
  - **Refuse bare p-value:** "p < 0.05 so significant" without effect size + CI gets bounced
  - **Interpretation glossary** (Cohen 1988 conventions, with explicit caveat that domain matters more than rules of thumb):
    - Cohen's d: 0.2 small, 0.5 medium, 0.8 large
    - Cliff's δ: 0.11 small, 0.28 medium, 0.43 large
    - Odds ratio: depends on context; flag any OR with CI crossing 1.0
  - **Direction sentence:** never just "groups differ" — always state which group is higher/lower
- **When NOT to use:**
  - Pure pedagogy where the explicit point is teaching p-value mechanics (e.g., a stats lecture on Type I error)
  - Pure descriptive statistics (means, SDs) without a hypothesis test
- **Eval scenarios:**
  - **01-happy-path:** Query: *"We ran a paired t-test on before/after blood pressure for 30 patients. p = 0.012, t(29) = 2.68, mean diff = 4.3 mmHg. Help me report this."* → Skill should produce a Cohen's dz (paired) + 95% CI + direction sentence. Rubric: (1) computes or names Cohen's dz (not unpaired d); (2) includes 95% CI; (3) names direction (e.g., "after BP was lower than before by 4.3 mmHg").
  - **02-edge-case:** Query: *"The Shapiro test says the differences aren't Normal (p = 0.003). I ran a Wilcoxon signed-rank: V = 38, p = 0.018. Now what?"* → Skill should switch to non-parametric effect size (Cliff's δ or paired r) — NOT report Cohen's d on non-Normal data. Rubric: (1) does NOT recommend Cohen's d; (2) recommends Cliff's δ or rank-biserial r; (3) includes 95% CI for the non-parametric metric.
  - **03-anti-trigger:** Query: *"For our stats lecture, explain how the p-value formula works and why p < 0.05 became conventional."* → Skill should NOT pivot to effect-size mandates; pedagogy about p-value mechanics is the legitimate scope. Rubric: (1) does NOT refuse the pedagogical request; (2) explains p-value mechanics as asked; (3) may optionally note that effect sizes are also important in real reporting, but does NOT block the lecture.

### Batch 1 PR template (use this for the PR body)

```markdown
## Summary

Batch 1: Phase 2 high-Σ low-effort cluster. Ships 4 skills (Σ ≥ 19 each) authored via PRAGMATIC discipline.

### Skills shipped

- `workflow/enforcing-seed-hygiene` v0.1.0 — first-cell seed gate + multi-library cookbook + CPU-pin determinism (Σ 20)
- `workflow/validating-temporal-fields` v0.1.0 — reject-future + min-year-fallback + event-vs-disclosure separation (Σ 19)
- `security/auditing-pinned-dependencies` v0.1.0 — grep-for-unpinned-installs across README/Dockerfile/CI/package.json (Σ 19)
- `ml-datasci/reporting-effect-sizes` v0.1.0 — effect-size selector + 95% CI + direction sentence; refuses bare p-value (Σ 19)

### Eval results (Sonnet-only PRAGMATIC)

<paste results>

### Test plan

<see PR template at top of plan>

### Integration deferred

Root README catalog + `skills/README.md` cross-track index + `CHANGELOG.md` updates deferred to Batch 6.
```

---

## Batch 2: Phase 3 stats discipline (3 skills)

**Branch:** `feature/v1.0.0-batch-2-stats-discipline`
**Short name (worktree dir):** `RCS-batch-2`
**Skills shipped:** 3
**Tracks touched (README updates):** `ml-datasci/` only

### 2.1 selecting-statistical-test (Σ 18)

- **Slug:** `selecting-statistical-test`
- **Track:** `ml-datasci`
- **Audience:** `[data-scientist, stats-student, instructor, ml-engineer]`
- **Evidence:** `DU-MSDSAI-4441-Final/README.md` (test-selection decision tree), all DU-MSDSAI-4441 weekly psets, `llm-safety-alignment-study` (McNemar / Wilcoxon / Cochran Q)
- **Frontmatter description:** *"Walks a decision tree from data characteristics (sample count, paired vs independent, measurement scale, distributional assumptions) to a recommended statistical test (t / Welch / Wilcoxon / Mann-Whitney / Sign / paired-t / Fisher / chi-squared / McNemar / Cochran-Q). Names the gating assumption check that determined the choice. Use when the user has a hypothesis and data in hand and needs to commit to a test before running it."*
- **What the skill teaches:**
  - Decision-tree walk: 1 vs 2+ groups → paired vs independent → continuous vs categorical → normal vs non-normal → equal variance vs Welch
  - For 2x2 categorical: chi-squared if all expected counts ≥ 5, Fisher if not; this is THE rule the DU-MSDSAI-4441-Final GRADING_ISSUES.md #7 flagged
  - For paired binary: McNemar (continuity-corrected if exact n ≥ 25)
  - For repeated-measures binary: Cochran's Q
  - **Always cite the gating assumption check that drove the choice** — e.g., "Shapiro p = 0.003 → non-Normal → Wilcoxon (not paired t)"
  - Refuses to recommend a test without first asking: design (paired/independent), measurement scale, sample size, distributional assumption status
- **When NOT to use:**
  - Already-decided test where the user just wants help running it (different skill)
  - Bayesian workflows (different skill)
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I have before/after blood pressure for 18 patients. Shapiro on the differences gives p = 0.003. Which test?"* → Skill should recommend Wilcoxon signed-rank (paired + non-Normal), explicitly citing the Shapiro result as the gating check. Rubric: (1) recommends Wilcoxon signed-rank; (2) identifies the design as paired; (3) names the Shapiro p as the gating assumption check.
  - **02-edge-case:** Query: *"I have a 2x2 contingency table: 3 successes / 7 failures vs 8 successes / 12 failures. Chi-squared or Fisher?"* → Skill should recommend Fisher because expected counts will fall below 5. Rubric: (1) recommends Fisher (not chi-squared); (2) names the expected-count-<-5 rule; (3) computes or estimates expected counts to justify.
  - **03-anti-trigger:** Query: *"Run a t-test on this column for me."* → Skill should NOT just run the test — must first elicit design (paired/independent), measurement scale, and assumption status. Rubric: (1) does NOT immediately recommend a test; (2) asks at least about paired vs independent; (3) asks at least about distributional assumption (normality or sample size justification for CLT).

### 2.2 checking-test-assumptions (Σ 18)

- **Slug:** `checking-test-assumptions`
- **Track:** `ml-datasci`
- **Audience:** `[data-scientist, stats-student, instructor, ml-engineer]`
- **Evidence:** `DU-MSDSAI-4441-Final/GRADING_ISSUES.md` (#1 Normality, #5 conditional-on-Normality, #7 chi-squared-expected-count), every 4441 weekly pset
- **Frontmatter description:** *"Runs the appropriate assumption checks for a chosen statistical test (Shapiro-Wilk for normality, Levene/Brown-Forsythe for equal variance, QQ-plot for residuals, Cook's D for influence) and reports pass/fail per assumption with the evidence (test statistic + p-value). Use whenever the user is about to run a parametric test, has just run one and wants to validate, or asks 'are the assumptions met?'."*
- **What the skill teaches:**
  - **Normality:** Shapiro-Wilk (n ≤ 50), Anderson-Darling (larger n), QQ-plot inspection always. p < 0.05 → reject Normality
  - **Equal variance:** Levene's test (more robust) over Brown-Forsythe over Bartlett's. p < 0.05 → unequal variance → use Welch's t instead of pooled t
  - **Residual diagnostics for regression:** plot residuals vs fitted (heteroscedasticity), QQ-plot of residuals (Normality of residuals), Cook's D > 1 (influential observations)
  - **Chi-squared expected counts:** for 2x2, all expected counts ≥ 5 → chi-squared OK; any < 5 → Fisher
  - **Report format:** per-assumption table — Assumption · Test · Statistic · p-value · Verdict (pass/fail) · Consequence-if-fail
  - **Refuse running parametric test without assumption check first**
- **When NOT to use:**
  - Non-parametric tests that have minimal assumptions (Sign test, randomization tests)
  - Already-known-to-violate cases where the user is intentionally robust-testing
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I want to run a two-sample t-test on tumor sizes between treatment and control. n=30 per group. Check assumptions."* → Skill should run/recommend Shapiro per group + Levene for equal variance + report Normality and equal-variance verdicts. Rubric: (1) recommends Shapiro per group (or Anderson-Darling); (2) recommends Levene's test; (3) reports a per-assumption table with verdicts.
  - **02-edge-case:** Query: *"Shapiro for group A: p = 0.12. Shapiro for group B: p = 0.001. Levene: p = 0.04. What now?"* → Skill should identify (a) Group B non-Normal → consider Mann-Whitney, (b) unequal variance → if sticking with parametric, Welch not pooled t. Rubric: (1) flags Group B non-Normality; (2) flags unequal variance; (3) recommends Mann-Whitney (or Welch as a fallback).
  - **03-anti-trigger:** Query: *"I'm running a randomization permutation test. Check assumptions."* → Skill should explain randomization tests have minimal distributional assumptions; the only "assumption" is exchangeability under the null. Rubric: (1) does NOT recommend Shapiro or Levene for a permutation test; (2) names exchangeability as the relevant assumption; (3) explains why parametric assumption checks don't apply.

### 2.3 auditing-train-test-split (Σ 18)

- **Slug:** `auditing-train-test-split`
- **Track:** `ml-datasci`
- **Audience:** `[data-scientist, ml-engineer]`
- **Evidence:** every DU-MSDSAI-4432-* notebook, `TRACT` (LOFO discipline), `ai-security-framework-crosswalk` (hub-firewall)
- **Frontmatter description:** *"Audits a train/test/validation split for leakage, stratification, group-aware violations, and temporal-order violations. Use when the user creates a train/test split, when classifier accuracy looks suspiciously high, when the same ID could appear in train and test, when time-series data is split randomly instead of by date, or when group-aware data (multiple rows per patient/user/customer) is split row-wise."*
- **What the skill teaches:**
  - **Leakage checks:**
    - Same ID in train and test? Fail.
    - Feature derived from the target? Fail. (e.g., "patient_outcome_severity_score" predicting "outcome")
    - Imputation/normalization fit on full dataset before split? Fail — fit on train, transform on test.
  - **Stratification:** for classification with imbalanced classes, use `stratify=y` to preserve class proportions
  - **Group-aware splitting:** when multiple rows share a group (patient_id, user_id), use GroupKFold / GroupShuffleSplit, NOT row-level random split
  - **Temporal splitting:** time-series data MUST split by date (train = past, test = future); random splits leak future information
  - **LOFO discipline:** for crosswalking / multi-source learning, leave-one-source-out cross-validation prevents the model from memorizing source quirks
  - **Hub-firewall:** when one source acts as a "hub" connecting others, exclude its representation when validating on held-out source
- **When NOT to use:**
  - Unsupervised methods without a held-out split
  - Bootstrap / cross-validation already accounting for leakage at the resampling layer
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I'm building a classifier on hospital readmission. Each row is one visit; some patients have multiple visits. I used `train_test_split(X, y, test_size=0.2, random_state=42)`. Audit it."* → Skill should flag group-leakage (same patient in train and test) and recommend GroupShuffleSplit by patient_id. Rubric: (1) identifies group-leakage (same patient in train+test); (2) recommends GroupShuffleSplit (or GroupKFold); (3) explains why row-level random split fails for visit data.
  - **02-edge-case:** Query: *"I'm forecasting demand from 5 years of weekly sales. I used `train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)`. Audit it."* → Skill should flag temporal leakage (random split mixes past and future) and recommend `TimeSeriesSplit` or train-on-past, test-on-future. Rubric: (1) flags the temporal violation; (2) recommends time-aware splitting (TimeSeriesSplit or date-based slice); (3) explains why shuffle=True is wrong for time series.
  - **03-anti-trigger:** Query: *"I'm running k-means clustering on customer segments. Audit my train/test split."* → Skill should explain unsupervised clustering doesn't need a train/test split in the supervised sense; suggest cluster-stability assessment (e.g., bootstrap silhouette) instead. Rubric: (1) does NOT criticize the absence of a train/test split; (2) names cluster-stability / bootstrap-silhouette as the appropriate validation; (3) clarifies that train/test split is a supervised-learning concept.

### Batch 2 PR template

Same structure as Batch 1, substituting:
- Title: `v1.0.0-batch-2: 3 stats discipline skills`
- Skills shipped: 3 entries for selecting-statistical-test / checking-test-assumptions / auditing-train-test-split

---

## Batch 3: Phase 4 ML eval cluster (3 skills)

**Branch:** `feature/v1.0.0-batch-3-ml-eval`
**Short name (worktree dir):** `RCS-batch-3`
**Skills shipped:** 3
**Tracks touched (README updates):** `ml-datasci/` only

### 3.1 evaluating-binary-classifiers (Σ 19)

- **Slug:** `evaluating-binary-classifiers`
- **Track:** `ml-datasci`
- **Audience:** `[data-scientist, ml-engineer, security-eng]`
- **Evidence:** `email-spam-classifier-naive-bayes-comparisson-roc`, `multiturn-injection-detection`, `llm-safety-alignment-study`, `DU-MSDSAI-4432-TitanicSurvivalClassifiers`, `DU-MSDSAI-4432-DiabetesDiseasePrediction`
- **Frontmatter description:** *"Produces a complete binary-classifier evaluation report from y_true and y_pred_proba: ROC curve + PR curve + calibration plot + confusion matrix + threshold-sweep + class-imbalance check + bootstrap 95% CI on each metric. Use whenever the user has a trained binary classifier and asks 'how good is it', when class imbalance is suspected, when the user only reports accuracy on imbalanced data, or when threshold selection is needed."*
- **What the skill teaches:**
  - Required plots: ROC, PR, calibration (reliability diagram), confusion matrix
  - Required metrics: ROC-AUC, PR-AUC, F1 at default threshold, accuracy/precision/recall/specificity at default threshold + at optimal threshold
  - Bootstrap 95% CI on AUC and F1 (n_bootstrap ≥ 1000)
  - **Class-imbalance check:** if minority class < 20% of data, accuracy is misleading; lead with PR-AUC and per-class F1
  - **Threshold sweep:** plot precision/recall/F1 across thresholds; do NOT default to 0.5 without checking
  - **Refuse to report bare accuracy** when classes are imbalanced
- **When NOT to use:**
  - Multi-class classification (different skill: evaluating-multiclass-classifiers)
  - Regression (different skill: evaluating-regression-models)
  - Ranking / retrieval (different skill: evaluating-rag-retrieval)
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I trained a logistic regression on spam vs ham. I have y_true and y_pred_proba arrays. Evaluate it."* → Skill should produce or specify ROC + PR + calibration + CM + threshold sweep + bootstrap CIs. Rubric: (1) names ROC + PR + calibration as required; (2) names threshold sweep (not assume 0.5); (3) names bootstrap CI on AUC.
  - **02-edge-case:** Query: *"My fraud classifier has 99% accuracy. Sounds great, right?"* → Skill should immediately ask about class balance — fraud is typically rare (<1%), 99% accuracy = always-predict-not-fraud. Rubric: (1) flags class imbalance as the likely explanation; (2) requests class distribution; (3) recommends PR-AUC + per-class recall over accuracy.
  - **03-anti-trigger:** Query: *"I have a 3-class classifier — benign, malicious, suspicious. Evaluate it."* → Skill should hand off to a multiclass-evaluation skill; binary-specific tools like ROC don't directly apply (one-vs-rest is a workaround, not a clean fit). Rubric: (1) identifies this as multiclass, not binary; (2) does NOT force binary ROC interpretation; (3) hands off to evaluating-multiclass-classifiers (planned).

### 3.2 building-baseline-models (Σ 17)

- **Slug:** `building-baseline-models`
- **Track:** `ml-datasci`
- **Audience:** `[data-scientist, ml-engineer, stats-student]`
- **Evidence:** every DU-MSDSAI-4432-* notebook (all jumped to "fancy model" without baselines)
- **Frontmatter description:** *"Builds simple baseline models (Dummy / LogisticRegression / RandomForest) before fitting a complex model, so the user knows what 'better than nothing' looks like. Use when the user is about to fit gradient boosting, deep learning, or any complex model; when the user reports a metric without comparison context; or when the user is unsure if their fancy model is actually better than chance."*
- **What the skill teaches:**
  - **Baseline ladder:**
    1. `DummyClassifier(strategy='stratified')` or `DummyRegressor(strategy='mean')` — pure-chance baseline
    2. Linear baseline: LogisticRegression (classification) or LinearRegression (regression)
    3. Tree baseline: RandomForestClassifier / RandomForestRegressor with default hyperparameters
  - **Same evaluation regime for all baselines** as the final model (same train/test split, same metric, same CV folds)
  - **Report comparison table:** baseline · metric · CI; final model · metric · CI; lift over baseline
  - **Refuse to celebrate a fancy-model metric without baseline comparison**
- **When NOT to use:**
  - Pure unsupervised work without a supervised target
  - Already-have-baseline cases where you just need to fit the next model in the ladder
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I'm training XGBoost on a binary classification task. What baselines should I add?"* → Skill should specify Dummy + Logistic + RandomForest with the same eval regime. Rubric: (1) recommends Dummy as the chance baseline; (2) recommends a linear baseline (LogReg); (3) requires the same train/test split for comparison.
  - **02-edge-case:** Query: *"My XGBoost gets 0.92 ROC-AUC. Is that good?"* → Skill should refuse to answer without baseline comparison; ask what Dummy and LogReg ROC-AUC are. Rubric: (1) does NOT call 0.92 "good" without context; (2) requests baseline metrics; (3) explains lift-over-baseline is the right framing.
  - **03-anti-trigger:** Query: *"I'm running PCA on my data to find the top components. What baselines do I need?"* → Skill should explain unsupervised PCA doesn't have a "baseline" in the supervised sense; suggest variance-explained sanity checks. Rubric: (1) does NOT force a Dummy baseline; (2) explains baselines are a supervised concept; (3) recommends variance-explained / Kaiser-criterion as the relevant sanity check.

### 3.3 evaluating-regression-models (Σ 17)

- **Slug:** `evaluating-regression-models`
- **Track:** `ml-datasci`
- **Audience:** `[data-scientist, ml-engineer, stats-student]`
- **Evidence:** `DU-MSDSAI-4432-MultiModelBikeShareRegression`, `DU-MSDSAI-4432-MultiModelDiseaseProg`
- **Frontmatter description:** *"Produces a complete regression-model evaluation report: RMSE + MAE + R² (with adjusted-R² for multi-feature) + residual plots (residuals vs fitted, QQ-plot of residuals) + cross-validation. Use whenever the user has a regression model and asks 'how good is it', when residual diagnostics are needed, when the user reports only R² without RMSE/MAE, or when CV is missing."*
- **What the skill teaches:**
  - Required metrics: RMSE (interpretable in target units), MAE (robust to outliers), R² and adjusted-R² (variance explained)
  - Required plots: residuals vs fitted (heteroscedasticity), QQ-plot of residuals (Normality), histogram of residuals (skew)
  - Required CV: k-fold (k=5 default) — report mean ± SD of the metric across folds
  - **Cohen's Q² / cross-validated R²** when comparing models
  - **Refuse to report R² alone** — always pair with RMSE or MAE for interpretability
- **When NOT to use:**
  - Classification (different skill)
  - Time-series regression where the right CV is walk-forward, not k-fold (note this caveat in the skill)
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I fit a multiple linear regression to predict house price from 8 features. Evaluate it."* → Skill should specify RMSE + MAE + adjusted-R² + residual plots + k-fold CV. Rubric: (1) names RMSE or MAE alongside R² (not R² alone); (2) requires adjusted-R² for multi-feature; (3) requires residual diagnostics (residuals vs fitted or QQ).
  - **02-edge-case:** Query: *"My R² is 0.85. Sounds great, right?"* → Skill should ask for RMSE in target units AND check whether R² was computed on train or test. Rubric: (1) requests RMSE in target units for interpretability; (2) flags the train-vs-test ambiguity; (3) requests CV result.
  - **03-anti-trigger:** Query: *"I'm forecasting monthly demand for 24 months ahead from 10 years of weekly data. Evaluate my model."* → Skill should flag that k-fold CV is wrong for time-series; recommend walk-forward CV or expanding-window CV. Rubric: (1) does NOT recommend standard k-fold CV; (2) recommends walk-forward / expanding-window CV; (3) explains why random k-fold leaks future information for time series.

### Batch 3 PR template — substitute as Batch 1.

---

## Batch 4: Phase 5 data + workflow hygiene (3 skills)

**Branch:** `feature/v1.0.0-batch-4-data-hygiene`
**Short name (worktree dir):** `RCS-batch-4`
**Skills shipped:** 3
**Tracks touched (README updates):** `workflow/` only

### 4.1 deduplicating-records (Σ 18)

- **Slug:** `deduplicating-records`
- **Track:** `workflow`
- **Audience:** `[data-engineer, data-scientist, security-eng]`
- **Evidence:** `genai_agentic_incidents` CHANGELOG.md 2.0.0 (three distinct dedupe bugs documented)
- **Frontmatter description:** *"Deduplicates records in a corpus / dataset / incident registry with discipline that avoids the index-stale, transitive-collapse, and ID-format-mismatch bugs. Use when ingesting data from multiple sources, merging registries, or whenever the user says 'we have duplicates' — especially after a recent merge or schema change."*
- **What the skill teaches:**
  - **Refresh indices after every merge:** before applying the next merge rule, rebuild any in-memory index over the working set. Stale indices were the genai_agentic_incidents 2.0.0 bug #1.
  - **Transitive collapse:** if A↔B and B↔C are duplicates, A↔C must also collapse. Verify by computing connected components in a duplicate graph, not by greedy pairwise merging. Bug #2 of 2.0.0.
  - **ID format normalization:** `AIID-N-OECD` and `AIID-N` referring to the same incident must be matched after stripping the source suffix. Bug #3.
  - **Multi-key dedup:** define an ordered list of keys (CVE id > source-canonical-url > fuzzy-title within ±1 year > author + date). Document each rule's confidence.
  - **Manual review threshold:** keep a "manual_review" bucket for borderline matches; never silent-collapse.
  - **Output a diff:** every dedup run produces `{merged: [...], borderline: [...], untouched: [...]}` for auditability.
- **When NOT to use:**
  - Exact-match dedup with a single trusted ID (e.g., primary key) — use SQL DISTINCT
  - Streaming dedup where the registry is append-only (different concerns)
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I have an incident corpus with 12,000 records merged from AIID, OECD AIM, and AIAAIC. After ingest I see duplicates. How do I dedupe?"* → Skill should specify multi-key + index-refresh + transitive-collapse + ID-normalization. Rubric: (1) names multi-key dedup with documented confidence per key; (2) names index-refresh after each merge; (3) names transitive-collapse via connected components.
  - **02-edge-case:** Query: *"We merged record A with B, then B with C, but A and C are still flagged as duplicates afterward. Why?"* → Skill should identify the transitive-collapse-failure pattern. Rubric: (1) names transitive-collapse as the failure mode; (2) recommends connected-components / union-find; (3) cites greedy pairwise merging as the anti-pattern.
  - **03-anti-trigger:** Query: *"I have a customers table with a primary key customer_id. Dedupe it."* → Skill should NOT engage the multi-key fuzzy workflow; suggest `SELECT DISTINCT` or `DROP DUPLICATES` on the primary key. Rubric: (1) does NOT force multi-key fuzzy dedup; (2) recommends primary-key DISTINCT; (3) explains the multi-key workflow is for cases where no single trusted ID exists.

### 4.2 pinning-reproducible-environments (Σ 17)

- **Slug:** `pinning-reproducible-environments`
- **Track:** `workflow`
- **Audience:** `[data-scientist, ml-engineer, security-eng, devops]`
- **Evidence:** every RCS-style repo Rock builds; harness `~/.claude/CLAUDE.md` QC.1
- **Frontmatter description:** *"Pins a project's environment for reproducibility — uv.lock / poetry.lock / requirements.lock for Python, package-lock.json / pnpm-lock.yaml for Node, renv.lock for R, Devcontainer / Dockerfile for system-level. Use when starting a new project, when 'works on my machine but not CI', when onboarding a teammate, or when reproducibility for a paper / regulatory submission is required."*
- **What the skill teaches:**
  - **Python:** `uv lock` (or `poetry lock`) produces `uv.lock` / `poetry.lock` with hashes; commit it. `pip-compile --generate-hashes` for plain pip.
  - **Node:** commit `package-lock.json` (npm) or `pnpm-lock.yaml`; use `npm ci` (not `npm install`) in CI for lockfile enforcement.
  - **R:** `renv::init()` → `renv.lock`. Commit it.
  - **Python version pin:** `.python-version` file or `requires-python = "==3.13.*"` in pyproject — explicit, not floating.
  - **System-level:** Devcontainer config with explicit base image SHA, or a Dockerfile with pinned base image (FROM python:3.13.0-slim@sha256:...).
  - **CI drift check:** weekly cron that re-locks and diffs; PR if the locked versions changed.
- **When NOT to use:**
  - Exploratory prototype where pinning friction outweighs benefit
  - Hot-reload library development where you intentionally float deps
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I'm starting a new Python ML project. How do I set up reproducible deps?"* → Skill should specify uv (or poetry) + commit lockfile + pin Python version + CI drift check. Rubric: (1) recommends uv lock or poetry lock (not bare pip install); (2) recommends committing the lockfile; (3) recommends pinning the Python version (.python-version or requires-python).
  - **02-edge-case:** Query: *"My teammate's Docker container has the same Dockerfile as mine but produces different model outputs. Why?"* → Skill should identify base-image-SHA drift (FROM python:3.13-slim today != FROM python:3.13-slim last month) and recommend pinning the digest. Rubric: (1) names base-image drift; (2) recommends FROM python@sha256:... digest pinning; (3) explains version tags can move.
  - **03-anti-trigger:** Query: *"I'm just experimenting in a Jupyter notebook on my laptop. Pin my environment?"* → Skill should NOT force the lockfile machinery; explain a throwaway notebook doesn't need it. Rubric: (1) does NOT force uv lock setup; (2) explains pinning is project-scoped, not session-scoped; (3) suggests revisiting if the experiment becomes a project.

### 4.3 auditing-data-quality (Σ 17)

- **Slug:** `auditing-data-quality`
- **Track:** `workflow`
- **Audience:** `[data-engineer, data-scientist, security-eng]`
- **Evidence:** every DU-MSDSAI-4432-* notebook (all jumped to modeling without data audits), `llm-toxicity-visual-analysis`, `genai_agentic_incidents`
- **Frontmatter description:** *"Audits a dataset for data quality — nulls, ranges, types, semantic class, cardinality, outliers, leakage between rows. Use when receiving a new dataset, before fitting any model, when something seems off in results, or when a dataset suddenly grew/shrunk between runs."*
- **What the skill teaches:**
  - **Per-column report:** type · null count · null % · min · max · mean · SD · unique values · sample values
  - **Semantic class detection:** ID / categorical / continuous / ordinal / text / datetime / boolean (per column)
  - **Outlier flags:** values > 3 SD or > 99th percentile, with context (is this expected?)
  - **Range sanity:** ages > 120, prices < 0, lat/lon outside ±90/±180
  - **Row-level integrity:** duplicate rows (with and without ID column), conflicting fact-pairs (same key, different value)
  - **Cardinality alarm:** any "categorical" column with cardinality > 100 unique values is suspect (might be free text masquerading as category)
- **When NOT to use:**
  - Already-curated benchmark dataset where the audit has been done
  - Streaming / unbounded data where a full-table scan is impractical (different patterns apply)
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I just got a 50k-row patient dataset for a classification task. Audit the data."* → Skill should run/recommend per-column null/range/type/cardinality + duplicate-row check. Rubric: (1) recommends per-column null and range audit; (2) recommends duplicate-row check (with and without ID); (3) recommends cardinality alarm for free-text columns.
  - **02-edge-case:** Query: *"My 'age' column has values from 0 to 250. Should I drop the outliers?"* → Skill should ask about semantic class (is 0 a placeholder? is 250 a data-entry error or a legit edge case?); flag suspect ranges but don't drop without context. Rubric: (1) does NOT immediately drop the outliers; (2) requests semantic context (is 0 a missing-value sentinel?); (3) recommends investigating before dropping.
  - **03-anti-trigger:** Query: *"I have a streaming pipeline ingesting 1M events/sec. Audit the data quality."* → Skill should NOT recommend full-table scan; recommend sampling + per-batch quality metrics + streaming alerts. Rubric: (1) does NOT recommend full-table audit on streaming data; (2) recommends sampling or per-batch metrics; (3) recommends streaming-friendly alerts (Great Expectations, Soda, custom).

### Batch 4 PR template — substitute as Batch 1.

---

## Batch 5: Phase 6 meta + context (3 skills)

**Branch:** `feature/v1.0.0-batch-5-meta`
**Short name (worktree dir):** `RCS-batch-5`
**Skills shipped:** 3
**Tracks touched (README updates):** `claude-code-meta/` and `workflow/`

### 5.1 writing-claude-code-skill (Σ 18)

- **Slug:** `writing-claude-code-skill`
- **Track:** `claude-code-meta`
- **Audience:** `[skill-author]`
- **Evidence:** this entire RCS authoring session; Anthropic Skill best-practices doc
- **Frontmatter description:** *"Walks the Anthropic Skill best-practices checklist plus the RCS Layer-3 documentation contract for authoring a new Claude Code skill. Use when the user wants to write a new skill, plugin skill, or marketplace skill — for any host (Claude Code, Copilot CLI, Gemini CLI, Anthropic API)."*
- **What the skill teaches:**
  - Naming: gerund-form, lowercase-kebab, ≤ 64 chars, no `anthropic`/`claude` reserved words
  - Frontmatter: required `name` + `description` (third-person, ≤ 1024 chars, what + when), plus RCS-custom fields (status, track, version, audience, evidence, last-updated)
  - Layer-3 H2 sections in order: When-to-use, When-NOT-to-use, Quick-start, Inputs/Args/Flags, Workflow, Outputs, Failure-modes, References, Examples, See-also, Status-&-version
  - Body ≤ 500 lines; bundle long content in `reference/`
  - Reference links one level deep (per Anthropic doc — Claude may partially read transitive refs)
  - Eval-first per Anthropic doc: write 3 scenarios before the body (RCS variant: PRAGMATIC is acceptable for batch authoring)
  - When to NOT engineer: if it's a one-off, not reusable across projects, project-specific (use CLAUDE.md), or mechanical (write a hook instead)
- **When NOT to use:**
  - User is asking about the Claude API or Anthropic SDK (different skill: claude-api)
  - User is writing a plugin manifest, hook script, or rules file (different skills, planned)
- **Eval scenarios:**
  - **01-happy-path:** Query: *"I want to write a skill that helps with auditing GraphQL schemas. Walk me through it."* → Skill should specify gerund-form slug, name/description rules, Layer-3 sections, eval-first. Rubric: (1) recommends gerund-form naming; (2) names the Layer-3 required H2 sections; (3) recommends writing evals before body.
  - **02-edge-case:** Query: *"My description is 'I can help you find vulnerabilities in your GraphQL schema.' Is that good?"* → Skill should flag first-person POV violation and rewrite as third-person. Rubric: (1) flags the first-person ('I can help') as wrong; (2) rewrites in third-person; (3) cites the Anthropic best-practices rule.
  - **03-anti-trigger:** Query: *"I have a one-off bash script that cleans up logs in this project. Should I make it a skill?"* → Skill should say no — this is project-specific tooling, belongs in scripts/ or CLAUDE.md, not a portable skill. Rubric: (1) does NOT recommend authoring a skill; (2) explains skills are reusable across projects; (3) suggests scripts/ or CLAUDE.md.

### 5.2 auditing-claude-md-hierarchy (Σ 18)

- **Slug:** `auditing-claude-md-hierarchy`
- **Track:** `claude-code-meta`
- **Audience:** `[skill-author, devops]`
- **Evidence:** Rock's harness QC.4b (400-line cap, cache hygiene)
- **Frontmatter description:** *"Audits a CLAUDE.md hierarchy for size budget, cache hygiene, and drift. Checks total line count across user CLAUDE.md + project CLAUDE.md + plugin CLAUDE.mds (cap: 400 lines, target: 250). Flags timestamps and per-run state that break cache reuse. Use when CLAUDE.md feels bloated, when token usage seems high at session start, or when adding a new instruction file."*
- **What the skill teaches:**
  - **Size budget:** total CLAUDE.md hierarchy ≤ 400 lines (hard cap), target 250 lines
  - **Cache hygiene:** no timestamps, no per-run identifiers, no dynamic content (those break the 5-minute prompt-cache TTL)
  - **`<system-reminder>` for dynamic content:** anything that changes per-session goes in a system-reminder block, NOT in CLAUDE.md
  - **Hierarchy precedence:** managed > user (~/.claude/CLAUDE.md) > project (./CLAUDE.md) > plugin CLAUDE.mds — know which one your rule lives in
  - **Per-directive audit:** for each line, ask "does this need to be in every cached prefix? Or can it be a skill (loaded on demand)?"
  - **Drift detection:** run `wc -l` against all CLAUDE.md files monthly; alert if total grows past target
- **When NOT to use:**
  - Single-file CLAUDE.md under 100 lines (not enough to audit)
  - First-time setup where the user is asking what to PUT in CLAUDE.md (different skill)
- **Eval scenarios:**
  - **01-happy-path:** Query: *"My CLAUDE.md hierarchy is bloated. Audit it."* → Skill should run `wc -l` on user + project + plugin CLAUDE.mds, report totals, flag against the 400-cap. Rubric: (1) names the 400-line cap (or 250 target); (2) recommends checking each level of the hierarchy; (3) recommends `<system-reminder>` for dynamic content.
  - **02-edge-case:** Query: *"My project CLAUDE.md has a line like 'Today is 2026-05-23'. Is that OK?"* → Skill should flag the timestamp as cache-breaking. Rubric: (1) flags the timestamp; (2) explains it breaks the 5-min prompt cache; (3) recommends moving it to a system-reminder hook or removing.
  - **03-anti-trigger:** Query: *"I just started a new project. What should I put in CLAUDE.md?"* → Skill should hand off to a different skill (setting-up-claude-md, planned); audit is for existing files. Rubric: (1) does NOT engage the audit workflow; (2) explains audit is for existing CLAUDE.md, not greenfield; (3) suggests the setup-CLAUDE-md path.

### 5.3 auditing-context-window-pressure (Σ 17)

- **Slug:** `auditing-context-window-pressure`
- **Track:** `workflow`
- **Audience:** `[skill-author, devops, ml-engineer]`
- **Evidence:** Rock's harness QC.4b (cache hygiene), this very session's context bloat
- **Frontmatter description:** *"Audits a Claude Code (or Anthropic API) session for context-window pressure — total context usage, cache hit rate, CLAUDE.md hierarchy size, tool-result bloat, conversation-history compression triggers. Use when the session feels slow, when token cost seems high, when prompt-cache hit rate is dropping, or before long-running multi-turn workflows."*
- **What the skill teaches:**
  - **Total context check:** what % of the 200k window is used? At >75% → activate token-efficient mode
  - **Cache hit rate:** under 70% → investigate (was a CLAUDE.md edited mid-session? Did a timestamp leak in?)
  - **CLAUDE.md hierarchy size:** ≤ 400 lines total (cross-reference auditing-claude-md-hierarchy)
  - **Tool-result bloat:** large file reads, full-repo greps, or subagent outputs >5KB inflate context fast — switch to subagent summaries or partial reads
  - **System-reminder accumulation:** check if dynamic content is leaking into the cached prefix
  - **Long-conversation compression:** Claude Code auto-compresses old messages — note that compression-then-decompression is cheaper than continuous bloat
  - **Triage steps:**
    1. Move long tool results (>5KB) into files; refer by path instead of inline
    2. Dispatch subagents with summaries-only return contracts
    3. Use `/clear` for true session restart (loses all context, last resort)
    4. Use `/compact` for in-place compression (preserves intent)
- **When NOT to use:**
  - Short interactive sessions under ~10 turns where pressure isn't a concern
  - One-shot API calls outside Claude Code
- **Eval scenarios:**
  - **01-happy-path:** Query: *"My Claude Code session is slow and feels like it's using too much context. Help me audit it."* → Skill should specify total-context check + cache-hit check + CLAUDE.md size + tool-result bloat. Rubric: (1) names the 75% context threshold (or "% of 200k window"); (2) recommends cache-hit-rate inspection; (3) recommends subagent summarization for large outputs.
  - **02-edge-case:** Query: *"My prompt cache hit rate just dropped from 90% to 30%. Why?"* → Skill should investigate CLAUDE.md edits, system-reminder content drift, or timestamp leaks. Rubric: (1) names CLAUDE.md edits as a possible cause; (2) names timestamp/dynamic-content leaks; (3) recommends inspecting recent changes to the cached prefix.
  - **03-anti-trigger:** Query: *"I'm making a quick 3-message API call from a Python script. Audit the context."* → Skill should explain context auditing is for long-running sessions; a 3-message API call doesn't have meaningful context pressure. Rubric: (1) does NOT force the full audit on a short call; (2) explains the skill is for long sessions; (3) suggests the user just check the API response token counts directly.

### Batch 5 PR template — substitute as Batch 1.

---

## Batch 6: Integration (run after all batches 1-5 have merged)

**Branch:** `feature/v1.0.0-batch-6-integration`
**Short name (worktree dir):** `RCS-batch-6`
**Skills shipped:** 0 (this batch updates catalogs only)
**Tracks touched:** none of the track READMEs; updates root README, skills/README.md, CHANGELOG.md

### Pre-check

Before starting Batch 6, confirm:
- All PRs from batches 1-5 are merged to main
- No open PRs exist for batches 1-5 (check `gh pr list --state open`)
- `git log --oneline main..origin/main` shows no upstream commits not yet pulled

### Steps

1. **Create worktree** from origin/main:
   ```bash
   git fetch origin
   git worktree add ../RCS-batch-6 -b feature/v1.0.0-batch-6-integration origin/main
   cd ../RCS-batch-6
   uv sync
   ```

2. **Consolidate changelog fragments** into CHANGELOG.md:
   - Read every file in `docs/superpowers/changelog-fragments/`
   - For each, add an `## [v1.0.0-batch-N] — <date>` section in CHANGELOG.md before the `## [Unreleased]` block
   - Preserve the fragment content verbatim under its section heading
   - After consolidation, delete the fragment files: `git rm docs/superpowers/changelog-fragments/*.md`

3. **Update root `README.md`** "Skill catalog" section:
   - Replace the placeholder table with the full list of shipped skills across all 5 tracks
   - Format: one row per shipped skill with `Skill · Track · What it does · Status · Σ`
   - Include the 2 Phase-1 skills + all skills shipped in batches 1-5
   - Update the trailing sentence to: `_N of ~80 planned skills shipped. See each track's README for the planned-skills roadmap._` (where N is the actual count)

4. **Update `skills/README.md`** cross-track index:
   - Replace the "Shipped" subsection with the full list of all shipped skills across all 5 tracks
   - Format: `[`slug`](track/slug/) | track | Σ`
   - Sort by Σ descending

5. **Lint sweep:**
   ```bash
   uv run python -m tools.lint_frontmatter $(find skills -name SKILL.md)
   uv run python -m tools.lint_skill_md $(find skills -name SKILL.md)
   for d in skills/*/*/; do
     [ -f "$d/SKILL.md" ] || continue
     uv run python -m tools.lint_links "$d"
   done
   ```
   All must print `OK`. Fix any failures.

6. **Run tests:**
   ```bash
   uv run pytest -q
   ```
   Must pass.

7. **Commit:**
   ```bash
   git add -A
   git commit -m "$(cat <<'EOF'
Consolidate batches 1-5: root catalog + cross-track index + CHANGELOG

Phase 2 (high-Σ), Phase 3 (stats discipline), Phase 4 (ML eval),
Phase 5 (data hygiene), Phase 6 (meta) merged into main via 5
independent batch PRs. This commit consolidates the per-batch
changelog fragments and updates the user-facing catalogs.

All 16 batch-shipped skills now visible in the root README catalog
and the skills/README.md cross-track index.
EOF
)"
   ```

8. **Tag** `v1.0.0-phase2-thru-6`:
   ```bash
   git tag -a v1.0.0-phase2-thru-6 -m "v1.0.0-phase2-thru-6: 16 skills shipped across 5 batches

Batches 1-5 authored independently in parallel via PRAGMATIC discipline.
Catalog consolidated and CHANGELOG updated in this integration commit."
   ```

9. **Push + PR + merge:**
   ```bash
   git push -u origin feature/v1.0.0-batch-6-integration
   git push origin v1.0.0-phase2-thru-6
   gh pr create --base main --head feature/v1.0.0-batch-6-integration \
     --title "v1.0.0-phase2-thru-6: catalog integration after 5 batch PRs" \
     --body "Consolidates changelog fragments + updates root README catalog + updates skills/README.md cross-track index after batches 1-5 merged. No new skills shipped in this PR — catalog-only."
   gh pr merge --merge --delete-branch
   ```

10. **Sync local main + cleanup:**
    ```bash
    cd ../RCS
    git checkout main
    git pull
    git worktree remove ../RCS-batch-6
    git worktree prune
    ```

11. **Install all newly-shipped skills** as symlinks in `~/.claude/skills/`:
    ```bash
    for skill in skills/workflow/*/ skills/security/*/ skills/ml-datasci/*/ skills/claude-code-meta/*/; do
      [ -f "$skill/SKILL.md" ] || continue
      name=$(basename "$skill")
      target="$HOME/.claude/skills/$name"
      # Skip if already symlinked or if a real directory exists at the target
      [ -L "$target" ] || [ -d "$target" ] && continue
      ln -s "$(pwd)/$skill" "$target"
      echo "Installed $name"
    done
    ```

### Batch 6 verification

After step 11, verify:
- All Σ ≥ 17 skills (the v1 ship batch) exist in `~/.claude/skills/` as symlinks
- A new Claude Code session lists them in the available-skills system reminder
- The root README's skill catalog table renders correctly on GitHub
- The `v1.0.0-phase2-thru-6` tag is pushed and visible at the repo's tags page

---

## Failure modes and recovery

**Two batches both modify the same track README:**
Batch 1 touches `workflow/`, `security/`, and `ml-datasci/` READMEs. Other batches touch a subset. Concurrent batch 1 + batch 2 will both touch `ml-datasci/README.md`. Mitigation: each batch only ADDS rows to "Shipped skills" and REMOVES rows from "Planned skills" — both operations are merge-friendly if rows don't overlap. If git auto-merge fails, the second-to-merge PR rebases on main and re-resolves.

**Sonnet-only eval fails for a skill:**
Skill ships as `status: drafting` (not `shipped`); the failure is documented in the changelog fragment + PR description. A future re-validation session can re-run the evals (in-session subagent dispatch, or via `tools.run_evals.py` if API key is available) and promote to shipped.

**A batch PR cannot be merged due to upstream conflicts:**
Run `git fetch origin && git rebase origin/main`. Resolve any conflicts (typically only in track READMEs). Force-push the branch (`git push -f`) and re-merge.

**Changelog fragment naming collision:**
Each batch's fragment name (`batch-N-<short-name>.md`) is unique by construction. If two sessions accidentally pick the same `<short-name>`, the second commit will fail. Rename and retry.

---

## Quick reference: which session runs which batch?

| Batch | Skills | Tracks | Worktree dir | Approx wall time |
|---|---|---|---|---|
| 1 | enforcing-seed-hygiene, validating-temporal-fields, auditing-pinned-dependencies, reporting-effect-sizes | workflow + security + ml-datasci | `RCS-batch-1` | 60-90 min |
| 2 | selecting-statistical-test, checking-test-assumptions, auditing-train-test-split | ml-datasci | `RCS-batch-2` | 45-60 min |
| 3 | evaluating-binary-classifiers, building-baseline-models, evaluating-regression-models | ml-datasci | `RCS-batch-3` | 45-60 min |
| 4 | deduplicating-records, pinning-reproducible-environments, auditing-data-quality | workflow | `RCS-batch-4` | 45-60 min |
| 5 | writing-claude-code-skill, auditing-claude-md-hierarchy, auditing-context-window-pressure | claude-code-meta + workflow | `RCS-batch-5` | 45-60 min |
| 6 | (integration only) | none (updates root) | `RCS-batch-6` | 15-30 min |

**Total skills shipped after all batches:** 16 (in addition to the 2 Phase-1 skills already shipped at v1.0.0-phase1).

**Parallelism:** Batches 1-5 are mutually independent. Run all 5 in parallel for fastest wall time, or sequentially if you prefer per-batch review.

**Batch 6 runs alone after all of 1-5 have merged.**
