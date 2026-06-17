# Rock's Claude Skills (RCS)

A library of 104 production-quality skills for Claude Code that encode the disciplines a security engineer, data scientist, or ML engineer would otherwise rebuild from scratch on every project. Catalog-free by design: no bundled framework controls, no ISO mirrors, no drift to maintain. Methodology only.

## What a skill does for you, in 30 seconds

A skill is a markdown file Claude reads when a relevant question comes up. Once installed, Claude consults it without being asked. Here is what that looks like.

**You ask Claude:**

> I ran a t-test on before/after blood pressure for 18 patients. Shapiro on the differences gives p = 0.003. The t-test gives p = 0.045. Is the drug effective?

**Without RCS,** Claude will probably answer the question literally and report the p-value. That is the wrong answer: the Shapiro result says the differences are not normally distributed, which means the t-test's assumptions are violated, and a p-value computed under a violated assumption is unreliable.

**With RCS installed,** Claude loads three skills automatically:

- `selecting-statistical-test` recognises that paired data plus a Shapiro p < 0.05 routes to Wilcoxon signed-rank, not paired-t
- `checking-test-assumptions` flags the Shapiro result as a gating failure and refuses to interpret the t-test
- `reporting-effect-sizes` refuses to call a bare p-value "significant" until Claude also produces an effect size with a 95% confidence interval and a direction sentence

Claude rejects the original t-test, recommends Wilcoxon, computes the effect size with its CI, and writes the result as one defensible sentence. You did not have to remember any of this. The discipline is in the skill.

## Install

Install on macOS or Linux with Claude Code. Requires `git` and Python 3.10+.

```bash
# 1. Clone the repo
git clone https://github.com/rocklambros/rcs.git
cd rcs

# 2. Create the target directory if missing
mkdir -p "$HOME/.claude/skills"

# 3. Symlink every shipped skill, skipping any name that already exists
for skill in skills/*/*/; do
  [ -f "$skill/SKILL.md" ] || continue
  name=$(basename "$skill")
  target="$HOME/.claude/skills/$name"
  if [ -L "$target" ] || [ -e "$target" ]; then
    echo "skip: $name (already present at $target)"
    continue
  fi
  ln -s "$(pwd)/$skill" "$target"
  echo "installed: $name"
done
```

The script is idempotent. Running it again only links skills you do not already have. To uninstall a specific skill, remove its symlink: `rm ~/.claude/skills/<name>`.

For Copilot CLI, Gemini CLI, or the Anthropic API, every `skills/<track>/<name>/SKILL.md` follows the [Anthropic Skills format](https://platform.claude.com/docs/en/agents-and-tools/agent-skills) and works in any host that supports the spec.

## A second example: composing skills

The 30-second example used three skills loaded by Claude on its own. Skills also compose deliberately. Here is a second pattern.

**You ask Claude:**

> I'm starting a new ML project to classify whether a patient will be readmitted within 30 days. Set up the project.

Claude loads `workflow/scaffolding-ml-research-notebook` and creates the project layout: pinned environment (`uv` lockfile), `src/` package, `data/raw` and `data/processed` split, `tests/`, a starter notebook. Inside the starter notebook's first cell, `workflow/enforcing-seed-hygiene` adds the multi-library seed block (`numpy`, `random`, the relevant ML framework) and the CPU-pin block that prevents cross-platform sampler drift. Before Claude lets you train anything, `ml-datasci/auditing-train-test-split` runs the leakage check and refuses to proceed if the same patient ID appears in both train and test (a real failure mode for hospital data. This is also why we have an `auditing-data-quality` skill that runs alongside).

The skills know about each other. Each one's `See also` section links the natural next steps. You stay in the flow. The disciplines compose without you stitching them together yourself.

## Concepts

The vocabulary used throughout this repo, defined inline:

- **Skill.** A single `SKILL.md` markdown file with frontmatter and 11 required sections. Claude reads the frontmatter description to decide whether to invoke the skill on a given turn. If invoked, it reads the body and follows the workflow inside.
- **Track.** One of five audience-driven directories under `skills/`: `security/`, `ml-datasci/`, `workflow/`, `teaching/`, `claude-code-meta/`. A skill lives in the track that matches its primary audience.
- **Σ (sigma) score.** A 1-to-20 priority estimate assigned at triage time. Σ approximates *frequency × cost-of-getting-it-wrong*: how often the gap the skill closes appears in real practice, multiplied by how badly things go when the gap is missed. Both factors are scored 1-5, the product lands in 1-25, and the result is rounded into the 1-20 catalog range. A Σ 20 skill closes a gap that hits every project in its audience and produces a catastrophic failure if missed (`enforcing-seed-hygiene` is one). A Σ 7 skill closes a specialty gap with a recoverable cost (`auditing-rlhf-reward-hacking` is one). The number is a sort key, not a quality score: a Σ 7 skill is not worse than a Σ 17 skill, it is more specialized. Read [`docs/explanation/sigma-score.md`](docs/explanation/sigma-score.md) for the full scoring rubric, the band structure (17-20 / 13-16 / 9-12 / 7-8), and what Σ does and does not tell you about whether a skill applies to YOUR project.
- **Status.** Each skill is one of three: `shipped` (full body, 3 passing evals, ready to use), `drafting` (body exists, evals incomplete or failing on one model), or `planned` (listed in a track README, no directory yet). Today the catalog is 100% shipped: 105 shipped, 0 drafting.
- **Eval.** Three JSON scenarios per skill (`evals/01-happy-path.json`, `02-edge-case.json`, `03-anti-trigger.json`) that test whether a model invoking the skill actually produces the expected behavior. The anti-trigger checks that the skill refuses or hands off when it should not engage.
- **PRAGMATIC.** The discipline used to author and validate every RCS skill released so far. Instead of running evals against all three Claude models (Haiku, Sonnet, Opus) per release, PRAGMATIC validates only against Sonnet in-session via subagent dispatch. The full 3-model harness in `tools/run_evals.py` is available but optional. The trade favors fast iteration over exhaustive coverage. The rationale is captured in each skill's CHANGELOG entry.

## Where to go next

You are reading the root document. Depending on what you came for:

- **You want a walked-through introduction.** Read [`docs/tutorials/getting-started.md`](docs/tutorials/getting-started.md). Install one skill, see it fire, see the difference, in about ten minutes.
- **You want to browse the full catalog.** See [`skills/README.md`](skills/README.md) for the cross-track index.
- **You want skills for your role.** Open the relevant track README: [`security/`](skills/security/), [`ml-datasci/`](skills/ml-datasci/), [`workflow/`](skills/workflow/), [`teaching/`](skills/teaching/), [`claude-code-meta/`](skills/claude-code-meta/).
- **You want a how-to recipe.** [`docs/how-to/install-and-invoke-a-skill.md`](docs/how-to/install-and-invoke-a-skill.md), [`docs/how-to/contribute-a-skill.md`](docs/how-to/contribute-a-skill.md), and [`docs/how-to/audit-your-docs-for-ai-slop.md`](docs/how-to/audit-your-docs-for-ai-slop.md).
- **You want to understand the concepts.** [`docs/explanation/what-is-a-skill.md`](docs/explanation/what-is-a-skill.md), [`docs/explanation/sigma-score.md`](docs/explanation/sigma-score.md), [`docs/explanation/pragmatic-discipline.md`](docs/explanation/pragmatic-discipline.md).
- **You want to contribute a new skill.** See [`CONTRIBUTING.md`](CONTRIBUTING.md). Read [`docs/conventions.md`](docs/conventions.md) and [`docs/eval-protocol.md`](docs/eval-protocol.md) before opening a PR.
- **You want to report a vulnerability.** See [`SECURITY.md`](SECURITY.md). Do not file a public issue for security problems.
- **You want to know what changed in a release.** See [`CHANGELOG.md`](CHANGELOG.md). Per-skill SemVer plus repo-level integration tags.
- **You want the design rationale.** See [`docs/superpowers/specs/2026-05-22-rcs-public-skills-repo-design.md`](docs/superpowers/specs/2026-05-22-rcs-public-skills-repo-design.md) for the original spec and [`docs/governance.md`](docs/governance.md) for versioning and deprecation policy.

## Top 10 skills by Σ

A teaser of the highest-priority skills. The full 105-row catalog lives in [`skills/README.md`](skills/README.md), sorted alphabetically by slug for direct lookup. The Σ column below is the per-skill priority score defined in the Concepts section above. For the full scoring methodology see [`docs/explanation/sigma-score.md`](docs/explanation/sigma-score.md).

| Skill | Track | What it does | Σ |
|---|---|---|---|
| [`enforcing-seed-hygiene`](skills/workflow/enforcing-seed-hygiene/) | workflow | First-cell seed gate (Python/NumPy/PyTorch/JAX/TF/R) + CPU-pin for cross-platform sampler determinism | 20 |
| [`validating-temporal-fields`](skills/workflow/validating-temporal-fields/) | workflow | Reject-future + min-year-fallback + event-vs-disclosure separation for temporal corpora | 19 |
| [`auditing-pinned-dependencies`](skills/security/auditing-pinned-dependencies/) | security | Grep audit for unpinned installs across README, Dockerfile, CI, package.json, mcp.json | 19 |
| [`reporting-effect-sizes`](skills/ml-datasci/reporting-effect-sizes/) | ml-datasci | Per-test-family effect-size selector + 95% CI + direction sentence. Refuses bare-p-value | 19 |
| [`evaluating-binary-classifiers`](skills/ml-datasci/evaluating-binary-classifiers/) | ml-datasci | ROC + PR + calibration + CM + threshold sweep + bootstrap 95% CI from `(y_true, y_pred_proba)` | 19 |
| [`auditing-mcp-server-pre-trust`](skills/security/auditing-mcp-server-pre-trust/) | security | Six-check audit before registering an MCP server | 18 |
| [`selecting-statistical-test`](skills/ml-datasci/selecting-statistical-test/) | ml-datasci | Decision-tree walk from data characteristics to a recommended test, naming the gating assumption | 18 |
| [`checking-test-assumptions`](skills/ml-datasci/checking-test-assumptions/) | ml-datasci | Per-test assumption checks (Shapiro, Levene, QQ, residual) with pass/fail verdicts | 18 |
| [`auditing-train-test-split`](skills/ml-datasci/auditing-train-test-split/) | ml-datasci | Leakage, stratification, group-aware, temporal-order audit of a train/test split | 18 |
| [`authoring-skill`](skills/claude-code-meta/authoring-skill/) | claude-code-meta | Anthropic best-practices + RCS Layer-3 contract for authoring a new skill | 18 |

The catalog has 105 shipped skills as of `v7.0.6`. Zero are drafting. See [`skills/README.md`](skills/README.md) for the rest.

## Governance

- **License.** MIT. See [`LICENSE`](LICENSE).
- **Contributing.** See [`CONTRIBUTING.md`](CONTRIBUTING.md). The contribution workflow is eval-first, gerund-named, no AI attribution.
- **Versioning.** Per-skill SemVer in each `SKILL.md` frontmatter (`version`). Repo-level integration tags use `vM.N-phaseK` for batch integrations and `vM.N.P` for single-skill patches. See [`docs/governance.md`](docs/governance.md).
- **Security.** See [`SECURITY.md`](SECURITY.md) for the reporting path.
- **Documentation contract.** See [`docs/conventions.md`](docs/conventions.md) for the per-skill Layer-3 documentation contract and [`docs/eval-protocol.md`](docs/eval-protocol.md) for the eval schema and pass thresholds.

## Acknowledgments

Skill design follows the [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) document and the patterns demonstrated by the official `anthropics/claude-code` skills, `obra/superpowers`, and `affaan-m/everything-claude-code` repositories.

## Disclaimer

Skills are tooling, not advice. They encode disciplines and decision trees observed in real research and engineering practice. Verify outputs against authoritative sources before relying on them in regulated or safety-critical contexts. Security skills in particular do not substitute for professional security assessment.
