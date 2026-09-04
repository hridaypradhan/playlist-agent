from __future__ import annotations

from typing import Any


def search_catalog(
    catalog: dict[str, dict[str, Any]],
    *,
    min_bpm: int | None = None,
    max_bpm: int | None = None,
    min_energy: float | None = None,
    max_energy: float | None = None,
    explicit: bool | None = None,
    exclude_artists: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Return catalog tracks matching the requested filters."""

    exclude_artists = exclude_artists or set()
    results = []

    for track in catalog.values():
        if min_bpm is not None and track["bpm"] < min_bpm:
            continue

        if max_bpm is not None and track["bpm"] > max_bpm:
            continue

        if min_energy is not None and track["energy"] < min_energy:
            continue

        if max_energy is not None and track["energy"] > max_energy:
            continue

        if explicit is not None and track["explicit"] != explicit:
            continue

        if track["artist"] in exclude_artists:
            continue

        results.append(track)

    return results