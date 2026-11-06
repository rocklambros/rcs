# Corrections Log

Version 1.1, owner Rock Lambros.

Append only, newest first, capped at the latest 20 pairs. Each entry records a sentence the skill wrote, the sentence Rock replaced it with, and the rule that should have caught it (or "no rule"). The skill reads this file before every draft and treats each pair as a tell to keep out of the new draft. A tell that shows up here twice is a candidate for a new `slop_lint.py` rule.

Entry format:

    ### 2026-09-20, slack
    Skill wrote: <the sentence as drafted>
    Rock's fix: <the sentence as sent>
    Rule: <rule id from slop_lint, the skill section, or "no rule">

## Entries

### 2026-10-03, linkedin rant
Skill wrote: Pick the approval screen your team clicks most and write every field on it as a check against the system of record. Whatever you can't write down is the only thing that should still reach a human.
Rock's fix: Pick the approval screen that is used the most, and for each field that an approver inspects by eye, add that to a check in code. If your agent governance involves requesting more approvers via a headcount, then read 7 again!
Rule: no rule. A rant post closes on a jab at the budget holder, with an exclamation point, after the instruction is spelled out step by step.

### 2026-10-03, linkedin rant
Skill wrote: (nothing, Rock added this beat)
Rock's fix: Please... we still can't stop clicking on cute elf holiday cards that land in our email.
Rule: no rule. Give a rant post one in group joke as a breather, drawn from a shared security pain and aimed at all of us, never at a person.

### 2026-10-03, linkedin rant
Skill wrote: I'm here to tell you that calling it a control is BS. We took the SOC's worst problem, rebuilt it for AI agents, and gave it a nicer button!
Rock's fix: Calling that a control is BS, and you're fooling yourselves. We took the SOC's worst problem, rebuilt it for AI agents, and said "Fire, meet fuel. Fuel, meet fire."
Rule: no rule. Rock's documented phrase was too formal here. He wants the blunt accusation, then a folk formula he'd say out loud.

### 2026-10-03, linkedin rant
Skill wrote: An approval queue is that same queue with a nicer button, and you're staffing it with the same tired people.
Rock's fix: It's human nature? Can't keep up? Click approve because "what are the chances???"
Rule: A-FRAGMENT-RUN fired on Rock's own line. Voice the target's internal monologue as a short run of questions, once per rant post. This differs from the banned drumroll of declarative fragments.

### 2026-10-03, linkedin rant
Skill wrote: I ran a SOC, and the queue beat the headcount every single time. Analysts close what they can't investigate.
Rock's fix: I ran a SOC. The queue beat the hell out of headcount every single time. Analysts will just close what they can't investigate. They are burned out and fatigued and even w/ an "agentic SOC", I haven't seen a "fully autonomous" one yet. Nor would I want to.
Rule: A-TOPIC-LABEL fired on "I ran a SOC." and Rock kept it every round. The credential stands alone as four words. Mild profanity is his in rant posts. Name the practitioners' burnout (warm to the people, hard on the pattern), put the hype term in scare quotes, and end on his personal stance.

### 2026-10-03, linkedin rant
Skill wrote: Six reads like the whole answer on its own. That's partly on us.
Rock's fix: No. 6 feels like the entire fix on its own. That's part on us, but that's also on the doomers out there saying "AI will kill us all! Humans will save us!"
Rule: no rule. Rock spreads the blame outward to a second target. The quoted line is a strawman (doomers don't argue humans save us), so detect mode keeps flagging it and Rock decides.

### 2026-10-03, linkedin rant
Skill wrote: Mitigation 7 is the part that works. It checks every request an agent makes to a downstream system against policy, in code, before it runs, and sends a human only the high consequence or irreversible stuff.
Rock's fix: Mitigation 7 is the meat of it. It puts authorization in code, pre-checks all downstream calls against policy...BEFORE EXECUTION... and HITL's only the high consequence or irreversible actions.
Rule: coffee-peer-voice one caps word per post, exceeded on purpose. Rock caps the mechanism that matters, uses ellipses as a pause, uses practitioner shorthand as a verb ("HITL's"), and reaches for spoken idiom ("the meat of it").

### 2026-10-03, linkedin rant
Skill wrote: Mitigations 1 through 5 strip out tools, functions, and permissions before the agent ever runs.
Rock's fix: Mitigations 1 through 5 tell you to restrict tools, functions, and permissions BEFORE the agent executes.
Rule: coffee-peer-voice caps allowance. Caps go on the timing word that carries the argument, and "tell you to" puts the reader in the sentence.

### 2026-10-03, linkedin rant
Skill wrote: Excessive Agency jumped to #3 in the 2026 LLM Top 10, and everybody read mitigation 6 (put a human in front of high impact actions) and went shopping for approval buttons.
Rock's fix: We ranked Excessive Agency as #3 on the 2026 LLM Top 10. [...] Mitigation 6 is the rubber stamp that everyone keeps buying. But you all stopped there!
Rule: no rule. When Rock helped make the thing, he says "we" and names the act, and passive "jumped to" erases his authority. Name the weak control for what it is ("the rubber stamp"), then hit the reader with a one line "But you all" paragraph.

### 2026-10-03, linkedin rant
Skill wrote: I'd change one thing in 7. It sorts by consequence, and at agent volume irreversible IS the job. Route on whether you can write the rule.
Rock's fix: If I were to change anything in No. 7, it's this: today it sends every high consequence or irreversible action to a human, and at agent volume that IS the job. I'd route on whether you can write the rule instead.
Rule: literal language (no linter rule). Rock had to ask what "sorts by consequence" meant. State the mechanism and what it does today in plain words. Never compress a mechanism into a label verb.

### 2026-10-03, linkedin rant
Skill wrote: Our OWASP list says the fix is mitigation 7. The market stopped reading at 6.
Rock's fix: We put the fix for Excessive Agency in the OWASP Top 10 for LLMs, but the industry skipped it and is purchasing approval buttons instead.
Rule: no rule. The hook names the risk and the full list so a stranger can place it, then names the behavior being attacked. Rock overrode the under 90 character hook target (137 characters).
