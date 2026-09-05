from playlist_agent.environment import load_catalog, load_playlist
from playlist_agent.state import PlaylistState
from playlist_agent.actions import (
    add_track,
    remove_track,
    reorder_by_energy,
)


def main() -> None:
    catalog = load_catalog("data/songs.json")
    playlist = load_playlist("data/playlists/demo.json")

    state = PlaylistState(
        name=playlist["name"],
        track_ids=playlist["tracks"].copy(),
        catalog=catalog,
    )

    print(f"Initial: {state.track_ids}")
    print(f"Duration: {state.duration_sec} seconds")

    remove_track(state, "track_001")

    print(f"\nAfter remove: {state.track_ids}")
    print(f"Duration: {state.duration_sec} seconds")

    add_track(state, "track_007")

    print(f"\nAfter add:    {state.track_ids}")
    print(f"Duration: {state.duration_sec} seconds")

    reorder_by_energy(state)

    print(f"\nAfter reorder: {state.track_ids}")
    print("Energies:", [track["energy"] for track in state.tracks])

    state.track_ids = [
        "track_002",
        "track_003",
        "track_005",
        "track_006",
    ]

    reorder_by_energy(state, ascending=False)

    print(f"\nDescending reorder: {state.track_ids}")
    print(
        "Energies:",
        [track["energy"] for track in state.tracks],
    )


if __name__ == "__main__":
    main()
