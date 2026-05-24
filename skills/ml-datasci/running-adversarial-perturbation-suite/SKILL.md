---
name: running-adversarial-perturbation-suite
description: >
  Runs a structured adversarial-perturbation robustness suite (FGSM, PGD, AutoAttack)
  against a trained vision or tabular classifier under a declared threat model
  (L-infinity / L2 / L0, white-box / black-box, targeted / untargeted, epsilon budget,
  iteration count). Produces a clean-accuracy vs robust-accuracy table per attack,
  an attack-success-rate breakdown, and a saved set of adversarial examples for
  inspection. Use when a deployed or pre-deployment vision / tabular model needs an
  adversarial-robustness measurement, when a regulator or downstream team asks for
  a robustness number, or when the user reports high clean accuracy and wants to know
  whether the model is brittle to small input perturbations. Refuses to engage on
  LLM prompt-injection or text-jailbreak scenarios (different attack surface, no
  continuous gradient — hand off to security/running-prompt-injection-eval).
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - ml-engineer
  - ai-security
  - security-eng
  - data-scientist
evidence:
  - multiturn-injection-detection
  - llm-safety-alignment-study
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Running an Adversarial Perturbation Suite

> **Tooling, not a safety certificate.** This skill measures robustness against a
> declared attack budget; a passing number under one ε does not generalize to a
> different ε, different L-norm, or a different attack family. The output is
> evidence for a robustness claim, not a robustness guarantee.

## When to use

Trigger this skill when the user asks for or implies one of:

- "How robust is this model to adversarial examples?" / "What's the robust accuracy?"
- A pre-deployment robustness check on a trained vision classifier (image, video frame, satellite, medical imaging) or a tabular classifier (fraud, credit, intrusion-detection) where small input perturbations matter
- A regulator, customer, or downstream team requests an adversarial-robustness number under a stated threat model
- High clean accuracy is reported and the user suspects brittleness (e.g., 99% clean accuracy on a security-critical task with no robustness data)
- The user names FGSM, PGD, AutoAttack, CW (Carlini-Wagner), or "ε-bounded adversarial example" in the request

## When NOT to use

Skip this skill and hand off when:

- The attack surface is **LLM prompt injection / jailbreak** — different threat model, no continuous gradient over text tokens, different toolkit → use `security/running-prompt-injection-eval`
- The attack surface is **physical-world adversarial patches** for printed or 3D-printed objects — needs printability + EOT (expectation-over-transformation), different specialty
- The attack surface is **model extraction / membership inference / model inversion** — privacy attacks, not perturbation robustness; different category
- The model has not been trained yet — robustness evaluation comes after training, not during architecture selection
- The user wants **adversarial training** (defensive method) rather than evaluation → adjacent skill, planned

## Quick start

User says: "I trained a ResNet-50 on CIFAR-10. Clean test accuracy is 94.3%. Run an adversarial robustness suite under L-infinity ε = 8/255."

Skill response: confirms threat model (L-infinity, ε = 8/255, white-box, untargeted), runs FGSM → PGD-20 → AutoAttack-standard against the test set (or a stratified subset), produces a per-attack robust-accuracy table, attack-success-rate breakdown, and saves the worst-case adversarial examples for visual inspection.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| model | callable / framework artifact | yes | — | The trained model (PyTorch nn.Module, TF Keras model, ONNX runtime, callable taking input → logits). |
| dataset | DataLoader / array pair | yes | — | Held-out test data the suite attacks. NOT the training data. Provide (x, y) pairs. |
| norm | "Linf" \| "L2" \| "L0" | yes | "Linf" | Distance metric defining the perturbation ball. Linf is most common for vision. |
| epsilon | float | yes | — | Perturbation budget in the SAME units as the input. Linf vision example: 8/255 ≈ 0.0314 for [0,1]-scaled pixels. State the units explicitly. |
| attacks | list of strings | no | ["FGSM", "PGD-20", "AutoAttack-standard"] | Which attacks to run. PGD-20 means 20 iterations. AutoAttack-standard is APGD-CE + APGD-DLR + FAB + Square. |
| step_size | float | no | epsilon / 4 | PGD step size. Common rule: alpha = epsilon / 4 for PGD-20, alpha = epsilon / 10 for PGD-100. |
| targeted | bool | no | false | If true, an adversarial example must fool the model into a specific class; if false, any wrong class counts. Targeted is harder. |
| target_class | int | no | — | Required if targeted=true. Either a single class or a per-sample target. |
| sample_size | int | no | min(len(dataset), 1000) | Number of test samples to attack. Full test set is most accurate; subsampling is acceptable for fast iteration. |
| save_examples | int | no | 32 | How many adversarial examples to save for visual inspection (per attack). |
| feasibility_constraints | callable | no | — | **TABULAR ONLY.** Function that takes a perturbed input and returns true if it satisfies domain constraints (categorical features in valid set, monotone constraints, integer constraints, sum-to-one constraints). Required for tabular; without it, "adversarial examples" may be infeasible inputs. |

## Workflow

Copy this checklist into the response and check off items as the suite progresses:

```
Adversarial-suite progress:
- [ ] Step 1: Declare threat model (norm, epsilon-with-units, white-box/black-box, targeted/untargeted)
- [ ] Step 2: Measure clean accuracy on the same test subset to be attacked
- [ ] Step 3: Run FGSM (one-step) — establishes a weak lower bound on robust accuracy
- [ ] Step 4: Run PGD-20 (iterative) — much stronger; the standard mid-effort attack
- [ ] Step 5: Run AutoAttack-standard — parameter-free ensemble; near-best-known attack
- [ ] Step 6: Compare attack strength: AutoAttack should be ≤ PGD-20 ≤ FGSM on robust accuracy. If not, the attack hyperparameters are wrong (likely step_size).
- [ ] Step 7: TABULAR ONLY — apply feasibility_constraints; report "feasibility-filtered robust accuracy" separately
- [ ] Step 8: Save adversarial examples (top-k by perturbation magnitude or worst-fooled) for inspection
- [ ] Step 9: Produce the report (per-attack table + threat-model declaration + sample images / rows + caveats)
```

### Step 1: Declare the threat model — BEFORE running anything

Every robustness number is conditional on a threat model. State all of:

- **Norm:** Linf (max per-pixel perturbation), L2 (Euclidean budget), L0 (number of pixels changed)
- **Epsilon with units:** "8/255 for [0,1]-scaled pixel inputs" or "0.5 for L2 in feature-space-normalized units." A bare "ε = 0.03" is not a threat model — it is a number.
- **Attacker access:** white-box (full model + weights + gradients), gray-box (architecture only), black-box (query-only). FGSM / PGD / AutoAttack are white-box; for black-box use Square Attack alone or transfer attacks.
- **Goal:** untargeted (any misclassification) or targeted (force a specific class)

Refusing to state the threat model is the most common reason robustness numbers are not comparable across papers.

### Step 2: Measure clean accuracy on the SAME subset

The clean accuracy on the attacked subset matters more than the clean accuracy on the full test set, because robust accuracy is reported as a fraction of the attacked subset. Mismatched denominators are a common reporting error.

### Step 3: FGSM (one-step)

FGSM is the cheapest attack and produces the WEAKEST adversarial examples. Use it as a sanity check, not as the robustness number. If FGSM-robust-accuracy already collapses to 0%, the model is brittle and stronger attacks are confirmation, not investigation.

```python
# Conceptual: x_adv = clip(x + epsilon * sign(grad_x L(f(x), y)), 0, 1)
```

### Step 4: PGD-20 (iterative, projected)

Standard mid-effort attack. 20 iterations, step size ≈ epsilon / 4, random start within the ε-ball. Reports a much tighter robust-accuracy upper bound than FGSM. If your robust-accuracy claim is based on PGD-20 alone, also run AutoAttack to verify.

### Step 5: AutoAttack-standard

Parameter-free ensemble (Croce & Hein 2020). No hyperparameter tuning, runs four diverse attacks in sequence; the model is "robust" on a sample only if ALL four fail. Treated by the community as the near-best-known attack for L-infinity / L2 benchmarks. Use AutoAttack-standard for any published or production-claimed robustness number.

### Step 6: Strictly-monotone attack-strength check

If `robust_accuracy(AutoAttack) > robust_accuracy(PGD-20)` or `robust_accuracy(PGD-20) > robust_accuracy(FGSM)`, the stronger attack ran into a bug — typically a too-large step size, gradient masking, or the model is in eval-mode-mismatch (BatchNorm running in train mode). Investigate before reporting.

### Step 7: TABULAR — feasibility filter

A "PGD example" on tabular data may set categorical features to non-existent levels, integer features to 0.37, or violate sum-to-one constraints. These are not real-world inputs. Apply the `feasibility_constraints` callable to every adversarial example; report BOTH unfiltered robust accuracy (interesting for research) and feasibility-filtered robust accuracy (the deployment-relevant number). If they differ by > 10 absolute points, the unfiltered number is misleading.

### Step 8: Save examples for visual inspection

For vision: save a 4x8 grid of clean image / adversarial image / perturbation × 10 (amplified for visibility). For tabular: save a row-diff table — clean row vs adversarial row vs L-infinity / L2 distance. The auditor reading the report needs to see what the perturbation actually looks like.

### Step 9: Final report

See `reference/report-template.md` for the canonical structure.

## Outputs

A markdown report:

1. **Threat-model declaration block** (norm, epsilon-with-units, white-box/black-box, targeted/untargeted, attack list, sample size, seed)
2. **Per-attack robust-accuracy table** — Attack · Hyperparameters · Robust accuracy · Attack success rate · Wall-clock time · CI (bootstrap on the attacked subset)
3. **Attack-strength sanity check** — pass / fail on the strict monotone ordering
4. **Visual / row-diff examples** — k saved per attack
5. **Tabular section** (if applicable) — feasibility-filtered vs unfiltered
6. **Caveats and what this DOES NOT measure** — different ε, different norm, different attack family, certified vs empirical, adaptive attacks against defenses

Saved files in `output_dir/`:

- `report.md` — the markdown report
- `examples/<attack>/<idx>.png` — adversarial example images (vision)
- `examples/<attack>/diffs.csv` — clean vs adversarial rows (tabular)
- `metrics.json` — machine-readable metric dump for downstream pipelines

## Failure modes

Known pitfalls and how this skill catches them:

- **Robustness-number-without-threat-model** — reporting "92% robust accuracy" with no ε, norm, or attack family. Caught by: Step 1 demand for an explicit threat-model declaration block that gates the rest of the workflow.
- **FGSM-only robustness claim** — FGSM is the weakest of the family; passing FGSM is necessary, not sufficient. Caught by: Step 4 + Step 5 both required; FGSM-only is flagged as "preliminary" not "robust accuracy."
- **Attack-strength inversion** — PGD-20 producing higher robust accuracy than FGSM indicates a bug (gradient masking, BatchNorm-in-train-mode, wrong step size). Caught by: Step 6 strict monotone check.
- **Gradient masking** — model has obfuscated gradients (rounding, stochastic defenses, non-differentiable preprocessing) so gradient-based attacks fail without true robustness. Caught by: AutoAttack's Square component (gradient-free) — if Square Attack succeeds where APGD fails, gradient masking is the explanation.
- **Tabular feasibility blindness** — reporting robust accuracy against perturbations that produce impossible inputs (categorical = 0.37, age = -3). Caught by: Step 7 mandatory feasibility filter with separately reported numbers.
- **Eval-mode mismatch** — model left in train() mode during attacks; BatchNorm and Dropout produce stochastic gradients, attacks degrade. Caught by: report-template includes a mandatory `model.training` assertion line.
- **Attacking training data** — robust accuracy on training data is meaningless and inflated. Caught by: Step 2 explicit "held-out subset" requirement.

## References

- `reference/threat-model-checklist.md` — full threat-model declaration template
- `reference/report-template.md` — canonical robustness-report markdown structure
- `reference/library-cheatsheet.md` — torchattacks, foolbox, AutoAttack, CleverHans — when to use which
- [Madry et al. 2018, *Towards Deep Learning Models Resistant to Adversarial Attacks*](https://arxiv.org/abs/1706.06083) — PGD reference
- [Goodfellow et al. 2014, *Explaining and Harnessing Adversarial Examples*](https://arxiv.org/abs/1412.6572) — FGSM reference
- [Croce & Hein 2020, *Reliable evaluation of adversarial robustness with an ensemble of diverse parameter-free attacks*](https://arxiv.org/abs/2003.01690) — AutoAttack reference
- [RobustBench leaderboard](https://robustbench.github.io/) — standardized benchmark; useful for sanity-checking your robust-accuracy numbers against published baselines

## Examples

### Example 1: ResNet-50 on CIFAR-10 under L-infinity ε = 8/255 (happy-path)

Input: "I trained a ResNet-50 on CIFAR-10. Clean test accuracy is 94.3%. Run an adversarial robustness suite under L-infinity ε = 8/255."

Output: skill declares the threat model (Linf, ε = 8/255 for [0,1] pixels, white-box, untargeted, sample_size = 1000 stratified test subset, seed = 42), measures clean accuracy on the subset (94.1%), runs FGSM (robust acc = 31.2%), PGD-20 (robust acc = 12.4%), AutoAttack-standard (robust acc = 9.8%), verifies monotone ordering (9.8 ≤ 12.4 ≤ 31.2 ✓), saves 32 adversarial examples per attack, and reports "Empirical robust accuracy under Linf ε = 8/255 (AutoAttack-standard): **9.8%** [95% bootstrap CI: 7.9, 11.9]. Model is **not** robust at this budget."

### Example 2: Tabular fraud classifier (edge-case — feasibility matters)

Input: "I have an XGBoost fraud classifier on tabular data with 14 features (8 continuous, 6 one-hot-encoded categoricals). What's the adversarial robustness?"

Output: skill asks for the threat model AND the feasibility constraint function. Without feasibility constraints it warns that PGD on one-hot columns produces non-binary outputs that aren't real fraud records. After receiving constraints (categoricals must stay in their original one-hot encoding; amount must remain non-negative integer cents), it runs PGD-20 + AutoAttack with project-to-feasible after each iteration step, reports unfiltered robust accuracy (12%) AND feasibility-filtered robust accuracy (61%), and explains that the 49-point gap means the unfiltered number overstates real-world risk.

### Example 3: LLM prompt injection (anti-trigger)

Input: "Run an adversarial robustness suite against my GPT-4 customer-service agent."

Output: skill refuses the request as out of scope. Explains that LLM prompt injection / jailbreak operates over discrete text tokens (no continuous gradient), so FGSM / PGD / AutoAttack do not apply; the right toolkit is a prompt-injection corpus (DAN, role-play, encoded-payload, instruction-override) evaluated under an authorized red-team RoE. Hands off to `security/running-prompt-injection-eval` and `security/running-multiturn-attack-suite`.

## See also

- `security/running-prompt-injection-eval` — LLM-side attack-suite analogue
- `security/running-encoded-payload-suite` — encoded-payload corpus (also LLM-side)
- `security/running-multiturn-attack-suite` — multi-turn LLM jailbreak suite
- `ml-datasci/evaluating-OOD-detection` — adjacent robustness specialty (planned)
- `ml-datasci/auditing-deep-learning-overfit` — adjacent training-discipline skill (planned)
- `ml-datasci/evaluating-binary-classifiers` — for the clean-accuracy denominator and bootstrap CI patterns

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored fresh during v7-batch-4 (adversarial-ML + RLHF + DP cluster) per RCS PRAGMATIC discipline
