"""Executable contract for the Brazilian Portuguese integration example."""
from __future__ import annotations

import csv
import io
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from fitness_programming_toolkit import read_program, summarize_program, write_csv

ROOT = Path(__file__).resolve().parents[1]


class PortugueseExampleTests(unittest.TestCase):
    def test_documented_example(self):
        source = ROOT / "examples/ficha_treino_ptbr.json"
        schema = json.loads((ROOT / "schemas/program-1.0.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(json.loads(source.read_text(encoding="utf-8")))
        program = read_program(source)
        result = summarize_program(program)
        expected = {
            "sessions_per_week": 1,
            "weekly_sets": 3,
            "weekly_reps": 28,
            "planned_sessions": 4,
            "planned_sets": 12,
            "planned_reps": 112,
        }
        self.assertEqual({key: result[key] for key in expected}, expected)
        stream = io.StringIO(newline="")
        write_csv(program, stream)
        rows = list(csv.DictReader(io.StringIO(stream.getvalue())))
        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0]["session_name"], "Treino A — membros inferiores")
        self.assertEqual(rows[-1]["week"], "4")
