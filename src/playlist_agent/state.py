from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PlaylistState:
    """Current observable state of a playlist-editing task."""

    name: str
    track_ids: list[str]
    catalog: dict[str, dict[str, Any]]

    @property
    def tracks(self) -> list[dict[str, Any]]:
        """Return the full metadata for tracks currently in the playlist."""
        tracks = []

        for track_id in self.track_ids:
            track = self.catalog.get(track_id)

            if track is not None:
                tracks.append(track)

        return tracks

    @property
    def duration_sec(self) -> int:
        """Return the total playlist duration in seconds."""
        return sum(track["duration_sec"] for track in self.tracks)

    @property
    def artists(self) -> list[str]:
        """Return artists in playlist order."""
        return [track["artist"] for track in self.tracks]