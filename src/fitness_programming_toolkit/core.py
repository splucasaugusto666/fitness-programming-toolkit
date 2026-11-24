"""Strict, dependency-free validator for a deliberately small workout format.

This is *not* a clinical safety checker or exercise recommendation engine.
Input and output are deterministic and intentionally do not perform network I/O.
"""

from __future__ import annotations

import csv
import io
import json
import math
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

MAX_BYTES = 2_000_000
MAX_SESSIONS = 30
MAX_EXERCISES_PER_SESSION = 50
MAX_SETS_PER_EXERCISE = 30
MAX_WEEKLY_SETS = 5000
DAYS = frozenset({
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
})
COLUMNS = (
    "program_id", "program_title", "week", "session_id", "session_name", "day_of_week",
    "exercise_id", "exercise_name", "set_number", "reps", "load_kg", "rpe", "rest_seconds",
)


class DataValidationError(ValueError):
    """Raised for invalid JSON structure or out-of-range program data."""


@dataclass(frozen=True)
class PrescriptionSet:
    reps: int
    load_kg: float | None
    rpe: float | None
    rest_seconds: int


@dataclass(frozen=True)
class Exercise:
    exercise_id: str
    name: str
    sets: tuple[PrescriptionSet, ...]


@dataclass(frozen=True)
class Session:
    session_id: str
    name: str
    day_of_week: str
    exercises: tuple[Exercise, ...]


@dataclass(frozen=True)
class Program:
    program_id: str
    title: str
    weeks: int
    sessions: tuple[Session, ...]
    schema_version: str = "1.0"


def _display_key(key: str) -> str:
    """Keep control characters and isolated surrogates out of error messages."""
    return key if key.isprintable() else ascii(key)


def _object(value: Any, path: str, *, fields: set[str], required: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DataValidationError(f"{path}: expected object")
    if any(not isinstance(key, str) for key in value):
        raise DataValidationError(f"{path}: object keys must be strings")
    missing = required - value.keys()
    if missing:
        raise DataValidationError(f"{path}: missing {', '.join(sorted(missing))}")
    unexpected = value.keys() - fields
    if unexpected:
        keys = ", ".join(_display_key(key) for key in sorted(unexpected))
        raise DataValidationError(f"{path}: unsupported {keys}")
    return value


def _string(value: Any, path: str, *, max_length: int = 120) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DataValidationError(f"{path}: expected nonempty string")
    if len(value) > max_length or value != value.strip():
        raise DataValidationError(f"{path}: must be trimmed, length <= {max_length}")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise DataValidationError(f"{path}: control characters are not allowed")
    if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
        raise DataValidationError(f"{path}: expected Unicode scalar values")
    return value


def _integer(value: Any, path: str, *, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise DataValidationError(f"{path}: expected integer in [{low}, {high}]")
    return value


def _number(value: Any, path: str, *, low: float, high: float) -> float:
    # Compare bounds before float conversion: Python integers can exceed float range.
    if type(value) not in (int, float) or not low <= value <= high or not math.isfinite(value):
        raise DataValidationError(f"{path}: expected finite number in [{low}, {high}]")
    return float(value)


def _array(value: Any, path: str, *, max_length: int) -> list[Any]:
    if not isinstance(value, list) or not 1 <= len(value) <= max_length:
        raise DataValidationError(f"{path}: expected nonempty array (max {max_length})")
    return value


def parse_program(payload: Mapping[str, Any]) -> Program:
    """Parse a JSON-shaped mapping; reject unknown keys and invalid numeric values.

    Every session is a weekly template repeated for `weeks`. This toolkit
    validates plan structure, not training suitability or physiological safety.
    """
    obj = _object(payload, "$", fields={"schema_version", "program_id", "title", "weeks", "sessions"},
                  required={"schema_version", "program_id", "title", "weeks", "sessions"})
    if obj["schema_version"] != "1.0":
        raise DataValidationError("$.schema_version: only '1.0' is supported")
    pid = _string(obj["program_id"], "$.program_id", max_length=64)
    title = _string(obj["title"], "$.title")
    weeks = _integer(obj["weeks"], "$.weeks", low=1, high=52)
    items = _array(obj["sessions"], "$.sessions", max_length=MAX_SESSIONS)
    sessions: list[Session] = []
    session_ids: set[str] = set()
    weekly_sets = 0
    for si, raw_session in enumerate(items):
        path = f"$.sessions[{si}]"
        s = _object(raw_session, path, fields={"session_id", "name", "day_of_week", "exercises"},
                    required={"session_id", "name", "day_of_week", "exercises"})
        sid = _string(s["session_id"], path + ".session_id", max_length=64)
        if sid in session_ids:
            raise DataValidationError(f"{path}.session_id: duplicate '{sid}'")
        session_ids.add(sid)
        sname = _string(s["name"], path + ".name")
        day = _string(s["day_of_week"], path + ".day_of_week")
        if day not in DAYS:
            raise DataValidationError(f"{path}.day_of_week: expected lowercase English weekday")
        exercises: list[Exercise] = []
        exercise_ids: set[str] = set()
        for ei, raw_exercise in enumerate(_array(s["exercises"], path + ".exercises",
                                                 max_length=MAX_EXERCISES_PER_SESSION)):
            ep = f"{path}.exercises[{ei}]"
            e = _object(raw_exercise, ep, fields={"exercise_id", "name", "sets"},
                        required={"exercise_id", "name", "sets"})
            eid = _string(e["exercise_id"], ep + ".exercise_id", max_length=64)
            if eid in exercise_ids:
                raise DataValidationError(f"{ep}.exercise_id: duplicate '{eid}' in session")
            exercise_ids.add(eid)
            ename = _string(e["name"], ep + ".name")
            sets: list[PrescriptionSet] = []
            for ti, raw_set in enumerate(_array(e["sets"], ep + ".sets",
                                                max_length=MAX_SETS_PER_EXERCISE)):
                sp = f"{ep}.sets[{ti}]"
                t = _object(raw_set, sp, fields={"reps", "load_kg", "rpe", "rest_seconds"},
                            required={"reps", "rest_seconds"})
                reps = _integer(t["reps"], sp + ".reps", low=1, high=1000)
                rest = _integer(t["rest_seconds"], sp + ".rest_seconds", low=0, high=7200)
                load = None if t.get("load_kg") is None else _number(t["load_kg"],
                                    sp + ".load_kg", low=0, high=5000)
                rpe = None if t.get("rpe") is None else _number(t["rpe"],
                                    sp + ".rpe", low=1, high=10)
                sets.append(PrescriptionSet(reps=reps, load_kg=load,
                                            rpe=rpe, rest_seconds=rest))
                weekly_sets += 1
                if weekly_sets > MAX_WEEKLY_SETS:
                    raise DataValidationError("$.sessions: maximum 5000 weekly sets exceeded")
            exercises.append(Exercise(exercise_id=eid, name=ename, sets=tuple(sets)))
        sessions.append(Session(session_id=sid, name=sname, day_of_week=day,
                                exercises=tuple(exercises)))
    return Program(program_id=pid, title=title, weeks=weeks, sessions=tuple(sessions))


def _unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DataValidationError(f"JSON: duplicate key {ascii(key)}")
        result[key] = value
    return result


def read_program(path: str | Path) -> Program:
    """Read no more than 2 MB of UTF-8 JSON from disk."""
    p = Path(path)
    with p.open("rb") as file:
        raw = file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise DataValidationError(f"{p}: exceeds {MAX_BYTES} bytes")
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_pairs)
    except DataValidationError:
        raise
    except (ValueError, RecursionError) as exc:
        raise DataValidationError(f"{p}: malformed UTF-8 JSON: {exc}") from exc
    return parse_program(payload)


def summarize_program(program: Program) -> dict[str, Any]:
    weekly_sets = sum(len(ex.sets) for s in program.sessions for ex in s.exercises)
    weekly_reps = sum(t.reps for s in program.sessions for ex in s.exercises
                      for t in ex.sets)
    return {
        "program_id": program.program_id,
        "title": program.title,
        "weeks": program.weeks,
        "sessions_per_week": len(program.sessions),
        "weekly_sets": weekly_sets,
        "weekly_reps": weekly_reps,
        "planned_sessions": len(program.sessions) * program.weeks,
        "planned_sets": weekly_sets * program.weeks,
        "planned_reps": weekly_reps * program.weeks,
    }


def _safe_cell(text: str) -> str:
    """Neutralize spreadsheet formulas in untrusted user-supplied text fields."""
    # Quoting alone does not prevent Excel/LibreOffice formula interpretation.
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def iter_csv_rows(program: Program) -> Iterator[tuple[str | int | float, ...]]:
    """Yield records in stable week / session / exercise / set order."""
    for week in range(1, program.weeks + 1):
        for session in program.sessions:
            for exercise in session.exercises:
                for ti, item in enumerate(exercise.sets, start=1):
                    yield (
                        _safe_cell(program.program_id), _safe_cell(program.title), week,
                        _safe_cell(session.session_id), _safe_cell(session.name),
                        session.day_of_week, _safe_cell(exercise.exercise_id),
                        _safe_cell(exercise.name), ti, item.reps,
                        "" if item.load_kg is None else item.load_kg,
                        "" if item.rpe is None else item.rpe, item.rest_seconds,
                    )


def write_csv(program: Program, stream: TextIO) -> None:
    """Write CSV incrementally to a caller-owned text stream opened with newline=""."""
    writer = csv.writer(stream, lineterminator="\r\n")
    writer.writerow(COLUMNS)
    writer.writerows(iter_csv_rows(program))


def export_csv(program: Program) -> str:
    """Return RFC4180-compatible CSV text, without writing to a file."""
    stream = io.StringIO(newline="")
    write_csv(program, stream)
    return stream.getvalue()
