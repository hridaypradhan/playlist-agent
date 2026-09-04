from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    """Load and return JSON data from a file."""
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_catalog(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load the song catalog and index songs by track ID."""
    songs = load_json(path)

    if not isinstance(songs, list):
        raise ValueError("Song catalog must contain a JSON list.")

    catalog = {}

    for song in songs:
        if not isinstance(song, dict) or "id" not in song:
            raise ValueError("Every song must be an object containing an 'id'.")

        catalog[song["id"]] = song

    return catalog


def load_playlist(path: str | Path) -> dict[str, Any]:
    """Load a playlist and validate its basic structure."""
    playlist = load_json(path)

    if not isinstance(playlist, dict):
        raise ValueError("Playlist must contain a JSON object.")

    if "name" not in playlist or "tracks" not in playlist:
        raise ValueError("Playlist must contain 'name' and 'tracks'.")

    if not isinstance(playlist["tracks"], list):
        raise ValueError("Playlist 'tracks' must be a JSON list.")

    return playlist