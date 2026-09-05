from playlist_agent.environment import (
    load_catalog,
    load_json,
    load_playlist,
)
from playlist_agent.evaluation import evaluate_playlist
from playlist_agent.state import PlaylistState


def main() -> None:
    test_case = load_json("examples/test1.json")

    catalog = load_catalog(test_case["catalog"])
    playlist = load_playlist(test_case["playlist"])

    state = PlaylistState(
        name=playlist["name"],
        track_ids=playlist["tracks"].copy(),
        catalog=catalog,
    )

    evaluation = evaluate_playlist(
        state,
        test_case["constraints"],
    )

    print(f"Passed: {evaluation['passed']}")
    print(f"Total:  {evaluation['total']}")
    print(f"Failed: {evaluation['failed_constraints']}")


if __name__ == "__main__":
    main()