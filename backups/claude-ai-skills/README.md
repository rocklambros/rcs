# Claude.ai Skill Backups

Version 1.0, owner Rock Lambros. Snapshot taken November 6, 2026.

This folder holds byte-exact copies of two skills from Rock's claude.ai account: `anti-ai-slop` (SKILL.md body 1.10, linter slop_lint 1.6.0) and `coffee-peer-voice` (1.18). The copies are a backup. They are not part of the RCS catalog, they skip the Layer-3 contract on purpose, and the install loop in the root README never links them, because it only reads `skills/*/*/`. CI ignores them too, since every workflow filters on `skills/**`.

`SHA256SUMS` lists the hash of every file as it was on the account when the snapshot was taken. Run `shasum -a 256 -c SHA256SUMS` from this folder to confirm nothing has drifted since.

## What Is Left Out

`coffee-peer-voice/references/voice-samples.md` is missing on purpose. It holds passages from a published book, and the file itself says not to publish it. A line in the repo `.gitignore` keeps it out if a copy ever lands here.

The anti-ai-slop frontmatter still reads `version: '1.9.0'` while its body says 1.10. That is how the live file reads, because the skill card that shipped 1.10 updated the body and left the frontmatter alone. The backup keeps the live bytes as they are.

## Restoring a Skill

Zip the skill's folder (for example `anti-ai-slop/`) and upload it to replace the skill on claude.ai. For coffee-peer-voice, put a copy of `voice-samples.md` back into `references/` first, because the skill reads it before every draft.

## Refreshing the Snapshot

Build a new bundle from the live skills and run its installer from the repo root. The installer stops before writing anything if a file here differs from the bundle, so pass `--force` when the change is the point of the refresh.

## Running the Linter Tests

From the repo root, run `python3 -m pytest -q backups/claude-ai-skills/anti-ai-slop/tests -p no:cacheprovider`. The suite needs Python 3.9 or later and pytest, and it reads no network.
