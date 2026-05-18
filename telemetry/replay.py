"""Replay a telemetry CSV at configurable speed."""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path


def replay_csv(path: Path, speed: float) -> None:
    """Print a telemetry session at replay speed."""

    if speed <= 0.0:
        raise ValueError("speed must be positive.")
    with path.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    previous_ms: int | None = None
    for row in rows:
        timestamp_ms = int(float(row.get("timestamp_ms", 0)))
        if previous_ms is not None:
            time.sleep(max(0.0, (timestamp_ms - previous_ms) / 1000.0 / speed))
        previous_ms = timestamp_ms
        print(row)


def main() -> None:
    """CLI entrypoint."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--speed", default=1.0, type=float)
    args = parser.parse_args()
    replay_csv(args.file, args.speed)


if __name__ == "__main__":
    main()
