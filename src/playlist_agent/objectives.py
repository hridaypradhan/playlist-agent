from __future__ import annotations

from typing import Any, Callable

from .state import PlaylistState

ObjectiveFunction = Callable[[PlaylistState], float]


def maximize_duration(state: PlaylistState) -> float:
    """Prefer playlists with greater total duration."""
    return float(state.duration_sec)


def maximize_track_count(state: PlaylistState) -> float:
    """Prefer playlists containing more tracks."""
    return float(len(state.track_ids))


OBJECTIVES: dict[str, ObjectiveFunction] = {
    "maximize_duration": maximize_duration,
    "maximize_track_count": maximize_track_count,
}


def get_objective_function(
    objective: dict[str, Any],
) -> ObjectiveFunction:
    """Return the scoring function specified by an objective."""

    objective_type = objective.get("type")

    if objective_type not in OBJECTIVES:
        available = ", ".join(sorted(OBJECTIVES))

        raise ValueError(
            f"Unknown objective '{objective_type}'. "
            f"Available objectives: {available}"
        )

    return OBJECTIVES[objective_type]
