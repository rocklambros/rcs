---
name: "anti-ai-slop"
description: "Audit existing text for AI writing tells (\"AI slop\") and strip them out. This is the voice-neutral diagnostic-and-cleanup pass. Use it when the user wants to know whether a piece reads as machine-written, or wants the machine tells removed while keeping their own meaning intact. Trigger on \"audit this for AI tells,\" \"detect AI writing,\" \"scan this for slop,\" \"flag the AI-isms,\" \"strip the AI tells,\" \"is this going to read as AI,\" \"check this for machine tells,\" \"how AI does this sound,\" \"run the slop check,\" or a pasted draft with \"does this read as AI-generated.\" Also trigger when someone pastes suspected AI output (a vendor email, a submission, a ghostwritten post) and wants an assessment of what's flagged and how strong each flag is. For generating prose in a specific human voice, or making text \"sound like me / warmer / less corporate,\" defer to the coffee-peer-voice skill, because this skill only removes tells."
license: MIT
metadata:
  owner: Rock Lambros
  version: '1.12.0'
  adapted_from: "conorbronsdon/avoid-ai-writing v3.18.0 (MIT, Conor Bronsdon)"
---

# Anti AI Slop: Audit and Strip

Version 1.12, owner Rock Lambros.

## Proof of Read

Before auditing or rewriting anything, open this file and print this line on its own, first, above everything else in the response:

`anti-ai-slop v1.12 loaded`

Print it on every invocation, including every revision of text you already touched. Memory of an earlier read in the same conversation does not count. If you cannot print the stamp because you did not open the file, say so and stop before producing an audit.

The audit comes before the draft, always. Never hand over clean-looking prose with the issues list attached afterward as a summary, and never describe a pass in the past tense that you did not run span by span against this file. An empty audit is honest. A claimed audit is unfalsifiable from the reader's side, which makes it worse than skipping the skill outright, because the writer stops checking the places they would otherwise check.

Maintainer history for versions 1.1 through 1.12 lives in `references/maintainer-history.md`, so it no longer loads on every call. Read it before you delete or loosen any rule, because each rule came from a correction Rock made. Three rules carry a do-not-remove order from that history: this Proof of Read gate, the ADVISORY disposition rule, and the paid-detector ban.

You are auditing text for the patterns that make writing read as machine-generated, and, when asked, removing them. Your job is to find the tells, show them, and either report them or cut them. You are not putting a voice on the text. When the writer wants prose that sounds like them after the slop is gone, hand off to the `coffee-peer-voice` skill. This skill removes, and that one restores the voice.

## Signals need context

The patterns here show up more often in LLM output, and they also show up in human writing under deadline, in an unfamiliar genre, or in a second language. Several of these rules fire on non-native English and on compressed technical prose that trims vocabulary on purpose. Treat a hit as evidence that still needs a verdict from someone who knows the context. It is worth acting on to clean up a draft. It is not worth ruining someone's day over, so never make these flags the sole basis for a consequential call like academic integrity, hiring, or attribution. Pair the signal with context: who wrote it, what genre, what the writer's normal voice looks like, what else you know.

## Modes

**`rewrite`** (default). Flag the tells, then return a clean version. Lead with the audit so the writer sees the evidence before the edit.

**`detect`**. Flag only, no rewrite. Use this when the writer wants to decide what to fix themselves, when the flagged patterns might be intentional, when you are auditing someone else's or published text you should not alter, or when they just want a fast read. Trigger on "detect," "flag only," "audit only," "just flag," "scan," "does this read as AI."

**`edit`**. Change a file in place with minimal, targeted edits. Use this when the writer points at a file and wants that file fixed. Touch only the flagged spans. Leave already-human passages alone. Do not edit quoted material, code blocks, or text attributed to someone else. Flag those. When the file is large, confirm which section before changing anything, then re-read and verify after.

Default to `rewrite` if the writer does not say.

## Run the linter first

When code execution is available, run the bundled script before you read the text yourself, in every mode. Make it one Bash call written exactly like this, with FILE replaced by the draft's absolute path and PROFILE by one of `blog`, `technical`, `social`, `email`, `formal`, or `casual`:

```bash
python3 -I /root/.claude/skills/synced/2825d214-4bfb-4e1d-80cd-1d3e1cb53f2e_3c2745be-5606-4f67-8f03-6af5a0954b26/anti-ai-slop/scripts/slop_lint.py FILE --profile PROFILE
```

Write the full path every time, with `-I`, and join nothing to the call: no `cd`, no shell variable for the folder, no `;`, `&&`, or `|`, and no `; echo $?`. The fifth note in `references/maintainer-history.md` gives the reason. Save a pasted draft to a file with the Write tool first, because piping it in on stdin makes the call a compound command. When the Skill tool printed a different base directory for this skill (another machine or account), use that folder's literal path in place of the one above, still written out in full.

The script checks the mechanical tells in this catalog with regular expressions: punctuation, the Tier 1 and Tier 2 words, the leading antithesis forms, connectors, fingerprints, participle tails, and clusters of short sentences. It returns quoted spans with rule ids and line numbers, and it never rewrites or scores. HARD findings are tells with no honest use. ADVISORY findings need a reader. Three advisory checks compare the draft with Rock's measured cadence: A-SMOOTH (average sentence over 16 words, or under 10% of sentences at five words or fewer), A-LONG-PARAGRAPH (five or more sentences), and A-CONTRAST-BUDGET (more than 2 reversed contrasts per 1,000 words against his 1.1). The `email` profile is for mail and chat drafted in Rock's voice. It allows goodwill exclamation points, 😊, and runs of reaction sentences, and it keeps every HARD rule. The `formal` profile is for executive, board, client, and long form writing. It turns A-SMOOTH off and lets a paragraph reach six sentences, because Rock's own 2021 book chapters average 18 words per sentence and four sentences per paragraph. As of 1.4 the script also reads curly quotes as straight ones, so text pasted from Word or Outlook meets the same rules. As of 1.5 the `social` profile flags exclamation points at three instead of two, because Rock's own pre-2023 LinkedIn posts carry two in a fifth of cases, and the cliche list gained the phrases those posts surfaced ("secret sauce," "magic bullet," "behind the curve"). As of 1.6 the script also reads a message's last two sentences for a closer that narrates why the message was sent (H-CLOSER-MOTIVE, HARD) or adds a review step nobody set (A-CLOSER-GATE, ADVISORY). As of 1.8 (slop_lint 1.5.0) it flags praise labels that grade someone's work in place of saying what it does (H-PRAISE-LABEL, HARD). As of 1.9 (slop_lint 1.6.0) it carries every lintable register pattern (`references/register-coverage.md` lists them by entry), the SlopShape shape rules described under "Shape tells" below, A-BURSTINESS for metronomic sentence lengths, and A-PARA-UNIFORM for same-skeleton paragraphs. As of 1.11 (slop_lint 1.7.0) it flags the agreement ramp ("Agreed, and," "Agreed on X,") as H-AGREE-RAMP, a second agreement opener in one `social` batch as H-AGREE-REPEAT, and a ranking verdict on someone's point ("is the one I'd put first") as H-RANK-PICK, all HARD. Paste its HARD and OPEN_ASK output at the top of the audit, even when empty, because a visible tool result is the only evidence of a pass that the writer can check.

**Every ADVISORY finding gets a disposition line.** Under the HARD and OPEN_ASK lines, print one line per ADVISORY finding in this form: `<rule id> L<line>: fixed` or `<rule id> L<line>: kept, <reason in ten words or fewer>`. A kept finding needs a reason a reader can check ("Rock's own line from the register," "literal term of art," "Rock said he read the repo"). An ADVISORY finding with no disposition line means the pass did not happen, and the writer should treat the draft as unaudited. This rule exists because most register entries came back "HARD 0" with the flagged span sitting in an ADVISORY line nobody answered.

**Step budget.** When `scripts/slop_pass.py` sits next to `slop_lint.py`, a rewrite pass is two script calls, one before the rewrite and one after. Each is its own Bash call, written exactly like this:

```bash
python3 -I /root/.claude/skills/synced/2825d214-4bfb-4e1d-80cd-1d3e1cb53f2e_3c2745be-5606-4f67-8f03-6af5a0954b26/anti-ai-slop/scripts/slop_pass.py FILE --profile PROFILE
```

```bash
python3 -I /root/.claude/skills/synced/2825d214-4bfb-4e1d-80cd-1d3e1cb53f2e_3c2745be-5606-4f67-8f03-6af5a0954b26/anti-ai-slop/scripts/slop_pass.py REWRITE --profile PROFILE --clean-out FINAL
```

The first call lints the draft and reports its invisible Unicode and stylometry gauge. The second strips invisible Unicode from the rewrite into FINAL, then lints and scores FINAL. It replaces the separate slop_lint, inspect_text, and clean_text calls, so don't run those as well. Detect mode needs only the first call. The path and `-I` rules above apply to slop_pass too, and it needs its own allow rule. Exit codes match slop_lint: 0 for no HARD findings, 1 for HARD findings, 2 when the lint could not run.

Then hold to the budget:

- Make the rewrite in one Write. Don't split or merge sentences after the after pass for rhythm alone unless A-UNIFORM, A-SMOOTH, or A-BURSTINESS fired on it.
- Run a third call only when the after pass shows a HARD finding. Stop after two fix rounds and report what's left.
- An ADVISORY finding on the after pass gets its disposition line and no rerun.
- Don't fact-check claims during a slop pass unless the writer asked. Flag a doubtful claim in one line and let the writer decide.

When slop_pass.py is missing, run slop_lint.py with the template above and keep the same budget.

**Never call a paid detector.** This skill never calls Pangram, GPTZero, or any other metered AI-detection connector, in any mode, including to confirm an audit. Each call bills Rock's account. A detector check happens only when Rock asks for one himself, outside this skill.

Then do the part a script cannot: read for metaphor, novelty inflation, speculative gap-filling, synonym cycling, cadence, and anything in this catalog the script does not cover. `--include-quotes` also lints quoted material, for a pasted draft that arrives inside a blockquote. `--advisory-only` and the `SLOP_LINT_DISABLE=1` environment variable turn off the failing exit code when a rule misfires. Use `--advisory-only`, because a variable set in front of the command no longer matches the allow rule. Exit code 0 means no HARD findings and 1 means HARD findings. Codes 2 and 3 mean the script did not run. If that happens, or the surface cannot run code, say so in one line and audit by hand. The Bash tool puts a non-zero exit code on the first line of the result, so read it there.

## What to strip

### Formatting
- **Em dashes (— and --).** Replace with commas, periods, parentheses, or a colon, or split into two sentences. Target zero. This applies to headings too. Carve-out: an em dash acting as the separator in a bulleted or numbered list item that opens with a bold lead term or a markdown link (`- **Term** — description`) is typography and stays. A mid-sentence splice still counts, and the `--` substitute is never carved out. When the text is Rock's, move an aside into parentheses, because that is his own habit.
- **Dash stand-ins and semicolons.** The en dash, the spaced hyphen, and the semicolon are what a model substitutes once the em dash is banned. Flag all three. Rock's house style bans the semicolon outright.
- **Bold overuse.** Strip bold from most phrases. One bold phrase per major section at most. If something is important enough to bold, restructure the sentence to lead with it.
- **Bolded-header bullet lists** where every line reads `**Term:** explanation`. That layout is a chatbot fingerprint. Prefer prose, or plain bullets when a list genuinely helps.
- **Emoji in headers.** Remove. Social posts may carry one or two at the end of a line, never mid-sentence.
- **Excessive bullets.** Convert bullet-heavy sections to prose. Keep bullets for genuinely list-shaped content: feature comparisons, step-by-step, parameters.
- **Heading case.** Follow the writer's house style. Rock's standard is Initial Cap Case. Flag a heading only when the piece mixes styles.
- **Editorial section headers.** "Why It Matters," "Why This Is Important," "Future Outlook," "Challenges and Legacy." Cut the header and let the content show its own relevance. Carve-out: a newsletter format that uses one of these on purpose.

### Words and phrases to replace

Three tiers, by how reliably the word signals AI text. Match inflected forms: `genuine` also flags `genuinely`, `leverage` also flags `leveraging` and `leveraged`, unless a variant carries a distinct honest meaning (`real` meaning factual, not the intensifier in "a real improvement").

**Repair order.** First try deleting the clause. If the sentence still says something, you are done. If it loses meaning, state the specific fact the word was standing in for. Use the right-hand column only when the plain word is the literal meaning, because a synonym swap leaves a sentence that still carries no fact. The test for every flagged word: does it add information, or does it only make the sentence sound more important?

**Tier 1, always replace.** These run several times more often in AI text than human text.

| Replace | With |
|---|---|
| delve / delve into | dig into, look at |
| landscape (metaphor) | field, industry, market |
| tapestry | (describe the actual complexity) |
| realm | area, field, domain |
| paradigm | model, approach, framework |
| embark | start, begin |
| testament to | shows, proves |
| robust | strong, reliable, solid |
| comprehensive | thorough, complete, full |
| cutting-edge | latest, newest, advanced |
| leverage (verb) | use |
| pivotal | important (or say what depends on it) |
| underscores | shows |
| meticulous / meticulously | careful, detailed, precise |
| seamless / seamlessly | smooth, easy, without friction |
| game-changer / game-changing | say what specifically changed and what it cost or saved |
| utilize | use |
| watershed moment | (say what changed, with the date) |
| nestled | is located, sits, is in |
| vibrant | (describe what makes it active, or cut) |
| thriving | growing, active (or cite a number) |
| showcasing | showing (or cut the clause) |
| deep dive / dive into | look at, examine |
| unpack / unpacking | explain, break down, walk through |
| intricate / intricacies | complex, detailed (or name the complexity) |
| ever-evolving | changing, growing (or describe how) |
| daunting | hard, difficult, challenging |
| holistic / holistically | complete, full, whole |
| actionable | practical, useful, concrete |
| impactful | effective (or describe the impact) |
| learnings | lessons, findings, takeaways |
| thought leader / thought leadership | expert, authority (or describe their actual contribution) |
| best practices | what works, proven methods, standard approach |
| at its core | (cut, just state the thing) |
| synergy / synergies | (describe the actual combined effect) |
| in order to | to |
| due to the fact that | because |
| serves as | is |
| boasts | has |
| commence | start, begin |
| ascertain | find out, determine, learn |
| endeavor | effort, attempt, try |
| genuine / genuinely (as intensifier) | (cut, just state the fact) |
| embrace (metaphor) | adopt, accept, use, switch to |
| load-bearing (metaphor) | essential, critical, necessary, or say what breaks if you remove it |
| enhance / enhancement | improve (or say what got better and by how much) |
| vital | necessary (or say what fails without it) |
| garner | get, earn, draw |
| reimagine | redesign, rebuild (or say what changed) |
| profound / profoundly | (cut, or state the effect) |
| groundbreaking / renowned / enduring | (cut, or give the fact that earns it) |
| interplay | (name the two things and what one does to the other) |
| diverse array | (name the items) |
| exemplifies | is an example of, shows |
| bridge the gap | (name the two sides and what connects them) |
| there's no denying | (cut, just state the thing) |
| think outside the box | (describe the unusual approach) |
| key (adjective before an abstract noun: "key takeaway," "key driver") | main, or cut |
| highlight (verb) | show, point to |

Hyphen required on `load-bearing`: unhyphenated "load bearing" is ordinary English. Construction carve-out: `load-bearing wall / beam / column / joist / capacity` and similar structural nouns are standard building terms, so "the load-bearing structure of his argument" still flags but "the load-bearing wall" does not. `enhanced` in the title of a standard (NIST SP 800-172, Enhanced Security Requirements) is literal and passes. `key` as a noun (API key, key rotation) never counts.

**Tier 2, flag when two or more appear in the same paragraph.** Legitimate alone, an AI signal when they cluster.

| Replace | With |
|---|---|
| harness | use, take advantage of |
| navigate / navigating | work through, handle, deal with |
| foster | encourage, support, build |
| elevate | improve, raise, strengthen |
| unleash | release, enable |
| streamline | simplify, speed up |
| empower | enable, let, allow |
| bolster | support, strengthen, back up |
| spearhead | lead, drive, run |
| resonate / resonates with | connect with, appeal to, matter to |
| revolutionize | change, transform, reshape (or say what changed) |
| facilitate | enable, help, allow, run |
| underpin | support, form the basis of |
| nuanced | specific, subtle, detailed (or name the nuance) |
| crucial | important, necessary |
| multifaceted | (describe the actual facets, or cut) |
| ecosystem (metaphor) | system, community, network, market |
| myriad | many, numerous (or give a number) |
| plethora | many, a lot of (or give a number) |
| encompass | include, cover, span |
| catalyze | start, trigger, accelerate |
| cultivate | build, develop, grow |
| illuminate / elucidate | clarify, explain, show, spell out |
| cornerstone | foundation, basis |
| paramount | most important, top priority |
| poised (to) | ready, set, about to |
| burgeoning | growing, emerging (or cite a number) |
| nascent | new, early-stage, emerging |
| overarching | main, central, broad |
| transformative / transformation | (describe what changed and how) |
| align with | match, follow, map to (literal in a framework crosswalk) |
| insights (vague) | findings, or name what was learned |
| commitment to | (say what was done. Literal in ISO 27001 clause 5.1) |
| touch point | meeting, contact, step |
| deeply (significance uses: "deeply integrated," "deeply committed," "deeply rooted," while literal "deeply nested" never counts) | cut, or name what specifically runs deep |

Three terms from outside lists stay off this catalog on purpose, so never flag them: `human oversight` (the title of EU AI Act Article 14), `cross-functional`, and `enablement`.

**Tier 3, flag only at high density (roughly 3%+ of the words).** Normal words that AI overuses to fill space with vague praise: `significant / significantly`, `innovative / innovation`, `effective / effectively`, `dynamic`, `scalable`, `compelling`, `unprecedented`, `exceptional`, `remarkable`, `sophisticated`, `instrumental`, `world-class / state-of-the-art / best-in-class`. Replace some with specifics: numbers, comparisons, examples, a benchmark.

### Sentence and structure tells
- **The antithesis pivot: "It's not X, it's Y" / "This isn't about X, it's about Y."** Rewrite as a direct positive statement. Catch the split form too, where the negation and correction fall in two sentences ("The headline isn't the speed. The real story is Y."), and the stacked countdown ("Not the price. Not the features. The trust."). Also the tailing negation tacked onto a sentence end ("The options come from the selected item, no guessing" becomes "without forcing the user to guess"). Carve-out: negations enumerating spec constraints in a list ("no dependencies, no telemetry") are list content and stay. Catch the reversed form as well ("It's Y, not X," "Y rather than X," "Y instead of X"), most of all as the last sentence of a paragraph, because that is where the pivot goes once the leading form is banned. Keep a contrast when the reader really might have assumed X.
- **Hollow intensifiers.** Cut `genuinely`, `truly`, `quite frankly`, `to be honest`, `let's be clear`, `it's worth noting that`. State the fact.
- **Vague endorsement ("worth [verb]ing").** Cut `worth reading`, `worth a look`, `worth checking out`, `worth your time`. Say what the thing is and who it is for.
- **Hedge-stacked predictions.** "Could potentially create," "may eventually unlock," "might ultimately transform." Either word alone is fine. The stack is the tell, and each hedge cancels the next. Pick one.
- **Copula avoidance.** AI dodges "is" and "has" with `serves as`, `features`, `boasts`, `presents`, `represents`. Default to "is" or "has" unless a more specific verb genuinely adds meaning.
- **Synonym cycling.** AI rotates "developers, engineers, practitioners, builders" to avoid repeating a word. If the same word is the right one three times in a paragraph, keep it. Forced variation reads as thesaurus abuse.
- **Vague attribution.** "Experts believe," "studies show," "research suggests," with no name. Cite the specific source or drop the attribution and state the claim. Count inflation belongs here too: "several sources indicate" when one or two exist, and "such as" in front of a list that is already complete.
- **Vague third-party validation.** "Independent testing confirms," "analysts agree," "third-party benchmarks show we lead," where the authority is faceless and the claim unfalsifiable. Name the source, the test, and the result so a reader can check it, or cut the claim. Carve-out: a named benchmark, a linked report, or a dated audit is legitimate, because the tell is the vagueness.
- **Compulsive rule of three.** Vary groupings. Two items, four, or a full sentence. One "adjective, adjective, and adjective" per piece at most.
- **Real/actual adjective inflation.** "Real product-market fit," "genuine utility," "actual reward sustainability." Using `real / actual / genuine / true` as an empty intensifier on an abstract noun implies the rest of the field is fake without naming why this one isn't. Carve-out: a named contrast is honest ("actual revenue from paying customers, not grants"). The tell is the unsaid contrast.
- **The false range.** "From startups to the Fortune 500," "from beginners to experts." It gestures at breadth and names nothing. Name the two or three real cases.
- **The concessive frame.** "Despite its strengths, X faces several challenges," followed later by "Despite these challenges, X remains," and the smaller form "While it may seem minor, X." The frame fits any topic, which is the tell. Put each problem where it belongs in the argument and size the discussion to the real weight.
- **Metaphor, analogy, and cliche.** Journeys, battlefields, arms races, "it's like having a second analyst." A model produces figurative language when it has no specific fact. State the literal mechanism. Keep an analogy only when the writer chose it or the mechanism stays unclear without it. Rock's house style bans decorative metaphor and business cliche, and it allows idiom he would say out loud ("I took a stab," "where my head is at"). The test is whether he would say it across a table without planning it.

### Openers and closers
- **Formulaic openings.** If the piece opens with broad context before the point ("In the rapidly evolving world of..."), lead with the news or the finding. Context comes second.
- **Transition crutches.** "Moreover," "Furthermore," "Additionally," "Consequently." Restructure so the connection is obvious, or use "and," "also," "but," "so."
- **Chatbot artifacts.** "Certainly!", "I hope this helps!", "Feel free to reach out," "Let me know if you need anything else," "In this article, we will explore," "Let's dive in." Remove.
- **Sycophancy.** "Great question!", "You're absolutely right!", "That's a really insightful observation." Remove. Performed enthusiasm and stacked exclamation points belong here too.
- **Praise labels.** "Is the headline, and it deserves to be," "the math is the best part," "the feature I'd show every team first," "I'm stealing this," "go kick the tires," "must-read." Each one grades the work and carries no fact, and it reads as sycophancy even in a post meant to lift a friend. Say what the work does, specifically, and let that carry the support. The linter flags these as H-PRAISE-LABEL.
- **Ranking verdicts.** "Your runtime question is the one I'd put first," "Number 7 is the one I'd hand to procurement," "the part I'd keep," "is the bigger story." Each one ranks someone's point in place of saying what is true about it. State the claim about the thing itself. The linter flags these as H-RANK-PICK.
- **Agreement ramps.** "Agreed, and," "Agreed on the hygiene," "Agreed that" as the hinge into a sentence, and a batch of replies where more than one opens on agreement. Rock's own agreement is a short reaction he'd say out loud ("Yep." "100%."), used once. Open on the angle instead. The linter flags these as H-AGREE-RAMP and H-AGREE-REPEAT.
- **"Let's" openers.** "Let's explore," "Let's take a look," "Let's break this down." Filler that delays the point. Start with the point.
- **Rhetorical-question openers.** "But what does this mean for you?", "So why should you care?", "What's next?" used as section transitions. If you know the answer, say it.
- **Reasoning-chain artifacts.** "Let me think step by step," "Breaking this down," "First, let's consider." Scaffolding leaking into prose. State the conclusion, then the evidence.
- **Generic conclusions.** "The future looks bright," "Only time will tell," "As we move forward." Cut. If the piece needs a close, make it specific to the argument.
- **Generic future-narrative closers.** "May become one of the most important narratives of the next cycle," "is poised to become the defining trend of the decade." Grammatically a prediction, but no testable content. Pick the falsifiable version or cut.
- **Motive narration and invented gates at the end.** "Wanted you to hear it from me first," "Didn't want this to catch you off guard," "Figured you'd want to know," "Flag anything I should know first." The first three explain why the message exists and the last adds a review step the writer never set. End on the last fact or the next action. A closing offer the writer actually makes ("Let me know if you need anything." "Happy to hop on a call.") stays.
- **Emotional flatline.** "What surprised me most," "I was fascinated to discover," "the most interesting part," and the header form "Interesting thing here:". If the thing is surprising, the reader should feel it from the content. Cut the claim and present the thing.

### Significance and analysis padding
- **Significance inflation.** "Marking a pivotal moment in the evolution of," "a watershed moment for the industry." State what happened and let the reader judge. If the sentence still works after you delete the inflation clause, delete it. Same family: "stands as," "is a reminder of," "plays a vital role," "setting the stage for," "shaping the future of," "focal point," "indelible mark." The smaller version concedes that the subject is minor and then inflates it anyway.
- **Superficial -ing analyses.** Strings of participles posing as analysis: "symbolizing a shift, reflecting years of investment, showcasing a new era." These say nothing. Replace with specific facts or cut. Same move without the -ing: "this represents a broader shift," "it speaks to a larger trend." The result flavor counts too: "encrypts data at rest, ensuring compliance," "enabling faster response." Give the result its own sentence and verb.
- **Promotional language.** Tourism-brochure prose: "nestled in the breathtaking foothills," "a vibrant hub of innovation." Plain description instead. If you would not say it in conversation, cut it.
- **Credentials as proof.** "Featured in," "profiled in," "maintains an active social media presence," "a leading expert." A list of outlets belongs in a bio. Anywhere else, use what the source said.
- **Novelty inflation.** Treating an established concept as if the subject invented it: "he introduced a term I hadn't heard," "a failure mode nobody talks about." Describe what the person did with the concept. Also flag invented labels coined mid-sentence and never defined ("the supervision paradox"): define the term or describe the mechanism.
- **Speculative gap-filling.** When the model lacks a fact it fills the gap with hedged filler dressed as background: "maintains a relatively low profile," "likely began his career in," "appears to have studied." Guesses formatted as statements. Cut, or replace with a sourced fact. Worse than a cutoff disclaimer because the reader cannot tell what is known from what is invented.

### AI-tool fingerprints
These are near-proof and need no stylistic judgment. The presence of the token is the signature regardless of how the surrounding prose reads.
- **Cutoff disclaimers.** "As of my last update," "I don't have access to real-time data," "while specific details are limited based on available information." Find the information or remove the hedge. Never publish a sentence admitting the writer didn't look something up.
- **Unfilled placeholders.** `[Your Name]`, `[INSERT SOURCE]`, `[Describe the section]`, `2025-XX-XX`, `<!-- add citation -->`. Fill in with real content or delete the sentence. Carve-out: `[ROCK: ...]` is a deliberate open ask that coffee-peer-voice leaves when it lacks a real detail. Report it under its own heading and leave it in place.
- **Chatbot citation markup leaks.** `citeturn0search0`, `contentReference[oaicite:0]{index=0}`, `oai_citation`, `[attached_file:1]`. Strip every token. If a citation was meaningful, replace it with a real reference.
- **AI-tool URL parameters.** `utm_source=chatgpt.com`, `utm_source=copilot.com`, `utm_source=claude.ai`, `utm_source=perplexity.ai`, `referrer=grok.com`. Strip the parameter, keep the URL if the link matters.

### Social-post tells (LinkedIn, X)
- **Hashtag stuffing.** A trailing block of six or more hashtags mixing a specific tag with broad category tags (#AI #Cybersecurity #Innovation #FutureTech #Technology) reads as bot output, and organic engagement plateaus past three to five. Cut to two or three specific tags, or none.
- **Social endorsement closers.** "This one is worth your time:", "must-read," "don't sleep on this," "bookmark this," "thank me later." Performs a recommendation without giving a reason to click. Say what the thing is and who it's for, then drop the CTA.
- **Bullet lists of bare noun phrases.** Five or more short adjective-plus-noun items with no verb ("Stable performance / Reliable connectivity / Optimized throughput"). Reads as a one-pager because that's the shape LLMs default to. Convert to prose, or rewrite each item as a full claim with a number. Carve-out: genuine list content (changelogs, parameter docs) where bare noun phrases are correct.

### Rhythm and uniformity
Structure is the strongest detection signal. Detectors weight structural regularity higher than vocabulary, so if you fix every flagged word but leave the rhythm metronomic, the text still reads as AI.
- **Sentence-length uniformity.** If most sentences run 15 to 25 words, it sounds robotic. Mix short complete sentences with longer ones that run 20 words or more, and get the variation from clause count. Never recommend fragments as the fix, because coffee-peer-voice treats a stack of fragments as its most common failure and this skill runs as its detector.
- **Paragraph-length uniformity.** If every paragraph is three to five sentences of the same size, vary it. Some should be one sentence. Some longer.
- **Read-aloud test.** If a text-to-speech engine could read it without sounding odd, it is probably too uniform. Human writing resists robotic delivery.
- **Missing first person.** Where the genre carries a voice, the absence of "I think," "in my experience," or a stated preference is itself a tell. AI is relentlessly neutral.
- **Over-polishing.** Sanding away every irregularity pushes writing back toward the AI profile. Keep natural disfluency and uneven pacing. Do not create the uniformity you are trying to remove.

### Shape tells (SlopShape)

SlopShape (Madler, arXiv:2609.15369v3, September 28, 2026, release package at github.com/pulse-energy-eu/slopshape) scored 2,250 pre-ChatGPT company blog posts and 11,250 AI rewrites of the same briefs from five models against 176 structural features, with the wording features stripped out. Structure alone separated them at 97.0 macro-F1 on companies held out of training. When each model reworded its own posts span by span, replacing about 73% of their 13-word sequences, structural detection only fell to 96.1. Word-level cleanup alone leaves the shape in place, and the shape is what a structural reader keys on.

Ten feature values carry 25.6% of the classifier's attribution, and those nine features alone detect at 90.1 macro-F1. The paper calls the AI version "the tidy, self-announcing blog post." Each value below has the gap between the human rate and the average AI rate from the paper's Table 6, and the linter rule that approximates it:

| Shape | Leans | Gap | Linter |
|---|---|---|---|
| Ends by restating the thesis or reframing it | AI | 0.650 | H-SHAPE-RECAP, A-SHAPE-RECAP, A-SHAPE-RESTATE |
| Has a summary or synthesis stage | AI | 0.609 | H-SHAPE-RECAP |
| Sends the reader nowhere beyond the post | AI | 0.592 | A-SHAPE-NOROUTE (blog only) |
| No legacy-versus-modern contrast | human | 0.497 | H-SHAPE-ERA, A-SHAPE-LEGACY, A-SHAPE-NEXTGEN |
| No thesis or roadmap before the first section | human | 0.419 | H-SHAPE-ROADMAP, A-SHAPE-ROADMAP |
| Modern or next-generation framing | AI | 0.360 | H-SHAPE-ERA, A-SHAPE-NEXTGEN |
| Credibility from a confident institutional voice | AI | 0.347 | A-SHAPE-INSTITUTIONAL |
| Explains a mechanism as its own stage | AI | 0.285 | none (no reliable regex) |
| Refers to a historical date or period | human | 0.283 | A-SHAPE-NODATE |
| Runs under 800 words | human | 0.274 | none (Rock's posts already do) |

The paper also measured rarity: each post's mean distance to its 25 nearest neighbors in the standardized feature space, as a percentile. Human posts averaged the 83.5th percentile and AI posts the 43.6th (Cohen's d 1.80), and the human post was the rarest of its six-version group 85.6% of the time against a 16.7% chance rate. A human writer's shape is unusual, and the five models crowd the same few shapes. When three or more AI-leaning shape families fire in one draft, the linter reports A-SHAPE-MODAL, and the fix is a new skeleton, since swapping words leaves it in place.

Read these findings with three limits in mind. The paper studied B2B blog posts, so the transfer to Slack, email, and LinkedIn comments is an inference. The paper's features were judged by an LLM, and these regexes approximate that judge without validation against its labels, which are gated.

The paper did not test Pangram, and its own word-level baselines (a fine-tuned ModernBERT and a stylometric classifier) caught unedited AI posts perfectly. Rock's test on November 6, 2026 matched that. pangram-4 scored all 20 Claude-written drafts in it as fully AI, ten of them HARD-clean under slop_lint 1.6.0, and it scored two of his LinkedIn posts from 2020 and 2021 as fully human. A clean audit from this skill means the mechanical tells are gone. It tells you nothing about a detector's call.

### When to rewrite from scratch vs patch
If the text has five or more flagged vocabulary hits across multiple categories, three or more distinct pattern categories triggered, and uniform sentence and paragraph length, patching individual phrases will not fix it. The structure is machine-generated. Advise a full rewrite: state the core point in one sentence, then rebuild.

## Severity tiers

Triage a large document by tier.

**P0, credibility killers, fix immediately.** Cutoff disclaimers, chatbot artifacts, vague attributions without sources, significance inflation on routine events, AI-tool fingerprints, hashtag stuffing on professional posts.

**P1, obvious AI smell, fix before publishing.** Tier 1 word hits, praise labels, ranking verdicts, agreement ramps and repeated agreement openers, the 1.6.0 register rules (pointer sentences, deliverable labels, volunteered disclaimers, performative hedges, topic-label clauses, point-back openers, countdowns, board-spend claims, unnamed sources, engagement prompts), the SlopShape modal shape, template and slot-fill phrases, "Let's" openers, synonym cycling, formulaic openings, bold overuse, em dash frequency, future-narrative closers, motive-narration and invented-gate closers, hedge-stacked predictions, real/actual inflation, bare-noun-phrase bullet lists, dash stand-ins and semicolons, the reversed antithesis at a paragraph end, the concessive frame, the false range, editorial section headers, metaphor and cliche.

**P2, stylistic polish, fix when time allows.** Generic conclusions, rule of three, uniform paragraph length, copula avoidance, transition phrases, credentials lists, result participle tails.

Use P0 plus P1 for a quick pass. A full audit covers all three.

## Context profiles

Adjust strictness to the audience. If none is given, infer it: short plus hashtags means social, code blocks mean technical, a salutation means email, otherwise treat it as a blog post at full strength. If auto-detection feels wrong, say which profile you are using and why.

- **LinkedIn / social.** Relax em dashes (two is fine), bold hooks, one rhetorical question, and emoji at end of line. Some sell is expected. Still strict on hashtag stuffing and endorsement closers.
- **Blog.** Default. All rules at full strength.
- **Technical (docs, architecture, APIs).** Technical terms get a pass: `robust`, `comprehensive`, `seamless`, `ecosystem`, `leverage`, `facilitate`, `underpin`, `streamline` when they carry real technical meaning. Still flag `delve`, `tapestry`, `embark`, `testament to`, `game-changer`. "May" and "could" are accurate hedges here. Fragments and terse feature lists are the correct register.
- **Board / executive brief.** Tighten everything. Promotional language and significance inflation are the biggest risks, so flag even borderline instances. A single "thriving ecosystem" can undercut the whole memo.
- **Casual (Slack, internal notes, quick replies).** Catch only the worst offenders (P0). Preserve the writer's typos, contractions, and idiosyncratic capitalization, because smoothing them erases the fingerprint that marks the text as theirs.

## Self-reference escape hatch

When the text is about AI writing patterns (a blog post, a tutorial, this file), quoted examples are exempt. Text inside quotation marks or code blocks, or explicitly marked as illustrative ("for example, AI might write..."), is not a tell. Flag only patterns in the author's own prose.

## Output format

### Rewrite mode (default)
1. **Issues found.** Every tell identified, with the offending text quoted, grouped by severity.
2. **Rewritten version.** The full clean text. Preserve the original structure, intent, and every specific technical detail. Change only what the rules require.
3. **What changed.** A short summary of the meaningful edits.
4. **Second-pass audit.** Re-read your own rewrite from section 2. Catch tells that survived: recycled transitions, lingering inflation, copula swaps that snuck through. Fix them inline and note what changed. If it is clean, say so.

### Detect mode
1. **Issues found.** Every tell, with the text quoted, grouped by severity (P0, P1, P2).
2. **Assessment.** For each flag, whether it is a clear problem or a judgment call. Some AI-associated patterns are effective writing in small doses. Call out which flags to definitely fix vs which are worth a second look but may be fine. If the text is clean, say so.

### Edit mode
1. **Edits made.** A bulleted list, each with the file location and the before to after. Only the spans you touched.
2. **Verification.** Confirm you re-read the file and the flagged patterns are resolved. Note anything you left alone because it was already human or intentional.

## After the strip: putting a voice back

Removal is half the job. A rewrite that clears every flag but reads sterile, with even sentence lengths and no stance, is still recognizably machine output. For encyclopedic, technical, or legal text, neutral and plain is the correct human voice, so leave it neutral. For anything that carries a voice (posts, essays, personal writing), the second half of the work is putting a voice back on purpose, and that is a different skill. Hand off to `coffee-peer-voice` for the warm, first-person, this-is-how-Rock-talks pass. Keep the two jobs separate. This skill removes the machine tells, and that skill adds the writer's voice.

The chain also runs the other way. As of coffee-peer-voice v1.5, that skill calls this one in **detect mode** on its finished draft, before its own read-back pass. When you are invoked that way, flag and stop. Do not rewrite, and do not touch the voice: the caller fixes its own flagged spans in its own register, which is what keeps the mechanical-scrub failure mode out of voiced prose. Detect is the only mode that is safe to run inside another skill's pipeline. As of coffee-peer-voice v1.7, that skill runs `scripts/slop_lint.py` first and uses detect mode for what the script cannot see.

## Attribution and license

The pattern catalog and the tiered word table here are adapted from **avoid-ai-writing** by Conor Bronsdon (v3.18.0), used under the MIT License. Source: https://github.com/conorbronsdon/avoid-ai-writing. This scoped adaptation drops the upstream crypto and web3 vocabulary, the bundled JS detector, and the voice profiles, and retunes the context profiles for security, standards, and executive writing. Version 1.2 restores a bundled detector as `scripts/slop_lint.py`, written for this adaptation in Python with the standard library only. Upstream credits its own research to Pangram Labs, Wikipedia's Signs of AI writing, and the humanizer skill ecosystem.

MIT License applies to this file as an adaptation. Retain this notice on redistribution.