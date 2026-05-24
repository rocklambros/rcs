# README Skeleton

Annotated, copy-pasteable scaffold for a project README. Written for a small Python library so the examples are concrete; swap the language-specific bits when porting to a different ecosystem.

The skeleton follows the six-section spine from `SKILL.md`. Each section carries a note in italics explaining what the section is teaching and why it comes at that position in the document. Strip the italic notes when publishing.

---

```markdown
# projectname

One sentence describing what the project is. A second sentence describing why
a reader who has never heard of it should care. Total: under 50 words.

*Note: this is the only paragraph most novice readers will read in full before
deciding to keep going. Lead with the user benefit, not the implementation.
Avoid adjectives that cannot be verified by trying the project.*

## Quick example

```python
import projectname

result = projectname.do_the_thing(input_data)
print(result)
# expected output: ...
```

*Note: copy-pasteable. No yak-shaving. The reader runs this, sees the expected
output, and now believes the project works. The example must run against the
default install with no further setup. If it cannot, the example is wrong;
either shrink the example or move the setup into the install section.*

## Install

```bash
pip install projectname
```

Requires Python 3.10 or newer.

*Note: one command per supported package manager. Pinned versions get a separate
sentence if relevant; do not derail the first-time reader with lockfile
discipline here (link out to `docs/how-to/pinning.md` if applicable).*

## A second example

```python
import projectname

# Same shape as the first example, but introduces one more concept.
result = projectname.do_the_thing_with_options(
    input_data,
    option_that_introduces_a_concept="value",
)
print(result.summary())
```

*Note: this is the second rung of the novice-to-advanced ladder. The reader
sees that the API is consistent, learns one more knob, and now has a sense of
what else is possible. Avoid jumping to advanced material; that lives in
docs/explanation/.*

## Concepts

A directed acyclic graph (DAG) is a set of nodes with directed edges and no
cycles. `projectname` uses DAGs to encode the user's hypothesis about which
variables cause which other variables; the library then estimates effects
along the paths the DAG names.

A confounder is a variable that affects both the treatment and the outcome.
The backdoor criterion identifies which confounders must be adjusted for to
estimate a causal effect from observational data.

*Note: define vocabulary only when about to be needed. Inline definitions, not
a glossary appendix. Keep this section short; deeper conceptual material lives
in docs/explanation/. The novice does not need the full theory to use the
library; they need just enough vocabulary to read the next section.*

## Where to go next

- [Tutorials](docs/tutorials/) — guided learning paths from zero to a fitted model
- [How-to guides](docs/how-to/) — recipes for specific tasks ("how do I do X?")
- [Concepts and design](docs/explanation/) — the math behind the API and why the API is shaped the way it is
- [API reference](docs/reference/) — auto-generated from docstrings via pdoc
- [Contributing](CONTRIBUTING.md) — development setup, PR conventions, test commands
- [Security policy](SECURITY.md) — how to report a vulnerability privately
- [Issue tracker](https://github.com/example/projectname/issues)

*Note: a reader who has finished the README must know where to go for the next
question without searching the repository. Every document the project ships
must be findable from this section in at most two clicks.*

## License

MIT. See [LICENSE](LICENSE).

*Note: one sentence. The license file carries the legal text.*
```

---

## When the skeleton does not fit

A few cases where the spine needs adjustment:

- **CLI tool, not a library.** Replace the Quick Example code block with a shell session showing the command, the flags, and the output. The discipline is the same; the surface is the shell instead of the import statement
- **Service or server, not a library or CLI.** The Quick Example becomes a sequence: start the server, hit it with `curl`, see the response. Keep it under 30 seconds end to end
- **Application with a GUI.** Replace the Quick Example with a screenshot annotated with three numbered call-outs (do this, then this, then this). Use words sparingly; the image does most of the work
- **Framework or convention rather than a runnable artifact.** Replace the Quick Example with the smallest possible adopter example (a 5-line file that uses the framework's API). The discipline is the same: show the thing working before discussing how it works
- **Single-file script.** Skip the README; put the explanation in a comment at the top of the file. A README for a 30-line script is overhead

## What to put in `docs/` (Diataxis split)

The four-document framework (Daniele Procida, diataxis.fr):

| `docs/` subdirectory | Purpose | Reader's question |
|---|---|---|
| `tutorials/` | Step-by-step learning paths | "Teach me." |
| `how-to/` | Recipes for specific tasks | "How do I do X?" |
| `explanation/` | Concepts, design decisions, the "why" | "Why is it this way?" |
| `reference/` | Auto-generated API reference | "What does this function take?" |

The distinction matters because each type optimizes for a different reader posture (learning, achieving, understanding, looking up). A tutorial that tries to be a reference loses the teaching arc; a reference that tries to be a tutorial loses the lookup speed.

## A note on what NOT to put at the top of the README

- A logo larger than the project name (pushes the first sentence off the screen)
- A row of badges that say nothing actionable (build status badge is fine; "made with love" badge is not)
- A table of contents for a document shorter than the table of contents
- A "demo GIF" before any explanation of what the project does
- The license name in a header (it goes at the bottom or in `LICENSE`)
- A roadmap section above the install section (roadmap belongs in `ROADMAP.md` or a GitHub Project)
- Marketing taglines ("the X for Y" is fine if X and Y are concrete; "the modern, blazing-fast, developer-friendly X for Y" is not)
