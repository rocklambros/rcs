"""Tests for lint_skill_md.

Validates that a SKILL.md body contains the required H2 sections per the
Layer-3 documentation contract: When to use, When NOT to use, Quick start,
Inputs / Arguments / Flags, Workflow, Outputs, Failure modes, References,
Examples, See also, Status & version. Order matters.
"""
from pathlib import Path
from tools.lint_skill_md import lint_skill_md


REQUIRED_SECTIONS = [
    "When to use",
    "When NOT to use",
    "Quick start",
    "Inputs / Arguments / Flags",
    "Workflow",
    "Outputs",
    "Failure modes",
    "References",
    "Examples",
    "See also",
    "Status & version",
]


def make_skill(tmp_path: Path, sections: list[str]) -> Path:
    """Helper: build a minimal SKILL.md with frontmatter and given H2 sections."""
    body = "\n\n".join(f"## {s}\n\ncontent for {s}" for s in sections)
    text = f"""---
name: a-skill
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22
---

# Title

{body}
"""
    p = tmp_path / "SKILL.md"
    p.write_text(text)
    return p


def test_all_required_sections_in_order_passes(tmp_path):
    p = make_skill(tmp_path, REQUIRED_SECTIONS)
    errors = lint_skill_md(p)
    assert errors == []


def test_missing_section_fails(tmp_path):
    p = make_skill(tmp_path, [s for s in REQUIRED_SECTIONS if s != "Failure modes"])
    errors = lint_skill_md(p)
    assert any("Failure modes" in e.message for e in errors)


def test_section_out_of_order_fails(tmp_path):
    out_of_order = REQUIRED_SECTIONS.copy()
    out_of_order[0], out_of_order[2] = out_of_order[2], out_of_order[0]
    p = make_skill(tmp_path, out_of_order)
    errors = lint_skill_md(p)
    assert any("order" in e.message.lower() for e in errors)


def test_body_over_500_lines_fails(tmp_path):
    huge = ["body line"] * 600
    text = f"""---
name: a-skill
description: A description.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist]
evidence: []
last-updated: 2026-05-22
---

# Title

""" + "\n".join(huge)
    p = tmp_path / "SKILL.md"
    p.write_text(text)
    errors = lint_skill_md(p)
    assert any("500 lines" in e.message for e in errors)


def test_extra_section_allowed(tmp_path):
    sections = REQUIRED_SECTIONS + ["Bonus section"]
    p = make_skill(tmp_path, sections)
    errors = lint_skill_md(p)
    assert errors == []
