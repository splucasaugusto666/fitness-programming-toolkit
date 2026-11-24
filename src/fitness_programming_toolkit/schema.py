"""Offline access to the versioned structural workout schema."""
from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def get_program_schema() -> dict[str, Any]:
    """Return a fresh copy of the bundled JSON Schema 2020-12 for format 1.0."""
    resource = files("fitness_programming_toolkit").joinpath("program-1.0.schema.json")
    return json.loads(resource.read_text(encoding="utf-8"))
