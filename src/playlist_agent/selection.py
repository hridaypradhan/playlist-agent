from __future__ import annotations

from itertools import combinations
from typing import Any

from .objectives import get_objective_function
from .state import PlaylistState
from .validator import validate_playlist


def select_additions(
    state: PlaylistState,
    constraints: dict[str, Any],
    objective: dict[str, Any],
) -> list[str] | None:
    """Choose additions that produce the best feasible playlist."""

    score_objective = get_objective_function(objective)

    available_ids = [
        track_id for track_id in state.catalog if track_id not in state.track_ids
    ]

    best_additions: list[str] | None = None
    best_score: float | None = None

    # Include the empty subset as a possible solution.
    for subset_size in range(0, len(available_ids) + 1):
        for subset in combinations(available_ids, subset_size):
            candidate_state = PlaylistState(
                name=state.name,
                track_ids=state.track_ids + list(subset),
                catalog=state.catalog,
            )

            # The current baseline can repair ascending energy
            # ordering deterministically by sorting.
            energy_order = constraints.get("energy_order")

            if energy_order in {"ascending", "descending"}:
                candidate_state.track_ids.sort(
                    key=lambda track_id: candidate_state.catalog[track_id]["energy"],
                    reverse=(energy_order == "descending"),
                )

            results = validate_playlist(
                candidate_state,
                constraints,
            )

            # Hard constraints define feasibility.
            if not all(results.values()):
                continue

            score = score_objective(candidate_state)

            if best_score is None or score > best_score:
                best_score = score
                best_additions = list(subset)

    return best_additions
