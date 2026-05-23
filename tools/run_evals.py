"""Eval harness: run scenarios against models, judge completions, apply thresholds."""
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click


TARGET_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-7",
]
JUDGE_MODEL = "claude-sonnet-4-6"

THRESHOLDS: dict[tuple[str, str], int] = {
    ("claude-haiku-4-5-20251001", "happy-path"): 2,
    ("claude-haiku-4-5-20251001", "edge-case"): 2,
    ("claude-haiku-4-5-20251001", "anti-trigger"): 2,
    ("claude-sonnet-4-6", "happy-path"): 3,
    ("claude-sonnet-4-6", "edge-case"): 3,
    ("claude-sonnet-4-6", "anti-trigger"): 2,
    ("claude-opus-4-7", "happy-path"): 3,
    ("claude-opus-4-7", "edge-case"): 3,
    ("claude-opus-4-7", "anti-trigger"): 3,
}

JUDGE_SYSTEM = """You are a strict literal evaluator. Given a skill's SKILL.md, a user query, the candidate model's response, and a list of rubric items, return a JSON object scoring each rubric item.

Each rubric item is scored independently. Partial credit is FALSE. The output MUST be valid JSON matching this schema:

{
  "results": [
    {"item": "<rubric item verbatim>", "pass": true|false, "rationale": "<one sentence>"},
    ...
  ]
}

Do not include any text outside the JSON object."""


@dataclass
class EvalScenario:
    skill: str
    scenario_id: str
    scenario_kind: str
    query: str
    files: list[str]
    expected_behavior: list[str]

    @classmethod
    def from_dict(cls, d: dict) -> "EvalScenario":
        return cls(
            skill=d["skill"],
            scenario_id=d["scenario_id"],
            scenario_kind=d["scenario_kind"],
            query=d["query"],
            files=d.get("files", []),
            expected_behavior=d["expected_behavior"],
        )


@dataclass
class RubricItemResult:
    item: str
    pass_: bool
    rationale: str


@dataclass
class JudgeResult:
    scenario_id: str
    completion: str
    rubric_results: list[RubricItemResult]
    score: str

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.rubric_results if r.pass_)


def load_scenarios(evals_dir: Path) -> list[EvalScenario]:
    scenarios: list[EvalScenario] = []
    for path in sorted(evals_dir.glob("0[1-3]-*.json")):
        data = json.loads(path.read_text())
        scenarios.append(EvalScenario.from_dict(data))
    return scenarios


def judge_response(
    scenario: EvalScenario,
    skill_body: str,
    completion: str,
    judge_client,
) -> JudgeResult:
    rubric_block = "\n".join(f"- {item}" for item in scenario.expected_behavior)
    judge_user = (
        f"SKILL.md body:\n{skill_body}\n\n"
        f"User query: {scenario.query}\n\n"
        f"Candidate model response:\n{completion}\n\n"
        f"Rubric items to score (each independent):\n{rubric_block}"
    )
    resp = judge_client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=2000,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": judge_user}],
    )
    raw = resp.content[0].text
    parsed = json.loads(raw)
    results = [
        RubricItemResult(item=r["item"], pass_=r["pass"], rationale=r["rationale"])
        for r in parsed["results"]
    ]
    passed = sum(1 for r in results if r.pass_)
    return JudgeResult(
        scenario_id=scenario.scenario_id,
        completion=completion,
        rubric_results=results,
        score=f"{passed}/{len(results)}",
    )


def check_threshold(model: str, scenario_kind: str, passed: int, total: int) -> bool:
    if total != 3:
        return False
    required = THRESHOLDS.get((model, scenario_kind))
    if required is None:
        return False
    return passed >= required


def run_skill_evals(skill_dir: Path, anthropic_client) -> dict:
    skill_body = (skill_dir / "SKILL.md").read_text()
    scenarios = load_scenarios(skill_dir / "evals")
    if len(scenarios) != 3:
        raise ValueError(
            f"{skill_dir} has {len(scenarios)} eval scenarios; v1 requires exactly 3"
        )

    summary = {
        "skill_dir": str(skill_dir),
        "run_date": datetime.now(timezone.utc).isoformat(),
        "models": {},
    }

    for model in TARGET_MODELS:
        model_results = []
        all_passed = True
        for scenario in scenarios:
            resp = anthropic_client.messages.create(
                model=model,
                max_tokens=4000,
                system=skill_body,
                messages=[{"role": "user", "content": scenario.query}],
            )
            completion = resp.content[0].text
            judge_result = judge_response(scenario, skill_body, completion, anthropic_client)
            scenario_passed = check_threshold(
                model, scenario.scenario_kind, judge_result.passed_count, len(scenario.expected_behavior)
            )
            if not scenario_passed:
                all_passed = False
            model_results.append({
                "scenario_id": scenario.scenario_id,
                "scenario_kind": scenario.scenario_kind,
                "score": judge_result.score,
                "passed_threshold": scenario_passed,
                "rubric_results": [asdict(r) for r in judge_result.rubric_results],
            })
        summary["models"][model] = {
            "all_passed": all_passed,
            "scenarios": model_results,
        }

    return summary


@click.command()
@click.argument("skill_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def main(skill_dir: Path) -> None:
    """Run evals for one skill directory across all 3 target models."""
    try:
        from anthropic import Anthropic
    except ImportError:
        click.echo("anthropic SDK not installed; run 'uv sync'", err=True)
        sys.exit(2)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        click.echo("ANTHROPIC_API_KEY not set; exporting required for eval runs", err=True)
        sys.exit(2)
    client = Anthropic()
    summary = run_skill_evals(skill_dir, client)
    run_date = summary["run_date"][:10]
    for model, model_summary in summary["models"].items():
        out = skill_dir / "evals" / f"results-{model}-{run_date}.json"
        out.write_text(json.dumps(model_summary, indent=2))
    overall_passed = all(m["all_passed"] for m in summary["models"].values())
    for model, m in summary["models"].items():
        status = "PASS" if m["all_passed"] else "FAIL"
        click.echo(f"  {model}: {status}")
    if not overall_passed:
        click.echo("\nOne or more models failed pass thresholds.", err=True)
        sys.exit(1)
    click.echo("\nAll thresholds met.")


if __name__ == "__main__":
    main()
