# How to install and invoke a skill

A recipe. Assumes you already know what RCS is (if not, read the [getting-started tutorial](../tutorials/getting-started.md) first).

## Install a single skill

```bash
cd <path-to-cloned-rcs>
ln -s "$(pwd)/skills/<track>/<slug>" "$HOME/.claude/skills/<slug>"
```

Replace `<track>` with one of `security`, `ml-datasci`, `workflow`, `teaching`, `claude-code-meta`, and `<slug>` with the skill's directory name.

## Install all 104 skills

Use the idempotent loop:

```bash
cd <path-to-cloned-rcs>
mkdir -p "$HOME/.claude/skills"
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

The script is safe to re-run; it skips names that already exist.

## Verify a skill is loaded

Start a Claude Code session. Inside the session, the system reminder at startup lists every loaded skill by name. Search for the slug you expect.

If the skill is not in the list, the most common causes are:

1. The symlink was created but points at a non-existent target (`ls -la "$HOME/.claude/skills/<slug>"` to check)
2. The symlink target exists but contains no `SKILL.md` file
3. The skill name conflicts with another skill installed from a different source; Claude Code uses the first one it finds

## Trigger a specific skill

Skills auto-activate when Claude reads a user prompt that matches the skill's `description` field. Skills do not need to be invoked by name. The right way to trigger one is to ask the question the skill is designed to answer.

Example: to trigger `ml-datasci/reporting-effect-sizes`, ask a question that mentions a p-value, a statistical test result, or a request to "report" or "write up" a test. Avoid asking the skill by name; that is brittle. Ask the question the skill was built for.

If you want to force-load a skill regardless of context, refer to it explicitly in your prompt: "Use the `reporting-effect-sizes` skill to evaluate this t-test result." Claude will treat the explicit reference as a routing hint.

## Compose multiple skills

Skills cross-link via their `See also` sections. When one skill triggers, Claude may load the linked skills in the same turn if the user's question spans both. Example: a question about a Bayesian model's diagnostics activates `running-bayesian-workflow`, which links to `enforcing-seed-hygiene` (for the CPU-pin determinism block); if the user's question also touches reproducibility, Claude loads both.

You do not have to manage this. The skill bodies declare their relationships.

## Uninstall one skill

```bash
rm "$HOME/.claude/skills/<slug>"
```

Removes the symlink only. The underlying skill files in the cloned repo stay.

## Uninstall every RCS skill

```bash
for slug in $(ls "$HOME/.claude/skills"); do
  target=$(readlink "$HOME/.claude/skills/$slug" 2>/dev/null)
  case "$target" in
    *github_projects/RCS/*|*/rcs/skills/*)
      rm "$HOME/.claude/skills/$slug"
      echo "removed: $slug"
      ;;
  esac
done
```

Only removes symlinks that point into a cloned RCS repository. Skills installed from other sources stay.

## Update to a newer release

```bash
cd <path-to-cloned-rcs>
git pull
# Re-run the install loop above to link any newly-shipped skills
```

The symlinks are stable across updates; only newly-added skills need new symlinks.

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `ln: File exists` | Target already symlinked or directory exists | The idempotent install loop handles this. Single-skill `ln -s` calls need `rm` first or a different target name |
| Skill not in startup system reminder | Symlink dangling, or target has no `SKILL.md` | `ls -la` the symlink and the target |
| Wrong skill activates for a question | Two skills have overlapping descriptions, or the question is genuinely ambiguous | Explicitly name the intended skill in the prompt |
| Skill loads but does not follow the workflow | The skill's body is too long and Claude skipped sections, or the model is too small | Check the model in use; small models may skim large skill bodies |
| Cannot find a skill that should exist | Catalog is sorted within batch waves, not strictly Σ-desc | Search `skills/README.md` by slug rather than scrolling |
