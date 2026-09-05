from __future__ import annotations

from typing import Any


def check_basic_feasibility(
    constraints: dict[str, Any],
) -> tuple[bool, str | None]:
    """Check for immediately contradictory hard constraints."""

    min_duration = constraints.get("min_duration_sec")
    max_duration = constraints.get("max_duration_sec")

    if (
        min_duration is not None
        and max_duration is not None
        and min_duration > max_duration
    ):
        return (
            False,
            "min_duration_sec exceeds max_duration_sec",
        )

    return True, None
