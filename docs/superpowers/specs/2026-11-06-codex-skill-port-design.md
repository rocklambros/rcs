# Codex Skill Port: claude.ai and RCS Skills in the ChatGPT App

**Date:** 2026-11-06
**Status:** Draft, pending owner review
**Owner:** Rock Lambros (klambros / RockCyber)
**Version:** 0.1
**Scope:** A repeatable port of 14 skills into `~/.codex/skills/` so the Codex runtime bundled in the ChatGPT desktop app can load them. Five come from the claude.ai account, nine from the RCS catalog. Eleven of the fourteen replace hand-made copies from 2026-09-29 that have drifted from their sources.

---

## 1. Intent and why

Rock uses the same handful of writing, voice, review, and premortem skills in claude.ai and in Claude Code. He wants them available in the ChatGPT app on this Mac. The ChatGPT app (26.1013) bundles Codex and reads skills from `$CODEX_HOME/skills/<name>/SKILL.md`, with `CODEX_HOME=~/.codex` set in its own config. A skill installed there appears in the Codex skill picker and in the model-visible prompt for Codex conversations inside the app.

A hand copy already exists. Eleven skills were ported on 2026-09-29 with prose edits, a per-skill runtime-notes section, and an `agents/openai.yaml` for the picker. Five weeks later the copies are stale: `coffee-peer-voice` is 1.2 there, 1.15 in `~/.claude/skills`, and 1.18 on claude.ai. Another hand copy would drift the same way. The fix is a port tool that regenerates the install from declared sources, keeps the hand-written adaptations as data instead of as edits buried in output files, and reports drift on demand.

## 2. Goals, non-goals, anti-goals

**Goals**

- G1. The 14 skills in §4 load in the ChatGPT app's Codex runtime and pass Codex's own `quick_validate.py`.
- G2. One command rebuilds the install from current sources. A second mode reports, without writing, which installed skills are behind their source and which hand adaptations no longer apply.
- G3. Hand adaptations from the September port survive the rebuild. They live in RCS as notes and patches, not as untracked edits in `~/.codex/skills`.
- G4. The two voice skills install in their self-contained form. `coffee-peer-voice` and `anti-ai-slop` on claude.ai read their references through the Notion connector, which Codex does not have. The `-portable` builds Rock produced on 2026-11-06 inline every reference and run from their own folder.
- G5. The tool never destroys a Codex skill it did not build.

**Non-goals**

- The other 40 skills in the claude.ai cache. Most are Anthropic built-ins (`docx`, `pptx`, `canvas-design`, `skill-creator`, and so on). Rock's remaining claude.ai skills (`x-weekly-originals`, `acs-weekly-status`, `paper-premortem`, and others) are out of scope for this port. Adding one later is a manifest entry.
- `paper-premortem`, even though `defensible-premortem` names it as a specialist. The runtime notes already say what to do when a named sibling is not installed.
- The rest of the RCS catalog. The port tool can take any RCS skill, but this port ships the nine already on Codex plus the five from claude.ai.
- House style for Codex. `~/.codex/AGENTS.md` is empty and stays that way. The voice skills carry their own rules.
- Scheduling. The tool runs when Rock runs it. No cron, no launchd, no hook.
- Pushing to GitHub or opening a PR. Work lands on the `feature/codex-port` branch and stops there until Rock says otherwise.
- The plain ChatGPT chat surface. Whether a non-Codex chat in the app reads `~/.codex/skills` was not verifiable from this machine. Codex conversations inside the app are the target.

**Anti-goals (failure even if it technically works)**

- A description silently truncated to fit Codex's 1024-character cap. Descriptions drive skill selection. The tool fails and names the skill instead.
- A rebuild that overwrites a Codex skill someone edited by hand after the last build.
- Output that changes on every run with identical inputs. No build timestamps inside `SKILL.md`.
- Any copy of `coffee-peer-voice/references/voice-samples.md` landing in the RCS repository. It holds published book text. The repository's `.gitignore` already names it. The tool reads it from OneDrive at port time and writes it only under `~/.codex/skills`.
- Any AI attribution in commits, file headers, or comments. The existing `PreToolUse-no-ai-attribution.sh` hook enforces this.

## 3. Constraints

**Codex validator rules**, from `~/.codex/skills/.system/skill-creator/scripts/quick_validate.py` as shipped in ChatGPT 26.1013:

| Rule | Value |
|---|---|
| Top-level frontmatter keys allowed | `name`, `description`, `license`, `allowed-tools`, `metadata` |
| `name` | matches `^[a-z0-9-]+$`, at most 64 characters, equals the directory name |
| `description` | string, at most 1024 characters, no `<` or `>` anywhere |
| `agents/openai.yaml` `interface.short_description` | 25 to 64 characters |

The Rust-side loader in the Codex binary (`skills/src/parser.rs`) reads `name` and `description` and carries `metadata` through. The September port confirmed that nesting RCS fields under `metadata` loads cleanly.

**Codex runtime facts the notes depend on.** Subagents are `spawn_agent`, `wait_agent`, `close_agent`, `send_input`, `list_agents`, gated by the `multi_agent` feature and `[agents] max_threads`. Sibling skills are invoked as `$skill-name`. The model-visible prompt lists each skill as `r0/<name>/SKILL.md` and defines a skill roots table with `r0` = `/Users/klambros/.codex/skills`, so the model can derive a skill's absolute folder. `codex debug prompt-input` renders that prompt as JSON without a model call. Confirmed on this machine with Codex CLI 0.162.1 and the app-bundled binary.

**Toolchain.** Neither `/opt/homebrew/bin/python3` nor `/usr/bin/python3` has PyYAML or pytest. The RCS virtualenv (`uv run python`) has both. Codex's `quick_validate.py` imports `yaml`, so it only runs under the RCS interpreter.

**Sources and their shapes**

| Source kind | Location | Shape |
|---|---|---|
| claude.ai cache | `~/Library/Application Support/<profile>/local-agent-mode-sessions/skills-plugin/*/*/skills/<name>/` | Live mirror the Claude desktop app keeps for its local agent mode. Path segments are session UUIDs and can change. Two profiles exist, `Claude` (rockcyber account) and `Claude-Zenity`. For two skills the profiles hold different copies: `defensible-premortem` under `Claude` has an unquoted description containing `: ` that no YAML parser accepts, and the `Claude-Zenity` copy is the same file with the description quoted. `clean-user-facing-text` under `Claude` hardcodes ten claude.ai sandbox paths of the form `/root/.claude/skills/synced/<uuid>_<uuid>/...`, and the `Claude-Zenity` copy is the standalone edition that uses a `SKILLS` placeholder instead. |
| portable zip | `~/Library/CloudStorage/OneDrive-RockCyber/Templates/Prompts/<name>-portable.zip` | Zip with a single top-level `<name>/` folder. Built by Rock from the claude.ai version with references inlined. |
| RCS | `~/github_projects/RCS/skills/<track>/<name>/` | RCS Layer-3 format: top-level `version`, `status`, `track`, `audience`, `evidence`, `last-updated` fields, track-prefixed sibling references such as `` `workflow/adversarial-premortem-single` ``. |
| local Claude Code | `~/.claude/skills/<name>/` | Real directories only for nine skills. The other 107 entries are symlinks into RCS. |

**Repository rules.** Code is production quality from the first commit: version and owner on artifacts, comments explain why, no placeholder implementations, pinned dependencies. American English, active voice, no em dashes or semicolons in prose. RCS tooling uses Python 3.11+, `click`, `pyyaml`, `pytest`, run through `uv run python -m tools.<module>`. Tests live in `tools/tests/`.

**Harness rules.** Writes outside the working directory need confirmation. Both targets here, `~/github_projects/RCS` and `~/.codex/skills`, sit under the home directory, which is a working directory for this session. The tool itself must never write anywhere else.

## 4. Skills in scope

| Skill | Source for this port | Existing Codex copy | Hand edits to preserve |
|---|---|---|---|
| `anti-ai-slop` | portable zip, 1.10-portable | none | path pinning (D2 token rewrite) plus a patch for the sentences that describe Claude Code allow rules |
| `coffee-peer-voice` | portable zip, 1.18-portable | yes, 1.2 | path pinning plus a patch for the Write and Edit tool wording |
| `clean-user-facing-text` | claude.ai cache, `Claude-Zenity` profile (standalone edition) | none | path pinning plus a patch for the sentence that defines `SKILLS` in Claude Skill-tool terms |
| `defensible-premortem` | claude.ai cache, `Claude-Zenity` profile, 0.1 draft | none | none |
| `adversarial-premortem` | claude.ai cache (byte-identical to `~/.claude/skills/adversarial-premortem`) | yes | subagent notes |
| `adversarial-premortem-complete` | RCS `workflow/` | yes | subagent notes, prose tool mapping |
| `adversarial-premortem-single` | RCS `workflow/` | yes | subagent notes |
| `authoring-skill` | RCS `claude-code-meta/` | yes | extensive: host substitutions, Codex validator rules, checklist items |
| `brutal-grader` | RCS `teaching/` (gitignored in RCS, private per-machine skill) | yes | subagent notes, prose tool mapping |
| `writing-onboarding-guide` | RCS `teaching/` | yes | sibling-skill note |
| `writing-release-notes-as-postmortem` | RCS `workflow/` | yes | sibling-skill note |
| `writing-repo-documentation` | RCS `workflow/` | yes | house style inlined in Step 6, cold-read mapping, `CLAUDE.md` references reworded |
| `writing-successor-primers` | RCS `workflow/` | yes | sibling-skill note |
| `writing-vdp-and-coordinated-disclosure` | RCS `security/` | yes | sibling-skill note |

All eleven existing copies carry `metadata.ported-from`, which is the marker the overwrite gate keys on.

## 5. Decisions

**D1. The tool lives in RCS, with a gitignored local overlay for private skills.** `tools/port_to_codex.py`, with its data under `tools/codex_port/` and tests in `tools/tests/test_port_to_codex.py`. RCS already claims cross-host portability in its README, already holds the lint tools the port reuses, and already mirrors Rock's claude.ai account under `backups/claude-ai-skills/`. The tracked manifest names paths on Rock's Mac. That is acceptable in a public repo because the paths reveal nothing beyond folder names. Alternative considered and rejected: the private harness repo, which would split the tool from the lint chain it depends on.

`brutal-grader` is gitignored in RCS as a private per-machine skill. Its port data cannot be tracked either, because its patch would reproduce roughly fifty lines of its prose. The tool therefore reads two manifests: `tools/codex_port/manifest.toml` (tracked, the 13 public skills) and `tools/codex_port/local/manifest.toml` (gitignored, absent on other machines). Notes and patches for overlay skills live under `tools/codex_port/local/notes/` and `local/patches/`. The overlay merges over the tracked manifest by skill name. A `.gitignore` line for `tools/codex_port/local/` ships with the tool. On a machine without the overlay, `brutal-grader` is simply not in the manifest, so nothing is reported missing.

**D2. Three layers per skill: mechanical, notes, patch.**

1. *Mechanical*, fully generated. Resolve the source. Copy its tree, skipping `__pycache__` and dotfiles. Parse the frontmatter with PyYAML. A source whose frontmatter does not parse fails that skill with a message naming the file and the parser error, because the fix belongs at the source. Normalize frontmatter: keep the five allowed keys, move every other top-level key under `metadata` with its value intact, add `metadata.ported-from` (source path with the home directory written as `~`) and `metadata.ported-to-codex` (the date the source content last changed, see D4). Rewrite backticked sibling references `` `<track>/<name>` `` to `` `$<name>` `` across every Markdown file in the tree. Rewrite path placeholder tokens the manifest declares for the skill, `SKILLS` to the absolute skills root and `SKILL_DIR` to the absolute folder of that skill, computed from the real home directory at build time. Rock's claude.ai skills use those two tokens so the model can build script paths. Codex gives the model the same information through its skill roots table, but a literal absolute path is what the skills themselves ask for ("write the full absolute path every time"). Append a `## Codex runtime notes` section.
2. *Notes*, hand-written data. `tools/codex_port/notes/<name>.md` holds the body of the runtime-notes section. A `_default.md` carries the one line every skill needs: siblings are `$skill-name`, and a sibling not installed under `~/.codex/skills` is applied inline. The September port's three note variants (sibling-only, subagent family, authoring-skill) seed the initial files.
3. *Patch*, hand-written data. `tools/codex_port/patches/<name>.patch` is a unified diff against the output of layers 1 and 2. It carries prose edits that cannot be generated, such as the `authoring-skill` host substitutions. A patch that fails to apply stops that skill, prints the rejected hunks, and leaves the installed copy untouched. The initial patches are extracted by diffing the September copies against a fresh mechanical build of their current sources, then pruned to the hunks that still make sense against the current source.

**D3. Picker metadata is manifest data.** `tools/codex_port/manifest.toml` lists each skill with its source kind, source location, `display_name`, `short_description`, and `default_prompt`. The eleven existing `openai.yaml` values seed the manifest. The tool validates `short_description` length and writes `agents/openai.yaml` from the manifest. No derived defaults: a skill without picker text fails the build with a clear message, because derived text is the kind of thing nobody reviews.

**D4. Drift detection by content hash, not by clock.** The tool computes a SHA-256 over the source tree. It writes a sidecar `~/.codex/skills/<name>/.rcs-port.json` holding `source_sha256`, `output_sha256`, `source`, and `built_on`. `metadata.ported-to-codex` in `SKILL.md` changes only when `source_sha256` changes, so repeated builds from unchanged sources produce byte-identical output. `--check` compares the stored source hash against the live source (source moved), the stored output hash against the installed tree (installed copy hand-edited), and dry-runs the patch (adaptation stale). Codex ignores the sidecar.

**D5. Overwrite gate.** A target directory is replaced only when it does not exist or its `SKILL.md` carries `metadata.ported-from`. `~/.codex/skills/.system` is never touched. A target whose installed hash differs from the sidecar's `output_sha256` is skipped with a warning unless `--force` is passed. The build stages into `~/.codex/.rcs-port-stage/`, outside the skills root, because Codex globs every `~/.codex/skills/*/SKILL.md` and would load a half-built stage. The stage sits on the same volume, so the swap into place is one atomic rename and a failed build never leaves a half-written skill.

**D6. Validation is Codex's validator, with a built-in fallback.** After the three layers, the tool runs `~/.codex/skills/.system/skill-creator/scripts/quick_validate.py` on the staged directory under its own interpreter (`sys.executable`, the RCS virtualenv), and applies the §3 rules itself when the script is absent. A validator that is present but exits with an import error is a toolchain failure and aborts the whole build with that message, never a silent skip. Any validation failure fails that skill. Descriptions are never edited by the tool. A description that violates a rule is fixed at the source or in the patch.

**D7. Voice skills install as their portable builds, version stamps intact.** The proof-of-read stamp prints `coffee-peer-voice v1.18-portable loaded`. Relabeling it `-codex` would fork a file Rock already maintains. The portable variant is the source of record for Codex until Rock says otherwise.

**D8. claude.ai cache resolution is explicit per skill.** Each cache-sourced manifest entry names its profile (`Claude` or `Claude-Zenity`). The tool globs `*/*/skills/<name>/SKILL.md` under that profile only and takes the newest match by modification time, which handles the session UUIDs changing. No cross-profile newest-wins rule: the two profiles already disagree on two skills (§3), and the choice is content, not timing. For this port `defensible-premortem` and `clean-user-facing-text` source from `Claude-Zenity`, `adversarial-premortem` from `Claude`. `check` reports, as information with no effect on the exit code, when the other profile holds a different copy of a cache-sourced skill.

**D9. Zip sources are extracted with a path-traversal guard.** Every member path is resolved and must stay inside the extraction directory. The zip must contain exactly one top-level folder whose name equals the skill name.

**D10. `adversarial-premortem` sources from the claude.ai cache.** It is byte-identical to the local Claude Code copy today. Taking the claude.ai copy keeps the "claude.ai set" rule uniform.

## 6. Command surface

```
uv run python -m tools.port_to_codex build [--only NAME ...] [--force] [--manifest PATH]
uv run python -m tools.port_to_codex check [--only NAME ...] [--manifest PATH]
uv run python -m tools.port_to_codex diff NAME
```

`capture` refuses when the installed copy differs from its source in a path listed under `defaults.capture_exclude`, which holds `references/voice-samples.md`, so published text can never reach the repository through a patch. `build` writes. `check` reports drift and exits non-zero on any of: source content changed since the last build, a patch that no longer applies, an installed tree edited since the last build, a source that cannot be found, or a staged skill that fails validation. Informational lines (another profile holds a different copy) do not affect the exit code. That makes `check` usable from a shell alias or a future hook. `diff` shows what `build` would change for one skill.

Exact flag names, output formatting, and module decomposition are the builder's.

## 7. Verification

The work is done when all of the following hold on this Mac.

1. `uv run python -m pytest tools/tests/test_port_to_codex.py` passes. Coverage includes frontmatter nesting, each validator rule, sibling-reference rewriting, note appending, patch application and patch failure, the overwrite gate, the hand-edit guard, zip traversal rejection, and byte-identical rebuilds.
2. `uv run python -m tools.port_to_codex build` exits zero for all 14 skills, and a second run reports no changes.
3. `uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/<name>`, run from the RCS root, prints `Skill is valid!` for each of the 14.
4. `codex debug prompt-input hello` lists all 14 skill names.
5. `uv run python -m tools.port_to_codex check` exits zero immediately after the build.
6. The installed `anti-ai-slop` linter tests pass from the installed location: `uv run python -m pytest -q ~/.codex/skills/anti-ai-slop/tests -p no:cacheprovider`, run from the RCS root.
8. Every installed `SKILL.md` that invokes a bundled script names an absolute path under `~/.codex/skills/` and contains no `SKILLS/` or `SKILL_DIR/` token and no `/root/.claude/` path. A test asserts this over the installed tree.
7. Rock opens a Codex conversation in the ChatGPT app, invokes `$coffee-peer-voice` on a short draft, and sees the `coffee-peer-voice v1.18-portable loaded` stamp. This is the only step that needs the app, and only Rock can run it.

## 8. Security notes

The tool reads only the paths named in the manifest and writes only under `~/.codex/skills/`. It makes no network calls. It runs `quick_validate.py` and the patch tool as subprocesses with argument lists, never through a shell string. Patch application uses `git apply --directory` against the staging directory, which refuses hunks that reach outside it. The skill scripts it installs (`slop_lint.py`, `clean_text.py`, and the rest) are Rock's own code and already pass the RCS linter tests. Nothing from `~/.codex/auth.json` or `config.toml` is read.

## 9. Left to the builder

- Module layout inside `tools/port_to_codex.py` and whether source resolution, transforms, and installation split into a package.
- YAML serialization details. PyYAML will re-emit folded descriptions as quoted strings. Codex reads the value, not the layout, so that is acceptable.
- The exact pruning of the initial patches. Hunks that only restate what the notes section says are dropped. Hunks that reword prose for Codex stay.
- Whether `check` prints a table or one line per skill.
- Test fixture construction. Small synthetic skills under `tools/tests/fixtures/` rather than copies of real skills, so tests do not depend on Rock's home directory.

## 10. Follow-ups outside this port

- `~/.claude/skills/coffee-peer-voice` and `anti-ai-slop` are behind claude.ai (1.15 vs 1.18, 1.6 vs 1.10). That is a Claude Code sync problem, not a Codex one, and is not addressed here.
- `defensible-premortem` on the rockcyber claude.ai account has the unquoted description that no YAML parser accepts. The Zenity account already carries the quoted fix. Re-uploading the quoted version to rockcyber removes the need to source that skill from the Zenity profile.
- `clean-user-facing-text` on the rockcyber account hardcodes sandbox UUID paths that break whenever claude.ai reassigns the session. The Zenity standalone edition with the `SKILLS` placeholder is the better upload for both accounts.
- `~/.claude/settings.json` was flagged unaudited at session start, and the `claude-mem` plugin moved from 15.8.0 to 15.11.0 without a recorded baseline. Both are harness hygiene items for a separate session.
