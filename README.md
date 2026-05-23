# Rock's Claude Skills (RCS)

Production-quality Claude Code skills for AI security researchers, data scientists, and ML engineers. Every skill encodes a discipline that would otherwise be rebuilt from scratch each project — statistical-test selection, leakage firewalls, seed hygiene, MCP pre-trust audits, adversarial premortems. Catalog-free by design: no bundled framework controls, no ISO mirrors, no drift to maintain. Methodology only.

## Audience routing

- **Security engineer or AI red-teamer?** Start with `skills/security/`.
- **Data scientist, ML engineer, or stats student?** Start with `skills/ml-datasci/`.
- **Researcher working across both?** Start with `skills/workflow/` (cross-cutting hygiene).
- **Instructor or TA?** Start with `skills/teaching/` (pedagogy patterns).
- **Claude Code skill author?** Start with `skills/claude-code-meta/`.

## Install

### Claude Code

Clone and symlink each skill you want into `~/.claude/skills/`:

```bash
git clone https://github.com/rocklambros/rcs.git
cd rcs
for skill in skills/*/*/; do
  name=$(basename "$skill")
  ln -s "$(pwd)/$skill" "$HOME/.claude/skills/$name"
done
```

### Copilot CLI, Gemini CLI, Anthropic API

The `skills/<track>/<name>/SKILL.md` files follow the Anthropic Skills format and work in any host that supports the spec. Symlink or copy the directories into your tool's skill discovery path. For the Anthropic API, upload via the SDK per the Skills guide.

## Skill catalog

| Skill | Track | What it does | Status | Σ |
|---|---|---|---|---|
| [`enforcing-seed-hygiene`](skills/workflow/enforcing-seed-hygiene/) | workflow | First-cell seed gate (Python/NumPy/PyTorch/JAX/TF/R) + CPU-pin for cross-platform sampler determinism + pre-commit hook | ✅ shipped | 20 |
| [`validating-temporal-fields`](skills/workflow/validating-temporal-fields/) | workflow | Reject-future + min-year-fallback + event-vs-disclosure separation for temporal corpora | ✅ shipped | 19 |
| [`auditing-pinned-dependencies`](skills/security/auditing-pinned-dependencies/) | security | Grep audit for unpinned installs across README / Dockerfile / CI / package.json / mcp.json | ✅ shipped | 19 |
| [`reporting-effect-sizes`](skills/ml-datasci/reporting-effect-sizes/) | ml-datasci | Per-test-family effect-size selector + 95% CI + direction sentence; refuses bare-p-value | ✅ shipped | 19 |
| [`evaluating-binary-classifiers`](skills/ml-datasci/evaluating-binary-classifiers/) | ml-datasci | ROC + PR + calibration + CM + threshold sweep + bootstrap 95% CI from `(y_true, y_pred_proba)` | ✅ shipped | 19 |
| [`auditing-mcp-server-pre-trust`](skills/security/auditing-mcp-server-pre-trust/) | security | Six-check audit before registering an MCP server | ✅ shipped | 18 |
| [`selecting-statistical-test`](skills/ml-datasci/selecting-statistical-test/) | ml-datasci | Decision-tree walk from data characteristics to a recommended test, naming the gating assumption | ✅ shipped | 18 |
| [`checking-test-assumptions`](skills/ml-datasci/checking-test-assumptions/) | ml-datasci | Per-test assumption checks (Shapiro / Levene / QQ / residual) with pass/fail verdicts | ✅ shipped | 18 |
| [`auditing-train-test-split`](skills/ml-datasci/auditing-train-test-split/) | ml-datasci | Leakage / stratification / group-aware / temporal-order audit of a train/test split | ✅ shipped | 18 |
| [`deduplicating-records`](skills/workflow/deduplicating-records/) | workflow | Multi-key dedup with index-refresh, union-find transitive collapse, and ID-format normalization | ✅ shipped | 18 |
| [`authoring-skill`](skills/claude-code-meta/authoring-skill/) | claude-code-meta | Anthropic best-practices + RCS Layer-3 contract for authoring a new skill | ✅ shipped | 18 |
| [`auditing-instruction-hierarchy`](skills/claude-code-meta/auditing-instruction-hierarchy/) | claude-code-meta | Audits the agent-instruction file hierarchy for size budget, cache hygiene, and drift | ✅ shipped | 18 |
| [`running-adversarial-premortem`](skills/workflow/running-adversarial-premortem/) | workflow | Multi-round adversarial premortem on spec / plan / paper / proof / codebase | ✅ shipped | 17 |
| [`pinning-reproducible-environments`](skills/workflow/pinning-reproducible-environments/) | workflow | Per-ecosystem lockfile pattern + runtime-version pinning + base-image digest pinning + CI drift-check | ✅ shipped | 17 |
| [`auditing-data-quality`](skills/workflow/auditing-data-quality/) | workflow | Per-column null / range / type / cardinality audit + semantic-class detection + row-level integrity | ✅ shipped | 17 |
| [`building-baseline-models`](skills/ml-datasci/building-baseline-models/) | ml-datasci | 3-rung baseline ladder (Dummy / Linear / RandomForest) on the same train/test split + same metric as the final model | ✅ shipped | 17 |
| [`evaluating-regression-models`](skills/ml-datasci/evaluating-regression-models/) | ml-datasci | RMSE + MAE + R² + adjusted-R² + residual plots + k-fold CV; refuses R² alone | ✅ shipped | 17 |
| [`auditing-context-window-pressure`](skills/workflow/auditing-context-window-pressure/) | workflow | Multi-turn session pressure audit: context %, cache-hit-rate, instruction-hierarchy size, tool-result bloat | 🔨 drafting | 17 |

_17 shipped + 1 drafting (18 total) of ~99 planned skills. See each track's README for the planned-skills roadmap; see [`docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md`](docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md) for the v2–v7 roadmap._

## Governance

- **License:** MIT (see `LICENSE`)
- **Contributing:** See `CONTRIBUTING.md` — eval-first workflow, gerund naming, no AI attribution
- **Versioning:** SemVer per skill (`frontmatter.version`) + loose repo-level batch tags (`v1`, `v1.1`, ...)
- **Documentation contract:** See `docs/conventions.md`

## Acknowledgments

Skill design follows the [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) document and the patterns demonstrated by the official `anthropics/claude-code` skills, `obra/superpowers`, and `affaan-m/everything-claude-code` repos.

## Disclaimer

Skills are tooling, not advice. They encode disciplines and decision trees observed in real research and engineering practice. Verify outputs against authoritative sources before relying on them in regulated or safety-critical contexts.
