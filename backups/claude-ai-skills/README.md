# Claude.ai Skill Backups

Version 1.1, owner Rock Lambros. coffee-peer-voice snapshot taken November 6, 2026. anti-ai-slop refreshed November 10, 2026.

This folder holds copies of two skills from Rock's claude.ai account: `anti-ai-slop` (SKILL.md 1.12, slop_lint 1.7.0, slop_pass 1.0.0) and `coffee-peer-voice` (1.18). The copies are a backup. They are not part of the RCS catalog, they skip the Layer-3 contract on purpose, and the install loop in the root README never links them, because it only reads `skills/*/*/`. CI ignores them too, since every workflow filters on `skills/**`.

coffee-peer-voice is a byte-exact copy of the account. anti-ai-slop 1.12 was built on November 10 from the live 1.11 files plus the 1.12 changes, so it is the source for the next upload. It matches the account once the folder is zipped and uploaded.

`SHA256SUMS` lists the hash of every file in this folder. Run `shasum -a 256 -c SHA256SUMS` from this folder to confirm nothing has drifted since.

## What Is Left Out

`coffee-peer-voice/references/voice-samples.md` is missing on purpose. It holds passages from a published book, and the file itself says not to publish it. A line in the repo `.gitignore` keeps it out if a copy ever lands here.

clean-user-facing-text is not backed up here. slop_pass calls its scripts when that skill sits next to anti-ai-slop, and it skips the Unicode and stylometry sections when it doesn't.

## Version Fields

The anti-ai-slop frontmatter reads `version: '1.12.0'`, matching its body. Through 1.11 it stayed at `1.9.0`, because the skill cards that shipped 1.10 and 1.11 changed the body and left the frontmatter alone. A card can't carry new files or frontmatter, so 1.12 ships as a folder upload.

## Restoring a Skill

Zip the skill's folder (for example `anti-ai-slop/`) and upload it to replace the skill on claude.ai. For coffee-peer-voice, put a copy of `voice-samples.md` back into `references/` first, because the skill reads it before every draft.

## Refreshing the Snapshot

Build a new bundle from the live skills and run its installer from the repo root. The installer stops before writing anything if a file here differs from the bundle, so pass `--force` when the change is the point of the refresh.

## Running the Linter Tests

From the repo root, run `python3 -m pytest -q backups/claude-ai-skills/anti-ai-slop/tests -p no:cacheprovider`. The suite needs Python 3.9 or later and pytest, and it reads no network. It covers slop_lint and slop_pass. The slop_pass clean-out test skips here, because it needs clean-user-facing-text installed next to the skill.
