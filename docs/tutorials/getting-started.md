# Getting started with RCS

This tutorial takes you from never having installed an RCS skill to seeing one fire on a real question, in about ten minutes. No prior experience with Claude Code skills is assumed.

## What you will have done by the end

1. Cloned RCS and symlinked one skill into your `~/.claude/skills/` directory
2. Opened a new Claude Code session and asked a question that activates that skill
3. Observed Claude consult the skill before answering, and seen the difference between the skill-loaded answer and the one Claude would have given without it
4. Removed the skill cleanly so the tutorial leaves no trace

Each step is small and testable. If a step does not produce the result described, stop and read the troubleshooting note before moving on.

## What you need before starting

- Claude Code installed. Check with `claude --version`. If the version number prints, you are set.
- `git` and a shell. macOS and Linux are tested. Windows under WSL works.
- About ten minutes.
- An empty or near-empty `~/.claude/skills/` directory. If yours is populated from another source, that is fine; the install script in the next step skips names that already exist.

## Step 1: Clone RCS

Pick a directory where you keep code repositories. The location does not matter; the symlinks will point back here regardless.

```bash
git clone https://github.com/rocklambros/rcs.git
cd rcs
```

If `git clone` fails, you do not have network access or git is not installed. Both are required.

## Step 2: Install one skill

For the tutorial, install one skill rather than the whole library. The one you will activate in step 3 is `ml-datasci/reporting-effect-sizes`. It refuses to call a p-value "significant" without an effect size.

```bash
mkdir -p "$HOME/.claude/skills"
ln -s "$(pwd)/skills/ml-datasci/reporting-effect-sizes" "$HOME/.claude/skills/reporting-effect-sizes"
ls -la "$HOME/.claude/skills/reporting-effect-sizes"
```

The last line should show a symlink pointing into the cloned repo. If it shows "No such file or directory", the symlink did not land; check the path in the second command for typos.

## Step 3: Activate the skill in a Claude Code session

In a terminal, start a fresh Claude Code session in any working directory (the directory does not need to be the cloned repo).

```bash
cd ~
claude
```

When Claude starts, it scans `~/.claude/skills/` and loads the frontmatter description of every skill it finds. The skill is now available without you doing anything else.

Type this question and press enter:

> I ran a t-test on before/after blood pressure for 18 patients. The p-value is 0.012. Is the drug effective?

Claude's response should:

1. Refuse to call the result "significant" or "effective" based on the p-value alone
2. Ask for or compute the effect size (Cohen's dz for paired data) with a 95% confidence interval
3. Name the direction (which group had lower BP, and by how much)

If Claude answers with just "yes, p < 0.05 means significant" or similar, the skill did not load. Most common cause: the symlink failed in step 2. Re-run `ls -la "$HOME/.claude/skills/reporting-effect-sizes"` and confirm it points to a directory containing a `SKILL.md` file.

## Step 4: See the difference

This is the meat of the tutorial. Ask the same question without the skill loaded, and compare.

```bash
rm "$HOME/.claude/skills/reporting-effect-sizes"
```

Start a fresh Claude Code session and ask the same question again:

> I ran a t-test on before/after blood pressure for 18 patients. The p-value is 0.012. Is the drug effective?

Without the skill, Claude will most likely answer the question literally and say something like "yes, p < 0.05 is conventionally considered statistically significant." That answer is technically correct about statistics convention but wrong about clinical decision-making. A p-value with no effect size tells you that the difference is detectable, not that it is meaningful. With the skill, Claude refuses to make that jump. Without the skill, it does not know to refuse.

The contrast is the value. The skill is not magic. It is a discipline encoded as a markdown file that Claude reads before answering.

## Step 5: Install the rest

Now you have a working example. To install all 104 skills:

```bash
cd <path-to-cloned-rcs>
for skill in skills/*/*/; do
  [ -f "$skill/SKILL.md" ] || continue
  name=$(basename "$skill")
  target="$HOME/.claude/skills/$name"
  if [ -L "$target" ] || [ -e "$target" ]; then
    echo "skip: $name"
    continue
  fi
  ln -s "$(pwd)/$skill" "$target"
  echo "installed: $name"
done
```

The script is idempotent. Running it a second time only links new skills you do not already have. Use it again whenever you pull updates from this repo.

## What to do next

You now know how to install RCS, how a skill activates, and what the difference is. The natural next steps depend on what you came for.

- **Want to see the full catalog?** Read [`skills/README.md`](../../skills/README.md). 104 skills, sorted by Σ within each batch wave.
- **Want skills for your role?** Open the track README for [security](../../skills/security/), [ml-datasci](../../skills/ml-datasci/), [workflow](../../skills/workflow/), [teaching](../../skills/teaching/), or [claude-code-meta](../../skills/claude-code-meta/).
- **Want to understand the concepts behind the catalog?** Read [`docs/explanation/what-is-a-skill.md`](../explanation/what-is-a-skill.md), [`docs/explanation/sigma-score.md`](../explanation/sigma-score.md), and [`docs/explanation/pragmatic-discipline.md`](../explanation/pragmatic-discipline.md).
- **Want to contribute a skill?** Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md), then [`docs/how-to/contribute-a-skill.md`](../how-to/contribute-a-skill.md) for the recipe.
- **Hit a bug?** File an issue using the bug-report template in `.github/ISSUE_TEMPLATE/`. For security problems, see [`SECURITY.md`](../../SECURITY.md) and do not file a public issue.

Welcome to RCS.
