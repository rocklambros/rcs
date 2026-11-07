"""Tests for the Codex port transform layer.

Frontmatter normalization keeps the five keys Codex allows at the top
level, nests everything else under ``metadata``, and records provenance.
"""
import pytest

from tools.codex_port.transform import TransformError, normalize_frontmatter
from tools.lint_frontmatter import parse_frontmatter
from tools.tests.codex_port_fixtures import CLAUDE_SKILL_MD, RCS_SKILL_MD


def body_of(text: str) -> str:
    end = text.find("\n---\n", 4)
    return text[end + len("\n---\n"):]


def test_rcs_fields_nest_under_metadata():
    out = normalize_frontmatter(RCS_SKILL_MD, "rcs:workflow/a-skill", "2026-11-06")
    fm, errors = parse_frontmatter(out)
    assert errors == []
    assert list(fm) == ["name", "description", "metadata"]
    assert fm["metadata"]["track"] == "workflow"
    assert fm["metadata"]["audience"] == ["skill-author"]
    assert fm["metadata"]["ported-from"] == "rcs:workflow/a-skill"
    assert fm["metadata"]["ported-to-codex"] == "2026-11-06"
    assert list(fm["metadata"])[-2:] == ["ported-from", "ported-to-codex"]


def test_claude_fields_nest_under_metadata():
    out = normalize_frontmatter(CLAUDE_SKILL_MD, "claude.ai:Claude/a-skill", "2026-11-06")
    fm, _ = parse_frontmatter(out)
    assert fm["metadata"]["version"] == "0.1 (draft)"
    assert fm["metadata"]["owner"] == "Rock"


def test_existing_metadata_merges_not_replaced():
    text = "---\nname: a-skill\ndescription: D.\nmetadata:\n  owner: Rock\nversion: '1.0'\n---\n\nBody.\n"
    fm, _ = parse_frontmatter(normalize_frontmatter(text, "dir:~/x/a-skill", "2026-11-06"))
    assert list(fm["metadata"]) == ["owner", "version", "ported-from", "ported-to-codex"]
    assert fm["metadata"]["owner"] == "Rock"


def test_allowed_keys_stay_top_level():
    text = "---\nname: a-skill\ndescription: D.\nlicense: MIT\nallowed-tools: [Bash]\n---\n\nBody.\n"
    fm, _ = parse_frontmatter(normalize_frontmatter(text, "dir:~/x/a-skill", "2026-11-06"))
    assert list(fm) == ["name", "description", "license", "allowed-tools", "metadata"]
    assert fm["license"] == "MIT"
    assert fm["allowed-tools"] == ["Bash"]


def test_body_is_byte_identical():
    out = normalize_frontmatter(RCS_SKILL_MD, "rcs:workflow/a-skill", "2026-11-06")
    assert body_of(out) == body_of(RCS_SKILL_MD)


def test_unparseable_frontmatter_raises_with_parser_message():
    text = "---\nname: a-skill\ndescription: Prefer the specialists when they fit: adversarial-premortem for a spec.\n---\n\nBody.\n"
    with pytest.raises(TransformError, match=r"mapping values"):
        normalize_frontmatter(text, "claude.ai:Claude/a-skill", "2026-11-06")


def test_description_is_not_touched():
    long_description = "x" * 1030
    text = f"---\nname: a-skill\ndescription: {long_description}\n---\n\nBody.\n"
    fm, _ = parse_frontmatter(normalize_frontmatter(text, "dir:~/x/a-skill", "2026-11-06"))
    assert fm["description"] == long_description


def test_output_is_stable():
    once = normalize_frontmatter(RCS_SKILL_MD, "rcs:workflow/a-skill", "2026-11-06")
    twice = normalize_frontmatter(once, "rcs:workflow/a-skill", "2026-11-06")
    assert twice == once


def test_long_description_stays_on_one_line():
    text = "---\nname: a-skill\ndescription: " + ("word " * 60).strip() + "\n---\n\nBody.\n"
    out = normalize_frontmatter(text, "dir:~/x/a-skill", "2026-11-06")
    assert out.count("\n---\n") == 1
    assert sum(1 for line in out.split("\n---\n")[0].splitlines() if line.startswith("description:")) == 1
    assert len(out.split("\n---\n")[0].splitlines()) == 6
