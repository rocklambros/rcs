---
name: running-chollet-ratio-check
description: >
  Picks a sensible model family for text or sequence classification using
  Chollet's samples-per-word ratio (n_samples / mean_sequence_length). The rule
  of thumb from Chollet's Deep Learning with Python: ratio < 1500 favors
  bag-of-words (logistic regression / linear SVM / shallow MLP on TF-IDF); ratio
  1500-15000 is a transition zone where small RNN / 1D-CNN can start to win on
  domain-specific data; ratio > 15000 makes a Transformer or pretrained
  fine-tune the right starting point. Triggers when a user is starting a text
  classification project, picking between a TF-IDF baseline and a deep model,
  or about to fine-tune a Transformer on a tiny dataset (where the ratio test
  predicts the deep model will overfit and underperform the linear baseline).
  Refuses to recommend a Transformer on a low-ratio dataset without an explicit
  pretraining or transfer-learning justification, and refuses to apply the
  ratio test to non-sequence data (tabular, image, audio).
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - stats-student
evidence:
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - llm-toxicity-visual-analysis
  - email-spam-classifier-naive-bayes-comparisson-roc
last-updated: 2026-05-23
---

# Running Chollet Ratio Check

## When to use

Trigger this skill when:

- A user is starting a text classification or sequence classification project (intent classification, sentiment, spam, toxicity, topic, complaint routing) and asks "should I use a deep model or a simple one?"
- The user is about to fine-tune a Transformer (BERT, RoBERTa, DistilBERT) on a tiny labeled dataset (under ~10K examples)
- The user is comparing a TF-IDF + logistic-regression / linear-SVM baseline against an LSTM or Transformer
- The user reports surprisingly weak deep-model performance on a small text dataset
- Keywords: text classification, samples-to-words, sequence length, BoW vs LSTM, BoW vs Transformer, samples-per-word ratio, Chollet ratio, when to use Transformer, when to use bag-of-words, fine-tuning on small data

## When NOT to use

Skip this skill and hand off when:

- The data is tabular (numeric / categorical columns) — there are no "sequences"; use `ml-datasci/building-baseline-models` instead
- The data is image — Chollet's ratio is text-specific; for image classification, the relevant rule of thumb is "use a pretrained backbone unless dataset > ~50K examples"
- The data is audio waveform — different scaling laws
- The user is doing token generation (LLM autoregressive output, sequence-to-sequence) — Chollet's ratio is for classification, not generation; for generative LLM eval, the question is fine-tuning vs RAG vs prompting, not BoW vs Transformer
- The user has a pretrained Transformer that was pretrained on the SAME domain as the task (medical-BERT on medical text) — pretraining shifts the ratio threshold downward and the rule of thumb is less informative; recommend small-dataset fine-tuning with strong regularization, early stopping, and aggressive validation
- The user is asking about RAG retrieval quality rather than classifier model choice → use `ml-datasci/evaluating-rag-retrieval` (planned)

## Quick start

User: "I have 7,000 customer-support tickets labeled with 6 intents. Average ticket length is ~280 words. Should I use BERT or TF-IDF + logistic regression?"

Response: compute ratio = 7000 / 280 = 25. Ratio of 25 is well below the 1500 threshold — recommend TF-IDF + linear classifier as the starting point. Predict the BERT fine-tune will overfit and underperform unless the user has domain-specific pretraining. Run the linear baseline, get a metric, and only escalate to a deep model if the linear baseline is genuinely insufficient for the use case.

```python
import numpy as np

n_samples = len(texts)
mean_seq_len = np.mean([len(t.split()) for t in texts])
ratio = n_samples / mean_seq_len
print(f"Chollet ratio = {ratio:.1f}")

if ratio < 1500:
    print("→ Bag-of-words (TF-IDF + LogisticRegression / LinearSVC). Deep models will likely overfit.")
elif ratio < 15000:
    print("→ Transition zone. Try BoW first; consider small RNN / 1D-CNN if BoW underperforms.")
else:
    print("→ Transformer or pretrained fine-tune is the right starting point.")
```

See `reference/chollet-ratio-decision-table.md` for the full decision table with model-family suggestions, regularization defaults, and warnings.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `texts` | iterable of str | yes | — | Training texts (NOT including test set). Used to compute `n_samples` and `mean_seq_len`. |
| `seq_len_unit` | str | no | `words` | One of `words`, `tokens`, `chars`. Default `words` matches the original Chollet framing (whitespace-split tokens). For subword-tokenized inputs, `tokens` is more honest. |
| `task_type` | str | yes | — | One of `classification`, `regression`. The ratio rule is derived from classification studies; for regression on text, treat the recommendation as advisory and add a baseline-comparison step. |
| `domain_pretraining_available` | bool | no | `False` | If `True` (e.g. medical-BERT on a medical task, legal-BERT on a legal task), the ratio threshold for "Transformer is reasonable" shifts down by ~3x; flag this in the recommendation. |
| `n_classes` | int | no | `2` | Number of output classes (for sanity-checking sample count per class). |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

```
Chollet ratio check progress:
- [ ] 0. Confirm task is text or sequence classification (not tabular / image / audio / generative)
- [ ] 1. Compute n_samples (training set only)
- [ ] 2. Compute mean_seq_len in chosen unit (words / tokens / chars)
- [ ] 3. Compute ratio = n_samples / mean_seq_len
- [ ] 4. Apply the decision table: ratio < 1500 → BoW; 1500 - 15000 → transition; > 15000 → Transformer
- [ ] 5. Adjust for domain pretraining if available (shift threshold ~3x lower)
- [ ] 6. Sanity-check per-class sample count (minimum ~50 per class for any model family)
- [ ] 7. Recommend the model family with explicit regularization defaults
- [ ] 8. Recommend the comparison plan: always run the BoW baseline before any deep model
```

### Step 1-3: Compute the ratio

Use the TRAINING set only — do not include test samples (those are held out). `mean_seq_len` is sensitive to outliers; check the distribution (median + 95th percentile) and document if heavy-tailed. For subword-tokenized inputs (BERT-tokenizer style), report the ratio in subword tokens, not whitespace words — they are roughly 1.3x apart in English.

### Step 4: Apply the decision table

| Ratio range | Recommended family | Why |
|---|---|---|
| `< 1500` | **TF-IDF + Logistic Regression / Linear SVM** (or shallow MLP on TF-IDF) | Deep models overfit on small text. Linear-on-TF-IDF has been the surprisingly hard baseline in text classification for two decades. |
| `1500 - 15000` | **Transition.** Try TF-IDF + linear baseline first. If insufficient, consider a small 1D-CNN, a small LSTM, or a small pretrained Transformer with aggressive regularization (dropout, early stopping, frozen lower layers). | Enough data for some non-linear capacity; not enough for a Transformer to dominate from scratch. |
| `> 15000` | **Transformer or pretrained fine-tune** (BERT, RoBERTa, DistilBERT, etc.) | Enough data for the model's capacity to be filled; deep contextual representations begin to win materially over BoW. |

### Step 5: Domain pretraining adjustment

If the user is fine-tuning a domain-matched pretrained model (medical-BERT on medical text, legal-BERT on legal text, finance-BERT on finance text), the effective ratio threshold drops because the model already encodes domain-relevant priors. Rough rule: threshold for "Transformer reasonable" drops from ~15000 to ~5000 with strong domain pretraining. Still flag in the recommendation that aggressive regularization + early stopping is required at the low end.

### Step 6: Per-class sample count sanity check

Independent of the ratio: any model family needs roughly 50+ examples per class minimum, and 200+ per class for stable F1. If `n_samples / n_classes < 50`, the dataset is too small for ANY supervised approach; recommend gathering more data, weak supervision, few-shot prompting against a pretrained LLM, or active learning.

### Step 7: Recommend with regularization defaults

The recommendation should include not just the family but the regularization defaults appropriate for the ratio:

- **BoW**: L2 regularization (sklearn default for LogisticRegression / LinearSVC); n-grams `(1, 2)` or `(1, 3)`; `min_df = 2` or `5`; sublinear TF; consider character n-grams for short / noisy text
- **1D-CNN or small LSTM**: 30-50% dropout; early stopping on val loss; embedding dimension <= 100; one or two layers
- **Transformer fine-tune**: low learning rate (2e-5 to 5e-5); 2-4 epochs maximum on small data; layer freezing for the lowest layers if ratio is near the threshold; early stopping

### Step 8: Comparison plan

Always run the BoW baseline FIRST, even when recommending a Transformer. Without the linear comparison, there is no evidence that the deep model is worth the cost. See `ml-datasci/building-baseline-models`.

## Outputs

A markdown recommendation with this structure:

1. **Computed ratio** — n_samples, mean_seq_len (with unit), ratio
2. **Decision-zone verdict** — BoW / transition / Transformer with the ratio threshold reasoning
3. **Domain-pretraining note** — adjusted threshold if applicable
4. **Per-class sample count check** — pass / fail and minimum-data warning if applicable
5. **Recommended family + regularization defaults** — concrete configuration
6. **Mandatory baseline-comparison plan** — always run TF-IDF + linear FIRST
7. **Residual risks** — heavy-tailed sequence-length distribution, domain mismatch, subword vs word tokenization choice

## Failure modes

Known anti-patterns and how this skill catches them:

- **Defaulting to BERT on a 500-sample dataset** — caught by step 4 ratio threshold; below 1500, BoW wins.
- **Reporting the deep-model metric without a baseline comparison** — caught by step 8 mandatory baseline.
- **Applying the ratio test to tabular / image / audio data** — caught by `When NOT to use` and step 0 task-type check.
- **Ignoring per-class minimum** — caught by step 6 sanity check; a high ratio still loses if any single class has 5 examples.
- **Using whitespace tokens for BERT-tokenizer inputs** — caught by `seq_len_unit` parameter being explicit; the ratio in subword tokens is ~1.3x different from whitespace words in English (and very different in agglutinative languages).
- **Recommending a Transformer without regularization defaults** — caught by step 7 regularization defaults requirement.
- **Treating the threshold (1500, 15000) as a hard cliff** — they are rules of thumb; the skill flags the transition zone explicitly and recommends running both families on borderline cases.

## References

- `reference/chollet-ratio-decision-table.md` — full decision table with regularization defaults
- Chollet 2018 *Deep Learning with Python*, Manning, chapter 6 (sequence-based text classification) — origin of the samples-per-word heuristic
- [Wang and Manning 2012 *Baselines and bigrams: Simple, good sentiment and topic classification*](https://aclanthology.org/P12-2018/) — the BoW + bigram baseline that is famously hard to beat
- [Yang and Liu 1999 *A re-examination of text categorization methods*](https://doi.org/10.1145/312624.312647) — early evidence that linear-on-TF-IDF is a strong baseline in text classification

## Examples

### Example 1: Low ratio, BoW wins (happy-path)

Input: "I have 7,000 customer-support tickets labeled with 6 intents. Average ticket length is ~280 words. Should I use BERT or TF-IDF + logistic regression?"

Output: Skill computes ratio = 7000 / 280 = 25. Recommends TF-IDF + linear classifier (L2 LogisticRegression, n-grams `(1, 2)`, `min_df = 2`, sublinear TF) as the starting point because ratio 25 is well below the 1500 threshold. Predicts BERT fine-tune will overfit and underperform without domain pretraining. Notes the 6 classes means ~1167 samples per class, which clears the 50-per-class minimum. Requires that BERT, if attempted, be compared head-to-head against the BoW baseline on the same val split.

### Example 2: High ratio, Transformer reasonable (edge-case)

Input: "I have 2,000,000 product reviews with ratings 1-5. Mean review length is ~95 words. We want to classify rating bucket (1, 2-3, 4-5). Which model?"

Output: Skill computes ratio = 2,000,000 / 95 ≈ 21,000. That clears the 15,000 threshold — Transformer or pretrained fine-tune is the right starting point. Still requires running the TF-IDF + linear baseline first per step 8 (it will be cheap on 2M docs and gives a real comparison number). Names regularization defaults for Transformer fine-tune: low LR (2e-5 to 5e-5), 2-4 epochs, early stopping. Flags that the rating-bucket-vs-text relationship is well-studied and pretrained sentiment models exist as a transfer starting point.

### Example 3: Tabular data (anti-trigger)

Input: "I have a tabular dataset — 30 numeric and categorical features per row, 20,000 rows. I want to predict customer churn. Should I use the Chollet ratio to pick between a deep model and a simple one?"

Output: Skill identifies this as tabular data, not text or sequence data. Explains that Chollet's ratio applies to text / sequence classification specifically — for tabular, the relevant rule of thumb is "tree-based models (gradient-boosted trees, random forest) win on tabular until you have hundreds of thousands of rows AND complex feature interactions that linear / tree models can't capture". Hands off to `ml-datasci/building-baseline-models` (Dummy → LinearLogReg → RandomForest → gradient-boosted trees) as the right baseline ladder. Does NOT force the text-specific ratio computation.

## See also

- `ml-datasci/building-baseline-models` — required pre-step regardless of ratio; always run a linear baseline before any deep model
- `ml-datasci/evaluating-binary-classifiers` — for binary text classification eval
- `ml-datasci/evaluating-multiclass-classifiers` — for multi-class text classification eval
- `ml-datasci/auditing-train-test-split` — required pre-step; ratio test assumes a clean train/test split

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-1, skill 3) via PRAGMATIC discipline
