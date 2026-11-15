#!/usr/bin/env python3
"""Build portable editions of anti-ai-slop 1.16 and coffee-peer-voice 1.20.

Version 1.1, owner Rock Lambros. November 15, 2026.

Portable means no Notion, no web fetch, no account-specific paths, every script
bundled, and client names redacted. The editions are for a Claude account where
Notion connectors and web fetch are not allowed.

Nothing private lives in this file, because the repo is public. Three inputs come
from local files at run time: the redaction list (it names the clients it removes),
the register export, and voice-samples.md (book passages, kept out of the repo).

Every text edit is anchored and must match exactly once, so a source change stops
the build instead of shipping a half-edited skill. A leak scan over both finished
trees stops the build before any zip is written.

Usage:
    python3 -I build_portable.py --skills DIR --register FILE --redactions FILE \
        [--voice-samples FILE] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

VERSION = "1.1.0"
# The anchors below are written against these releases. A new release needs new anchors.
EXPECTED = {
    "anti-ai-slop": "Version 1.16, owner Rock Lambros.",
    "coffee-peer-voice": "Version 1.20, owner Rock Lambros.",
}
CLEAN_SCRIPTS = (
    "clean_text.py",
    "common.py",
    "inspect_text.py",
    "score_stylometry.py",
    "text_unicode.py",
)
# The main editions hard-code their own claude.ai account folder in every script call.
ACCOUNT_RX = r"/root/\.claude/skills/synced/[0-9a-f-]+_[0-9a-f-]+/"


def edit(text: str, old: str, new: str, label: str) -> str:
    """Replace one anchored span, or stop the build if it doesn't match exactly once."""
    n = text.count(old)
    if n != 1:
        sys.exit(f"{label}: anchor found {n} times: {old[:80]!r}")
    return text.replace(old, new, 1)


class Redactor:
    """Applies the local redaction list and scans finished trees for anything it missed."""

    def __init__(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        self.rules = [
            (scope, re.compile(pat), rep) for scope, pat, rep in data["redact"]
        ]
        self.leak_terms = list(data["leak_terms"])
        self.allowed = [tuple(a) for a in data.get("allowed_spans", [])]
        if not self.rules or not self.leak_terms:
            sys.exit(f"{path}: redact and leak_terms must both be non-empty")

    def apply(self, text: str, scope: str) -> str:
        for where, rx, rep in self.rules:
            if where in ("all", scope):
                text = rx.sub(rep, text)
        return text

    def scan(self, tree: Path, account_path: str) -> list[str]:
        hits = []
        generic = re.compile(
            r"\b\d{1,3}(?:\.\d{1,3}){3}\b|[\w.+-]+@[\w-]+\.[\w.]+|/root/\.claude|"
            + re.escape(account_path)
        )
        for p in sorted(tree.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(tree).as_posix()
            text = p.read_text(encoding="utf-8")
            for term in self.leak_terms:
                tail = r"(?![\w])" if term[-1].isalnum() else ""
                for m in re.finditer(
                    r"(?<![\w])" + re.escape(term) + tail, text, re.IGNORECASE
                ):
                    span = text[max(0, m.start() - 20) : m.end() + 20]
                    if not any(
                        rel.endswith(f) and a.lower() in span.lower()
                        for f, a in self.allowed
                    ):
                        hits.append(f"{rel}: {term}: {span!r}")
            for m in generic.finditer(text):
                hits.append(f"{rel}: address or account path: {m.group(0)}")
        return hits


def notion_to_md(text: str) -> str:
    """Turn Notion-flavored Markdown escapes into plain Markdown."""
    text = re.sub(r"\\([\[\]_$|*#!~`>])", r"\1", text)
    text = re.sub(r"<code>(.*?)</code>", r"`\1`", text)
    return text.replace("<br />", "\n")


def read_register(path: Path) -> tuple[str, str]:
    """Accept a saved Notion fetch result (JSON) or a Markdown export of the page."""
    raw = path.read_text(encoding="utf-8")
    stamp = "date not recorded"
    try:
        text = json.loads(raw)["text"]
        m = re.search(r"as of ([0-9T:.\-]+Z)", text)
        stamp = m.group(1) if m else stamp
        body = re.search(r"<content>\n(.*)\n</content>", text, re.DOTALL).group(1)
    except (json.JSONDecodeError, KeyError, AttributeError, TypeError):
        body = raw
    if "## Entries\n" not in body:
        sys.exit(
            f"{path}: no '## Entries' heading, so this isn't the Voice Corrections Register"
        )
    return body.split("## Entries\n", 1)[1].lstrip("\n"), stamp


SNAPSHOT_HEAD = """# Voice Corrections Register (Portable Snapshot)

Version 1.0 portable, owner Rock Lambros. Snapshot of the Notion page "Voice Corrections Register" as fetched {stamp}. Built for the portable edition of coffee-peer-voice on an account with no Notion connector.

Client names, client staff, client customers, and client network addresses are replaced with placeholders such as [Client A], [Client A CFO], and [client IP]. A placeholder is never a name to use in a draft.

This copy is read-only. It doesn't update itself, and edits made to it in a session vanish when the session ends. New corrections follow "The Corrections Register" section of SKILL.md: printed under NOT LOGGED for Rock to carry over to the Notion page by hand.

Entry format:

```
### YYYY-MM-DD, channel
Skill wrote: <the sentence as drafted>
Rock's fix: <the sentence as sent>
Rule: <rule id from slop_lint, the skill section, or "no rule">
```

## Entries

"""

AAS_NOTE = (
    "\n\nPortable edition note: built from 1.16 for a Claude account with no Notion connector and no web fetch. "
    "Nothing in this edition reads a web page or a connector. It differs from the main edition in four ways. "
    "Every script path is written from this skill's own folder (SKILL_DIR below), so it works in any account. "
    "The cleaner scripts from the clean-user-facing-text skill ship in `scripts/clean/`, and `slop_pass.py` uses "
    "them on its own. The person counter ships as `scripts/slop_person_count.py` in place of the copy this file "
    "used to write to `/tmp`. Client names, client staff, client customers, and client network addresses are "
    "redacted from every file. Rebuild this edition from the main one when the main one changes, because a hand "
    "edit here drifts."
)

CPV_NOTE = (
    "\n\nPortable edition note: built from 1.20 for a Claude account with no Notion connector and no web fetch. "
    "Nothing in this edition reads a web page or a connector. The corrections register ships as a redacted "
    "snapshot in `references/voice-corrections-register.md`, and new corrections get printed for Rock to carry "
    "over by hand, because this account can't write to the Notion page. The linter (slop_lint 1.9.0 from "
    "anti-ai-slop 1.16) ships in `scripts/`, and the cleaner scripts from clean-user-facing-text ship in "
    "`scripts/clean/`, so every gate runs with no other skill installed. Every script path is written from this "
    "skill's own folder. Client names, client staff, client customers, and client network addresses are redacted "
    "from every file. The twelfth note's byte-identical rule covers the main edition's two copies. This edition "
    "gets rebuilt from them, never hand edited."
)

CPV_REGISTER = """## The Corrections Register

The corrections log ships with this skill as `references/voice-corrections-register.md`, a snapshot of Rock's Notion page "Voice Corrections Register". It holds pairs of a sentence this skill produced and the fix Rock made, newest first. Read it before every draft and treat each pair as a tell to keep out of the draft. Client and customer names in it are replaced with placeholders like [Client A], and a placeholder never goes into a draft as if it were a name.

This account can't reach the Notion page, so a correction can't be logged from here. When Rock corrects a sentence you wrote, print the entry in the format the snapshot shows, under the line `NOT LOGGED: no register on this account. Paste into the Voice Corrections Register.`, so he can carry it over. Never tell Rock a correction is logged from this account. Never edit this skill's files on disk as a way to log one, because that copy disappears when the session ends and the edit only looks like it worked. That one mistake is how a month of corrections got lost.

"""


def build_aas(src: Path, root: Path, red: Redactor) -> None:
    shutil.copytree(
        src / "anti-ai-slop",
        root,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"),
    )
    (root / "scripts" / "clean").mkdir()
    for s in CLEAN_SCRIPTS:
        shutil.copy2(
            src / "clean-user-facing-text" / "scripts" / s,
            root / "scripts" / "clean" / s,
        )

    md = (root / "SKILL.md").read_text(encoding="utf-8")
    md = edit(md, "  version: '1.16.0'", "  version: '1.16.0-portable'", "aas")
    md = edit(
        md,
        "Version 1.16, owner Rock Lambros.",
        "Version 1.16 portable, owner Rock Lambros.",
        "aas",
    )
    md = edit(
        md, "`anti-ai-slop v1.16 loaded`", "`anti-ai-slop v1.16 portable loaded`", "aas"
    )
    md = edit(
        md,
        "the ADVISORY disposition rule, and the paid-detector ban.",
        "the ADVISORY disposition rule, and the paid-detector ban." + AAS_NOTE,
        "aas",
    )
    md = re.sub(ACCOUNT_RX + "anti-ai-slop", "SKILL_DIR", md)
    md = edit(
        md,
        "When the Skill tool printed a different base directory for this skill (another machine or account), use that folder's literal path in place of the one above, still written out in full.",
        "SKILL_DIR stands for the base directory the Skill tool printed when it loaded this skill. Write that folder's literal path in its place, in full, in every call, because a shell variable holding it matches no allow rule.",
        "aas",
    )
    md = edit(
        md,
        "The path and `-I` rules above apply to slop_pass too, and it needs its own allow rule.",
        "The path and `-I` rules above apply to slop_pass too, and it needs its own allow rule. It uses the cleaner scripts bundled in `scripts/clean/`, so no other skill has to be installed.",
        "aas",
    )

    # Person counter: lift the source embedded in SKILL.md into scripts/ and point the section at it.
    m = re.search(
        r"```python\n(#!/usr/bin/env python3\n\"\"\"slop_person_count.*?)```\n",
        md,
        re.DOTALL,
    )
    if not m or md.count('"""slop_person_count') != 1:
        sys.exit("aas: embedded slop_person_count source not found exactly once")
    counter = edit(
        m.group(1),
        "Ships inside anti-ai-slop SKILL.md (1.13).\nUsage: python3 -I /tmp/slop_person_count.py FILE",
        "Ships as anti-ai-slop scripts/slop_person_count.py (portable 1.16).\nUsage: python3 -I <skill dir>/scripts/slop_person_count.py FILE",
        "counter",
    )
    (root / "scripts" / "slop_person_count.py").write_text(counter, encoding="utf-8")
    md = (
        md[: m.start()]
        + "The counter's source is `scripts/slop_person_count.py`.\n"
        + md[m.end() :]
    )
    md = edit(
        md,
        "A skill update card can edit only this file, so the counter ships here as source, and the session writes it to a fixed path before running it.",
        "In this portable edition the counter ships as `scripts/slop_person_count.py`, so nothing gets written to `/tmp`.",
        "aas",
    )
    md = edit(
        md,
        "First write the script below with the Write tool to `/tmp/slop_person_count.py`, exactly as shown. Overwriting an earlier copy is fine. Then run it as one Bash call",
        "Run it as one Bash call",
        "aas",
    )
    md = edit(
        md,
        "python3 -I /tmp/slop_person_count.py FILE",
        "python3 -I SKILL_DIR/scripts/slop_person_count.py FILE",
        "aas",
    )
    md = edit(
        md,
        "The fixed path exists for the allow rule, `Bash(python3 -I /tmp/slop_person_count.py *)`, for the reason in the fifth maintainer note.",
        "Its allow rule is `Bash(python3 -I SKILL_DIR/scripts/slop_person_count.py *)` with SKILL_DIR written out, for the reason in the fifth maintainer note.",
        "aas",
    )
    (root / "SKILL.md").write_text(red.apply(md, "all"), encoding="utf-8")

    sp = (root / "scripts" / "slop_pass.py").read_text(encoding="utf-8")
    sp = edit(sp, '__version__ = "1.0.0"', '__version__ = "1.0.1"', "slop_pass")
    sp = edit(
        sp,
        'DEFAULT_CLEAN_DIR = HERE.parent.parent / "clean-user-facing-text" / "scripts"',
        "# Portable edition (1.0.1): prefer the cleaner bundled in scripts/clean, so the\n"
        "# pass runs on an account with no clean-user-facing-text skill installed.\n"
        '_BUNDLED_CLEAN_DIR = HERE / "clean"\n'
        '_SIBLING_CLEAN_DIR = HERE.parent.parent / "clean-user-facing-text" / "scripts"\n'
        "DEFAULT_CLEAN_DIR = _BUNDLED_CLEAN_DIR if _BUNDLED_CLEAN_DIR.is_dir() else _SIBLING_CLEAN_DIR",
        "slop_pass",
    )
    (root / "scripts" / "slop_pass.py").write_text(sp, encoding="utf-8")

    tp = (root / "tests" / "test_slop_pass.py").read_text(encoding="utf-8")
    tp = edit(
        tp,
        'COMPANION = SCRIPT.parent.parent.parent / "clean-user-facing-text" / "scripts"',
        'COMPANION = SCRIPT.parent / "clean"  # portable edition: bundled cleaner',
        "test_slop_pass",
    )
    (root / "tests" / "test_slop_pass.py").write_text(tp, encoding="utf-8")

    for p in [root / "scripts" / "slop_lint.py", *(root / "references").glob("*.md")]:
        p.write_text(red.apply(p.read_text(encoding="utf-8"), "all"), encoding="utf-8")
    rc = root / "references" / "register-coverage.md"
    rc.write_text(
        rc.read_text(encoding="utf-8").rstrip()
        + "\n\nPortable edition: the register itself ships, redacted, in the portable coffee-peer-voice as `references/voice-corrections-register.md`.\n",
        encoding="utf-8",
    )


def build_cpv(
    src: Path, root: Path, red: Redactor, register: str, samples: Path
) -> None:
    (root / "references").mkdir(parents=True)
    (root / "scripts" / "clean").mkdir(parents=True)
    shutil.copy2(
        src / "coffee-peer-voice" / "references" / "voice-guide.md",
        root / "references" / "voice-guide.md",
    )
    shutil.copy2(samples, root / "references" / "voice-samples.md")
    (root / "references" / "voice-corrections-register.md").write_text(
        register, encoding="utf-8"
    )
    shutil.copy2(
        src / "anti-ai-slop" / "scripts" / "slop_lint.py",
        root / "scripts" / "slop_lint.py",
    )
    for s in CLEAN_SCRIPTS:
        shutil.copy2(
            src / "clean-user-facing-text" / "scripts" / s,
            root / "scripts" / "clean" / s,
        )

    md = (src / "coffee-peer-voice" / "SKILL.md").read_text(encoding="utf-8")
    md = edit(
        md,
        "Version 1.20, owner Rock Lambros.",
        "Version 1.20 portable, owner Rock Lambros.",
        "cpv",
    )
    md = edit(
        md,
        "`coffee-peer-voice v1.20 loaded`",
        "`coffee-peer-voice v1.20 portable loaded`",
        "cpv",
    )
    md = edit(
        md,
        "carries the lintable half as H-ORDER-QUESTION, H-LABEL-NOUN, and five advisories.",
        "carries the lintable half as H-ORDER-QUESTION, H-LABEL-NOUN, and five advisories."
        + CPV_NOTE,
        "cpv",
    )
    m = re.search(
        r"## The Corrections Register\n.*?(?=## Calibrating\n)", md, re.DOTALL
    )
    if not m or md.count("## The Corrections Register\n") != 1:
        sys.exit("cpv: Corrections Register section not found exactly once")
    md = md[: m.start()] + CPV_REGISTER + md[m.end() :]
    md = edit(
        md,
        "Then run the linter that ships with `anti-ai-slop`. It lives at `scripts/slop_lint.py` inside that skill's folder, next to the SKILL.md you open for its stamp. Run it as one Bash call written exactly like this, under the invocation rules in step 2 of the Finishing Pass, with DRAFT replaced by the draft's absolute path and PROFILE by one of the profiles below:",
        "Then run the copy of slop_lint 1.9.0 that ships with this skill at `scripts/slop_lint.py`. Run it as one Bash call written exactly like this, under the invocation rules in step 2 of the Finishing Pass, with DRAFT replaced by the draft's absolute path, PROFILE by one of the profiles below, and SKILL_DIR by the base directory the Skill tool printed when it loaded this skill, written out in full:",
        "cpv",
    )
    md = re.sub(
        ACCOUNT_RX + "anti-ai-slop/scripts/slop_lint.py",
        "SKILL_DIR/scripts/slop_lint.py",
        md,
    )
    md = re.sub(
        ACCOUNT_RX + "clean-user-facing-text/scripts/", "SKILL_DIR/scripts/clean/", md
    )
    md = edit(
        md,
        "Then run the `anti-ai-slop` skill in detect mode for what a script cannot see: metaphor, novelty inflation, gap-filling, synonym cycling. Flag only, no rewrite. Open that file and print its stamp the same way you printed this one.",
        'Then read for what a script cannot see: metaphor, novelty inflation, gap-filling, synonym cycling. Flag only, no rewrite. When the `anti-ai-slop` skill is installed in this account, run it in detect mode for this read, and open its file and print its stamp the same way you printed this one. When it isn\'t, do the read yourself against the "What to Avoid" list in this file and say in one line that detect mode ran from this file.',
        "cpv",
    )
    md = edit(
        md,
        "Invoke the `clean-user-facing-text` skill, open its SKILL.md, and run its workflow on the draft with the bindings below. Its folder sits next to this skill's folder, the same way `anti-ai-slop` does.",
        "It runs the cleaner scripts from the `clean-user-facing-text` skill, bundled in this skill's `scripts/clean/` folder, with the bindings below. The calls below are the whole workflow, so the cleaner's own SKILL.md isn't needed.",
        "cpv",
    )
    md = edit(
        md,
        "The paths below are the claude.ai and Cowork paths. When the Skill tool printed a different base directory for this skill, build the same paths from the folder that holds it, and still write them out in full in every call.",
        "In the paths below, SKILL_DIR is the base directory the Skill tool printed when it loaded this skill. Write it out in full in every call.",
        "cpv",
    )
    md = edit(
        md,
        "The linter lives in the `anti-ai-slop` folder, so its path differs from the cleaner scripts in steps 3 and 5:",
        "The linter sits in `scripts/`, one level above the cleaner scripts in steps 3 and 5:",
        "cpv",
    )
    if re.search(ACCOUNT_RX, md):
        sys.exit("cpv: an account path is still in SKILL.md")
    (root / "SKILL.md").write_text(red.apply(md, "all"), encoding="utf-8")
    for p in (
        root / "references" / "voice-guide.md",
        root / "references" / "voice-samples.md",
        root / "scripts" / "slop_lint.py",
    ):
        p.write_text(red.apply(p.read_text(encoding="utf-8"), "all"), encoding="utf-8")


def zip_folder(folder: Path, zpath: Path) -> None:
    """One top-level folder and one SKILL.md, which is what the claude.ai uploader accepts."""
    zpath.unlink(missing_ok=True)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                z.write(p, (Path(folder.name) / p.relative_to(folder)).as_posix())
    names = zipfile.ZipFile(zpath).namelist()
    if {n.split("/", 1)[0] for n in names} != {folder.name} or sum(
        n.endswith("/SKILL.md") for n in names
    ) != 1:
        sys.exit(f"{zpath.name}: zip layout check failed")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--skills",
        required=True,
        type=Path,
        help="folder holding anti-ai-slop, coffee-peer-voice, and clean-user-facing-text",
    )
    ap.add_argument(
        "--register",
        required=True,
        type=Path,
        help="saved Notion fetch result (JSON) or Markdown export of the Voice Corrections Register",
    )
    ap.add_argument(
        "--redactions",
        required=True,
        type=Path,
        help="local redaction file, never committed (see README)",
    )
    ap.add_argument(
        "--voice-samples",
        type=Path,
        help="defaults to SKILLS/coffee-peer-voice/references/voice-samples.md",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path.cwd(),
        help="where the two zips go (default: current folder)",
    )
    ap.add_argument("--version", action="version", version=f"build_portable {VERSION}")
    args = ap.parse_args()

    src = args.skills.resolve()
    for name, marker in EXPECTED.items():
        if marker not in (src / name / "SKILL.md").read_text(encoding="utf-8"):
            sys.exit(
                f"{name}: expected '{marker}' in SKILL.md. The anchors fit that release only, so update them first."
            )
    samples = (
        args.voice_samples
        or src / "coffee-peer-voice" / "references" / "voice-samples.md"
    ).resolve()
    if not samples.is_file():
        sys.exit(
            f"voice samples not found at {samples}. Pass --voice-samples, since the repo leaves that file out."
        )
    red = Redactor(args.redactions)
    entries, stamp = read_register(args.register)
    register = red.apply(
        SNAPSHOT_HEAD.format(stamp=stamp) + notion_to_md(entries).rstrip() + "\n",
        "register",
    )

    with tempfile.TemporaryDirectory() as tmp:
        build = Path(tmp)
        aas = build / "aas" / "anti-ai-slop"
        cpv = build / "cpv" / "coffee-peer-voice"
        aas.parent.mkdir(parents=True)
        build_aas(src, aas, red)
        build_cpv(src, cpv, red, register, samples)
        hits = red.scan(build, str(src))
        for h in hits:
            print("LEAK", h)
        if hits:
            sys.exit(f"{len(hits)} leak hits, nothing zipped")
        args.out.mkdir(parents=True, exist_ok=True)
        for folder, zname in (
            (aas, "anti-ai-slop-portable.zip"),
            (cpv, "coffee-peer-voice-portable.zip"),
        ):
            zip_folder(folder, args.out / zname)
            print("built", args.out / zname)


if __name__ == "__main__":
    main()
