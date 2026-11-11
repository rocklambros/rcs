"""Tests for the Codex port transform layer.

Frontmatter normalization keeps the five keys Codex allows at the top
level, nests everything else under ``metadata``, and records provenance.
"""
import pytest

from tools.codex_port.manifest import Manifest, SkillEntry, SourceSpec
from tools.codex_port.transform import (
    TransformError,
    append_runtime_notes,
    load_notes,
    normalize_frontmatter,
    rewrite_path_tokens,
    rewrite_sibling_refs,
    transform_tree,
)
from tools.lint_frontmatter import parse_frontmatter
from tools.tests.codex_port_fixtures import CLAUDE_SKILL_MD, RCS_SKILL_MD, make_skill_dir


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


def test_sibling_refs_rewritten():
    assert rewrite_sibling_refs("`workflow/a` and `security/b` (planned)") == "`$a` and `$b` (planned)"


def test_non_sibling_backticks_untouched():
    text = "`scripts/x.py` and `workflow/` and workflow/a without ticks and `ml-datasci/Upper`"
    assert rewrite_sibling_refs(text) == text


def test_path_tokens_rewritten(tmp_path):
    root = tmp_path / "codex" / "skills"
    text = "python3 -I SKILL_DIR/scripts/l.py\npython3 -I SKILLS/a-skill/scripts/x.py\n`SKILLS` stands for (SKILL_DIR)\n"
    expected = (
        f"python3 -I {root.as_posix()}/a-skill/scripts/l.py\n"
        f"python3 -I {root.as_posix()}/a-skill/scripts/x.py\n"
        "`SKILLS` stands for (SKILL_DIR)\n"
    )
    assert rewrite_path_tokens(text, root, "a-skill") == expected


def test_notes_appended_once_with_exact_heading():
    out = append_runtime_notes("# T\n\nBody.\n", "- one\n- two\n\n")
    assert out == "# T\n\nBody.\n\n## Codex runtime notes\n\n- one\n- two\n"


def test_notes_refuse_double_append():
    once = append_runtime_notes("# T\n", "- one\n")
    with pytest.raises(TransformError, match=r"Codex runtime notes"):
        append_runtime_notes(once, "- one\n")


def test_load_notes_prefers_local_then_named_then_default(tmp_path):
    local = tmp_path / "local"
    tracked = tmp_path / "tracked"
    (tracked / "notes").mkdir(parents=True)
    (tracked / "notes" / "_default.md").write_text("default\n")
    assert load_notes("a-skill", (local, tracked)) == "default\n"
    (tracked / "notes" / "a-skill.md").write_text("named\n")
    assert load_notes("a-skill", (local, tracked)) == "named\n"
    (local / "notes").mkdir(parents=True)
    (local / "notes" / "a-skill.md").write_text("local\n")
    assert load_notes("a-skill", (local, tracked)) == "local\n"


def test_load_notes_missing_raises(tmp_path):
    with pytest.raises(TransformError, match=r"a-skill"):
        load_notes("a-skill", (tmp_path,))


def manifest_with_notes(tmp_path):
    tracked = tmp_path / "tracked"
    (tracked / "notes").mkdir(parents=True)
    (tracked / "notes" / "_default.md").write_text("- sibling note\n")
    return Manifest(codex_home=tmp_path / "codex", cache_roots={}, rcs_root=tmp_path / "rcs", skills={}, data_dirs=(tracked,))


def entry_for(name, path_tokens=False):
    return SkillEntry(
        name=name,
        source=SourceSpec("rcs", track="workflow"),
        display_name="A Skill",
        short_description="x" * 30,
        default_prompt=f"Use ${name}.",
        path_tokens=path_tokens,
    )


def test_transform_tree_touches_all_markdown(tmp_path):
    manifest = manifest_with_notes(tmp_path)
    skill = make_skill_dir(
        tmp_path / "stage", "a-skill", RCS_SKILL_MD,
        {"references/x.md": "See `workflow/other-skill`. SKILL_DIR/scripts/l.py\n", "scripts/x.py": "# `workflow/other-skill`\n"},
    )
    transform_tree(skill, entry_for("a-skill"), manifest, "2026-11-06")
    skill_md = (skill / "SKILL.md").read_text()
    fm, _ = parse_frontmatter(skill_md)
    assert fm["metadata"]["ported-to-codex"] == "2026-11-06"
    assert "`$other-skill`" in skill_md
    assert "`workflow/other-skill`" not in skill_md
    assert skill_md.endswith("\n## Codex runtime notes\n\n- sibling note\n")
    assert (skill / "references" / "x.md").read_text() == "See `$other-skill`. SKILL_DIR/scripts/l.py\n"
    assert (skill / "scripts" / "x.py").read_text() == "# `workflow/other-skill`\n"


def test_transform_tree_rewrites_tokens_when_enabled(tmp_path):
    manifest = manifest_with_notes(tmp_path)
    skill = make_skill_dir(tmp_path / "stage", "a-skill", CLAUDE_SKILL_MD)
    transform_tree(skill, entry_for("a-skill", path_tokens=True), manifest, "2026-11-06")
    skill_md = (skill / "SKILL.md").read_text()
    root = (tmp_path / "codex" / "skills").as_posix()
    assert f"python3 -I {root}/a-skill/scripts/l.py DRAFT" in skill_md
    assert f"python3 -I {root}/a-skill/scripts/x.py DRAFT" in skill_md
    assert "`SKILLS` stands for" in skill_md
