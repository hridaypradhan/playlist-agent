from playlist_agent.environment import load_catalog, load_playlist
from playlist_agent.state import PlaylistState


CATALOG_PATH = "data/songs.json"
PLAYLIST_PATH = "data/playlists/demo.json"


def main() -> None:
    catalog = load_catalog(CATALOG_PATH)
    playlist = load_playlist(PLAYLIST_PATH)

    state = PlaylistState(
        name=playlist["name"],
        track_ids=playlist["tracks"],
        catalog=catalog,
    )

    print(f"Catalog tracks: {len(state.catalog)}")
    print(f"Playlist: {state.name}")
    print(f"Playlist tracks: {len(state.tracks)}")
    print(f"Playlist duration: {state.duration_sec} seconds")

    print("\nCurrent playlist:")
    for track in state.tracks:
        print(
            f"  {track['title']} - {track['artist']} "
            f"({track['bpm']} BPM, energy {track['energy']:.2f})"
        )


if __name__ == "__main__":
    main()