"""eval_runner.py template — used by scaffolding-llm-eval-harness.

Emits results-<utc-iso>.jsonl with one row per (candidate_model, scenario) pair.
Every row carries the five required fields documented in the README:
  - model_id              (with revision pin)
  - dataset_hash          (sha256 of canonical-serialized scenarios)
  - prompt_version        (semver of the prompt template)
  - judge_model           (string or null)
  - result_row            (scenario_id, completion, rubric_scores, timestamp)

Run: `make eval` (which calls `python eval_runner.py --output results-<ts>.jsonl`).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

# CHANGE ME per your harness config
CANDIDATE_MODELS: list[str] = [
    # "anthropic/claude-haiku-4-5@2025-10-01",
    # "anthropic/claude-sonnet-4-6@2026-02-19",
    # "anthropic/claude-opus-4-7@2026-04-15",
]
JUDGE_MODEL: str | None = None  # e.g. "anthropic/claude-opus-4-7@2026-04-15"
PROMPT_VERSION = "0.1.0"
PROMPT_PATH = Path("prompts") / f"v{PROMPT_VERSION}.txt"
SCENARIOS_DIR = Path("scenarios")


def canonical_dataset_hash(scenarios: list[dict[str, Any]]) -> str:
    """Stable sha256 over the sorted scenario list. Detects silent edits."""
    canonical = json.dumps(scenarios, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def load_scenarios() -> list[dict[str, Any]]:
    scenarios = []
    for path in sorted(SCENARIOS_DIR.glob("*.json")):
        with path.open() as f:
            scenarios.append(json.load(f))
    return scenarios


def call_candidate(model_id: str, prompt: str, query: str) -> str:
    """Replace this stub with the actual API call to the candidate model.

    The stub returns a placeholder so the harness skeleton runs end-to-end
    before the user wires their API client.
    """
    return f"[stub completion from {model_id}]"


def call_judge(
    judge_model: str,
    completion: str,
    rubric_items: list[str],
    query: str,
) -> list[dict[str, Any]]:
    """Replace this stub with the actual judge call. Returns one dict per rubric item."""
    return [
        {"item": item, "pass": False, "rationale": "[stub: not graded]"}
        for item in rubric_items
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Output results-*.jsonl path")
    args = parser.parse_args()

    scenarios = load_scenarios()
    if not scenarios:
        print("No scenarios found under scenarios/. Add at least one before running.", file=sys.stderr)
        return 2

    dataset_hash = canonical_dataset_hash(scenarios)
    prompt_template = PROMPT_PATH.read_text()
    now = dt.datetime.now(dt.UTC).isoformat()

    if not CANDIDATE_MODELS:
        print("Edit CANDIDATE_MODELS in eval_runner.py before running.", file=sys.stderr)
        return 2

    with open(args.output, "w") as out:
        for model_id in CANDIDATE_MODELS:
            for scenario in scenarios:
                completion = call_candidate(model_id, prompt_template, scenario["query"])
                rubric_results = (
                    call_judge(JUDGE_MODEL, completion, scenario["expected_behavior"], scenario["query"])
                    if JUDGE_MODEL is not None
                    else None
                )
                row = {
                    "model_id": model_id,
                    "dataset_hash": dataset_hash,
                    "prompt_version": PROMPT_VERSION,
                    "judge_model": JUDGE_MODEL,
                    "result_row": {
                        "scenario_id": scenario["scenario_id"],
                        "scenario_kind": scenario["scenario_kind"],
                        "completion": completion,
                        "rubric_results": rubric_results,
                        "timestamp": now,
                    },
                }
                out.write(json.dumps(row) + "\n")

    print(f"Wrote {args.output} (dataset_hash={dataset_hash[:12]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
