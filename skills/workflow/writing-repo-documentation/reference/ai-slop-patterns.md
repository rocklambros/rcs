# AI-Slop Pattern Catalog

Reference for `writing-repo-documentation`. Each entry lists a pattern, a concrete substring, the substitution, and a one-line reason. Examples that contain the bad pattern are quoted; do not strip the quotes when applying the substitution to your own draft, only when applying it to the live prose.

## How to use this catalog

1. Read each pattern's "match" column. If your draft contains that pattern, mark it.
2. Apply the substitution. The substitution preserves the information; it strips the noise.
3. The reason column tells you why the pattern signals AI authorship (or generic-corporate authorship). Knowing why prevents the same pattern from reappearing in the next paragraph.

This catalog complements two upstream sources: the global `~/.claude/CLAUDE.md` style rules (em-dashes, semicolons, sentence-initial conjunctions, the slop-word list) and the Wikipedia page on signs of AI writing (which adds bulleted-prose habit, emoji decoration, and heading sprawl). When the catalog disagrees with either source, defer to the source.

## Family 1: Marketing superlatives

| Match | Substitute with | Reason |
|---|---|---|
| "comprehensive solution" | name the actual scope ("library for X", "CLI for Y") | "Comprehensive" is unverifiable; the reader cannot test whether the project is comprehensive without using it |
| "powerful" | name the actual capability | A reader cannot evaluate "powerful" without trying; the word is filler |
| "robust" | name the specific property (handles malformed input, recovers from network errors, etc.) | "Robust" is what a project should be, not what a project should claim to be |
| "seamless" | describe the actual integration steps | If integration is seamless, the description of the steps will demonstrate it |
| "state-of-the-art" / "cutting-edge" | name the technique ("backdoor-criterion adjustment", "TPE sampler") | A named technique is verifiable; an adjective is not |
| "transformative" | delete; describe the actual change in behavior | Reserved for revolutions, not libraries |
| "next-generation" | name what generation came before and what changed | A reader without the prior context cannot evaluate the claim |
| "best-in-class" | give the comparison with named alternatives | A claim without a comparison is marketing |
| "industry-leading" | delete; the project's actual results speak louder than the adjective | If the results are good, name them; if they are not, the adjective will not help |
| "world-class" | delete | A project is not improved by adjectives without referents |

## Family 2: Metaphor clichés

| Match | Substitute with | Reason |
|---|---|---|
| "embark on a journey" | "this tutorial walks through X" | "Embark on a journey" is a meme of AI writing; readers have learned to spot it |
| "delve into" / "dive into" | "examines" or "covers" | "Delve" is statistically over-represented in LLM output |
| "rich tapestry of" | name the specific things being woven | "Rich tapestry" is filler; the next noun usually carries the meaning alone |
| "in the ever-evolving landscape of X" | delete the framing; start with the next concrete sentence | The framing adds no information |
| "in today's fast-paced world" | delete | The reader knows what world they live in |
| "the world of X" | "X" | The "world of" framing adds nothing |
| "navigate the complexities of" | name one specific complexity | "Navigating complexities" is hand-waving |
| "unlock the potential of" | name what the unlocked thing does | "Unlock" is corporate magic; the reader wants the action |
| "harness the power of" | "use" or "call" | "Harness" is a stagecoach verb |
| "empowers users to" | "lets users" or just describe the action | "Empower" is corporate flattery |

## Family 3: Hedge filler

| Match | Substitute with | Reason |
|---|---|---|
| "it's worth noting that" | delete; start with the next clause | If it is worth noting, the noting is the point |
| "it's important to note that" | delete; same reason | The reader will weight what they read; do not pre-weight it for them |
| "it should be remembered that" | delete | The reader is the one remembering |
| "ultimately" | delete | If a conclusion is the conclusion, it does not need a label |
| "in essence" | delete; rewrite the sentence to be the essence | "In essence" usually precedes a restatement of the previous sentence |
| "in conclusion" / "in summary" | delete at start of section; rewrite the sentence | "In summary" without a long preceding section is filler |
| "needless to say" | delete | If it is needless, say nothing |
| "truly" / "really" / "actually" / "very" | delete | Empty intensifiers per the global style rules |
| "as previously mentioned" | delete or write the specific reference ("see § Install above") | Vague back-references annoy readers |
| "the following" | delete; the colon already signals what follows | "The following" before a list is a meme |

## Family 4: Formatting tics

| Match | Substitute with | Reason |
|---|---|---|
| em-dash ( — ) | comma or period | Em-dashes are a Claude-family habit; CLAUDE.md forbids them |
| semicolon ( ; ) in prose | period and a new sentence | Same as above; CLAUDE.md forbids them in prose |
| sentence-initial "And" / "But" / "Or" | reword the sentence to start with a noun or a verb | CLAUDE.md style rule; signals casual / blog-post register where formal documentation register is wanted |
| bulleted prose (three sentences turned into three bullets) | run them together as a paragraph | If reading the bullets aloud sounds like a sentence read in chunks, they are a sentence |
| heading sprawl (five one-line sections in a row) | collapse the one-liners into a paragraph under a single heading | A heading promises a meaningful subsection |
| emoji decoration (🚀, ✨, 🎯 prepended to sections) | use markdown headings without the decoration | Emoji-as-bullet is a blog-post move; project docs hold up better without them |
| over-use of bold | bold only the term being defined; never bold whole sentences | When everything is bold, nothing is bold |
| over-use of code-fences for single words | use backticks (`code`), not fenced blocks, for inline terms | Fenced blocks are for multi-line snippets |
| markdown tables for two-row data | use two sentences | A two-row table is harder to read than the prose that would replace it |

## Family 5: Faux-balance

| Match | Substitute with | Reason |
|---|---|---|
| "while X has its critics, others argue..." | take a position; name the strongest counter directly | False balance dilutes the actual argument |
| "on the other hand" used as a default conjunction | use only when actually presenting a counter-position | Overused, it signals stalling |
| "there are pros and cons" without listing them | list the pros, list the cons, take the position | A claim without the table is a non-claim |
| "it depends" with no follow-up | name the variables it depends on | "It depends" is correct but useless alone |
| "some experts say... while others say..." with no named experts | name the experts or the source documents | Unsourced both-sidesing reads as AI hedge |

## Family 6: Sycophantic openers

| Match | Substitute with | Reason |
|---|---|---|
| "Let's dive in!" | delete; the next concrete sentence is the start | The reader is already reading; they do not need to be invited |
| "Let's explore" | delete; describe what is being explored directly | "Let's" frames the reader as a passive companion |
| "Great question!" | delete | A README does not respond to questions |
| "Certainly!" / "Of course!" | delete | Same reason |
| "I'd be happy to help you with..." | delete; this is documentation, not a chat | Removes the chat-assistant register |
| "this article will cover..." | delete the meta-sentence; structure the cover with headings | A document's structure tells the reader what it covers |
| "join us on a journey" | delete | "Journey" as metaphor is forbidden by the global style rules anyway |

## Family 7: Self-reference

| Match | Substitute with | Reason |
|---|---|---|
| "this document" / "this article" / "this README" | use the heading structure to refer to sections | Self-reference is a tic that breaks the reader's flow |
| "we will now examine" | restructure as a heading | The heading IS the announcement |
| "as you can see" | delete | If the reader can see, they see; if they cannot, the phrase will not help |
| "as we discussed" | name the specific reference or delete | Vague back-references annoy readers |
| "in this section" | delete; the heading establishes the section | Redundant |

## Family 8: Voice and tone drift

| Match | Substitute with | Reason |
|---|---|---|
| First-person "we" in a single-author project | recast in third person or describe the action | "We" without a referent group is a tic |
| Drift between "you" and "the user" within one section | pick one and hold it | Voice drift is a cold-read failure |
| Mid-doc switch from imperative ("Install with...") to declarative ("Users install with...") | pick one and hold it | Same as above |
| Title Case Sentence Headings | sentence case | Title-case sentence headings are a corporate-template tic |
| Exclamation marks in headings or section bodies (other than warnings) | delete | Exclamation marks signal marketing register |

## After the audit

When the catalog is walked end to end, the draft will be measurably shorter and measurably more informative. The substitution is not stylistic preference; it is information density. If a phrase can be deleted without losing meaning, it was carrying no meaning and was noise. The reader's attention is the constraint being optimized.

The Wikipedia article on signs of AI writing covers patterns not catalogued here (citation-fabrication tics, faux-quotation marks, list-of-three-with-final-being-the-real-point). Read it once and add to this catalog any pattern that surfaces in your own drafts.
