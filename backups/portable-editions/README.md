# Portable Skill Editions

Version 1.0, owner Rock Lambros. Added November 15, 2026.

`build_portable.py` turns the claude.ai editions of anti-ai-slop 1.16 and coffee-peer-voice 1.20 into portable editions for a Claude account where Notion connectors and web fetch aren't allowed. It writes `anti-ai-slop-portable.zip` and `coffee-peer-voice-portable.zip`. Each zip holds one folder at the top level and one SKILL.md, because the claude.ai skill uploader rejects anything else.

Like `../claude-ai-skills/`, this folder sits outside the RCS catalog. The install loop in the root README never links it, and CI ignores it, since every workflow filters on `skills/**`.

## What the Portable Editions Change

The script edits copies and never touches its inputs. Compared with the main editions:

- The corrections register ships inside coffee-peer-voice as `references/voice-corrections-register.md`, a redacted snapshot of the Notion page. A correction made on the portable account prints under `NOT LOGGED` for Rock to paste into the Notion page by hand.
- Each skill carries every script it runs. coffee-peer-voice gets its own copy of `slop_lint.py`, and both skills get the clean-user-facing-text scripts in `scripts/clean/`. anti-ai-slop also gets `scripts/slop_person_count.py`, which the main edition writes to `/tmp` from source embedded in its SKILL.md.
- Script paths start from `SKILL_DIR`, the base directory the Skill tool prints when it loads the skill. The clean-user-facing-text standalone edition uses a `SKILLS` placeholder for the folder that holds every skill, and `SKILL_DIR` is narrower, because it names one skill's own folder.
- Client names, client staff, client customers, and client network addresses are replaced with placeholders such as `[Client A]` and `[client IP]` in every file.

## What Stays Out of This Repo

This repo is public, so three inputs come from local files at run time:

- The redaction file. It lists the names it removes, so committing it would publish them. The `.gitignore` line `backups/portable-editions/*.local.json` keeps a copy saved here out of git.
- The register export. It holds client mail and Slack before redaction.
- `voice-samples.md`, for the reason in `../claude-ai-skills/README.md`.

## Rebuilding

Run this in a Claude session that has the main editions installed:

1. Fetch the Voice Corrections Register with the Notion connector. A large page gets saved to a file, so note the path the fetch reports. A Markdown export of the page works too.
2. Put the redaction file somewhere outside the repo, or in this folder under a name ending in `.local.json`.
3. Run the script from the repo root:

```bash
python3 -I backups/portable-editions/build_portable.py \
  --skills /root/.claude/skills/synced/<org>_<account> \
  --register <saved fetch or export> \
  --redactions <path>/redactions.local.json \
  --out <output folder>
```

`--skills` names the folder that holds `anti-ai-slop`, `coffee-peer-voice`, and `clean-user-facing-text`. `--voice-samples` defaults to the copy inside `--skills`.

The script stops before it writes a zip in three cases:

- An anchored edit doesn't match exactly once.
- The source skills aren't 1.16 and 1.20, because the anchors fit those releases only. A new release needs new anchors in the script.
- The leak scan finds a redaction term, an email address, an IP address, or an account path anywhere in either finished folder.

## Redaction File Format

JSON with three keys. `redact` holds rules as scope, regular expression, and replacement, where scope is `all` (every bundled text file) or `register` (the snapshot only). `leak_terms` holds the names the scan checks for, matched without regard to case. `allowed_spans` holds file suffix and span pairs for published text that names someone on purpose, such as Rock's own public posts. The example uses invented names:

```json
{
  "version": "1.0",
  "owner": "Rock Lambros",
  "redact": [
    ["all", "\\bExample Corp\\b", "[Client A]"],
    ["register", "\\bPat\\b", "[client colleague P]"]
  ],
  "leak_terms": ["Example Corp", "Pat"],
  "allowed_spans": [["coffee-peer-voice/references/voice-samples.md", "Pat Public"]]
}
```

## Tested

On November 15, 2026 the script rebuilt the two portable zips Rock received that day from the same inputs. File for file, the trees matched, apart from the build date in each SKILL.md and one register entry that went in after the fetch used for the test. From a fresh unpack, anti-ai-slop's 227 tests passed, including the clean-out test, which runs against the bundled cleaner. Every bundled script ran on a sample blog draft. Pointed at the 1.12 and 1.18 copies in `../claude-ai-skills/`, the script stops at the version check.
