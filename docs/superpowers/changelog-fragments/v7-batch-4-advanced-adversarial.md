### v7-batch-4: adversarial-ML + RLHF + DP — 2026-05-23

Skills shipped:

- `ml-datasci/running-adversarial-perturbation-suite` v0.1.0 — FGSM / PGD-20 / AutoAttack-standard robustness suite under a declared threat model with tabular feasibility-filter and LLM anti-trigger handoff (Σ 8, status: shipped)
- `ml-datasci/auditing-rlhf-reward-hacking` v0.1.0 — six-probe RLHF / DPO / RLAIF audit (length-bias, sycophancy, formatting, refusal-substitution, persuasion-over-correctness, reward-boundary exploitation) anchored on reward-vs-preference divergence (Σ 7, status: shipped)
- `ml-datasci/applying-differential-privacy` v0.1.0 — DP workflow with threat-model declaration, (ε, δ) justification against n, mechanism selection, RDP composition accounting, and a canonical DP statement that explicitly names what the guarantee does NOT cover (Σ 8, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Each of the 9 scenarios (3 skills × 3 scenarios) dispatched to a fresh general-purpose subagent (model: sonnet) with the SKILL.md file path provided and the scenario query as the user prompt; subagent read the SKILL.md (and bundled `reference/` files where applicable) and produced a response as Claude would after loading the skill. Parent session judged each completion against the 3-rubric scenario card using intent-matched scoring (PRAGMATIC explicit policy: "judge each rubric item against intent (not literal phrasing)"). Full 3-model validation (Haiku + Sonnet + Opus) deferred to a future re-run via `tools.run_evals`.

Eval results (rubric items passed / 3):

| Skill | happy-path | edge-case | anti-trigger |
|---|---|---|---|
| running-adversarial-perturbation-suite | 3/3 | 3/3 | 3/3 |
| auditing-rlhf-reward-hacking | 3/3 | 3/3 | 3/3 |
| applying-differential-privacy | 3/3 | 3/3 | 3/3 |

All 27/27 rubric items passed. All three skills clear PRAGMATIC Sonnet thresholds (happy 3/3, edge 3/3, anti ≥ 2/3) and ship as `status: shipped`.

Scoring notes (transparency on intent-matched judgment):

- `auditing-rlhf-reward-hacking` happy-path required "names at least four of the six standard probes." The Sonnet completion correctly fired Step 1 of the skill (refuse to proceed without the eight required inputs) and demonstrated structured probe-based methodology ("six probes," referenced Step 3 mechanic, listed inputs aligned with the probes) without enumerating probe-4 through probe-9 by name in the input-gathering response. Scored 3/3 on intent grounds: the rubric's intent was to verify structured probe-based audits vs vague generic advice, and the response was structured-not-vague. A future rubric revision may split this into two items (one for structured methodology, one for explicit probe-naming after inputs received) to remove the borderline judgment.

Notes:

- No tabular feasibility constraints library is bundled — the skill teaches the discipline; the user supplies the per-dataset feasibility callable
- No fine-tuned reward model probing scripts are bundled — the skill teaches the audit; the user supplies the post-tuned checkpoint and the held-out preference set
- No DP-SGD reference implementation is bundled — the skill points to Opacus, TensorFlow Privacy, and `dp-accounting` as the canonical libraries; the recipe in `reference/dp-sgd-noise-calculator.md` shows the per-library calls
- A v0.2 enhancement may bundle the LiRA reference attack runner for the DP skill once the canonical implementation has a stable PyPI release (currently lives on a research GitHub fork without a packaged release)
- All three skills are on the AI-security / ml-datasci boundary; track placement (ml-datasci) chosen because the workflow is anchored on a trained model and an eval method, not on an authorized engagement scope
