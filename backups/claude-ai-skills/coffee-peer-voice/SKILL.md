---
name: "coffee-peer-voice"
description: "Draft or rewrite prose in Rock's casual, warm, peer-to-peer voice. Use it for every message or post Rock will send as himself (Slack, Teams, DM, text, email, LinkedIn post or comment, status update, intro, heads up), even when the request only says \"write a slack message\" or \"draft a reply\" and never mentions voice. Also use it when the user wants writing that sounds human or \"like a real person,\" wants the AI tone stripped from a draft, or names AI writing tells: \"make this sound human,\" \"casual tone,\" \"less corporate,\" \"remove the AI slop.\" Trigger on sentence structure complaints too, since fragment stacking is the most common way this voice fails: \"write in full sentences,\" \"stop writing fragments,\" \"too choppy,\" \"it reads clipped,\" or any correction pointing at sentences missing a subject or verb."
---

# Coffee Peer Voice

Version 1.18, owner Rock Lambros.

## Proof of Read

Before writing any of the user's prose, open this file and print this line on its own, first, above everything else in the response:

`coffee-peer-voice v1.18 loaded`

Print it on every invocation, including every revision of a draft you already produced. Memory of an earlier read in the same conversation does not count. If you cannot print the stamp because you did not open the file, say so and stop before writing the draft.

Fourth maintainer note: the stamp exists because this skill failed in production on 2026-09-03. It was read once at the top of a session, then eight subsequent drafts were produced from memory, and the model told Rock it had run the pass each time. The read-back pass in the last section is the first thing to disappear when the file is not in front of you, and its absence is invisible to the reader. A stamp Rock can check in one second is the only control that survives that failure mode. Do not remove it.

Fifth maintainer note: the four tells added in 1.6 (topic-label openers, clefts, do-X-and-Y-happens, performative hedging) all come from a 2026-09-04 Slack draft where Rock caught each one in review and the skill had no rule for any of them. The confidence-number rule in "Have a point of view" changed in the same pass, because the old wording invited a percentage without requiring it be real and produced a fabricated 90% in a message headed for an executive. Deliberately absent: any rule about sentences opening with "So." Rock uses that on purpose for a casual register, and an earlier draft of this note tried to ban it.

Sixth maintainer note: 1.7 came out of a 2026-09-20 review. Rock reported that all ten of his most recent corrections were tells this skill or anti-ai-slop already had a rule for, split about evenly between mechanical tells and cadence tells, so coverage had stopped being the constraint. Three causes were visible in the files. Nothing outside the model checked a draft. This file wrote its own instructions in the patterns it bans, with 12 reversed antitheses and 3 semicolons by the linter's count. The voice target held no sentence Rock wrote. 1.7 answers each cause: `slop_lint.py` runs on every draft, this file's own prose was rewritten until the linter found no semicolon and no antithesis in it, and `references/` holds Rock's samples and his corrections log. The linter does not reopen the third note, because it returns quoted spans and no score, its HARD list is limited to tells with no honest use, and the fix loop stops after two passes. The same review imported what a "Writing Rules" doc had that the two skills lacked: literal language, the portability test, no invented details, template shapes, and credentials lists. Four of that doc's rules were left out on purpose because each would hurt Rock: its ban on "human oversight" (the title of EU AI Act Article 14), its bans on "cross-functional" and "enablement," its instruction to vary vocabulary, and its advice to replace em dashes with semicolons.

Seventh maintainer note: 1.8 came out of a 2026-09-21 analysis of Rock's sent mail. Of 16,392 sent items across two years, 2,971 were mail he typed to other people (132,592 words). The rest was bulk sends, calendar replies, templated briefs, and mail to himself. `references/voice-guide.md` holds what that corpus measured, and three rules changed to match it. Short reaction sentences are his (about 27% of his sentences run five words or fewer), so the fragment rule now bans only the stacked dramatic kind. His exclamation points sit on thanks and goodwill, so they are allowed there. Rock decided on the same day that idiom he would say out loud stays and decorative metaphor stays banned, which replaced the "Write literally" rule from 1.7. The data also confirmed the bans: "crucial" appears zero times in his typing, "not just" about once per 10,000 words, and a true em dash in 14 messages that otherwise read as AI assisted. One limit to remember: his register barely moves by audience in email, so the public, formal, and academic columns in the guide are proposals until samples calibrate them.

Eighth maintainer note: 1.9 measured Rock's own text in chapters 8 to 11 of The CISO Evolution (24,446 words drafted in 2021, before any AI assistance was possible) and used it to replace the proposed formal column in the voice guide with measured numbers. The book register runs 18 words per sentence and four sentences per paragraph, which is closer to generic prose than his email is, so the base register stays the target for posts and chat. Seven features came out the same in both corpora, and the guide lists them as the core of the voice. The samples file now holds four passages from the chapter 9 to 11 drafts, tagged by register.

Ninth maintainer note: 1.10 measured 60 LinkedIn posts and 40 comments Rock published between 2016 and November 2022, before AI assistance was possible, and it replaced the proposed public column in the voice guide with measured numbers. Two proposals were wrong. His posts carry exclamation points at 12 per 1,000 words, on outrage as well as thanks, and they use "w/" and the ellipsis. The corpus also answered the question email could not: a post of his runs 40 to 80 words in two or three paragraphs, opens on the news or the claim, and ends on a plain statement or a short line, almost never on a question. The samples file now holds nine public passages plus openers and closers. The same corpus showed the third place where his standing rules are stricter than his own history: figurative language ran 5.4 per 1,000 words in those posts, and the rule still bans the decorative kind.

Tenth maintainer note: 1.12 moved the corrections log out of this skill and into a Notion page, the Voice Corrections Register. Between September 20 and October 2, 2026, sessions told Rock they had updated `references/corrections.md` and the entries never reached the skill. A session's copy of this skill is a snapshot that disappears when the session ends, so an edit to it succeeds on disk, gets reported as done, and is gone. When this skill was last synced, the log held 11 entries, all from October 3. The register is the fix because any session with the Notion connector can write to it, the write lasts, and Rock can check it. The rule that a logged correction must come with the register link exists for the same reason as the stamp in the fourth note. Do not remove either one.

Eleventh maintainer note: 1.14 came out of a 2026-10-09 Slack heads up to a colleague. The draft ended on two lines Rock flagged as slop: "Wanted you to hear it from me before the intro goes out." and "Flag anything I should know first." The first explains why the message was sent, claims a tact Rock never expressed, and has no subject. The second invents a review step he never set. The session that wrote it never loaded this skill, because a plain request for a short Slack message matched none of the trigger phrases in the old description, so 1.14 rewrites the description to fire on any message or post Rock sends as himself. slop_lint 1.3.1 returned zero HARD findings on that draft, and slop_lint 1.4.0 (shipped in anti-ai-slop 1.6) adds H-CLOSER-MOTIVE and A-CLOSER-GATE for the two shapes. The closer rule below is narrow on purpose. Rock's measured email closers include "Let me know if you need anything." and "Happy to hop on a call.", so a ban on every closing offer or ask would strip his own voice. A 1.13 card from the same session carried only the closer rule, and 1.14 replaces it.

Twelfth maintainer note: 1.15 adds the Finishing Pass at the end of this file, which runs the `clean-user-facing-text` skill on every draft after the read-back. Rock asked for it on 2026-10-23 so the text he sends is in his voice and free of invisible Unicode watermark carriers. The same day he chose the gated version, where a stylometry score decides whether the cleaner rewrites, over a strip-only version that would have left the third note untouched. The cleaner's own rules say it must keep the writer's voice and add nothing the source lacks, so the pass names the read-back draft as its source and holds any rewrite to every rule in this file. The Claude Code copy and the claude.ai and Cowork copy of this skill must stay byte-identical. Change both together or neither.

Thirteenth maintainer note: 1.16 changes only how this file tells you to run scripts. Rock asked for it on 2026-10-31 because the Finishing Pass was the largest source of his repeat permission prompts. "Run the scripts from the `scripts/` folder" plus three bare script names produced one chained line on every run: a shell variable holding the folder, a `python3 -I -c` call to pull one field out of the JSON report, `| grep` on the stats, and `; echo "exit=$?"`. No allow rule can match a line like that, so every run stopped for a manual approval.

Every invocation is now `python3 -I` followed by the full script path, one script per Bash call, and step 2 of the Finishing Pass states the rule and its reason. Rock's allow rules match from the first character and include `-I`, so a call that drops `-I`, adds another flag, or names the folder through a variable prompts again. Keep every command example in this file in that exact shape. The paths name the claude.ai and Cowork folders, which the sync builds from Rock's organization and account IDs and keeps across re-syncs. The Claude Code copy carries the same text, and step 2 tells a session on another machine how to build its own paths, so the byte-identical rule in the twelfth note still holds.

Fourteenth maintainer note: 1.17 came out of a 2026-11-06 request from Rock after register tells kept reaching him. Two changes. First, slop_lint 1.6.0 (anti-ai-slop 1.9) now carries every register pattern a regex can see, and this file now requires a printed disposition line for every ADVISORY finding, because most register entries read "HARD 0" while the flagged span sat in an ADVISORY line the session never answered. Second, the new "Write To The Human Shape" section turns the SlopShape paper's measurements (Madler, arXiv:2609.15369v3) into drafting moves, so a draft starts in the human shape and the linter checks it afterward. That section names its limits, and the third note still holds: the linter reports spans and counts, and nothing in this file grades a draft.

Fifteenth maintainer note: 1.18 records Rock's November 6, 2026 Pangram test in "Write To The Human Shape" and adds his rule that this skill never calls Pangram or any other paid detector. He set the rule because each call bills his account. Do not remove it.

Write like you're across a small table from a smart friend, coffee in hand. Stay warm and direct, and leave your guard down. You respect them enough to skip the throat-clearing and just talk. The reader should feel like a person wrote this for them.

This is a voice skill with no fixed output format. Match the format the user already wants (email, post, paragraph) and change how it sounds. Every draft ends with the Finishing Pass in the last section.

Maintainer note: this skill restates the anti-slop rules from the master writing_style on purpose rather than inheriting them, because inherited voice rules don't survive execution. If the master bans change, change them here too.

Second maintainer note: the complete-sentence rule in 1.2 replaced an earlier instruction to "drop a four-word sentence." Don't reintroduce it. Rhythm variation comes from clause count, and every sentence keeps its subject and verb.

Third maintainer note: the read-back pass added in 1.3 is deliberately unscored. An earlier 1.3 attempt used a numeric AI-detection self-grade plus observable exit criteria and got reverted to 1.2. Don't reintroduce a score. This pass is a structural read for cadence, pivots, and filler. It stays away from word-level scrubbing, because scrubbing every tell mechanically stiffens the prose into a worse tell than the one you removed. Rock made one exception on 2026-10-23, recorded in the twelfth note: the Finishing Pass reads a stylometry tier from `clean-user-facing-text` and uses it to decide whether the cleaner rewrites. The read-back pass itself stays unscored, and you never grade your own draft.

## The Voice in One Breath

Talk, don't present. Contractions are fine and usually right. Mix short complete sentences with longer, winding ones that follow a thought where it goes. Sound like you've actually done the thing you're describing. When something's hard or annoying or uncertain, say so. A real person has opinions and admits the messy parts. And warmth here means familiarity, the shorthand of someone who knows you. It never means flattery.

## What to Do

**Vary the rhythm on purpose.** AI defaults to sentences of nearly equal length, paragraph after paragraph of the same shape. That flatness is the single clearest tell. Get the variation from clause count. Let one sentence carry a single clause and the next one run three, and move the subordinate clause to the front sometimes instead of always trailing it. Read it back. If every line is the same size, break it up. When it reads flat, vary the clause structure and keep every sentence complete. Rock's measured numbers are the target: a mean near 12 words, a median near 10, about a quarter of sentences at five words or fewer, and about one in ten past 25. The full table is in `references/voice-guide.md`.

**Write in complete sentences, and let short ones react.** Rock's typed mail is full of short sentences. Most are complete ("I get it." "That works for me."), and the rest are reactions he would say out loud ("Got it." "Sounds good." "Weird."). Both belong in email and chat, and a few belong in a post. The tell is a different thing: a stack of dramatic fragments built for a reveal ("Ninety-day SLA? Dead." "No source needed."), which is the most recognizable AI post shape there is. Every sentence that carries an argument gets a subject and a verb. Imperatives count as complete, so "Bring your patch SLA." is a full sentence with an implied you and it can stay exactly that short. Don't pad an imperative with a because-clause just to make it look longer.

**Say the connection out loud.** When two sentences sit next to each other and the logic between them is only implied, name it with because, so, which, and, or but. "No source code required. The patch is the disclosure." becomes "No source code is required because the patch is the disclosure." Juxtaposition makes the reader do work you should have done.

**Change the shape of the piece too.** Machine prose stays detectable from structure alone even after every word is fixed: same entry point, even emotional temperature throughout, tidy landing with the lesson spelled out. Open where a friend would actually start the story, sometimes mid-scene, sometimes with the punchline first. Let one paragraph run hot while the next stays matter-of-fact. Skip the stated takeaway in about half of pieces and end on the sharpest detail or the open question, because a friend trusts you to get it. Before shipping, glance at the last few pieces you produced. If this one has the same skeleton, change the skeleton.

**Use contractions and plain words.** "Don't," "you're," "it's," "I'd." Reach for the everyday word over the dressed-up one: use over utilize, help over facilitate, show over demonstrate, start over embark, about over regarding.

**Anchor in something real, by name.** Use a specific number, a concrete example, or an incident Rock actually told you about. Name the actual paper, person, vendor, incident, and date. "A recent study" and "a company I know" are how machines talk. A friend tells you which study and which company. One real detail does more than three paragraphs of overview.

**Use only the material you were given.** Build every name, number, date, quote, and first person story from what Rock supplied in this conversation or from a source you opened. When the draft needs a detail you don't have, write `[ROCK: what you need]` in its place and keep drafting. Rock signs this prose, so an incident you invented becomes his false statement. This skill already sent one fabricated confidence number toward an executive (see the fifth maintainer note), and an invented anecdote is the same failure.

**Write plainly, and keep the idiom.** Idiom that Rock would say out loud is part of his voice ("I took a stab," "where my head is at," "anyone with a red pen kills it in five minutes"). Keep one that arrives on its own and add none to sound casual, because his mail carries fewer than one per 1,000 words by a partial count. Decorative metaphor stays banned: journeys, battlefields, tapestries, double-edged swords, comfort objects, and staged analogies like "it's like having a second analyst." Business cliche stays banned with it. A model produces that kind of figure when it has no specific fact to offer. The test is whether Rock would say the phrase across a table without planning it. If the phrase sets a scene or exists to make the point sound bigger, state the literal thing.

**Run the portability test.** If a sentence could move into a post on a different topic without edits, it carries no information. Replace it with a fact that belongs only to this piece, or cut it.

**Have a point of view, sized to your evidence.** It's fine to say something's frustrating, overrated, or that you're not sure. Only attach a number to your confidence if you actually computed one, because an invented percentage reads as calibrated and isn't. When there's no number, name what would change your mind instead. Relentless positivity with no rough edges reads as machine-smooth, and so does hedging every claim identically no matter how solid it is.

**Talk to "you," speak as "I."** Address the reader directly. Own your take in the first person. That's what makes it feel like a conversation.

**Let it be a little imperfect.** Allow a tangent, an aside in parentheses, a "yeah, but in reality" caveat, or a digression that never quite pays off. Readers take those irregularities as a sign that a person wrote it.

## What to Avoid (the AI Tells)

These are the patterns Wikipedia editors, the StoryScope corpus work, and plain reading flag most often as machine writing. Clear them out.

- **The em dash and its stand-ins.** The en dash, the spaced hyphen, and the semicolon are what a model substitutes once the em dash is banned, and Rock's standing rule bans the semicolon too. Put an aside in parentheses, which is Rock's own habit at 10 to 12 per 1,000 words, or use a comma, a period, or a colon.
- **Inflated significance.** "Plays a pivotal role," "stands as a testament," "is a crucial part of the broader landscape," the "-ing" tails that fake analysis ("...highlighting its importance"), and the result tails that do the same job ("...ensuring compliance," "...enabling faster response"). Cut the puff, state the thing, and give a real result its own sentence and verb.
- **Rule-of-three padding.** AI stacks adjectives and list items in threes by reflex: "innovative, transformative, and groundbreaking." If you didn't choose all three for a reason, lose one.
- **The antithesis pivot.** "Not only X but Y," "It's not just A, it's B," "It isn't about X, it's about Y," and any framing that stages an ordinary idea as a grand reveal ("It's not a city, it's a living adversary"). If two ideas do contrast, say each one straight and let the reader feel the gap.
- **The reversed antithesis.** "It's Y, not X," "Y rather than X," "Y instead of X," most of all as the last sentence of a paragraph. This is where the pivot goes once the leading form is banned, and it stages the same reveal. A contrast is fine when the reader really might have assumed X. Otherwise state Y and stop.
- **The "however / moreover / furthermore / consequently" crutch.** Don't lean on a small set of formal connectors. Split the sentence in two, or use a plain "but" or "so" mid-sentence.
- **Throat-clearing and insight-teasers.** "It's worth noting that," "It's important to remember," "In today's fast-paced world," "In conclusion," "Here's the thing," "Here's what most people miss," "You see." These promise a point instead of making one. If you've spotted what most people miss, state the miss and let it land on its own.
- **Topic-label openers.** "On WP." "The nono piece." "One design note." "The loop is clean." These announce what a paragraph is about instead of saying the thing. Nobody talks like this. Open with the claim and let the subject be obvious from it.
- **Clefts and nominalized subjects.** "The reason X is Y," "What matters here is Z," "The thing that broke was Q." Say it with a plain subject and verb: "X matters because Y."
- **Do-X-and-Y-happens.** "Drop it silently and every rate is wrong." "Blind it to FP and containment never fires." It's a punchy shape that stacks fast. State the conditional plainly with if or when.
- **Performative hedging.** "I'd like to be wrong here," "correct me if I'm wrong, but," "maybe I'm missing something." These pretend at doubt while implying the reader erred. If the uncertainty is real, say where it actually sits: what you haven't seen, what you're inferring from.
- **The dread cliché.** "What keeps me up at night," "what keeps people up at night," "what keeps CISOs up at night," and the whole anxiety-gesture family. Name the actual risk, who eats it, and what it costs.
- **Flattery and validation.** "Great question," "You're absolutely right," "I'd be happy to help," "Absolutely!", and rubber-stamping whatever was just said. A friend doesn't grade your questions. They start answering like they've been thinking about the same problem. If you praise something, praise it specifically and say why, or skip it. Warmth comes from familiarity and directness, and it survives disagreement. Performed enthusiasm belongs on this list too. Rock's own exclamation points sit on thanks and goodwill in email and chat ("Looking forward to it!"), so keep them there, keep them out of arguments, and allow one at most in public writing.
- **Bolded-header bullet lists** where every line reads "**Term:** explanation." That layout is a chatbot fingerprint. Prefer prose, or plain bullets when a list helps.
- **Promotional / travel-brochure tone.** Admiring, salesy adjectives where neutral description would do. "Breathtaking," "rich tapestry," "must-see."
- **Vague attribution.** "Critics argue," "many experts say," "it is widely regarded." Name who, or drop it.
- **Template shapes.** The concessive frame ("Despite its strengths, X faces several challenges," "While it may seem minor"), the false range ("from startups to the Fortune 500"), and editorial headers ("Why It Matters," "Future Outlook"). Each one is a slot a model fills on any topic. Put a problem where it belongs in the argument, name the two or three real cases, and let the content show its own relevance.
- **Credentials as proof.** "Featured in," "profiled in," "a leading expert." A list of outlets belongs in a bio. In an argument, use what the source said.
- **Tidy summary endings** that restate everything you just said. Trust the reader. End where the idea ends.
- **Motive narration and invented gates at the end.** A closing line that explains why Rock is sending the message or how he feels about sending it: "Wanted you to hear it from me first," "Didn't want this to catch you off guard," "Figured you'd want to know," "Just wanted to loop you in." A closing ask that adds a review step or a deadline Rock never set: "Flag anything I should know first," "Let me know if there are any concerns before I proceed." Both stage tact or caution nobody expressed, and a model reaches for them when the content has run out. End on the last fact or on what Rock is doing next ("I'm going to make the intro."). The linter flags the first shape as H-CLOSER-MOTIVE and the second as A-CLOSER-GATE. His own closers stay, because `references/voice-guide.md` measured them in his mail: "Looking forward to it." "Let me know if you need anything." "Happy to hop on a call." "I'll let you two take it from here." Keep an ask that sets a gate only when Rock asked for one, and then name what he's waiting on.

One caution: don't try to scrub every tell at once with mechanical rules, or the prose goes stiff and generic, which reads as even more artificial. Fix the obvious offenders (em dashes, antithesis pivots, inflated significance, flattery, the formal connectors) and let the natural rhythm carry the rest. The linter now owns the mechanical tells, so spend your own attention on shape, cadence, and whether the piece says anything.

## Write To The Human Shape

SlopShape (Madler, arXiv:2609.15369v3, September 28, 2026) compared 2,250 company blog posts written before ChatGPT with 11,250 AI versions of the same briefs. Structure alone told them apart at 97.0 macro-F1, and rewording each AI post span by span, which replaced about 73% of its 13-word sequences, only moved that to 96.1. Fixing words leaves the shape where it was, so these moves happen while drafting, before the linter runs. Each one carries the paper's gap between the human rate and the AI rate.

**Open on the thing.** Start on the news, the claim, or the first person line, never on an announcement of what the piece will cover (thesis and roadmap first, gap 0.419). Rock's posts open on the news or the claim 47% of the time.

**End somewhere the opening didn't go.** The largest human-AI gap in the paper belongs to a closing that restates the thesis (0.650), and the second largest to a summary stage (0.609). End on a new point, the next step, the last fact, or a short line. If the last paragraph could swap places with the first, rewrite the last one.

**Drop the old-way-versus-new-way frame.** AI posts organize around replacing a "legacy, manual, or reactive" model with a "modern" one (gap 0.497) and call things "modern, next-generation, or future-ready" (0.360). Say what the reader runs today, what broke, and when.

**Put a date on it.** Human posts refer to specific dates and periods (gap 0.283). Name the day, the month, or the year of the event, the report, or the change.

**Earn credibility from something real.** AI posts lean on a confident institutional voice (gap 0.347). Rock's credibility comes from what he did, a named source, or a number. Use his experience only when he supplied it in this conversation, under "Use only the material you were given."

**Send the reader somewhere when the channel allows it.** Human posts route the reader to a resource (gap 0.592). A post that mentions a report carries its link. A comment carries no link unless Rock adds one, and a book plug in a community Slack says where to get it in plain words.

**Keep it short.** Short pieces lean human (gap 0.274). Rock's posts run 40 to 80 words, so don't pad toward the AI length.

The paper's rarity measure is the part to copy most carefully. It scored each post by its distance from its 25 nearest neighbors in the feature space, and human posts sat in the rare regions (83.5th percentile on average against 43.6th for AI, Cohen's d 1.80), while the five models crowded into the same few shapes. A fixed humanizing recipe applied to every draft builds a new crowd, so vary the skeleton from piece to piece. Draw the opening and the closing from Rock's measured mix in `references/voice-guide.md` instead of reaching for the same move twice: posts open on the news or the claim about half the time, on a first person line about one in six, and on a question, a short line, or thanks about one in ten each, and they end on a plain statement about half the time and on a short line about a quarter. Within a piece, sentence lengths should vary the way his do. His samples run a sentence-length coefficient of variation between 0.34 and 0.68, and the linter flags anything under 0.30 as A-BURSTINESS.

The paper studied B2B blog posts, so carrying it to Slack, email, and comments is an inference. Its features were judged by an LLM, and the linter's regexes approximate that judge without validation against its labels.

No pass in this skill gets a draft past an AI detector, and Rock measured it. On November 6, 2026 he ran ten drafts this skill wrote under 1.16 and ten rewrites of the same content under 1.17 and slop_lint 1.6.0 through pangram-4. All 20 came back fully AI (fraction AI 1.0), including the ten that were HARD-clean, while two of his own LinkedIn posts from 2020 and 2021 came back fully human. The shape moves in this section serve Rock's readers. They don't change a detector's call, so never claim or imply that a draft will pass one.

## Quick Before / After

These pairs are synthetic and show the mechanics only. For how Rock sounds, read `references/voice-samples.md`.

**Before (AI voice):**
> It's worth noting that effective communication plays a pivotal role in building strong, lasting, and meaningful relationships. However, many people struggle with this crucial skill.

**After (coffee peer):**
> Most of us are bad at talking to each other, and it costs us. You misread one email from a teammate and a week later you're working around a problem that didn't exist.

**Before:**
> **Key Takeaway:** Consistency is essential. Moreover, it is important to remember that small efforts compound over time into significant results.

**After:**
> Show up on the boring days, the ones where nothing seems to move. Twenty minutes every Tuesday gets you further than a big Saturday session, mostly because the Saturday session keeps getting skipped.

**Before (fragment stack):**
> Shipping a patch does half the attacker's work. No source code required. The patch is the disclosure. Ninety-day SLA? Dead.

**After (complete sentences, varied clause count):**
> Shipping a patch now does half the attacker's work for them. A capable enough model diffs your patched binary against the last release, figures out what you just fixed, and writes the exploit. No source code is required because the patch is the disclosure. Most vulnerability management policies still carry a ninety-day SLA, and that window assumes the attacker needs weeks to build an exploit.

Note what changed in the fragment pair. The rhythm survives, and it now comes from clause count. Every sentence has its subject and verb, and the causal link that the fragment version left implied is stated with "because."

**Before (every line a mic-drop):**
> AI doesn't break your security. It exposes the security you never had. Every control you skipped is now a door. Every assumption you made is now a bet. The model doesn't attack you. It just tells the truth faster than you can hide it.

**After (plumbing restored, one earned landing):**
> Most of what AI exposes in your security was already broken. The controls you skipped and the assumptions nobody tested are easy for an agent to find, because it tries everything at once where a human pen tester works through a list. Speed is the only new part, and it means you learn about the gaps when the attacker does.

The before is six sentences and six engineered landings, two of them negative parallelism ("doesn't break, exposes" and "doesn't attack, tells the truth"). The after states the contrast once, in plain terms, and ends on a consequence the reader can act on. That's the cadence the read-back pass below is built to catch.

## Rock's Voice Guide, Samples, and Corrections

Read `references/voice-guide.md` first. It was measured from 2,971 emails Rock typed himself, and it is the base register for every channel. Pick the register from its shift table (base, public, formal, or academic) by the channel and the audience, and name your pick in one line above the draft so Rock can correct it. When Rock asks for a more formal or a more academic tone, move one column to the right and keep what the guide says holds in every register. For a post, follow the guide's "How A Post Is Built" section: 40 to 80 words in two or three short paragraphs, open on the news or the claim, put any question inside the post, and end on a plain statement or a short line. Caps on one word can carry the emphasis. Two exclamation points are fine in a post, and a stack of them is not.

Then read `references/voice-samples.md` before drafting. The samples are passages Rock wrote or fully hand edited, and they are the voice target. Each sample carries a register tag. Take sentence length and paragraph size from a sample only when its register matches the draft, and take the fingerprints (direct "you," asides in parentheses, plain disagreement) from all of them. Borrow no sentence and no topic from them. If the samples file still carries its TEMPLATE status line, say so in one line above the draft and continue, because Rock needs to know the voice target is missing.

## The Corrections Register

The live corrections log is the Notion page "Voice Corrections Register" (page ID `3ef1c206e61981379452c3b25ba2573e`, https://app.notion.com/p/3ef1c206e61981379452c3b25ba2573e). It holds pairs of a sentence this skill produced and the fix Rock made, newest first. Fetch it with the Notion connector before every draft and treat each pair as a tell to keep out of the draft. `references/corrections.md` is a frozen copy from October 3, 2026. Read it only when Notion is unavailable, and in that case say in one line above the draft that the register couldn't be read and the fallback is stale.

When Rock corrects a sentence you wrote, add the entry to the register yourself, in the format the page shows, directly under its Entries heading. Then fetch the page again to confirm the entry is there. Only after that check may you tell Rock it's logged, and that reply must include the register link. If the write fails or Notion isn't connected, print the formatted entry under the line `NOT LOGGED: register write failed` so Rock can see it didn't happen. Never edit this skill's files on disk as a way to log a correction, because that copy disappears when the session ends and the edit only looks like it worked. That one mistake is how a month of corrections got lost.

## Calibrating

If the user gives you a draft, keep their meaning and their facts intact, because your job is the voice and the argument is theirs. If they're writing something formal where warmth would be wrong (a legal notice, a compliance statement), check before loosening it. Default, though, is friendlier than they expect, and they can always ask you to dial it back.

Match the length to the channel. Slack and chat replies run short, and past roughly 400 words the reader skims and the best point dies in paragraph six. Long-form belongs in a doc.

## Before You Print: Run the Linter, Then the Detector

Save the finished draft to a file with the Write tool, and keep its absolute path (DRAFT below). Then run the linter that ships with `anti-ai-slop`. It lives at `scripts/slop_lint.py` inside that skill's folder, next to the SKILL.md you open for its stamp. Run it as one Bash call written exactly like this, under the invocation rules in step 2 of the Finishing Pass, with DRAFT replaced by the draft's absolute path and PROFILE by one of the profiles below:

```bash
python3 -I /root/.claude/skills/synced/2825d214-4bfb-4e1d-80cd-1d3e1cb53f2e_3c2745be-5606-4f67-8f03-6af5a0954b26/anti-ai-slop/scripts/slop_lint.py DRAFT --profile PROFILE
```

Use `email` for email, Slack, and chat, `social` for LinkedIn and X, `blog` for newsletters and long posts, `formal` for executive, board, client, and long form writing, and `technical` for docs. The `casual` profile exists for auditing someone else's chat messages. The `email` profile allows what Rock does in his own mail (goodwill exclamation points, 😊, and a run of reaction sentences) and keeps every HARD rule. The tool call is the proof that the check ran, and it is stronger than a stamp because Rock can see the output. Paste the HARD and OPEN_ASK lines above the draft, even when there are none.

Fix every HARD span yourself, in voice, by deleting the clause or stating the specific fact. Read each ADVISORY span and decide, because many are fine and the linter cannot tell an earned landing from an engineered one. Then print the decision: one line per ADVISORY finding under the HARD and OPEN_ASK lines, in the form `<rule id> L<line>: fixed` or `<rule id> L<line>: kept, <reason in ten words or fewer>`. A kept finding needs a reason Rock can check ("his own line from the register," "he said he ran it," "literal term"). A missing disposition line means the pass did not run. Never keep an A-SMOOTH, A-BURSTINESS, or A-SHAPE finding because the topic is technical (register, 2026-10-12), and never split a clause into its own sentence only to clear one (register, 2026-10-04). Run the linter a second time after your fixes and then stop. Two passes is the cap, since chasing a clean report is the over scrub failure the third maintainer note describes. If a HARD rule misfires on a term Rock needs, keep the term, name the rule that misfired, and move on.

Then run the `anti-ai-slop` skill in detect mode for what a script cannot see: metaphor, novelty inflation, gap-filling, synonym cycling. Flag only, no rewrite. Open that file and print its stamp the same way you printed this one. If this surface cannot run code, or the script exits with code 2 or 3 (it did not run), say so in one line and let detect mode cover the mechanical tells by hand. Only exit code 1 means the draft has HARD findings. The Bash tool puts a non-zero exit code on the first line of the result, so read it there and never append `; echo $?`.

Three rules on what to do with the flags:

- Fix the flagged spans yourself, in voice. Do not let anti-ai-slop rewrite them. Its replacements are mechanical by design, and mechanical scrubbing produces the stiff, sanded prose that reads as a worse tell than the one you removed.
- Voice goes last. That skill's own handoff section puts this one after it, and detect mode is the only exception because it changes nothing.
- A flag is evidence that still needs a reader's verdict. That skill says so in its own second section. A flagged word that is the precise technical term stays, and so does a flagged pattern the writer chose on purpose.

**Never call a paid detector.** This skill never calls Pangram, GPTZero, or any other metered AI-detection connector, at any step, including to check a finished draft. Each call bills Rock's account. A detector check happens only when Rock asks for one himself, outside this skill's pass.

This is a gate on the finished draft. The bans in "What to Avoid" stay written out here for the reason in the first maintainer note above, and nothing from the second skill's rule list carries into this one.

## Before You Print: Read It Back

Everything above is how you write the draft. This is the last pass, run after the linter and the detector, before the draft leaves your hands.

Every revision is a new invocation. A one-line tweak to a draft you produced two turns ago gets the full read-back pass, because edits made from memory are how the tells creep back in. Re-read this file first, print the stamp, then revise.

Do two things, in order. First confirm the draft actually follows the rules above. Then read for the failure mode those rules miss on their own: prose where every single line is built to land.

You can follow every rule above and still read as machine-written, because this tell isn't in any one sentence. It's in the cadence of the whole. When each sentence sets up and knocks down, when every line is quotable, when the piece reads like a string of mic-drops, a reader feels the engineering even if they can't name it. Real writing breathes. Most sentences carry information and get out of the way, and one or two actually land. A piece where all of them land is as artificial as a piece where none do.

Read the whole draft back, in your head, at speaking pace. Then check for these:

- **Mic-drop cadence.** Is most of the piece trying to be quotable? Count the sentences built to punch. More than a couple per few paragraphs and the rhythm has become a metronome. Let the plumbing sentences go back to being plumbing. Keep the one or two landings the content earned and flatten the rest into plain statement.
- **Manufactured zingers.** For each clever turn, ask whether the content earned it or you inserted it for effect. If you can cut the cleverness and lose nothing but the performance, cut it.
- **Negative parallelism.** Scan specifically for "not X, but Y," "it's not just X, it's Y," "isn't about X, it's about Y," "less X, more Y," and the "doesn't do X so much as Y" cousins. They stage an ordinary point as a reveal. Say each idea straight and let the reader feel the contrast without the scaffolding.
- **Paragraph-signaling filler.** Sentences whose only job is to announce a turn: "Here's the thing." "But it gets worse." "And that's where it falls apart." "Let me explain." They're throat-clearing dressed as a transition. Delete them and open the next paragraph with the actual point.
- **Fragment stacks and aphorism runs.** A row of subject-verb-less punches, or a row of standalone epigrams, is the most recognizable AI post shape there is. Rejoin them into complete sentences with the causal links stated, the way the complete-sentence rule above describes. Reaction sentences Rock would say out loud are fine in email and chat.
- **The last line.** Read the final sentence on its own. If it explains why the message exists, describes the sender's intent toward the reader, or adds a gate Rock didn't set, cut it and let the sentence before it end the message.

One targeted revision pass is usually enough. If fixing a flagged line makes the sentence stiffer, more generic, or more obviously scrubbed than the tell you removed, stop and keep the original. The engineered-to-land rhythm and the mechanical over-scrub are both machine tells, and trading one for the other is not a fix. Don't grade it, don't score it, don't keep re-running it chasing a cleaner read. Past a point each pass removes more voice than tells. When a sharp friend reading it wouldn't clock it, you're done.

## Before You Print: Finishing Pass

This runs on every draft, after the read-back and before anything prints. Invoke the `clean-user-facing-text` skill, open its SKILL.md, and run its workflow on the draft with the bindings below. Its folder sits next to this skill's folder, the same way `anti-ai-slop` does.

1. The draft that came out of the read-back is the source. Its first person, asides, contractions, reaction sentences, and register are Rock's voice, and the cleaner keeps them.
2. Use the draft file you already saved for the linter (DRAFT). Run each script as its own Bash call, written exactly the way the templates in steps 3 to 5 show it: `python3 -I`, a space, the script's full absolute path, then its arguments. Use no `cd`, no shell variable holding a folder, no `;`, `&&`, `||`, or `|` joining two steps, no redirect such as `2>&1` or `> file`, no `; echo $?`, and never `python3 -c` or a heredoc.

   Read each script's output as printed, take the exit code from the first line of the Bash result, read files with the Read tool, and make any rewrite with the Edit or Write tool. This form holds for the whole pass, even where the `clean-user-facing-text` or `anti-ai-slop` file shows a different one.

   The reason, so the next editor keeps it: Claude Code remembers an approval only as a rule that matches the start of one single command. Rock keeps one allow rule per script, in the form `Bash(python3 -I <full script path> *)`. A chained line, a folder held in a variable, or an inline `python3 -c` matches none of those rules, so every run stops for a manual approval. A call without `-I` misses too, because the rules match from the first character and `-I` is part of them.

   The paths below are the claude.ai and Cowork paths. When the Skill tool printed a different base directory for this skill, build the same paths from the folder that holds it, and still write them out in full in every call.

3. Score the draft with this call, then read the `Density Tier:` line of the report. The plain report prints the tier near the top, so there is nothing to parse. A draft under 30 words reports `Status: insufficient_length`, so go straight to step 5. The script exits with code 1 when the score is high, and that code is how it reports the score.

   ```bash
   python3 -I /root/.claude/skills/synced/2825d214-4bfb-4e1d-80cd-1d3e1cb53f2e_3c2745be-5606-4f67-8f03-6af5a0954b26/clean-user-facing-text/scripts/inspect_text.py --stylometry DRAFT
   ```

4. When the tier is `high`, rewrite once, in DRAFT, with the Edit or Write tool. The rewrite follows every rule in this file and keeps every fact. Then run the linter once more with the profile you used before, and fix any HARD span in voice. The linter lives in the `anti-ai-slop` folder, so its path differs from the cleaner scripts in steps 3 and 5:

   ```bash
   python3 -I /root/.claude/skills/synced/2825d214-4bfb-4e1d-80cd-1d3e1cb53f2e_3c2745be-5606-4f67-8f03-6af5a0954b26/anti-ai-slop/scripts/slop_lint.py DRAFT --profile PROFILE
   ```

   When the tier is `low` or `medium`, leave the prose as it is.
5. Strip invisible Unicode into FINAL, a new file next to DRAFT, with this call. Then read FINAL with the Read tool. Its contents are the draft you print.

   ```bash
   python3 -I /root/.claude/skills/synced/2825d214-4bfb-4e1d-80cd-1d3e1cb53f2e_3c2745be-5606-4f67-8f03-6af5a0954b26/clean-user-facing-text/scripts/clean_text.py DRAFT -o FINAL --stats --no-normalize-spaces
   ```

6. Below the HARD and OPEN_ASK lines, add one line in this form: `finishing pass: tier <tier>, <n> Unicode characters removed, rewrite <yes or no>`. The line is the proof the pass ran, and it does the job for the cleaner that the stamp does for this file.

If this surface cannot run code, or a script exits with an error, say so in one line and print the read-back draft. The cleaner's scripts have no by-hand fallback.