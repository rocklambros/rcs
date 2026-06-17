# Round and final report format

Label the premortem with the artifact under review, its commit or version if known, and the date.

## Per-round block

```
Round N. Layer name.
Perspectives spawned: [list, and any skipped with reason]

Premortem narrative.
One paragraph describing the failure state six months out for this layer. Concrete, not abstract.

Findings, surviving at Plausible or above.
Numbered list. For each finding:
- Impact: Critical, High, Medium, or Low
- Confidence: posterior band (prior band, one line on what moved it)
- Evidence anchor: file, line, spec section, or data artifact
- Failure mode: what actually breaks and how
- Blind spot: the assumption that let this slip
- Opportunity cost: what leaving it unfixed costs

Cross-attack log.
Which perspective challenged which verdict, how the confidence moved, and why.
```

## After the final round

```
Dropped ledger.
One line per dropped finding: claim, evidence anchor, posterior band, reason for the drop.
Tail risks: Critical irreversible findings below Plausible, each with the trigger that would raise its confidence.

Convergence statement.
Which round triggered the stop signal, or confirmation that 5 rounds completed.

Prioritized remediation plan.
Order by expected cost reduction per unit of effort, where expected cost is impact weighted
by posterior confidence. A Critical that is Very likely outranks a Critical that is Plausible.
When two items tie on expected cost, the cheaper fix ranks higher. For each item:
- The finding it closes
- The specific change: code path, config, process, or decision
- The owner archetype
- The verification step that proves it landed

Residual risk.
What remains unaddressed and why accepting it is defensible, or what would need to change for
it to become addressable. Include the parked tail risks here by reference.
```
