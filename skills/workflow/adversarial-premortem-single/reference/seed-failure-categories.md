# Seed failure categories

Use these as starting points for Round 1. Skip any that obviously do not apply.

## Premise failure

The claim is wrong; the data don't support it; the proof is flawed. Examples: regression coefficient is significant but wrong direction; classifier accuracy was inflated by leakage; theorem assumes a property the system lacks.

## Methodology failure

The experimental design is wrong; the eval is biased; the dedupe is broken. Examples: train/test contamination; judge model rates its own output favorably; corpus dedup did not refresh indices after merge.

## Implementation failure

Code does not match design; off-by-one; race condition; memory leak. Examples: schema enforced in docs but not in code; concurrent writers can corrupt state; long-running job times out at exactly the wrong moment.

## Operational failure

System is deployed wrong; monitoring is missing; rollback is impossible. Examples: rollback procedure never tested; canary traffic split is 0%; metric is collected but not alerted on.

## Reception failure

Audience misinterprets the result; title oversells; limitations are buried. Examples: paper title implies general claim but methods section limits to one dataset; risk score is reported but uncertainty band is hidden in an appendix.

## Defense-in-depth-creates-false-confidence failure

Multiple layers of "safety" mask the actual brittle component. Examples: input validation + rate limiting + WAF — all happen to be misconfigured because they were copied from a different system; multiple eval gates all judge the same property in correlated ways.
