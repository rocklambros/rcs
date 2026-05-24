# How to audit your docs for AI slop

A recipe for applying the [`workflow/writing-repo-documentation`](../../skills/workflow/writing-repo-documentation/) skill's discipline to your own project's documentation. Use it on a README, a CONTRIBUTING, a tutorial, or any prose Claude has touched.

## What "AI slop" means here

Patterns that statistically over-appear in machine-generated prose. They are not always wrong individually; they are wrong as a cluster because readers have learned to recognize the cluster and discount the content. The full catalog is in [`reference/ai-slop-patterns.md`](../../skills/workflow/writing-repo-documentation/reference/ai-slop-patterns.md). The eight families:

1. Marketing superlatives (`comprehensive`, `robust`, `seamless`)
2. Metaphor clichés (`delve into`, `rich tapestry`, `ever-evolving landscape`)
3. Hedge filler (`it is worth noting that`, `ultimately`, `in essence`)
4. Formatting tics (em-dashes, prose semicolons, sentence-initial conjunctions, heading sprawl, emoji decoration)
5. Faux balance (`while X has its critics, others argue`)
6. Sycophantic openers (`Let's dive in`, `Great question`)
7. Self-reference (`this article will cover`, `as you can see`)
8. Voice and tone drift (first-person "we" without a referent group, mid-doc voice switch)

## Quick scan

Find the worst offenders fast:

```bash
# from your project root
for f in $(find . -maxdepth 3 -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*"); do
  em=$(grep -c '—' "$f" 2>/dev/null)
  semi=$(grep -cE '; [a-z]' "$f" 2>/dev/null)
  slop=$(grep -ciE '\b(comprehensive|robust|seamless|delve|tapestry|ever-evolving|empowers|cutting-edge|state-of-the-art|navigate the complexit)\b' "$f" 2>/dev/null)
  [ "$em" -gt 0 ] || [ "$semi" -gt 0 ] || [ "$slop" -gt 0 ] && echo "$f: em-dash=$em, semi=$semi, slop=$slop"
done
```

The first pass tells you which files to attack. Sort by total signal and start at the top.

## Per-file audit pattern

For each flagged file:

1. **Read it cold.** Skim once for the gist. If a sentence stops you, mark it. The skill's Step 7 (cold-read test) treats the first confusion point as the first rewrite target
2. **Walk the slop catalog.** Open `reference/ai-slop-patterns.md` and grep for each pattern. For every match, apply the substitution in the catalog
3. **Apply the six-section spine** (if the file is a README): what+why, runnable example, install, second example, concepts, where-to-next. Missing sections are findings
4. **Check cross-links.** Every doc the project ships must be reachable from the README in at most two clicks. Orphans are findings
5. **Re-read.** Confirm the substitutions did not lose information. The rewrite should be information-denser, not just shorter

## Automated sweep (for em-dashes and prose semicolons)

A Python script that handles the two most common slop signals in bulk, preserving code blocks and explicit teaching examples:

```python
#!/usr/bin/env python3
"""Replace em-dashes and prose semicolons in markdown, skipping code blocks."""
import sys
from pathlib import Path

def sweep(path: Path, keep_lines: set[int] = None) -> tuple[int, int]:
    """Return (em_dash_replacements, semi_replacements)."""
    keep_lines = keep_lines or set()
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    in_code = False
    em, semi = 0, 0
    out = []
    for i, line in enumerate(lines, start=1):
        if line.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or i in keep_lines:
            out.append(line)
            continue
        new = line
        # Em-dash with surrounding spaces → period + capitalize next
        if " — " in new:
            parts = new.split(" — ")
            for j in range(1, len(parts)):
                if parts[j] and parts[j][0].islower():
                    parts[j] = parts[j][0].upper() + parts[j][1:]
            new = ". ".join(parts)
            em += new.count(". ") - line.count(". ")
        # Prose semicolon (followed by space + lowercase) → period + capitalize next
        if "; " in new:
            parts = new.split("; ")
            for j in range(1, len(parts)):
                if parts[j] and parts[j][0].islower():
                    parts[j] = parts[j][0].upper() + parts[j][1:]
            new = ". ".join(parts)
            semi += new.count(". ") - line.count(". ")
        out.append(new)
    path.write_text("".join(out))
    return em, semi


if __name__ == "__main__":
    for path in (Path(p) for p in sys.argv[1:]):
        em, semi = sweep(path)
        print(f"{path}: -{em} em-dashes, -{semi} semicolons")
```

Save as `scripts/sweep-ai-slop.py`, then:

```bash
python3 scripts/sweep-ai-slop.py README.md CONTRIBUTING.md docs/*.md
```

Verify each change with `git diff` before committing. The script does not catch:

- Em-dashes without surrounding spaces (`one—two`); rare
- Em-dashes inside `<code>` spans or links; preserved
- Semicolons in code blocks; preserved
- Semicolons followed by uppercase or numbers; preserved (often legitimate)
- Marketing superlatives, metaphor clichés, hedge filler, sycophantic openers, faux balance, voice drift; these require human judgment

For the remaining six families, walk the catalog manually.

## Test the rewrite

The skill's Step 7 cold-read test is the verification. If you cannot find a fresh reader, read the doc aloud after a 24-hour gap. The gap is not optional; fresh eyes substitute for fresh ears.

A faster approximation: ask Claude to read the doc and identify the first place a "first-time reader who has never seen this project" would lose the thread. The model is a passable cold reader for the novice tier.

## Common mistakes

- **Sweeping without reading.** The script changes punctuation; the prose may now read worse because a long sentence was split awkwardly. Read each diff before committing
- **Deleting information.** Substitutions should preserve meaning. If the slop word was carrying real signal ("the library is robust to malformed input"), the substitution should name the property ("the library handles malformed input safely"), not delete it
- **Treating the slop catalog as an aesthetic preference.** It is not. Each pattern in the catalog is a measurable signal of statistical over-representation in machine-generated text. Readers have learned to spot the cluster, and the cluster makes them discount the content. The discipline is about not getting discounted, not about taste
- **Skipping `teaching/README.md` as the style template.** That doc has the cleanest slop profile in the project. Read it once; use it as the reference for what the bar looks like
