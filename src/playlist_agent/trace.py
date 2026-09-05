from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TraceLogger:
    """Write structured agent events to a JSONL trace file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Start each run with a fresh trace.
        self.path.write_text("", encoding="utf-8")

        self.step = 0

    def log(self, event: str, **data: Any) -> None:
        """Write one event to the trace."""
        self.step += 1

        record = {
            "step": self.step,
            "event": event,
            **data,
        }

        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")