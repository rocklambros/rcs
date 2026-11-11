"""Tests for slop_pass.py. Version 1.0.0, owner Rock Lambros.

Run from the repo root:
    python3 -m pytest -q backups/claude-ai-skills/anti-ai-slop/tests -p no:cacheprovider

The clean-out test needs clean-user-facing-text installed as a sibling skill
folder, so it skips in the RCS backup, where that skill isn't stored.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "slop_pass.py"
COMPANION = SCRIPT.parent.parent.parent / "clean-user-facing-text" / "scripts"
NO_COMPANION = "/nonexistent/clean-user-facing-text/scripts"
CLEAN_PROSE = "We shipped the fix on Tuesday and the error rate fell to zero.\n"
SLOP_PROSE = "We need to delve into this, because the design is robust.\n"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def draft(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_clean_prose_exits_zero(tmp_path: Path) -> None:
    res = run(str(draft(tmp_path, CLEAN_PROSE)), "--profile", "blog", "--clean-dir", NO_COMPANION)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "HARD=0" in res.stdout


def test_hard_tell_exits_one(tmp_path: Path) -> None:
    res = run(str(draft(tmp_path, SLOP_PROSE)), "--profile", "blog", "--clean-dir", NO_COMPANION)
    assert res.returncode == 1, res.stdout + res.stderr
    assert "H-VOCAB" in res.stdout


def test_advisory_only_reports_and_exits_zero(tmp_path: Path) -> None:
    res = run(
        str(draft(tmp_path, SLOP_PROSE)),
        "--profile",
        "blog",
        "--advisory-only",
        "--clean-dir",
        NO_COMPANION,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert "H-VOCAB" in res.stdout


def test_missing_file_exits_two(tmp_path: Path) -> None:
    res = run(str(tmp_path / "missing.md"), "--profile", "blog")
    assert res.returncode == 2
    assert "no such file" in res.stderr


def test_clean_out_must_be_a_new_file(tmp_path: Path) -> None:
    path = draft(tmp_path, CLEAN_PROSE)
    res = run(str(path), "--profile", "blog", "--clean-out", str(path))
    assert res.returncode == 2
    assert "new file" in res.stderr


def test_missing_companion_skips_and_still_lints(tmp_path: Path) -> None:
    out = tmp_path / "final.md"
    res = run(
        str(draft(tmp_path, CLEAN_PROSE)),
        "--profile",
        "blog",
        "--clean-out",
        str(out),
        "--clean-dir",
        NO_COMPANION,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert res.stdout.count("skipped") == 2
    assert not out.exists()


@pytest.mark.skipif(
    not (COMPANION / "clean_text.py").is_file(),
    reason="clean-user-facing-text is not installed next to this skill",
)
def test_clean_out_strips_zero_width_space(tmp_path: Path) -> None:
    out = tmp_path / "final.md"
    res = run(
        str(draft(tmp_path, "Plain​ text.\n")),
        "--profile",
        "blog",
        "--clean-out",
        str(out),
        "--no-stylometry",
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert "removed=1" in res.stdout
    assert "​" not in out.read_text(encoding="utf-8")
