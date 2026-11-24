"""Test structural agreement and the intentionally documented runtime-only rules."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from fitness_programming_toolkit import DataValidationError, parse_program

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/program-1.0.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


def load(name):
    return json.loads((ROOT / "tests/fixtures" / name).read_text(encoding="utf-8"))


class JsonSchemaTests(unittest.TestCase):
    def test_schema_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(SCHEMA)

    def test_valid_fixtures(self):
        for sample in (
            load("schema_valid.json"),
            load("csv_contract_input.json"),
            json.loads((ROOT / "examples/strength_program.json").read_text(encoding="utf-8")),
        ):
            VALIDATOR.validate(sample)
            parse_program(sample)

    def test_invalid_fixture(self):
        self.assert_rejected_by_both(load("schema_invalid.json"))

    def assert_rejected_by_both(self, value):
        self.assertFalse(VALIDATOR.is_valid(value))
        with self.assertRaises(DataValidationError):
            parse_program(value)

    def test_structural_rejection_matrix(self):
        cases = [
            ("schema_version", 1), ("weeks", True), ("weeks", 53), ("weeks", 0),
            ("weeks", 1.5), ("program_id", "x" * 65), ("title", "x" * 121),
            ("title", ""), ("title", "  "), ("title", "leading\u00a0"),
            ("title", "\u3000leading"), ("title", "x\u007fy"),
            ("title", "x\ny"), ("title", "x\u2028"), ("sessions", []),
            ("unexpected", True),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                sample = load("schema_valid.json")
                sample[key] = value
                self.assert_rejected_by_both(sample)
        for key, value in [("reps", 1001), ("rest_seconds", -1), ("rpe", 11),
                           ("load_kg", -1), ("load_kg", True), ("unknown", 1)]:
            with self.subTest(key=key, value=value):
                sample = load("schema_valid.json")
                sample["sessions"][0]["exercises"][0]["sets"][0][key] = value
                self.assert_rejected_by_both(sample)

    def test_missing_required_and_nested_constraints(self):
        for target, key in [("program", "title"), ("session", "day_of_week"),
                            ("exercise", "name"), ("set", "rest_seconds")]:
            with self.subTest(target=target):
                p = load("schema_valid.json")
                s = p["sessions"][0]
                e = s["exercises"][0]
                t = e["sets"][0]
                del {"program": p, "session": s, "exercise": e, "set": t}[target][key]
                self.assert_rejected_by_both(p)
        for key, value in [("day_of_week", "Monday"), ("exercises", [])]:
            p = load("schema_valid.json")
            p["sessions"][0][key] = value
            self.assert_rejected_by_both(p)

    def test_runtime_only_duplicate_ids(self):
        for kind in ("session", "exercise"):
            with self.subTest(kind=kind):
                p = load("schema_valid.json")
                items = p["sessions"] if kind == "session" else p["sessions"][0]["exercises"]
                duplicate = copy.deepcopy(items[0])
                duplicate["name"] = "Different name, same identifier"
                items.append(duplicate)
                self.assertTrue(VALIDATOR.is_valid(p))
                with self.assertRaises(DataValidationError):
                    parse_program(p)

    def test_runtime_only_aggregate_limit(self):
        p = load("schema_valid.json")
        # 4 sessions * 50 exercises * 30 sets = 6000; each array is individually valid.
        p["sessions"] = [
            {"session_id": f"s{i}", "name": "Session", "day_of_week": "monday",
             "exercises": [{"exercise_id": f"e{j}", "name": "Exercise",
                            "sets": [{"reps": 1, "rest_seconds": 0} for _ in range(30)]}
                           for j in range(50)]}
            for i in range(4)
        ]
        self.assertTrue(VALIDATOR.is_valid(p))
        with self.assertRaisesRegex(DataValidationError, "maximum 5000"):
            parse_program(p)

    def test_runtime_only_integral_float(self):
        p = load("schema_valid.json")
        p["weeks"] = 1.0
        self.assertTrue(VALIDATOR.is_valid(p))
        with self.assertRaises(DataValidationError):
            parse_program(p)


if __name__ == "__main__":
    unittest.main()
