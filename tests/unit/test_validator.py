from playlist_agent.environment import load_catalog, load_json, load_playlist
from playlist_agent.state import PlaylistState
from playlist_agent.validator import validate_playlist


def main() -> None:
    test_case = load_json("evaluation/cases/test1.json")

    catalog = load_catalog(test_case["catalog"])
    playlist = load_playlist(test_case["playlist"])

    state = PlaylistState(
        name=playlist["name"],
        track_ids=playlist["tracks"].copy(),
        catalog=catalog,
    )

    results = validate_playlist(
        state,
        test_case["constraints"],
    )

    print(f"Playlist: {state.name}")
    print(f"Duration: {state.duration_sec} seconds")
    print("\nConstraint validation:")

    for constraint, passed in results.items():
        symbol = "PASS" if passed else "FAIL"
        print(f"  {symbol}: {constraint}")

    passed_count = sum(results.values())

    print(
        f"\nSatisfied: {passed_count}/{len(results)} constraints"
    )


if __name__ == "__main__":
    main()