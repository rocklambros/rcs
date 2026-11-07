"""Tests for the Codex port install layer.

The sidecar records what was built from what. The gate decides whether a
target directory may be replaced. The swap is atomic and rolls back. The
check types are the vocabulary the pipeline reports in.
"""
import os
from pathlib import Path

import pytest

from tools.codex_port.install import (
    SIDECAR,
    CheckReport,
    CheckStatus,
    Gate,
    InstallError,
    Sidecar,
    gate,
    install,
    installed_sha256,
    read_sidecar,
    stage_root,
    write_sidecar,
)
from tools.codex_port.sources import tree_sha256
from tools.tests.codex_port_fixtures import MINIMAL_SKILL_MD, make_skill_dir

PORTED_SKILL_MD = (
    "---\nname: a-skill\ndescription: Does a thing.\nmetadata:\n"
    "  ported-from: rcs:workflow/a-skill\n  ported-to-codex: '2026-11-06'\n---\n\n# A skill\n\nBody.\n"
)


def sidecar_for(skill_dir: Path, output_sha256: str | None = None) -> Sidecar:
    return Sidecar(
        name=skill_dir.name,
        source="rcs:workflow/a-skill",
        source_sha256="a" * 64,
        output_sha256=output_sha256 or installed_sha256(skill_dir),
        ported_on="2026-11-06",
    )


def skills_root(tmp_path: Path) -> Path:
    root = tmp_path / "codex" / "skills"
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_sidecar_roundtrip(tmp_path):
    skill_dir = make_skill_dir(tmp_path, "a-skill", PORTED_SKILL_MD)
    sidecar = sidecar_for(skill_dir)
    write_sidecar(skill_dir, sidecar)
    assert (skill_dir / SIDECAR).is_file()
    assert read_sidecar(skill_dir) == sidecar
    assert read_sidecar(make_skill_dir(tmp_path / "other", "a-skill", PORTED_SKILL_MD)) is None


def test_malformed_sidecar_raises(tmp_path):
    skill_dir = make_skill_dir(tmp_path, "a-skill", PORTED_SKILL_MD)
    (skill_dir / SIDECAR).write_text("{not json")
    with pytest.raises(InstallError, match=SIDECAR.replace(".", r"\.")):
        read_sidecar(skill_dir)


def test_installed_sha256_ignores_sidecar(tmp_path):
    skill_dir = make_skill_dir(tmp_path, "a-skill", PORTED_SKILL_MD, {"scripts/x.py": "1\n"})
    before = installed_sha256(skill_dir)
    write_sidecar(skill_dir, sidecar_for(skill_dir))
    assert installed_sha256(skill_dir) == before
    assert before == tree_sha256(skill_dir)


def test_stage_root_sits_outside_skills_root(tmp_path):
    assert stage_root(tmp_path / "codex") == tmp_path / "codex" / ".rcs-port-stage"


@pytest.mark.parametrize(
    "case,expected",
    [
        ("absent", Gate.ABSENT),
        ("no-skill-md", Gate.FOREIGN),
        ("foreign", Gate.FOREIGN),
        ("legacy", Gate.PORTED_LEGACY),
        ("clean", Gate.PORTED_CLEAN),
        ("edited", Gate.PORTED_EDITED),
    ],
)
def test_gate_absent_foreign_legacy_clean_edited(tmp_path, case, expected):
    target = skills_root(tmp_path) / "a-skill"
    if case == "no-skill-md":
        target.mkdir()
    elif case == "foreign":
        make_skill_dir(target.parent, "a-skill", MINIMAL_SKILL_MD)
    elif case == "legacy":
        make_skill_dir(target.parent, "a-skill", PORTED_SKILL_MD)
    elif case == "clean":
        make_skill_dir(target.parent, "a-skill", PORTED_SKILL_MD)
        write_sidecar(target, sidecar_for(target))
    elif case == "edited":
        make_skill_dir(target.parent, "a-skill", PORTED_SKILL_MD)
        write_sidecar(target, sidecar_for(target))
        (target / "SKILL.md").write_text(PORTED_SKILL_MD + "Hand edit.\n")
    assert gate(target) is expected


def test_gate_symlink_refused_and_link_target_intact(tmp_path):
    real = make_skill_dir(tmp_path / "elsewhere", "a-skill", PORTED_SKILL_MD)
    target = skills_root(tmp_path) / "a-skill"
    target.symlink_to(real, target_is_directory=True)
    stage = make_skill_dir(stage_root(tmp_path / "codex"), "a-skill", PORTED_SKILL_MD + "New.\n")
    assert gate(target) is Gate.SYMLINK
    with pytest.raises(InstallError, match=r"symlink"):
        install(stage, target, force=True)
    assert target.is_symlink()
    assert (real / "SKILL.md").read_text() == PORTED_SKILL_MD
    assert stage.is_dir()


def test_gate_system_refused(tmp_path):
    target = skills_root(tmp_path) / ".system"
    assert gate(target) is Gate.SYSTEM
    stage = make_skill_dir(stage_root(tmp_path / "codex"), ".system", PORTED_SKILL_MD)
    with pytest.raises(InstallError, match=r"\.system"):
        install(stage, target, force=True)


def test_gate_foreign_refused(tmp_path):
    target = make_skill_dir(skills_root(tmp_path), "a-skill", MINIMAL_SKILL_MD)
    stage = make_skill_dir(stage_root(tmp_path / "codex"), "a-skill", PORTED_SKILL_MD)
    with pytest.raises(InstallError, match=r"ported-from"):
        install(stage, target, force=True)
    assert (target / "SKILL.md").read_text() == MINIMAL_SKILL_MD


def test_install_into_absent_target(tmp_path):
    target = skills_root(tmp_path) / "a-skill"
    stage = make_skill_dir(stage_root(tmp_path / "codex"), "a-skill", PORTED_SKILL_MD)
    assert install(stage, target, force=False) is Gate.ABSENT
    assert (target / "SKILL.md").read_text() == PORTED_SKILL_MD
    assert not stage.exists()


def test_install_replaces_legacy_copy(tmp_path):
    target = make_skill_dir(skills_root(tmp_path), "a-skill", PORTED_SKILL_MD, {"references/old.md": "old\n"})
    stage = make_skill_dir(stage_root(tmp_path / "codex"), "a-skill", PORTED_SKILL_MD + "New.\n")
    assert install(stage, target, force=False) is Gate.PORTED_LEGACY
    assert (target / "SKILL.md").read_text() == PORTED_SKILL_MD + "New.\n"
    assert not (target / "references" / "old.md").exists()
    assert not (stage.parent / "a-skill.old").exists()
    assert not stage.exists()


def test_install_refuses_edited_without_force_and_allows_with_force(tmp_path):
    target = make_skill_dir(skills_root(tmp_path), "a-skill", PORTED_SKILL_MD)
    write_sidecar(target, sidecar_for(target))
    (target / "SKILL.md").write_text(PORTED_SKILL_MD + "Hand edit.\n")
    stage = make_skill_dir(stage_root(tmp_path / "codex"), "a-skill", PORTED_SKILL_MD + "New.\n")
    with pytest.raises(InstallError, match=r"--force"):
        install(stage, target, force=False)
    assert (target / "SKILL.md").read_text() == PORTED_SKILL_MD + "Hand edit.\n"
    assert install(stage, target, force=True) is Gate.PORTED_EDITED
    assert (target / "SKILL.md").read_text() == PORTED_SKILL_MD + "New.\n"


def test_install_rolls_back_when_swap_fails(tmp_path, monkeypatch):
    target = make_skill_dir(skills_root(tmp_path), "a-skill", PORTED_SKILL_MD)
    stage = make_skill_dir(stage_root(tmp_path / "codex"), "a-skill", PORTED_SKILL_MD + "New.\n")
    real_replace = os.replace
    calls = []

    def flaky_replace(src, dst):
        calls.append((src, dst))
        if len(calls) == 2:
            raise OSError("disk went away")
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", flaky_replace)
    with pytest.raises(OSError, match=r"disk went away"):
        install(stage, target, force=False)
    assert (target / "SKILL.md").read_text() == PORTED_SKILL_MD
    assert not (stage.parent / "a-skill.old").exists()
    assert stage.is_dir()


def test_check_report_defaults():
    report = CheckReport(name="a-skill", status=CheckStatus.OK)
    assert report.details == ""
    assert report.info == []
    assert CheckReport(name="b", status=CheckStatus.OK).info is not report.info
