"""Compare buffered and streaming CSV writes on identical synthetic input."""
from __future__ import annotations

import hashlib
import json
import platform
import tempfile
import time
import tracemalloc
from pathlib import Path

from fitness_programming_toolkit import export_csv, parse_program, write_csv


def synthetic_program():
    sessions = []
    for si in range(5):
        exercises = [
            {"exercise_id": f"e{ei}", "name": "Synthetic exercise", "sets": [
                {"reps": 8, "rest_seconds": 90, "load_kg": 25, "rpe": 7}
                for _ in range(20)
            ]}
            for ei in range(50)
        ]
        sessions.append({"session_id": f"s{si}", "name": "Synthetic session",
                         "day_of_week": "monday", "exercises": exercises})
    return parse_program({"schema_version": "1.0", "program_id": "benchmark",
                          "title": "Synthetic 52-week plan", "weeks": 52,
                          "sessions": sessions})


def measure(program, path, streaming):
    def run():
        with path.open("w", encoding="utf-8", newline="") as stream:
            if streaming:
                write_csv(program, stream)
            else:
                stream.write(export_csv(program))

    # Timing is measured separately: tracing allocations affects wall time.
    start = time.perf_counter()
    run()
    seconds = time.perf_counter() - start
    tracemalloc.start()
    try:
        run()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    return {"bytes": path.stat().st_size, "sha256": digest,
            "peak_python_bytes": peak, "seconds": round(seconds, 4)}


def main():
    program = synthetic_program()
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        buffered = measure(program, root / "buffered.csv", False)
        streamed = measure(program, root / "streamed.csv", True)
    assert buffered["sha256"] == streamed["sha256"]
    print(json.dumps({"python": platform.python_version(), "platform": platform.platform(),
                      "rows": 260000, "buffered": buffered, "streamed": streamed}, indent=2))


if __name__ == "__main__":
    main()
