---
name: writing-repo-documentation
description: >
  Writes a project's human-authored documentation (README, CONTRIBUTING,
  SECURITY, docs/, wiki) as a teaching artifact that takes the reader from
  a first-glance question to a confident contributor. Walks five steps:
  identify the audience hierarchy (novice, regular user, contributor,
  maintainer), map the document hierarchy (which file at which scope),
  draft the README spine, layer a novice-to-advanced progression within
  each document, and self-audit against the AI-slop pattern catalog in
  reference/. Use when starting a new public repo, when the README is
  stale or marketing-flavored, when contributors keep asking the same
  onboarding questions, when novices bounce off the first paragraph, or
  when refreshing docs before an open-source release or audit. Refuses
  to generate API reference from docstrings (Sphinx, pdoc, TypeDoc, or
  rustdoc are the right fit) and refuses to draft documentation without
  a concrete project context to ground the prose.
version: 0.1.0
status: shipped
track: workflow
audience:
  - data-scientist
  - ml-engineer
  - security-eng
  - skill-author
  - devops
evidence:
  - RCS-root-readme
  - genai_agentic_incidents
  - llm-safety-alignment-study
  - DU-MSDSAI-4441-Final
last-updated: 2026-05-24
---

# Writing Repository Documentation

## When to use

Trigger this skill when any of the following describes the situation:

- A new public repository is going up and there is no README yet
- The README opens with promotional language ("powerful", "comprehensive", "seamless solution") rather than what the project does
- New contributors keep asking the same onboarding questions in issues or chat
- A novice opened the README, scrolled, and closed the tab without trying anything
- An open-source release, an audit, or a hand-off is scheduled and the docs were last touched a year ago
- The README is a wall of API tables with no narrative path through them
- A CONTRIBUTING.md or SECURITY.md is missing in a repository that accepts outside contributions or handles sensitive data
- A new docs/ subdirectory needs structure (where do tutorials go, where do explanations go, where does reference go)
- A wiki page is requested and there is no editorial standard for what goes in the wiki versus in the repo itself

This skill applies across forges: GitHub, GitLab, Gitea, Codeberg, Forgejo, self-hosted. The conventions are forge-neutral. The file names and the rendering pipeline differ slightly per forge but the structure does not.

## When NOT to use

Skip this skill and hand off when:

- The user wants API reference generated from docstrings. That is the job of Sphinx (Python), pdoc (Python), TypeDoc (TypeScript), rustdoc (Rust), or godoc (Go). Reference auto-generation is a different category of work because the source of truth is the code, not the prose. Hand off and recommend the appropriate generator
- The user wants a one-page CLI script documented inline. A 30-line script gets a top comment, not a README
- The user wants internal-only documentation living in a private wiki with no external audience. Internal docs have different conventions (lighter on first-time-reader scaffolding, heavier on cross-team handoffs)
- The user wants design proposals, RFCs, or architecture decision records (ADRs). Those have their own templates and lifecycle. ADRs in particular are append-only and dated. This skill writes living documents
- The user wants academic-paper writing. That has its own form (abstract / intro / related work / method / results / discussion) and a different audience contract
- A draft already exists and the user only wants line-level proofreading. That is editing, not authoring. This skill walks structure first. Line-level edits are a sub-step of the larger workflow

## Quick start

User says: "I am open-sourcing `causalgraph`, a small Python library that estimates causal effects from observational data via DAG-based adjustment. Write the README."

The five-step walk:

1. **Audience hierarchy** (60 seconds). Four tiers for almost any project: novice (has not used the tool, may not know the field), regular user (uses the tool, may not contribute), contributor (sends PRs), maintainer (owns releases). For `causalgraph`: novice is a data scientist new to causal inference. Regular user is a practitioner running observational studies. Contributor adds estimators. Maintainer cuts releases.
2. **Document hierarchy** (90 seconds). README is the front door for novice + regular user. CONTRIBUTING is for contributors. SECURITY is for anyone reporting a vulnerability. `docs/` is the place for material that does not fit in a README (tutorials, conceptual explanations, the underlying math). A wiki is for material that updates faster than the code (changelogs of external dependencies, third-party integrations).
3. **README spine** (10 minutes). Six sections in this order:
   1. One-sentence what + one-sentence why-you-care
   2. A 30-second concrete example (runnable, copy-pasteable, no setup beyond install)
   3. Install
   4. A second example that shows one step deeper
   5. Concepts (the vocabulary needed to read the rest)
   6. Where to go next (link to `docs/tutorials/`, `docs/explanation/`, `docs/reference/`, CONTRIBUTING, the issue tracker)
4. **Layer the novice-to-advanced rungs** (15 minutes). Within each section, lead with the concrete and follow with the abstract. The novice reads sections 1 through 3 and stops with a working install. The intermediate reader reaches section 5 and now has the vocabulary. The advanced reader follows the `docs/` links.
5. **Self-audit** (5 minutes). Walk the AI-slop pattern list in [`reference/ai-slop-patterns.md`](reference/ai-slop-patterns.md). For each match, apply the substitution in that file. Then do a cold-read test: ask someone who has never seen the project to read the README aloud and stop at the first sentence that confuses them. The first confusion point is the first thing to fix.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| project_path | str | yes | (none) | Filesystem path or repo URL. The skill reads existing files (README, CONTRIBUTING, src/, package metadata) to ground the prose in actual project state, not abstract assumptions |
| audience_tiers | list[str] | no | ["novice", "regular-user", "contributor", "maintainer"] | Which tiers to write for. Drop a tier when the project has no audience there (e.g., a personal-scratch repo may have no contributor tier) |
| scope | "readme-only" \| "readme+contributing" \| "full-hierarchy" | no | "readme+contributing" | Determines which files the skill drafts in one pass. Full-hierarchy adds SECURITY.md and a `docs/` skeleton |
| target_reading_time_minutes | int | no | 5 | The README's first three sections must be readable in this budget at typical reading speed (~250 words per minute). A 5-minute target = roughly 1,250 words for sections 1-3 |
| forge | "github" \| "gitlab" \| "gitea" \| "codeberg" \| "forgejo" \| "other" | no | "github" | Adjusts file names (`.github/` versus `.gitea/`) and rendering conventions (mermaid support varies). Content is forge-neutral |
| existing_draft_path | str \| None | no | None | If provided, the skill audits the draft against the AI-slop catalog and the spine, then rewrites. Otherwise it drafts from scratch |
| diataxis_split | bool | no | true | When `scope` is full-hierarchy, scaffold `docs/` along Diataxis lines (tutorials, how-to, explanation, reference). Some teams prefer a flat `docs/` instead |

## Workflow

Copy this checklist into the response and check off each step as it lands:

```
Repo-documentation progress:
- [ ] Step 1: Identify the audience tiers present in this project
- [ ] Step 2: Map the document hierarchy (file at scope), grounded in the project's actual state
- [ ] Step 3: Draft the README spine (6 sections in order)
- [ ] Step 4: Layer novice → advanced within each section (concrete first, abstract after)
- [ ] Step 5: Draft CONTRIBUTING + SECURITY if scope > readme-only
- [ ] Step 6: AI-slop self-audit against reference/ai-slop-patterns.md
- [ ] Step 7: Cold-read test (a person who has not seen the project reads it aloud. First confusion point is the first rewrite target)
- [ ] Step 8: Cross-link: README → docs/ → CONTRIBUTING → SECURITY (no orphan documents)
```

### Step 1: Audience hierarchy

The default four tiers (novice, regular user, contributor, maintainer) cover most projects. A project may have fewer. A personal-scratch repository has no contributor tier. A closed-source internal library has no novice tier. Knowing the tiers tells the writer which sections to draft and where to stop deepening.

Novice and regular user share the README. Contributor reads CONTRIBUTING. Maintainer reads CONTRIBUTING plus an internal release runbook (often kept in a private location). Security researchers read SECURITY.md. A reader who cannot find the right document on the first try is more likely to give up than to ask, so cross-links between documents matter as much as the documents themselves.

### Step 2: Document hierarchy

| File | Audience | Purpose |
|---|---|---|
| `README.md` | Novice + regular user | What it is, why care, how to install, how to use, where to go next |
| `CONTRIBUTING.md` | Contributor | Development setup, branch + PR conventions, test commands, code style, review process |
| `SECURITY.md` | Security researcher | How to report a vulnerability privately, expected response time, scope, safe-harbor language |
| `CODE_OF_CONDUCT.md` | Contributor + community | Behavior norms, enforcement, contact path |
| `CHANGELOG.md` | Returning user + maintainer | What changed per release, with attention to breaking changes (cross-reference `writing-release-notes-as-postmortem`) |
| `docs/tutorials/` | Novice | Step-by-step learning paths from zero to a working result |
| `docs/how-to/` | Regular user | Recipes for specific tasks ("how do I do X?") |
| `docs/explanation/` | Intermediate user | Concepts, design decisions, the "why" behind the API |
| `docs/reference/` | Power user | Auto-generated API reference (handled by Sphinx, pdoc, etc.) |

The Diataxis framework (Daniele Procida, 2017) names the four `docs/` subtypes and gives clear criteria for which content goes where. Use it as the default structure when full-hierarchy scope is in scope.

### Step 3: The README spine

Six sections, in order:

1. **What it is + why care** (1-2 sentences each, ≤ 50 words total). The first sentence must let a reader who has never heard of the project decide whether to keep reading. Lead with the user benefit, not the implementation
2. **30-second concrete example.** A runnable snippet that shows the project's core action. Install + import + one call + a visible result. No yak-shaving. A reader copies this, runs it, sees the result, and now believes the project works
3. **Install.** One command per supported package manager. Pinned versions documented separately if relevant (cross-reference `pinning-reproducible-environments`)
4. **A second, slightly deeper example.** Same shape as the first, but uses one more concept. This is the rung from "got it running" to "got an idea of what else is possible"
5. **Concepts.** The vocabulary a reader needs to understand the rest of the docs. Define terms inline, not as a glossary appendix (a reader will not flip back). Keep this section short. Deeper conceptual material lives in `docs/explanation/`
6. **Where to go next.** Links to `docs/tutorials/`, `docs/how-to/`, `docs/explanation/`, `docs/reference/`, CONTRIBUTING, the issue tracker, and (if applicable) the chat channel. A reader who has finished the README must know where to go for the next question without searching

What the README does NOT contain at top level: the full API table, the full changelog, the design history, badges that say nothing, a logo above the title that pushes the first sentence off the screen, a table of contents for a document that is shorter than the table of contents.

### Step 4: Layer the novice-to-advanced rungs

Inside each section, lead with the concrete and follow with the abstract. Define terms only when they are about to be needed. Five concrete techniques:

- **Run before define.** Show a working example before introducing the vocabulary. A reader who has run the code will accept a definition. A reader who has not will skim past it
- **One concept per paragraph.** Two new concepts in one paragraph forces the reader to track both at once. Split them
- **Rungs, not ramps.** Give explicit stopping points ("If you only need X, stop here"). Most readers will stop earlier than expected. Named stopping points let them do so without feeling they missed something
- **Promote the link, not the digression.** When a tangent deserves a paragraph, write a sentence and link to the paragraph in `docs/explanation/`. The README stays readable. The deep dive stays available
- **Show the failure mode.** Right after the working example, show one common mistake and what the error looks like. The reader will hit this mistake and now knows the error message before the search engine does

### Step 5: CONTRIBUTING and SECURITY (when scope includes them)

CONTRIBUTING.md sections, in order: (1) development setup (commands, not prose), (2) where the tests live and how to run them, (3) branch and commit conventions, (4) PR template expectations, (5) code style and lint commands, (6) review process and expected response time, (7) release process (if external contributors might cut releases) or a pointer to who owns releases. Cross-reference `writing-vdp-and-coordinated-disclosure` for the disclosure-policy half of SECURITY.md.

SECURITY.md sections, in order: (1) how to report a vulnerability (private channel, not a public issue), (2) what to expect (acknowledgement time, fix-and-disclose timeline), (3) scope (what is in, what is out), (4) safe-harbor language for good-faith research, (5) credits / hall of fame if applicable. See `security/writing-vdp-and-coordinated-disclosure` for the full template.

### Step 6: AI-slop self-audit

Walk the catalog in [`reference/ai-slop-patterns.md`](reference/ai-slop-patterns.md). The catalog is grouped into seven families: marketing superlatives, metaphor clichés, hedge filler, formatting tics, faux-balance, sycophantic openers, and self-reference. For each pattern, the catalog gives a substitution and a one-line reason. Apply substitutions in place. Do not delete the sentence. Rewrite it. Information is being preserved. Only the noise is being stripped.

Two cross-references that complement this catalog:

- The Wikipedia page "Signs of AI writing" lists patterns from a different angle (heading sprawl, emoji decoration, bulleted-prose habit). Read it once
- This repository's `~/.claude/CLAUDE.md` style rules forbid em-dashes, semicolons, sentences starting with conjunctions, and a list of corporate filler words. Apply those rules to documentation too. They were written for code comments and prose alike

### Step 7: Cold-read test

A test for documentation is not a unit test. It is a person who has not seen the project reading the document aloud and stopping at the first sentence that confuses them. The reader does not need to be a domain expert (in fact a non-expert is more useful for the novice tier). Record where they stopped, why, and what they expected to read instead. The first confusion point is the first rewrite target.

A solo author who cannot find a cold reader can approximate the test by reading the document aloud after a 24-hour gap (the gap matters. Fresh eyes substitute for fresh ears). A second approximation is asking a model to read the README and identify the first place a "data scientist who has never used causal inference" would lose the thread.

### Step 8: Cross-link discipline

Every document the project ships must be findable from the README in at most two clicks. A SECURITY.md that lives in the repo root but is not linked from README is functionally invisible. A `docs/explanation/` page that is not linked from a `docs/tutorials/` page leaves the curious reader without a path. Walk every document after drafting and verify the cross-link graph has no orphans.

## Outputs

Concrete artifacts this skill produces:

1. **`README.md`** at the project root, ≤ ~1,500 words for sections 1-3, layered novice-to-advanced
2. **`CONTRIBUTING.md`** at the project root if scope includes contributors
3. **`SECURITY.md`** at the project root if scope is full-hierarchy
4. **`docs/`** skeleton with `tutorials/`, `how-to/`, `explanation/`, `reference/` subdirectories (Diataxis) when `diataxis_split=true` and scope is full-hierarchy
5. **A per-document review checklist** flagging which AI-slop patterns appeared in the draft and which were substituted, so the next author can spot the same patterns themselves
6. **A cross-link map** (text or mermaid) showing how each document points to each other document. Orphan documents are flagged

## Failure modes

- **Promotional opener** ("a comprehensive solution for X"). Strips the first sentence of all signal because the words are generic. Caught by: Step 6 audit against the marketing-superlatives family in the slop catalog
- **Concept overload in paragraph 1.** Introducing three new terms in one paragraph leaves the novice unable to follow. Caught by: Step 4's one-concept-per-paragraph rule
- **No runnable example before the API table.** Forces the reader to build a mental model from the API alone. Caught by: Step 3's mandatory 30-second example as section 2
- **Documentation that ages out silently.** README references a command that was renamed three releases ago. Caught by: a CI check that runs the README's quick-start example in a fresh container as part of release validation. The README example is treated as a smoke test
- **Heading sprawl.** Five sections, each one line long. Caught by: collapse one-line sections into the surrounding prose. A heading is a promise that a meaningful subsection follows
- **Em-dashes, semicolons, "delve into", "navigate the complexities", "in the ever-evolving landscape of...".** All caught by: the AI-slop catalog in `reference/ai-slop-patterns.md`, the global CLAUDE.md style rules, and the Wikipedia article on signs of AI writing
- **Orphan documents.** A SECURITY.md or `docs/explanation/concepts.md` that lives in the repo but is not linked from anything else. Caught by: Step 8 cross-link discipline
- **First-person voice.** README says "We built this to solve X". Reader does not know who "we" is and the phrasing does not survive the project changing hands. Use third person: "The library solves X." Same rule that applies to skill frontmatter applies here
- **Drifting between you-form and one-form.** The README must pick a voice and hold it. Mixing "you can install" and "users install" inside two paragraphs is jarring. Pick second-person ("install with...") and stay there, or pick imperative ("Install with...") and stay there
- **Bulleted prose.** Three sentences turned into three bullets when the sentences are part of one thought. Caught by: read the section aloud. If the bullets sound like a sentence read in chunks, they were a sentence

## References

- [`reference/ai-slop-patterns.md`](reference/ai-slop-patterns.md). 60+ pattern catalog with per-pattern substitution and reason. Covers marketing superlatives, metaphor clichés, hedge filler, formatting tics, faux-balance, sycophantic openers, self-reference
- [`reference/readme-skeleton.md`](reference/readme-skeleton.md). Annotated, copy-pasteable README scaffold for a Python library, with section-by-section notes on what each rung is teaching and what to swap when porting to a different language or domain
- [`reference/document-hierarchy-by-audience.md`](reference/document-hierarchy-by-audience.md). Matrix mapping audience tiers to documents, with file-name conventions per forge and a Diataxis-aligned `docs/` layout
- [Diataxis (Daniele Procida)](https://diataxis.fr/). The four-document framework (tutorials, how-to, explanation, reference) that informs the `docs/` skeleton
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). Independent slop catalog from a different community. Cross-reference for patterns the local catalog may not surface
- [Plain language guidelines (plainlanguage.gov)](https://www.plainlanguage.gov/). Federal-government plain-language standard. Complements the educational-tone goal
- `workflow/writing-successor-primers`. The hand-off counterpart. This skill writes for arriving readers, that one writes for departing authors
- `workflow/writing-release-notes-as-postmortem`. The CHANGELOG counterpart
- `security/writing-vdp-and-coordinated-disclosure`. The SECURITY.md counterpart
- `teaching/writing-onboarding-guide`. The multi-audience onboarding-doc skill for larger launches that span several teams

## Examples

### Example 1: New Python library, README from scratch (happy-path)

Input: "I am open-sourcing `causalgraph`, a Python library that estimates causal effects from observational data via DAG-based adjustment. Write the README."

Output: Step 1 audience tiers. Novice (data scientist new to causal inference), regular user (practitioner running observational studies), contributor (adds estimators), maintainer (cuts releases). Step 2 document hierarchy. README plus CONTRIBUTING plus SECURITY plus `docs/{tutorials,how-to,explanation,reference}`. Step 3 README spine:

1. *What it is + why care.* "`causalgraph` estimates the causal effect of a treatment on an outcome from observational data, by drawing a directed acyclic graph and adjusting for the confounders the graph names. It exists because the standard regression coefficient is biased when the graph has unmeasured paths that observational data alone cannot detect."
2. *30-second example.* Install one line, import one line, define a 4-node DAG one line, call `estimate(...)` one line, print the result. The reader sees `+0.42 [95% CI 0.18, 0.65]` and now believes the library works.
3. *Install.* `pip install causalgraph`. One sentence on Python version requirements.
4. *Second example.* Same shape, but adds a mediator and contrasts total effect with direct effect. The reader now sees that the choice of adjustment set is the load-bearing decision.
5. *Concepts.* Two paragraphs: what a DAG is (one sentence), what the backdoor criterion does (one sentence), why mediator-adjustment biases the total effect (one sentence), what the E-value is and why it ships alongside every estimate (one sentence). No deeper math. Links to `docs/explanation/identification.md` for the formal version.
6. *Where to go next.* Links to the four `docs/` subdirectories, CONTRIBUTING, issue tracker.

Step 6 self-audit catches one phrase ("powerful library for causal inference") and substitutes ("library for causal effect estimation"). Step 7 cold-read by a colleague flags one undefined term in section 5 ("confounder") which gets a parenthetical definition inline. Step 8 verifies every link resolves.

### Example 2: Audit a draft README that has AI-slop patterns (edge-case)

Input: a draft README that reads "**causalgraph** is a powerful and comprehensive solution that empowers data scientists to seamlessly delve into the rich tapestry of causal inference. In this ever-evolving landscape of observational studies, our cutting-edge library leverages state-of-the-art DAG algorithms — providing a robust framework for navigating the complexities of confounding. Let's dive in!"

Output: per-pattern findings table (concrete substring + named slop family + substitution + one-line reason). For this paragraph:

- "powerful and comprehensive solution" → marketing superlative cluster → "library" (the noun does the work. The adjectives signal nothing) → reason: a reader cannot evaluate "powerful" without trying it. The word is filler
- "empowers data scientists to" → empty verb cluster → delete the framing. Lead with the action: "estimates causal effects from observational data" → reason: "empowers" is a verb-as-flattery, not a verb-as-action
- "seamlessly delve into the rich tapestry of" → metaphor cliché + empty intensifier → delete and replace with a concrete domain noun: "for causal inference" → reason: "delve into the rich tapestry" appears in millions of AI-generated documents and signals AI authorship to readers who have learned to spot it
- "In this ever-evolving landscape of" → time-and-place cliché → delete (the sentence works without it) → reason: nothing in the rest of the sentence depends on the landscape framing
- "cutting-edge" / "state-of-the-art" → marketing superlative → delete. Describe the actual technique ("backdoor-criterion adjustment over user-supplied DAGs") → reason: a reader cannot verify "cutting-edge". The named technique is verifiable
- " — " (em-dash) → formatting tic → replace with a comma or a period → reason: em-dashes are a Claude-family habit and a CLAUDE.md-banned character
- "robust framework for navigating the complexities of" → faux-precision filler → "framework that adjusts for measured confounders. Does not adjust for unmeasured confounders, which is the limitation no observational design escapes" → reason: name the limitation, do not hide it behind "navigating complexities"
- "Let's dive in!" → sycophantic-opener cluster → delete (or replace with the start of the next concrete section) → reason: the exclamation mark plus the inclusive "Let's" signals AI authorship. The reader is already reading, they do not need to be invited

Rewritten paragraph: "`causalgraph` estimates causal effects from observational data via DAG-based adjustment for measured confounders. The library does not adjust for unmeasured confounders, which is the limitation no observational design escapes. Every estimate ships with an E-value sensitivity number so the reader can judge robustness."

The information density goes up. The word count goes down by a third. The AI-authored feel disappears.

### Example 3: Auto-generate API reference from docstrings (anti-trigger)

Input: "I have a Python library with type hints and docstrings on every public function. Generate the API reference."

Output: This is API reference generation, not human-authored project documentation. The two are different jobs. Auto-generated reference docs have the source code as their source of truth and update on every commit. Human-authored docs encode editorial decisions the code does not contain (what is teaching content, what is hidden, what example illustrates which concept). Recommended tools by language:

- Python: Sphinx (with autodoc + napoleon extensions) or pdoc. Sphinx is the conventional choice and integrates with `readthedocs.io`. Pdoc is lighter and produces a single static site from docstrings alone
- TypeScript / JavaScript: TypeDoc for TypeScript, JSDoc for plain JavaScript
- Rust: rustdoc (built into the toolchain. `cargo doc` ships it)
- Go: godoc (built in)
- Java: Javadoc (built in)

Set up the tool, point it at the source tree, configure the output directory to `docs/reference/`, and link to it from the README's "Where to go next" section. This skill writes the README and the surrounding tutorials, how-to, and explanation docs. Reference generation belongs to the tool ecosystem the language already has. If the user does not have docstrings yet, that is a different prerequisite: write the docstrings first, then run the generator.

## See also

- `workflow/writing-successor-primers`. Pairs with this skill on the other side of a project hand-off. This one welcomes arriving readers, that one carries the founding-author context forward
- `workflow/writing-release-notes-as-postmortem`. The CHANGELOG counterpart. Reads as a release-by-release postmortem, not a marketing announcement
- `security/writing-vdp-and-coordinated-disclosure`. The SECURITY.md counterpart with full disclosure-policy template
- `teaching/writing-onboarding-guide`. When the audience hierarchy spans several teams (engineer / scientist / executive / security / auditor) and a single README is the wrong shape
- `claude-code-meta/authoring-skill`. The skill-authoring counterpart. Both share the eval-first-then-body discipline but optimize for different audiences (skills are read by an LLM. Project docs are read by a human)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-24
