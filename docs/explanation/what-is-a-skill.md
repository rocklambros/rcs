# What is a skill

The concept, not the recipe. For the recipe see [`docs/how-to/contribute-a-skill.md`](../how-to/contribute-a-skill.md).

## The shortest definition

A skill is a markdown file with structured frontmatter that Claude reads when a relevant question comes up. The frontmatter says when to consult the file; the body says what to do.

## What a skill is not

A skill is not a function. It does not execute. It does not have inputs and outputs in the program-input-output sense. It is text that Claude consults the way a doctor consults a clinical guideline before treating a patient: the text is not the treatment, but the treatment is shaped by the text.

A skill is not a prompt template. A prompt template is a fill-in-the-blank text that a developer instantiates and sends to a model. A skill stays inert until Claude reads a user's actual question, decides the skill is relevant, and applies the discipline the skill encodes. The developer does not invoke it.

A skill is not a tool. Tools are functions Claude can call. A skill is text Claude can read. Some skills describe how to use tools, but the skill itself is documentation.

A skill is not memory. Memory persists information about a specific user, project, or conversation across sessions. A skill is the same for every user; it encodes a discipline, not a fact.

## Why skills exist

The same discipline gets rebuilt every project. A data scientist remembers, eventually, that adjusting for a mediator biases the total effect estimate. A security engineer remembers, eventually, that running an MCP server without auditing its network egress is a supply-chain risk. A statistician remembers, eventually, that a p-value without an effect size is not a finding. Every practitioner who has worked in a domain for years has a few hundred such disciplines.

The skill format captures one such discipline as text Claude can apply on behalf of anyone, regardless of whether the person asking knows the discipline exists. The data scientist who has never heard of the backdoor criterion still gets the right adjustment set, because the skill carries that knowledge and Claude carries the skill.

## What a skill contains

Every skill in RCS has the same shape, enforced by `tools/lint_skill_md.py`:

1. **Frontmatter** with eight required fields. The two that drive discovery are `name` (the slug) and `description` (the text Claude reads to decide whether to load the skill on a given turn).
2. **Eleven required H2 sections in order**: When to use, When NOT to use, Quick start, Inputs / Arguments / Flags, Workflow, Outputs, Failure modes, References, Examples, See also, Status & version.

The structure is enforced because Claude's ability to find and apply the skill depends on it. A skill with no `When NOT to use` section will engage on cases it should refuse. A skill with no `Failure modes` section will not catch its own anti-patterns. The contract is non-negotiable.

## How Claude finds a skill

When a Claude Code session starts, the runtime scans `~/.claude/skills/` and reads the frontmatter of every skill it finds. The frontmatter `description` field becomes part of Claude's system context for that session, labeled with the skill's slug.

When a user sends a message, Claude scans its loaded skill descriptions to see which ones match. A match is fuzzy: the question does not need to use any specific words from the description. The description is written third-person so the matching happens reliably ("triggers whenever the user reports a t-test result..." matches better than "I can help you with t-tests").

If a skill matches, Claude reads the full SKILL.md body before answering. The body's `Workflow` section gives the steps; the `Failure modes` section names what to refuse. Claude follows the body the way it would follow any other instruction in its context.

## How a skill differs from a slash command

A slash command is invoked by name (`/sc:analyze`, `/run`, `/init`). A skill is invoked by relevance to the question. The two formats coexist; some functionality is better as a command (rare, explicit, parameterized), and some is better as a skill (frequent, contextual, judgment-based).

The same workflow can sometimes be expressed either way. The choice depends on how often the user wants to opt in. A `/spell-check` slash command makes sense because spell-checking is an explicit action; a `spell-checking` skill would constantly activate on every prose-shaped message, which is wrong.

## What makes a skill good

A good skill is one where:

- The description matches reliably on the questions it should answer and not on the ones it should not
- The workflow is concrete enough that a reader who has never done this before can follow it
- The failure modes name specific anti-patterns the skill catches, with the symptom that triggers each
- The Examples section shows two real cases (happy path and edge case) at minimum
- The skill refuses or hands off when out of scope, instead of attempting a poor version of someone else's job

A bad skill is one where the description is vague (it activates too often), the workflow is abstract (Claude cannot follow it), or the failure modes are absent (the skill produces confidently-wrong answers).

The RCS catalog has 104 shipped skills. Each one was evaluated against 3 scenarios (happy, edge, anti-trigger) before earning `status: shipped`. The evaluation is not "is this beautifully written" but "does Claude do the right thing when this skill is loaded and a user asks the relevant question". The skill works when the answer changes for the better.

## Where the format comes from

The skill format comes from Anthropic's [Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) document. RCS extends the Anthropic-required `name` and `description` fields with six more (`version`, `status`, `track`, `audience`, `evidence`, `last-updated`) that the lint enforces. The 11 required H2 sections are RCS-specific; the Anthropic spec only requires the frontmatter. The RCS additions are documented in [`docs/conventions.md`](../conventions.md).

The format works across hosts. The same `SKILL.md` file is loaded by Claude Code, Copilot CLI, Gemini CLI, and the Anthropic API. Different hosts may scan different directories or use different invocation conventions, but the file's contents are portable.

## Further reading

- [`docs/explanation/sigma-score.md`](sigma-score.md) — the ROI metric in every catalog row
- [`docs/explanation/pragmatic-discipline.md`](pragmatic-discipline.md) — how skills are validated before they ship
- [`docs/conventions.md`](../conventions.md) — the frontmatter and section spec
- [`docs/eval-protocol.md`](../eval-protocol.md) — the eval scenario schema and pass thresholds
- [`docs/how-to/contribute-a-skill.md`](../how-to/contribute-a-skill.md) — the recipe for adding your own
