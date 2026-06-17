# Confidence bands, calibration penalties, and the drop rule

Every finding carries two independent axes. Keep them separate at all times: a finding can be Critical and Remote, or Low and Very likely. The drop rule acts on confidence. The remediation order acts on both.

## Impact (blast radius if the failure mode fires)

- **Critical** — produces wrong results, unsafe behavior, data loss, or a security breach. Often irreversible.
- **High** — significant degradation, recoverable but expensive, or a real exploit path that needs a precondition.
- **Medium** — correctness or reliability gap that surfaces under load or edge cases.
- **Low** — confuses the implementer or adds friction without changing outcomes.

Calibrate impact to blast radius and reversibility. A reversible annoyance is not Critical no matter how irritating.

## Confidence (how strongly the evidence supports that the failure mode is real)

- **Very likely** — direct evidence, hard to explain away. Rough orientation above 80 percent.
- **Likely** — strong evidence, a weaker counterargument exists. Roughly 55 to 80 percent.
- **Plausible** — real evidence on both sides, genuinely uncertain. Roughly 30 to 55 percent.
- **Unlikely** — the counterargument is stronger than the claim. Roughly 10 to 30 percent.
- **Remote** — the claim needs a chain of conditions that mostly do not hold. Below 10 percent.

The percentages orient calibration. They are not gates. Do not print a decimal on a finding unless you can cite a real base rate behind it (a CVE frequency, an incident from this team's history, a measured benchmark delta). A fabricated number is worse than an honest band.

## Updating prior to posterior

For each finding, move from the spawning perspective's starting band to an adjudicated posterior:

1. **Prior** — the starting band the subagent assigned.
2. **Evidence** — the strongest counterargument, any corroboration from other perspectives, and the calibration penalties below.
3. **Posterior** — the adjudicated band after the evidence moves the prior, with one line naming what moved it.

Calibration penalties lower confidence regardless of how alarming the finding reads:

- The subagent did not actually open the artifact it attacks → cap at Plausible, usually lower.
- The finding rests on an assumption about unspecified behavior → lower it one band.
- The same finding from several perspectives is correlated evidence from one spec reading, not independent confirmation → do not raise the band on count alone. Raise it only when the perspectives bring genuinely different evidence.

## The drop rule

The main report keeps findings at Plausible or above. Anything that lands at Unlikely or Remote after updating drops out of the round body and the remediation plan and goes to the dropped ledger.

The ledger is not a delete. Record every dropped finding in one compact line: the claim, its evidence anchor, the posterior band, and the one reason it dropped. A dropped finding you can retrieve is a downgrade. A dropped finding with no trace is a liability.

**Tail-risk carve-out.** A Critical and irreversible finding that lands below Plausible does not get deleted with the rest. Park it in a separate tail-risk line in the ledger with the specific trigger that would raise its confidence. Dropping a low-probability catastrophe because it scored Unlikely is how a premortem misses the thing that ends up mattering.
