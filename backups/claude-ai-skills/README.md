# Claude.ai Skill Backups

Version 1.2, owner Rock Lambros. coffee-peer-voice snapshot taken November 6, 2026. anti-ai-slop refreshed and clean-user-facing-text added November 10, 2026.

This folder holds copies of three skills from Rock's claude.ai account: `anti-ai-slop` (SKILL.md 1.12, slop_lint 1.7.0, slop_pass 1.0.0), `clean-user-facing-text` (no version field on the account, includes the November 10 paired-mode paragraph), and `coffee-peer-voice` (1.18). The copies are a backup. They are not part of the RCS catalog, they skip the Layer-3 contract on purpose, and the install loop in the root README never links them, because it only reads `skills/*/*/`. CI ignores them too, since every workflow filters on `skills/**`.

coffee-peer-voice and clean-user-facing-text are byte-exact copies of the account, apart from the upstream LICENSE described below. anti-ai-slop 1.12 was built on November 10 from the live 1.11 files plus the 1.12 changes, and Rock uploaded it to the account the same day as anti-ai-slop-1.12.zip.

`SHA256SUMS` lists the hash of every file in this folder. Run `shasum -a 256 -c SHA256SUMS` from this folder to confirm nothing has drifted since.

## What Is Left Out

`coffee-peer-voice/references/voice-samples.md` is missing on purpose. It holds passages from a published book, and the file itself says not to publish it. A line in the repo `.gitignore` keeps it out if a copy ever lands here.

## Upstream Code

clean-user-facing-text is adapted from the skill of the same name in Guillaume Meyer's [watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover), released under the MIT License. `clean-user-facing-text/LICENSE` is a copy of the upstream LICENSE file. It ships here because MIT requires the copyright and permission notice to travel with the code, and it is the one file in that folder that isn't on the account. slop_pass calls this skill's scripts when it sits next to anti-ai-slop, and it skips the Unicode and stylometry sections when it doesn't.

## Version Fields

The anti-ai-slop frontmatter reads `version: '1.12.0'`, matching its body. Through 1.11 it stayed at `1.9.0`, because the skill cards that shipped 1.10 and 1.11 changed the body and left the frontmatter alone. A card can't carry new files or frontmatter, so 1.12 ships as a folder upload.

## Restoring a Skill

Zip the skill's folder (for example `anti-ai-slop/`) and upload it to replace the skill on claude.ai. For coffee-peer-voice, put a copy of `voice-samples.md` back into `references/` first, because the skill reads it before every draft.

## Refreshing the Snapshot

Build a new bundle from the live skills and run its installer from the repo root. Read the skills from the account, not from a Claude session's synced skill folder, because that folder is a cache that can lag the account: on November 10 a session still showed anti-ai-slop 1.11 after 1.12 had been uploaded. The installer stops before writing anything if a file here differs from the bundle, so pass `--force` when the change is the point of the refresh.

## Running the Linter Tests

From the repo root, run `python3 -m pytest -q backups/claude-ai-skills/anti-ai-slop/tests -p no:cacheprovider`. The suite needs Python 3.9 or later and pytest, and it reads no network. It covers slop_lint and slop_pass. clean-user-facing-text sits next to anti-ai-slop here, so every slop_pass test runs, including the clean-out test.
