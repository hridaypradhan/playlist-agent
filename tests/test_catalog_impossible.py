from playlist_agent.baseline import run_baseline
from playlist_agent.environment import (
    load_catalog,
    load_json,
    load_playlist,
)
from playlist_agent.state import PlaylistState
from playlist_agent.trace import TraceLogger


def main() -> None:
    test_case = load_json("examples/test_catalog_impossible.json")

    catalog = load_catalog(test_case["catalog"])
    playlist = load_playlist(test_case["playlist"])

    state = PlaylistState(
        name=playlist["name"],
        track_ids=playlist["tracks"].copy(),
        catalog=catalog,
    )

    logger = TraceLogger("outputs/test_baseline_trace.jsonl")

    print("Initial playlist:")
    print(state.track_ids)
    print(f"Duration: {state.duration_sec} seconds")

    evaluation = run_baseline(
        state,
        test_case["constraints"],
        test_case["objective"],
        logger,
    )

    if not evaluation["success"]:
        print("\nResult: FAILURE")
        print(f"Reason: {evaluation['reason']}")
        return

    print("\nFinal playlist:")
    print(state.track_ids)
    print(f"Duration: {state.duration_sec} seconds")

    print(f"Constraints: " f"{evaluation['passed']}/{evaluation['total']}")

    print("\nFinal tracks:")

    for track in state.tracks:
        print(
            f"  {track['id']}: "
            f"{track['title']} - {track['artist']} "
            f"({track['bpm']} BPM, "
            f"energy {track['energy']:.2f}, "
            f"{track['duration_sec']} sec)"
        )


if __name__ == "__main__":
    main()
