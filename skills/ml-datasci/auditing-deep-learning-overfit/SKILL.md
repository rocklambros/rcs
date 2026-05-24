---
name: auditing-deep-learning-overfit
description: >
  Audits a deep-learning training run for overfit using train/validation loss gap,
  learning curves vs sample size, weight-norm growth across epochs, and effective-rank
  diagnostics, then distinguishes overfit from train/val distribution shift, label
  noise, and underfit. Use when training a deep network (CNN, RNN, Transformer, dense
  MLP) and validation loss diverges from training loss, when a model that "looked
  good" generalizes poorly to a held-out set, when deciding whether to add
  regularization or collect more data, or when triaging a failed training run.
  Refuses to apply the same diagnostics to classical ML (sklearn/XGBoost) where
  k-fold CV is the right tool, and refuses to call every train/val gap "overfit"
  without ruling out shift and label noise.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer]
evidence:
  - llm-toxicity-visual-analysis
  - multiturn-injection-detection
last-updated: 2026-05-23
---

# Auditing Deep Learning for Overfit

## When to use

Trigger this skill when:

- Training a deep network (CNN, RNN, LSTM, Transformer, dense MLP) and the validation loss is rising while train loss continues to drop
- A model with strong training metrics generalizes poorly on a held-out test set
- Deciding whether to add regularization (dropout, weight decay, data augmentation) or collect more data
- Triaging a failed training run before tuning further hyperparameters
- A reviewer asks "is this overfit?" and the user has the training history available

## When NOT to use

Skip and hand off when:

- The model is classical ML (sklearn, XGBoost, LightGBM, RandomForest) — use k-fold CV instead; the diagnostics in this skill are deep-learning-specific (epoch-level curves, weight norms, effective rank do not apply to a fully-fit tree ensemble)
- The training run never reached the "memorize the train set" regime (train loss is still high) — that is underfit, not overfit; this skill notes it but the action is different
- The val loss is non-monotonic by design (e.g., adversarial training, curriculum learning) — the diagnostics assume a standard training regime
- The user wants a generalization theory analysis (PAC-Bayes bounds, VC dimension); this skill is operational, not theoretical

## Quick start

User says: "I'm training a ResNet on a 5000-image classification task. Train loss is at 0.05, validation loss bottomed out at 0.42 by epoch 30 and has been climbing since. Is it overfit?"

Skill response: walks the diagnostic decision tree — (1) confirm train loss → 0 while val loss rises (classic overfit signature), (2) check for distribution shift (does val have different class balance or augmentation regime than train?), (3) check for label noise (sample 50 mis-classified val examples; if many are mislabeled, the "overfit" diagnosis is wrong), (4) check weight-norm trajectory (rising weight norm indicates memorization), (5) recommend ordered remediations: data augmentation first (cheap), then dropout/weight decay, then early stopping if not already used, then collecting more data, finally reducing model capacity. Reports the diagnostic verdict + recommended next step, NOT a single regularization knob.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| train_loss | array of float | yes | — | Per-epoch training loss. |
| val_loss | array of float | yes | — | Per-epoch validation loss. Must align by epoch with train_loss. |
| train_metric | array of float | no | — | Per-epoch training accuracy / F1 / etc. for non-loss-based diagnosis. |
| val_metric | array of float | no | — | Same, validation. |
| weight_norms | array of float | no | — | Per-epoch weight norm (L2 over all parameters). When present, used in Step 4. |
| train_distribution_summary | dict | no | — | Class balance, mean/std of input features per class. Used to detect train/val shift. |
| val_distribution_summary | dict | no | — | Same for validation. |
| n_train | int | yes | — | Training-set size. Drives the "more data?" recommendation. |

## Workflow

```
Overfit audit progress:
- [ ] Step 1: Confirm overfit signature (train loss ↓, val loss ↑ after some epoch)
- [ ] Step 2: Rule out underfit (is train loss still high? Different problem)
- [ ] Step 3: Rule out train/val distribution shift (class balance, feature stats)
- [ ] Step 4: Rule out label noise in val (sample mis-classified val examples)
- [ ] Step 5: Check weight-norm trajectory if available (rising = memorization)
- [ ] Step 6: Diagnose: classic overfit, partial overfit, shift, label noise, underfit
- [ ] Step 7: Recommend remediation in ordered priority — NOT a single knob
```

### Step 1: Confirm the signature

A classic overfit signature has BOTH:

- Train loss monotonically decreasing toward zero (or train accuracy approaching 100%)
- Validation loss decreasing initially, then bottoming out and rising

If validation loss is FLAT (not rising), the model has plateaued, not overfit. Different remediation.

If train loss is HIGH and val loss is similar, the model is underfit. Different remediation.

### Step 2: Rule out underfit

If train accuracy < 90% (or train loss has not dropped near floor), the model has not yet memorized the train set; there is no overfit to diagnose. The action is more capacity / longer training / better optimization, not regularization.

### Step 3: Rule out distribution shift

If train and val have:

- Different class balance (e.g., train 50/50, val 90/10)
- Different augmentation regime applied to train but not val (or vice versa)
- Different preprocessing
- Different time period (temporal leakage)
- Different source (multi-source dataset with one source held out)

Then the gap is shift, NOT overfit. Regularization will not fix shift; matching the distributions or domain-adaptation will.

### Step 4: Rule out label noise

If 5-10% of validation labels are wrong, the validation loss has a floor below which it cannot drop — even a perfect model will look "overfit" against noisy labels.

- Sample 50 mis-classified val examples
- Manually inspect (or have a labeler inspect)
- If ≥ 5% of those 50 are actually mis-labeled, the val set needs cleaning before any overfit verdict

### Step 5: Weight-norm trajectory

If `weight_norms` was supplied:

- Rising weight norm across epochs while val loss rises → classic memorization signature; weight decay / L2 regularization is well-targeted
- Stable or shrinking weight norm while val loss rises → the issue is not parameter-magnitude memorization; representational over-fitting; data augmentation / dropout is better-targeted

### Step 6: Diagnose

Combining Steps 1-5, classify the run as one of:

- **Classic overfit** — Step 1 yes, Step 2 ruled out, Step 3 ruled out, Step 4 ruled out, Step 5 weight-norm rising
- **Partial overfit + shift** — Step 1 yes AND Step 3 finds a meaningful shift; remediate both
- **Apparent overfit but actually label noise** — Step 4 finds bad val labels
- **Underfit** — Step 2 finds train loss still high
- **Plateau** — Step 1 val loss flat, not rising

### Step 7: Recommend in priority order

For classic overfit, recommend in cheapness order:

1. **Early stopping** — stop training at the val-loss minimum epoch (free)
2. **Data augmentation** — cheap, expands effective train size (rotation/flip/color jitter for images, paraphrase/back-translation for text)
3. **Dropout** — increase rate (typical 0.1 → 0.3)
4. **Weight decay** — increase if rising weight norm was seen
5. **Reduce model capacity** — fewer layers / smaller width; last resort because it can hurt the high-data regime
6. **Collect more data** — when n_train is small relative to model size (use a sample-complexity rule of thumb: roughly 100-1000 examples per learnable feature for tabular, 10²-10³ images per class for vision with augmentation)

Do NOT recommend a single knob without naming the others.

## Outputs

A markdown report with:

1. **Run identity** — model name, n_train, n_val, n_epochs trained
2. **Diagnostic table**: Step · Check · Verdict · Evidence
3. **Loss curves plot** (train + val on shared axis, val minimum marked)
4. **Weight-norm trajectory** (if supplied)
5. **Diagnosis** (one of the 5 in Step 6)
6. **Remediation list** in priority order, NOT a single knob

## Failure modes

- **"Add dropout" reflex** — diagnosing overfit and immediately recommending dropout without ruling out shift or label noise. Caught by: Steps 3-4 are mandatory before Step 7.
- **K-fold-CV-for-DL** — applying classical-ML k-fold CV to a deep network as the overfit diagnostic. K-fold is expensive at deep-learning scale and the per-epoch curves are richer. Hand off to `evaluating-binary-classifiers` / `evaluating-multiclass-classifiers` only if the user is doing classical ML.
- **Misnaming shift as overfit** — declaring "overfit" when train and val differ in distribution; the cure (regularization) does not address the disease. Caught by: Step 3.
- **Single-epoch verdict** — looking at one epoch's gap and calling overfit. Need the trajectory across epochs.
- **Ignoring effective rank** — for very wide networks (modern transformers), effective rank of activation matrices is sometimes a more sensitive overfit signal than weight norm. Note this in the remediation but do not require it.

## References

- `reference/diagnostic-decision-tree.md` — the Step 1-6 decision tree as a flowchart
- `reference/regularization-priority.md` — when to pick which regularizer
- [Goodfellow Bengio Courville — Deep Learning, Ch 7 (Regularization)](https://www.deeplearningbook.org/)
- [Zhang et al. 2017 — Understanding deep learning requires rethinking generalization](https://arxiv.org/abs/1611.03530)

## Examples

### Example 1: Classic ResNet overfit on 5K images (happy-path)

Input: ResNet-18, 5000 training images, 1000 validation. Train accuracy 99.2% by epoch 30, val accuracy peaked 78% at epoch 12 then dropped to 71% by epoch 30. Weight norm 2.1× initial.

Output: Step 1 yes (train → 0, val rising). Step 2 ruled out (train accuracy high). Step 3 user confirms train and val are drawn from the same source with the same augmentation, ruled out. Step 4 user samples 50 mis-classified val examples; 3 mislabeled (6%), borderline but recommends cleanup before strong verdict. Step 5 weight norm rising, classic memorization. Diagnosis: classic overfit + minor val label noise. Remediation priority: (1) early stopping at epoch 12, (2) clean the ~6% mislabeled val records and re-evaluate, (3) add data augmentation (random crop + color jitter), (4) if still overfit, increase weight decay from 1e-4 to 5e-4. Do NOT jump to dropout without trying the cheaper steps.

### Example 2: Train/val class-balance shift (edge-case)

Input: BERT fine-tune for sentiment. Train is balanced 50/50 positive/negative. Val is 90/10 positive/negative because it was scraped from a different time window. Train loss → 0.1, val loss higher than expected but FLAT not rising.

Output: Step 1 says signature is partial (val flat not rising). Step 3 finds the class-balance shift. Diagnosis: this is shift, not overfit. Remediation: rebalance val to match train (or train to match val, depending on deployment target); reweight the val loss; or evaluate per-class metric (PR-AUC) instead of overall loss. Do NOT add regularization — it will not help shift.

### Example 3: sklearn XGBoost classifier (anti-trigger)

Input: "My XGBoost classifier has 96% train accuracy and 78% test accuracy. Help me audit for overfit."

Output: Skill identifies XGBoost as classical ML, hands off. Recommends `evaluating-binary-classifiers` for the train-vs-test gap, k-fold CV for robust generalization estimate, and `early_stopping_rounds` parameter on the XGBoost training call as the equivalent of "early stopping" for tree boosting. Explains weight-norm / effective-rank diagnostics do not apply to a tree ensemble.

## See also

- `ml-datasci/evaluating-binary-classifiers` — classical-ML evaluation path
- `ml-datasci/evaluating-multiclass-classifiers` — same for multi-class
- `ml-datasci/scaffolding-pytorch-training-loop` — for setting up training so these diagnostics are available
- `ml-datasci/auditing-train-test-split` — if "overfit" turns out to be a leakage issue

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
