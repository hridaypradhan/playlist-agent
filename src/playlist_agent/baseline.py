from __future__ import annotations

from typing import Any

from .actions import add_track, remove_track, reorder_by_energy
from .evaluation import evaluate_playlist
from .selection import select_additions
from .feasibility import check_basic_feasibility
from .state import PlaylistState
from .trace import TraceLogger


def repair_invalid_tracks(
    state: PlaylistState,
    constraints: dict[str, Any],
    logger: TraceLogger,
) -> None:
    """Remove tracks that individually violate hard constraints."""

    must_keep = set(constraints.get("must_keep", []))
    min_bpm = constraints.get("min_bpm")
    allow_explicit = constraints.get("allow_explicit", True)

    # Iterate over a copy because the playlist may change during the loop.
    for track_id in state.track_ids.copy():
        track = state.catalog[track_id]

        if min_bpm is not None and track["bpm"] < min_bpm:
            if track_id in must_keep:
                continue

            logger.log(
                "action",
                action="remove_track",
                track_id=track_id,
                reason="violates_min_bpm",
                evidence={
                    "track_bpm": track["bpm"],
                    "required_min_bpm": min_bpm,
                },
            )

            remove_track(state, track_id)
            continue

        if not allow_explicit and track["explicit"]:
            if track_id in must_keep:
                continue

            logger.log(
                "action",
                action="remove_track",
                track_id=track_id,
                reason="explicit_not_allowed",
                evidence={
                    "track_explicit": track["explicit"],
                    "allow_explicit": allow_explicit,
                },
            )

            remove_track(state, track_id)


def add_selected_tracks(
    state: PlaylistState,
    constraints: dict[str, Any],
    objective: dict[str, Any],
    logger: TraceLogger,
) -> bool:
    """Select and add tracks that optimize the objective feasibly."""

    additions = select_additions(
        state,
        constraints,
        objective,
    )

    if additions is None:
        logger.log(
            "failure",
            reason="no_feasible_addition_set",
            evidence={
                "current_duration_sec": state.duration_sec,
                "min_duration_sec": constraints.get("min_duration_sec"),
                "max_duration_sec": constraints.get("max_duration_sec"),
            },
        )
        return False

    logger.log(
        "decision",
        action="select_additions",
        reason="optimize_objective",
        evidence={
            "objective": objective["type"],
            "current_duration_sec": state.duration_sec,
            "min_duration_sec": constraints.get("min_duration_sec"),
            "max_duration_sec": constraints.get("max_duration_sec"),
            "selected_track_ids": additions,
        },
    )

    for track_id in additions:
        track = state.catalog[track_id]

        logger.log(
            "action",
            action="add_track",
            track_id=track_id,
            reason="execute_selected_addition",
            evidence={
                "objective": objective["type"],
                "track_duration_sec": track["duration_sec"],
                "track_bpm": track["bpm"],
                "track_energy": track["energy"],
                "track_artist": track["artist"],
            },
        )

        add_track(state, track_id)

    return True


def repair_energy_order(
    state: PlaylistState,
    constraints: dict[str, Any],
    logger: TraceLogger,
) -> None:
    """Repair a supported energy-order constraint if necessary."""

    order = constraints.get("energy_order")

    if order is None:
        return

    if order not in {"ascending", "descending"}:
        raise ValueError(f"Unsupported energy order: {order}")

    energies_before = [track["energy"] for track in state.tracks]

    if order == "ascending":
        is_valid = all(
            energies_before[i] <= energies_before[i + 1]
            for i in range(len(energies_before) - 1)
        )
        ascending = True

    else:
        is_valid = all(
            energies_before[i] >= energies_before[i + 1]
            for i in range(len(energies_before) - 1)
        )
        ascending = False

    if is_valid:
        return

    track_ids_before = state.track_ids.copy()

    reorder_by_energy(
        state,
        ascending=ascending,
    )

    logger.log(
        "action",
        action="reorder_playlist",
        reason="violates_energy_order",
        evidence={
            "requested_order": order,
            "track_ids_before": track_ids_before,
            "track_ids_after": state.track_ids.copy(),
            "energies_before": energies_before,
            "energies_after": [track["energy"] for track in state.tracks],
        },
    )


def log_validation(
    state: PlaylistState,
    constraints: dict[str, Any],
    logger: TraceLogger,
) -> dict[str, Any]:
    """Evaluate the playlist and record the result."""

    evaluation = evaluate_playlist(state, constraints)

    logger.log(
        "validation",
        passed=evaluation["passed"],
        total=evaluation["total"],
        failed_constraints=evaluation["failed_constraints"],
    )

    return evaluation


def run_baseline(
    state: PlaylistState,
    constraints: dict[str, Any],
    objective: dict[str, Any],
    logger: TraceLogger,
) -> dict[str, Any]:
    """Run the deterministic playlist-repair baseline."""

    feasible, reason = check_basic_feasibility(constraints)

    if not feasible:
        logger.log(
            "failure",
            reason="infeasible_constraints",
            evidence={
                "detail": reason,
            },
        )

        return {
            "success": False,
            "reason": "infeasible_constraints",
            "constraints_evaluated": False,
            "passed": None,
            "total": len(constraints),
            "failed_constraints": None,
        }

    # Initial observation.
    log_validation(state, constraints, logger)

    # Repair per-track violations.
    repair_invalid_tracks(
        state,
        constraints,
        logger,
    )

    log_validation(state, constraints, logger)

    # Select and execute additions.
    additions_succeeded = add_selected_tracks(
        state,
        constraints,
        objective,
        logger,
    )

    if not additions_succeeded:
        evaluation = evaluate_playlist(
            state,
            constraints,
        )

        return {
            "success": False,
            "reason": "no_feasible_addition_set",
            "constraints_evaluated": True,
            **evaluation,
        }

    log_validation(state, constraints, logger)

    # Repair ordering.
    repair_energy_order(
        state,
        constraints,
        logger,
    )

    # Final observation.
    final_evaluation = log_validation(
        state,
        constraints,
        logger,
    )

    return {
        "success": len(final_evaluation["failed_constraints"]) == 0,
        "reason": (
            None
            if len(final_evaluation["failed_constraints"]) == 0
            else "constraints_remain_unsatisfied"
        ),
        "constraints_evaluated": True,
        **final_evaluation,
    }
