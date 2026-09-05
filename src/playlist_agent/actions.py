from __future__ import annotations

from .state import PlaylistState


def remove_track(state: PlaylistState, track_id: str) -> None:
    """Remove a track from the current playlist.

    Raises:
        ValueError: If the track is not currently in the playlist.
    """
    if track_id not in state.track_ids:
        raise ValueError(f"Cannot remove '{track_id}': track is not in the playlist.")

    state.track_ids.remove(track_id)


def add_track(state: PlaylistState, track_id: str) -> None:
    """Add a catalog track to the current playlist.

    Raises:
        ValueError: If the track does not exist in the catalog or
            is already in the playlist.
    """
    if track_id not in state.catalog:
        raise ValueError(
            f"Cannot add '{track_id}': track does not exist in the catalog."
        )

    if track_id in state.track_ids:
        raise ValueError(f"Cannot add '{track_id}': track is already in the playlist.")

    state.track_ids.append(track_id)


def reorder_by_energy(
    state: PlaylistState,
    ascending: bool = True,
) -> None:
    """Reorder the playlist by track energy."""

    state.track_ids.sort(
        key=lambda track_id: state.catalog[track_id]["energy"],
        reverse=not ascending,
    )
