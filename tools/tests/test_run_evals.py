"""Tests for run_evals.

Verifies the eval harness parses scenario JSONs, dispatches to a mocked
Anthropic client, judges completions with a mocked judge, and applies
pass thresholds per docs/eval-protocol.md.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.run_evals import (
    EvalScenario,
    JudgeResult,
    load_scenarios,
    judge_response,
    check_threshold,
)


def write_scenario(tmp_path: Path, filename: str, payload: dict) -> Path:
    p = tmp_path / filename
    p.write_text(json.dumps(payload))
    return p


def test_load_scenarios_returns_three(tmp_path):
    evals_dir = tmp_path / "evals"
    evals_dir.mkdir()
    for i, kind in enumerate(["happy-path", "edge-case", "anti-trigger"], start=1):
        write_scenario(evals_dir, f"0{i}-{kind}.json", {
            "skill": "a-skill",
            "scenario_id": f"0{i}-{kind}",
            "scenario_kind": kind,
            "query": "test query",
            "files": [],
            "expected_behavior": ["item 1", "item 2", "item 3"],
        })
    scenarios = load_scenarios(evals_dir)
    assert len(scenarios) == 3
    assert {s.scenario_kind for s in scenarios} == {"happy-path", "edge-case", "anti-trigger"}


def test_judge_response_parses_strict_json(tmp_path):
    """judge_response uses a mocked Anthropic client; verifies it parses
    the expected JSON-formatted judge output."""
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=json.dumps({
            "results": [
                {"item": "item 1", "pass": True, "rationale": "yes"},
                {"item": "item 2", "pass": False, "rationale": "no"},
                {"item": "item 3", "pass": True, "rationale": "yes"},
            ]
        }))]
    )
    scenario = EvalScenario(
        skill="a-skill",
        scenario_id="01-happy-path",
        scenario_kind="happy-path",
        query="q",
        files=[],
        expected_behavior=["item 1", "item 2", "item 3"],
    )
    result = judge_response(
        scenario=scenario,
        skill_body="# Skill",
        completion="some response",
        judge_client=mock_client,
    )
    assert isinstance(result, JudgeResult)
    assert result.score == "2/3"


def test_threshold_haiku_happy_path_passes_2_of_3():
    assert check_threshold(model="claude-haiku-4-5-20251001", scenario_kind="happy-path", passed=2, total=3) is True


def test_threshold_haiku_happy_path_fails_1_of_3():
    assert check_threshold(model="claude-haiku-4-5-20251001", scenario_kind="happy-path", passed=1, total=3) is False


def test_threshold_sonnet_happy_path_requires_3_of_3():
    assert check_threshold(model="claude-sonnet-4-6", scenario_kind="happy-path", passed=2, total=3) is False
    assert check_threshold(model="claude-sonnet-4-6", scenario_kind="happy-path", passed=3, total=3) is True


def test_threshold_sonnet_anti_trigger_allows_2_of_3():
    assert check_threshold(model="claude-sonnet-4-6", scenario_kind="anti-trigger", passed=2, total=3) is True


def test_threshold_opus_requires_3_of_3_everywhere():
    for kind in ["happy-path", "edge-case", "anti-trigger"]:
        assert check_threshold(model="claude-opus-4-7", scenario_kind=kind, passed=2, total=3) is False
        assert check_threshold(model="claude-opus-4-7", scenario_kind=kind, passed=3, total=3) is True
