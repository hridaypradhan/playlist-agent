from __future__ import annotations

import argparse
import json
from pathlib import Path

from playlist_agent.baseline import run_baseline
from playlist_agent.environment import (
    load_catalog,
    load_json,
    load_playlist,
)
from playlist_agent.state import PlaylistState
from playlist_agent.trace import TraceLogger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the deterministic playlist baseline."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to a playlist curation test case JSON file.",
    )

    return parser.parse_args()


def save_playlist(
    state: PlaylistState,
    output_path: Path,
) -> None:
    """Save the current playlist state as JSON."""

    output = {
        "name": state.name,
        "tracks": state.track_ids,
    }

    output_path.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()

    test_case = load_json(args.input)

    catalog = load_catalog(test_case["catalog"])
    playlist = load_playlist(test_case["playlist"])

    state = PlaylistState(
        name=playlist["name"],
        track_ids=playlist["tracks"].copy(),
        catalog=catalog,
    )

    input_path = Path(args.input)
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_playlist = (
        output_dir / f"{input_path.stem}_playlist.json"
    )
    output_trace = (
        output_dir / f"{input_path.stem}_trace.jsonl"
    )

    logger = TraceLogger(output_trace)

    print(f"Test case: {args.input}")
    print(f"Playlist: {state.name}")
    print(f"Initial tracks: {len(state.track_ids)}")
    print(f"Initial duration: {state.duration_sec} seconds")

    evaluation = run_baseline(
        state,
        test_case["constraints"],
        test_case["objective"],
        logger,
    )

    print("\nResult:")

    if evaluation["success"]:
        save_playlist(state, output_playlist)

        print("SUCCESS")
        print(
            f"Constraints: "
            f"{evaluation['passed']}/{evaluation['total']}"
        )
        print(f"Final duration: {state.duration_sec} seconds")
        print(f"Playlist output: {output_playlist}")
        print(f"Trace output: {output_trace}")

    else:
        print("FAILURE")
        print(f"Reason: {evaluation['reason']}")
        print(
            f"Constraints: "
            f"{evaluation['passed']}/{evaluation['total']}"
        )
        print(f"Trace output: {output_trace}")


if __name__ == "__main__":
    main()