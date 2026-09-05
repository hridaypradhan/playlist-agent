from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest import result

from playlist_agent.objectives import get_objective_function
from playlist_agent.baseline import run_baseline
from playlist_agent.environment import (
    load_catalog,
    load_json,
    load_playlist,
)
from playlist_agent.state import PlaylistState
from playlist_agent.trace import TraceLogger

CASES_DIR = Path("evaluation/cases")
OUTPUT_PATH = Path("evaluation/results.json")


def run_case(case_path: Path) -> dict[str, Any]:
    """Run the baseline on one evaluation case."""

    test_case = load_json(case_path)

    catalog = load_catalog(test_case["catalog"])
    playlist = load_playlist(test_case["playlist"])

    state = PlaylistState(
        name=playlist["name"],
        track_ids=playlist["tracks"].copy(),
        catalog=catalog,
    )

    trace_path = Path("outputs") / f"{case_path.stem}_evaluation_trace.jsonl"

    logger = TraceLogger(trace_path)

    initial_duration = state.duration_sec

    result = run_baseline(
        state,
        test_case["constraints"],
        test_case["objective"],
        logger,
    )

    expected = test_case.get("expected", {})

    expected_success = expected.get("success")

    expectation_met = (
        result["success"] == expected_success if expected_success is not None else True
    )

    objective_type = test_case["objective"]["type"]

    if result["success"]:
        objective_function = get_objective_function(test_case["objective"])
        objective_score = objective_function(state)
    else:
        objective_score = None

    if "reason" in expected:
        expectation_met = expectation_met and result["reason"] == expected["reason"]

    if "final_track_ids" in expected:
        expectation_met = (
            expectation_met and state.track_ids == expected["final_track_ids"]
        )

    if "objective_score" in expected:
        expectation_met = (
            expectation_met and objective_score == expected["objective_score"]
        )

    return {
        "case": case_path.name,
        "success": result["success"],
        "reason": result["reason"],
        "constraints_evaluated": result["constraints_evaluated"],
        "passed_constraints": result["passed"],
        "total_constraints": result["total"],
        "objective": objective_type,
        "objective_score": objective_score,
        "initial_duration_sec": initial_duration,
        "final_duration_sec": state.duration_sec,
        "initial_track_count": len(playlist["tracks"]),
        "final_track_count": len(state.track_ids),
        "trace_events": logger.step,
        "expectation_met": expectation_met,
        "final_track_ids": state.track_ids.copy(),
    }


def main() -> None:
    cases = sorted(CASES_DIR.glob("*.json"))

    if not cases:
        raise RuntimeError(f"No evaluation cases found in {CASES_DIR}")

    results = []

    for case_path in cases:
        result = run_case(case_path)
        results.append(result)

        outcome = "SUCCESS" if result["success"] else "INFEASIBLE"
        expectation = "MET" if result["expectation_met"] else "UNMET"

        if result["constraints_evaluated"]:
            constraint_summary = (
                f"{result['passed_constraints']}/"
                f"{result['total_constraints']} constraints"
            )
        else:
            constraint_summary = "constraints not evaluated"

        print(
            f"{result['case']}: Test Expectation {expectation} | "
            f"System Outcome = {outcome} | "
            f"{constraint_summary}"
        )

    summary = {
        "case_count": len(results),
        "success_count": sum(result["success"] for result in results),
        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(f"\nEvaluation results: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
