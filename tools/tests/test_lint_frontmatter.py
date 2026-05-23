"""Tests for lint_frontmatter.

The linter parses YAML frontmatter from a SKILL.md path and validates
Anthropic-required fields (name, description) plus RCS custom fields
(version, status, track, audience, evidence, last-updated).
"""
import pytest
from pathlib import Path
from tools.lint_frontmatter import lint_frontmatter, LintError


def write_skill_md(tmp_path: Path, frontmatter: str, body: str = "# Title\n\nbody") -> Path:
    """Helper: write a SKILL.md with the given frontmatter and body."""
    p = tmp_path / "SKILL.md"
    p.write_text(f"---\n{frontmatter}\n---\n\n{body}\n")
    return p


def test_valid_frontmatter_passes(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: selecting-statistical-test
description: >
  Walks a decision tree from data characteristics to a recommended test.
  Use when the user has a hypothesis and data and needs to commit to a test.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, stats-student]
evidence: [DU-MSDSAI-4441-Final]
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert errors == []


def test_missing_name_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("name" in e.message for e in errors)


def test_name_over_64_chars_fails(tmp_path):
    long_name = "x" * 65
    p = write_skill_md(tmp_path, frontmatter=f"""\
name: {long_name}
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("64 characters" in e.message for e in errors)


def test_name_with_reserved_word_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: anthropic-helper
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("reserved" in e.message.lower() for e in errors)


def test_name_with_uppercase_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: SelectingTest
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("lowercase" in e.message.lower() for e in errors)


def test_description_over_1024_chars_fails(tmp_path):
    long_desc = "x" * 1025
    p = write_skill_md(tmp_path, frontmatter=f"""\
name: a-skill
description: {long_desc}
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("1024 characters" in e.message for e in errors)


def test_description_first_person_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: a-skill
description: I can help you process spreadsheets.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("third-person" in e.message.lower() for e in errors)


def test_invalid_status_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: a-skill
description: A description.
version: 0.1.0
status: maybe-someday
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("status" in e.message for e in errors)


def test_invalid_track_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: a-skill
description: A description.
version: 0.1.0
status: shipped
track: random-track
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("track" in e.message for e in errors)


def test_missing_version_fails(tmp_path):
    p = write_skill_md(tmp_path, frontmatter="""\
name: a-skill
description: A description.
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22""")
    errors = lint_frontmatter(p)
    assert any("version" in e.message for e in errors)


def test_no_frontmatter_fails(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("# No frontmatter here\n\nbody\n")
    errors = lint_frontmatter(p)
    assert any("frontmatter" in e.message.lower() for e in errors)
