from playlist_agent.catalog import search_catalog
from playlist_agent.environment import load_catalog


def main() -> None:
    catalog = load_catalog("data/songs.json")

    results = search_catalog(
        catalog,
        min_bpm=110,
        explicit=False,
    )

    print("Matching tracks:")

    for track in results:
        print(
            f"  {track['id']}: {track['title']} - {track['artist']} "
            f"({track['bpm']} BPM, energy {track['energy']:.2f})"
        )


if __name__ == "__main__":
    main()