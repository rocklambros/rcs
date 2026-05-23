# Chollet samples-per-word ratio — decision table

The ratio is `n_samples / mean_seq_len` on the training set, using the chosen `seq_len_unit` (words, subword tokens, or chars).

## Decision table

| Ratio | Family | Concrete recommendation | Regularization defaults | Warnings |
|---|---|---|---|---|
| `< 100` | **Too small for any supervised model** | Few-shot prompting against a pretrained LLM; weak supervision; gather more data | n/a | Per-class count is likely < 20; supervised metrics will be noise |
| `100 - 1500` | **TF-IDF + linear** | `TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)` + `LogisticRegression(C=1.0, max_iter=1000)` or `LinearSVC(C=1.0)` | L2 (sklearn default); strong feature pruning via min_df | Deep models will likely overfit |
| `1500 - 5000` | **Transition (BoW favored)** | TF-IDF + linear baseline FIRST. If insufficient, try a small 1D-CNN with frozen pretrained embeddings (GloVe, fastText). | Dropout 0.4-0.5; early stopping on val loss; embedding dim ≤ 100 | Fine-tuning a Transformer from scratch is risky |
| `5000 - 15000` | **Transition (deep starts winning on domain data)** | TF-IDF baseline FIRST, then small RNN / 1D-CNN, then small pretrained Transformer with frozen lower layers (only fine-tune top 2-4 layers) | Dropout 0.3; layer freezing; LR 2e-5 to 5e-5; ≤ 3 epochs | Without domain pretraining, marginal gains; with pretraining (medical-BERT etc.), Transformer often wins |
| `> 15000` | **Transformer fine-tune** | Pretrained BERT / RoBERTa / DistilBERT; full or partial fine-tune | LR 2e-5 to 5e-5; 2-4 epochs; weight decay 0.01; warmup steps | Still run BoW baseline for comparison |
| `> 100000` | **Transformer fine-tune likely best; consider larger architectures** | Full fine-tune of larger pretrained model | Standard fine-tune defaults | Diminishing returns past a few million; consider compute cost |

## Domain pretraining adjustment

If the pretrained model was pretrained on data matching the task domain (medical text → medical-BERT, scientific text → SciBERT, legal text → legal-BERT), the effective threshold for "Transformer is reasonable" drops by roughly 3x. So:

- `> 5000` with domain pretraining = "Transformer fine-tune reasonable" (instead of `> 15000`)
- `> 1500` with domain pretraining = "transition, Transformer worth trying with aggressive regularization" (instead of `> 5000`)

The BoW baseline is still mandatory regardless.

## Per-class minimum

Independent of the ratio: at least ~50 samples per class is required for any model family to produce stable F1 estimates. For an N-class task, this means `n_samples >= 50 * N` as a floor. With imbalanced classes, the floor applies to the rarest class — `min_per_class_count >= 50`.

If the per-class minimum fails, no choice of model family will rescue the dataset; the right move is to gather more data, use weak supervision, or move to few-shot prompting against a pretrained LLM.

## Subword vs whitespace tokenization

The original Chollet framing uses whitespace-tokenized words. For modern pretrained Transformers using subword (WordPiece, BPE, SentencePiece) tokenization:

- English: subword tokens ≈ 1.3x whitespace words
- Agglutinative or morphologically rich languages (Turkish, Finnish, German compounds): subword tokens can be 2-3x whitespace words
- Logographic scripts (Chinese, Japanese): subword tokens and "words" are not directly comparable; recommend measuring in characters

When reporting the ratio for a Transformer use case, report in the token unit that the model actually consumes (subword tokens), because the per-sample sequence length the model processes is what determines the effective ratio.

## What the ratio does NOT capture

- **Label noise**: a 100,000-sample dataset with 30% mislabeled examples is worse than a 10,000-sample dataset with 1% noise
- **Domain shift between train and test**: even a high ratio fails if test distribution differs from train
- **Class imbalance**: a high ratio with one class dominating is still failure-prone; pair with per-class count check
- **Sequence-length variance**: a high mean with a heavy tail (some 10-word docs, some 5,000-word docs) violates the "mean is representative" assumption; report median + 95th percentile alongside mean

When any of these conditions hold, treat the ratio recommendation as a starting point, not the final answer.
