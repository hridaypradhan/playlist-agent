from playlist_agent.trace import TraceLogger


def main() -> None:
    logger = TraceLogger("outputs/test_trace.jsonl")

    logger.log(
        "validation",
        passed=1,
        total=6,
        failed_constraints=[
            "min_bpm",
            "allow_explicit",
            "unique_artist",
            "energy_order",
            "max_duration_sec",
        ],
    )

    logger.log(
        "action",
        action="remove_track",
        track_id="track_001",
        reason="violates_min_bpm",
        evidence={
            "track_bpm": 105,
            "required_min_bpm": 110,
        },
    )

    logger.log(
        "validation",
        passed=2,
        total=6,
        failed_constraints=[
            "allow_explicit",
            "unique_artist",
            "energy_order",
            "max_duration_sec",
        ],
    )

    print(f"Trace written to: {logger.path}")


if __name__ == "__main__":
    main()