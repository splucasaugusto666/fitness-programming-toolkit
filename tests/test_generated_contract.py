"""Deterministic generated contract checks with synthetic data only."""
from __future__ import annotations

import copy
import csv
import io
import json
import random
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from jsonschema import Draft202012Validator

from fitness_programming_toolkit import (
    DataValidationError,
    export_csv,
    parse_program,
    summarize_program,
)
from fitness_programming_toolkit.cli import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/strength_program.json"
VALIDATOR = Draft202012Validator(
    json.loads((ROOT / "schemas/program-1.0.schema.json").read_text(encoding="utf-8"))
)


def generate(seed):
    rng = random.Random(seed)
    sessions = []
    for si in range(rng.randint(1, 4)):
        exercises = []
        for ei in range(rng.randint(1, 4)):
            sets = []
            for _ in range(rng.randint(1, 5)):
                item = {"reps": rng.randint(1, 1000), "rest_seconds": rng.randint(0, 7200)}
                if rng.choice((True, False)):
                    item["load_kg"] = rng.choice((None, 0, 5000, rng.random() * 5000))
                if rng.choice((True, False)):
                    item["rpe"] = rng.choice((None, 1, 10, 1 + rng.random() * 9))
                sets.append(item)
            exercises.append({"exercise_id": f"e{ei}", "name": 'Agachamento, "ação"', "sets": sets})
        sessions.append({"session_id": f"s{si}", "name": "Sessão 🏋", "day_of_week": "monday",
                         "exercises": exercises})
    return {"schema_version": "1.0", "program_id": f"p{seed}", "title": "Treino sintético",
            "weeks": rng.randint(1, 6), "sessions": sessions}


class GeneratedContractTests(unittest.TestCase):
    def test_generated_valid_plans(self):
        for seed in range(64):
            with self.subTest(seed=seed):
                data = generate(seed)
                VALIDATOR.validate(data)
                program = parse_program(data)
                expected = [(s, e, i, t) for s in data["sessions"] for e in s["exercises"]
                            for i, t in enumerate(e["sets"], 1)]
                weeks = data["weeks"]
                summary = summarize_program(program)
                self.assertEqual(summary["weekly_sets"], len(expected))
                self.assertEqual(summary["planned_sets"], weeks * len(expected))
                self.assertEqual(summary["planned_reps"], weeks * sum(t["reps"] for _, _, _, t in expected))
                rows = list(csv.DictReader(io.StringIO(export_csv(program))))
                self.assertEqual(len(rows), len(expected) * weeks)
                self.assertEqual(export_csv(program), export_csv(parse_program(copy.deepcopy(data))))
                for pos, row in enumerate(rows):
                    s, e, i, t = expected[pos % len(expected)]
                    self.assertEqual(int(row["week"]), pos // len(expected) + 1)
                    self.assertEqual((row["session_id"], row["exercise_id"], int(row["set_number"])),
                                     (s["session_id"], e["exercise_id"], i))
                    self.assertEqual(int(row["reps"]), t["reps"])
                    self.assertEqual(int(row["rest_seconds"]), t["rest_seconds"])
                    for key in ("load_kg", "rpe"):
                        self.assertEqual(row[key], "" if t.get(key) is None else str(float(t[key])))

    def test_generated_invalid_mutations(self):
        for seed in range(64):
            for field, value in (("weeks", 0), ("weeks", True), ("title", ""),
                                 ("program_id", "x" * 65), ("schema_version", "2.0"),
                                 ("sessions", [])):
                with self.subTest(seed=seed, field=field, value=value):
                    data = generate(seed)
                    data[field] = value
                    self.assertFalse(VALIDATOR.is_valid(data))
                    with self.assertRaises(DataValidationError):
                        parse_program(data)

    def test_source_cannot_be_replaced(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "plan.json"
            shutil.copyfile(EXAMPLE, source)
            before = source.read_bytes()
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                status = main(["export-csv", str(source), "-o", str(source), "--force"])
            self.assertEqual(status, 2)
            self.assertIn("destination must differ", stderr.getvalue())
            self.assertEqual(source.read_bytes(), before)

    def test_source_alias_cannot_be_replaced(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "plan.json"
            shutil.copyfile(EXAMPLE, source)
            alias = Path(temp) / "alias.csv"
            try:
                alias.hardlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("hard links unavailable")
            before = source.read_bytes()
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                status = main(["export-csv", str(source), "-o", str(alias), "--force"])
            self.assertEqual(status, 2)
            self.assertIn("destination must differ", stderr.getvalue())
            self.assertEqual(source.read_bytes(), before)
            self.assertTrue(source.samefile(alias))
