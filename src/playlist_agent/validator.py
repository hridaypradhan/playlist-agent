from __future__ import annotations

from typing import Any

from .state import PlaylistState


def validate_playlist(
    state: PlaylistState,
    constraints: dict[str, Any],
) -> dict[str, bool]:
    """Check whether the current playlist satisfies each constraint."""

    results: dict[str, bool] = {}

    if "min_bpm" in constraints:
        minimum = constraints["min_bpm"]
        results["min_bpm"] = all(
            track["bpm"] >= minimum for track in state.tracks
        )

    if "allow_explicit" in constraints:
        if constraints["allow_explicit"]:
            results["allow_explicit"] = True
        else:
            results["allow_explicit"] = all(
                not track["explicit"] for track in state.tracks
            )

    if constraints.get("unique_artist"):
        artists = state.artists
        results["unique_artist"] = len(artists) == len(set(artists))

    if constraints.get("energy_order") == "ascending":
        energies = [track["energy"] for track in state.tracks]
        results["energy_order"] = all(
            energies[i] <= energies[i + 1]
            for i in range(len(energies) - 1)
        )

    if "must_keep" in constraints:
        required_tracks = constraints["must_keep"]
        results["must_keep"] = all(
            track_id in state.track_ids
            for track_id in required_tracks
        )

    if "max_duration_sec" in constraints:
        results["max_duration_sec"] = (
            state.duration_sec <= constraints["max_duration_sec"]
        )

    return results