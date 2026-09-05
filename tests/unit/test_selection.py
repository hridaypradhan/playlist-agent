from playlist_agent.baseline import repair_invalid_tracks
from playlist_agent.environment import (
    load_catalog,
    load_json,
    load_playlist,
)
from playlist_agent.selection import select_additions
from playlist_agent.state import PlaylistState
from playlist_agent.trace import TraceLogger


def main() -> None:
    test_case = load_json("evaluation/cases/test1.json")

    catalog = load_catalog(test_case["catalog"])
    playlist = load_playlist(test_case["playlist"])

    state = PlaylistState(
        name=playlist["name"],
        track_ids=playlist["tracks"].copy(),
        catalog=catalog,
    )

    logger = TraceLogger("outputs/test_selection_trace.jsonl")

    repair_invalid_tracks(
        state,
        test_case["constraints"],
        logger,
    )

    print("State after removals:")
    print(state.track_ids)
    print(f"Duration: {state.duration_sec} seconds")

    additions = select_additions(
        state,
        test_case["constraints"],
        test_case["objective"],
    )

    print("\nSelected additions:")
    print(additions)

    added_duration = sum(catalog[track_id]["duration_sec"] for track_id in additions)

    print(f"Added duration: {added_duration} seconds")
    print(f"Projected duration: " f"{state.duration_sec + added_duration} seconds")


if __name__ == "__main__":
    main()
