from __future__ import annotations

from typing import Any

from .state import PlaylistState
from .validator import validate_playlist


def evaluate_playlist(
    state: PlaylistState,
    constraints: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate the current playlist and return structured results."""

    results = validate_playlist(state, constraints)

    failed_constraints = [
        name for name, passed in results.items() if not passed
    ]

    return {
        "results": results,
        "passed": sum(results.values()),
        "total": len(results),
        "failed_constraints": failed_constraints,
    }