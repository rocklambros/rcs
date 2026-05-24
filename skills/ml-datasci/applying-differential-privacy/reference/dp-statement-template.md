# Canonical DP Statement Template

Use this paragraph in any model card, paper, release announcement, or compliance document that claims a DP guarantee. Fill the bracketed fields.

```
The [release / training / query workload] satisfies
( ε = [ε_value], δ = [δ_value] )-differential privacy with respect to
[record-level / user-level / group-level] adjacency on a dataset of n = [n] records,
under [RDP / advanced / basic] composition with [Poisson / deterministic] subsampling
at rate q = [q_value]. The mechanism is [Gaussian / Laplace / DP-SGD / Exponential]
with [noise multiplier σ = [σ_value] / noise scale b = [b_value]]. Privacy
accounting was performed using [Opacus / TensorFlow Privacy / dp-accounting / custom
implementation cited below].

The guarantee covers [statistical inference about whether a specific record was in
the training set / attribute disclosure of specified attributes / reconstruction of
individual records] by an adversary with [query / model-weights / output] access.

The guarantee does NOT cover:
- Hyperparameter tuning that ran on this data outside the DP budget (a separate ε
  budget must be allocated, or hyperparameters must be selected on non-private data)
- Adversaries with direct database access (this is an access-control concern, not a
  DP concern)
- Other releases of overlapping data — composition across separate releases
  applies and is not captured in this single statement
- Side channels including model-architecture choices made based on the private data,
  feature engineering driven by private statistics, prompt selection in
  fine-tuned LLMs, or human-in-the-loop curation
- Information leaked through the metadata (file counts, document lengths,
  vocabulary statistics) of the release itself

Empirical attack evaluation: [LiRA / shadow-model / none performed] returned
membership-inference AUC = [empirical_auc] on the released model. The DP guarantee
implies a theoretical upper bound on this AUC of approximately
[theoretical_upper_bound_auc] under the chosen (ε, δ).
```

## Worked example

```
The fine-tuning procedure satisfies (ε = 2.0, δ = 1e-7)-differential privacy with
respect to record-level adjacency on a dataset of n = 100,000 records, under RDP
composition with Poisson subsampling at rate q = 0.00256. The mechanism is DP-SGD
with noise multiplier σ = 1.1. Privacy accounting was performed using Opacus 1.4.0
(PyTorch).

The guarantee covers statistical inference about whether a specific patient
discharge summary was in the training set by an adversary with query access to
the released model.

The guarantee does NOT cover:
- Hyperparameter tuning (learning rate, clipping bound, architecture) was performed
  on a 5K-record held-out subset outside the DP budget; this is a documented
  side-channel that compromises the ε guarantee modestly for any record in that
  subset
- Adversaries with direct access to the source EHR system
- Other releases of overlapping cohorts — composition across separate releases
  applies and is not captured in this single statement
- Side channels including the model architecture choice (BERT-base) and tokenizer
  vocabulary, which were selected before DP training began but are still influenced
  by exploratory analysis of the data

Empirical attack evaluation: LiRA returned membership-inference AUC = 0.53 on the
released model (very close to chance, well below the DP-implied upper bound of
approximately 0.78 at ε = 2.0).
```

## Common errors in DP statements

- **"This model is DP."** — Not a statement. Reject and rewrite with full parameters.
- **Missing δ** — ε alone is meaningless without δ; (ε = 1, δ = 0.5) is a vacuous guarantee.
- **Missing adjacency level** — record-level vs user-level matters when a single user contributes many records; user-level DP is much stronger and costs more noise.
- **Missing accountant** — under basic composition, claimed ε may be 10x optimistic vs the RDP-accounted reality (or vice versa).
- **Missing what-it-does-not-cover** — a DP statement that does not name side channels invites overclaiming.
- **Missing empirical attack** — a strong theoretical bound with no empirical check leaves implementation bugs undetected.
