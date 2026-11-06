# Voice Corrections Register: Linter Coverage

Version 1.0, owner Rock Lambros. Built November 6, 2026 against the register as fetched November 5, 2026 (112 entries, October 3 to November 5). slop_lint 1.6.0.

This file maps every register entry to the rule that now catches it, or says why no regex can. Names of clients and colleagues are left out on purpose, because the harness-engineering repo that backs this skill up is public. Read the register itself for the full entry.

## Summary

64 of the 112 entries carry at least one span a rule can see. Eight of those were already covered before 1.6.0 (praise labels, closers, A-SMOOTH, A-FRAGMENT-RUN, A-TOPIC-LABEL, and paste vocabulary). The other 56 are new in 1.6.0. The remaining 48 entries are judgment calls about stance, heat, audience, or facts, and a regex that tried to catch them would fire on Rock's own sentences. Those stay with the read-back pass and with Rock.

Most register entries say "slop_lint returned HARD 0." That was true because the rule did not exist, and in a smaller share because the session overrode an ADVISORY finding. The disposition rule in anti-ai-slop 1.9 and coffee-peer-voice 1.17 closes the second gap: every ADVISORY finding gets a printed line saying fixed or kept and why.

## New HARD Rules

| Rule | Register entries | What it catches |
|---|---|---|
| H-POINTER | 2026-11-05 slack | "Details are on the PR" pointer sentences |
| H-DELIVERABLE-LABEL | 2026-10-06 slack, 2026-10-29 slack, 2026-10-31 email | "Two sentences you can use as they stand," "good w/ the shape," "a check folks can take home" |
| H-DISCLAIMER | 2026-10-31 email | A volunteered "I'll keep X and any product pitch out" |
| H-LANDED | 2026-10-31 email | "the tabletop landed" and other talk-shaped nouns that landed or resonated |
| H-PERF-HEDGE | 2026-10-09 email, 2026-10-24 blog | "so I'm biased, but," "discount my enthusiasm," "hype it anyway," plus the coffee-peer-voice 1.6 list |
| H-TOPIC-CLAUSE | 2026-10-13 comment, 2026-10-23 post, 2026-10-14 post, 2026-11-02 blog rewrite | Any sentence opening "On <noun phrase>," with temporal openers and "On prem" exempt |
| H-POINTBACK | 2026-10-29 slack, 2026-10-22 comment, 2026-10-06 slack | "the last thing I want your read on," "I'd underline one line," "X is the one I'd drop" |
| H-COUNTDOWN | 2026-10-16 slack | "54 days left of the ninety" |
| H-BOARD-SPEND | 2026-10-16 post | Any board approving a purchase, tool, or spend |
| H-PAIRED-CONTRAST | 2026-10-14 post | "makes you feel better and tells your board nothing," "gives comfort, not assurance" |
| H-VAGUE-SOURCE | coffee-peer-voice rule, never linted before | "a recent study" with no publisher, "a company I know" |
| H-ENGAGEMENT-BAIT | 2026-10-19 slack | "Thoughts?" and comment prompts as the last line of a post |
| H-THROAT additions | 2026-10-16 slack, 2026-10-09 post | "There are two ways this goes," "starting here:" setups, "Here's the kicker," "The catch?" |
| H-CONNECTOR additions | 2026-11-02 blog paste | "Interestingly," "Crucially," "Importantly," "Notably," "Essentially," |
| H-PRAISE-LABEL additions | 2026-10-13 comment, 2026-11-02 post paste, 2026-10-09 meme | "is exactly the phrase," "doesn't shy away from," "I respect the honesty" |
| H-VOCAB addition | 2026-10-30 post paste | "unveiled" |
| H-SHAPE-ROADMAP, H-SHAPE-RECAP, H-SHAPE-ERA | SlopShape core values | "In this post, we'll," "In short," "built for a slower era," "future-proof," "in an era of" |

## New ADVISORY Rules

| Rule | Register entries | What it catches |
|---|---|---|
| A-XREF | 2026-11-05 slack, 2026-10-07 email | "items 2 and 3," "ask 6," "see above" |
| A-HEDGE-STACK | 2026-10-31 slack | "I imagine it would," "would likely" |
| A-FIRSTPERSON-CLAIM | 2026-10-30 email, 2026-10-26 comment (twice), 2026-10-24 blog (twice), 2026-10-03 rant | First person actions and feelings that need Rock's confirmation |
| A-ROCK-TERM | 2026-10-14 email | "on premises" for "on prem" |
| A-PEER-IMPERATIVE | 2026-10-14 email | "Name, send him" style orders to peers |
| A-NO-OBJECT | 2026-10-11 blog, 2026-10-09 post | "I'd want to see more," "nobody knows." |
| A-COLON-LIST | 2026-10-04 blog | A colon followed by an inline list |
| A-STAGED-REVEAL | 2026-10-22 comment, 2026-10-04 blog | "is already written down," "had it right the whole time" |
| A-GENERALIZATION | 2026-10-09 post | "Every time X, we Y" on one case |
| A-NOUN-LABEL | 2026-10-22 comment, 2026-10-16 slack | "That read is," "The cheap one is" |
| A-CLICHE additions | 2026-10-09 rant (twice), 2026-10-04 blog (three), 2026-10-14 comment | "whose badge it wore," "the same hop," "the attacker's column," "back there" |
| A-CLEFT addition | 2026-10-23 post | "What decided this week was dumber." |
| A-VOCAB additions | 2026-11-02, 2026-10-31, 2026-10-30 pastes, 2026-10-31 slack | demonstrates, emphasized, essentially, honestly, clearly, definitively, explicitly, conspicuously, brilliant, "we're aligned," "big picture" |
| A-ASKS-UNLISTED | 2026-10-07 email, 2026-10-31 slack (third hit) | Three or more asks in prose with no numbered list |
| A-LENGTH | 2026-10-07 email, 2026-10-12 slack | Email or chat over 400 words, a post over 300 |
| A-ACRONYM | 2026-10-30 post (twice), 2026-10-11 blog, 2026-10-09 rant, 2026-10-04 blog | An acronym used before it is spelled out |
| A-CODE-IN-SOCIAL | 2026-10-26 comment | File names and snake_case identifiers in a social post |
| A-REPORT-NO-LINK | 2026-10-09 rant | A post that mentions a report and carries no link |
| A-CLOSING-QUESTION | 2026-10-19 slack | A generic engagement question as the last line of a post |
| A-INITIAL-CONJ | 2026-11-02 blog paste, 2026-10-31 post paste | Sentences opening with And, But, Or, Yet, or Nor ("So" passes) |
| A-SYNONYM-CYCLE | 2026-10-04 blog | tries, attempts, and runs rotated for one unit |
| A-BURSTINESS, A-PARA-UNIFORM | 2026-10-29 course answers | Metronomic sentence lengths and same-skeleton paragraphs |
| A-DO-X-AND-Y | coffee-peer-voice 1.6 rule, never linted before | "Drop it silently and every rate is wrong." |
| A-SHAPE-* and A-SHAPE-MODAL | SlopShape core values | Roadmap openings, recap closings, closings that restate the opening, legacy-versus-modern contrasts, no date, institutional voice, no route out |

## Not Lintable

These 48 entries record a judgment a regex cannot make without firing on Rock's own writing. The read-back pass in coffee-peer-voice owns them.

| Kind | Count | Register entries |
|---|---|---|
| Stance and heat (agree before adding an angle, hype at Rock's size, rant level, scorched earth memes, owning a mistake bluntly) | 25 | 2026-11-04 x reply, 2026-10-31 slack, 2026-10-30 meme, 2026-10-23 post (two), 2026-10-14 post, 2026-10-14 comment, 2026-10-11 blog, 2026-10-09 post (two), 2026-10-09 rant (three), 2026-10-09 meme, 2026-10-09 email, 2026-10-04 blog, 2026-10-03 rant (nine) |
| Audience and argument (who is in the room, each bullet carries its ask, tie each paragraph to the post's line, name the specific thing) | 11 | 2026-11-02 blog, 2026-11-01 chat, 2026-10-22 slack, 2026-10-19 slack, 2026-10-16 post, 2026-10-14 email, 2026-10-14 comment, 2026-10-09 post, 2026-10-09 email, 2026-10-04 blog (two) |
| Facts and source fidelity (names, roles, access, scope of a source, tools Rock actually runs) | 7 | 2026-11-01 slack, 2026-10-22 slack, 2026-10-20 slack, 2026-10-14 email, 2026-10-12 email, 2026-10-04 blog (two) |
| Beats Rock adds himself and the skill must never invent | 4 | 2026-10-09 post, 2026-10-04 blog (two), 2026-10-03 rant |
| Report formats owned by another skill | 1 | 2026-10-12 slack (the acs-weekly-status header line) |
