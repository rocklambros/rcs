# Audience discovery prompts

Questions to ask the launching team before authoring the onboarding doc. The answers map directly to which sections from `audience-archetypes.md` the doc will need.

## 1. Who has to do something with this system in the next 90 days?

Pick the 2-5 reader profiles whose primary decision must be answered by this doc. Anyone who is "informed but not deciding" does not need a section — they get the TL;DR.

Common groupings:

- **Internal service launch:** engineer + scientist + executive
- **External library release:** engineer + maintainer + (optional) executive
- **Internal tool with compliance posture:** engineer + security + executive
- **Course module:** student + instructor + (optional) external reviewer
- **Dataset publication:** scientist + engineer + (optional) auditor
- **Model launch:** scientist + engineer + executive + security

## 2. For each audience, what one decision will they make after reading?

If you cannot name the decision in one sentence, the audience does not belong in this doc.

- Engineer → *"Can I integrate this in the current sprint?"*
- Scientist → *"Is the output reliable enough for my downstream work?"*
- Executive → *"Should I sponsor / fund / approve this?"*
- Security → *"Does this clear our policy bar?"*
- Auditor → *"Can I attest to its operation?"*
- Student → *"What do I need to know before I touch this?"*
- Instructor → *"How do I teach this with it?"*

## 3. What is the system NOT for?

Three to five concrete misuses you want to prevent. These go in the out-of-scope section verbatim. Sources:

- Look at the pre-launch design doc's "non-goals" list
- Ask the engineering team what they would refuse to support in the first 30 days
- Ask the product team what use cases they had to deprioritize
- Ask the security team what risk classes are out of bounds

## 4. Who owns it after launch?

The TL;DR needs: team name, Slack channel, on-call rotation (if applicable), escalation path. If any of these are missing, the doc is not ready to ship — launch readiness gate.

## 5. What is the system's current status?

Alpha / beta / GA / sunset. Sets reader expectation. An engineer reading a beta API treats failures differently than a GA API. An executive reading a beta-status doc evaluates risk differently than a GA-status doc.

## 6. Is there an existing doc this replaces?

If yes, produce a migration map alongside the new doc: which sections in the old doc move where, what is removed, what is new. Helps existing readers find what changed.

## 7. What is the single feedback channel?

One channel. One owner. One triage cadence. If feedback is fragmented per audience, the team misses signal because each channel looks "quiet."

## Sanity check before writing

- ≥ 2 distinct reader profiles? (If 1, skip this skill — use a single-audience doc.)
- Primary decision named for EACH audience? (If not, drop the audience.)
- Owner + channel known? (If not, gate the launch.)
- Status declared? (If not, default to "beta" with a deadline to declare.)
- Not-for list has ≥ 3 entries? (If not, push back — every system has things it is not for.)

If all six pass, the doc is ready to be drafted from `onboarding-template.md`.
