"""Tests for lint_links.

Validates that markdown links from SKILL.md to bundled reference files
do not go more than one level deep (per Anthropic best-practices doc:
'Claude may partially read files when they're referenced from other
referenced files').
"""
from pathlib import Path
from tools.lint_links import lint_links


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_skill_with_direct_reference_passes(tmp_path):
    skill = tmp_path / "skills/workflow/example/SKILL.md"
    write_file(skill, "# Skill\n\nSee [reference/topic.md](reference/topic.md).")
    write_file(tmp_path / "skills/workflow/example/reference/topic.md", "# Topic")
    errors = lint_links(skill.parent)
    assert errors == []


def test_skill_with_two_level_deep_reference_fails(tmp_path):
    """SKILL.md links to advanced.md which links to details.md — fails."""
    skill = tmp_path / "skills/workflow/example/SKILL.md"
    write_file(skill, "# Skill\n\nSee [reference/advanced.md](reference/advanced.md).")
    write_file(
        tmp_path / "skills/workflow/example/reference/advanced.md",
        "# Advanced\n\nSee [details.md](details.md) for more.",
    )
    write_file(tmp_path / "skills/workflow/example/reference/details.md", "# Details")
    errors = lint_links(skill.parent)
    assert any("one level deep" in e.message.lower() or "two-level" in e.message.lower() for e in errors)


def test_skill_with_broken_reference_fails(tmp_path):
    skill = tmp_path / "skills/workflow/example/SKILL.md"
    write_file(skill, "# Skill\n\nSee [reference/missing.md](reference/missing.md).")
    errors = lint_links(skill.parent)
    assert any("broken" in e.message.lower() or "not found" in e.message.lower() for e in errors)


def test_external_url_ignored(tmp_path):
    skill = tmp_path / "skills/workflow/example/SKILL.md"
    write_file(skill, "# Skill\n\nSee [Anthropic](https://platform.claude.com/docs/).")
    errors = lint_links(skill.parent)
    assert errors == []
