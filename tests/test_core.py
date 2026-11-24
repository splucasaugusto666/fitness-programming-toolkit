from __future__ import annotations

import copy
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from fitness_programming_toolkit import (
    DataValidationError, export_csv, parse_program, read_program, summarize_program,
)
from fitness_programming_toolkit.cli import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "examples/strength_program.json").read_text(encoding="utf-8"))


class ProgramTests(unittest.TestCase):
    def sample(self):
        return copy.deepcopy(EXAMPLE)

    def test_parse_and_summary(self):
        summary = summarize_program(parse_program(self.sample()))
        self.assertEqual(summary["weeks"], 4)
        self.assertEqual(summary["weekly_sets"], 7)
        self.assertEqual(summary["weekly_reps"], 68)
        self.assertEqual(summary["planned_sets"], 28)
        self.assertEqual(summary["planned_reps"], 272)
        self.assertEqual(summary["planned_sessions"], 8)

    def test_rows_per_week(self):
        rows = list(csv.DictReader(io.StringIO(export_csv(parse_program(self.sample())))))
        self.assertEqual(len(rows), 28)
        self.assertEqual(rows[0]["week"], "1")
        self.assertEqual(rows[-1]["week"], "4")
        self.assertEqual(rows[-1]["exercise_id"], "row")

    def test_missing_optional_fields_csv_blanks(self):
        rows = list(csv.DictReader(io.StringIO(export_csv(parse_program(self.sample())))))
        self.assertEqual(rows[3]["rpe"], "")
        self.assertEqual(rows[3]["load_kg"], "")

    def test_formula_injection_in_all_user_text(self):
        plan = self.sample()
        plan["title"] = "=SUM(A1:A2)"
        plan["program_id"] = "+CMD"
        s = plan["sessions"][0]
        s["session_id"] = "-12+4"
        s["name"] = "@DANGEROUS"
        s["exercises"][0]["exercise_id"] = "=A1"
        s["exercises"][0]["name"] = "=1+1"
        row = next(csv.DictReader(io.StringIO(export_csv(parse_program(plan)))))
        for key in ("program_title", "program_id", "session_id", "session_name",
                    "exercise_id", "exercise_name"):
            self.assertTrue(row[key].startswith("'"), key)

    def test_invalid_root(self):
        with self.assertRaisesRegex(DataValidationError, "expected object"):
            parse_program([])

    def test_missing_key(self):
        data = self.sample()
        del data["weeks"]
        with self.assertRaisesRegex(DataValidationError, "missing weeks"):
            parse_program(data)

    def test_unknown_key(self):
        data = self.sample()
        data["ignored"] = True
        with self.assertRaisesRegex(DataValidationError, "unsupported ignored"):
            parse_program(data)

    def test_version_must_match(self):
        data = self.sample()
        data["schema_version"] = "2.0"
        with self.assertRaisesRegex(DataValidationError, "only '1.0'"):
            parse_program(data)

    def test_weeks_bool_rejected(self):
        data = self.sample()
        data["weeks"] = True
        with self.assertRaisesRegex(DataValidationError, "weeks"):
            parse_program(data)

    def test_weeks_upper_bound(self):
        data = self.sample()
        data["weeks"] = 53
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_duplicate_sessions(self):
        data = self.sample()
        data["sessions"][1]["session_id"] = "day-a"
        with self.assertRaisesRegex(DataValidationError, "duplicate"):
            parse_program(data)

    def test_duplicate_exercise_in_session(self):
        data = self.sample()
        data["sessions"][0]["exercises"].append(copy.deepcopy(data["sessions"][0]["exercises"][0]))
        with self.assertRaisesRegex(DataValidationError, "duplicate"):
            parse_program(data)

    def test_exercise_repeated_across_sessions_is_allowed(self):
        data = self.sample()
        data["sessions"][1]["exercises"][0]["exercise_id"] = "squat"
        self.assertEqual(len(parse_program(data).sessions), 2)

    def test_day_validation(self):
        data = self.sample()
        data["sessions"][0]["day_of_week"] = "segunda"
        with self.assertRaisesRegex(DataValidationError, "weekday"):
            parse_program(data)

    def test_nonempty_sessions(self):
        data = self.sample()
        data["sessions"] = []
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_nonempty_sets(self):
        data = self.sample()
        data["sessions"][0]["exercises"][0]["sets"] = []
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_bool_reps_rejected(self):
        data = self.sample()
        data["sessions"][0]["exercises"][0]["sets"][0]["reps"] = True
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_reps_zero_rejected(self):
        data = self.sample()
        data["sessions"][0]["exercises"][0]["sets"][0]["reps"] = 0
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_float_rest_rejected(self):
        data = self.sample()
        data["sessions"][0]["exercises"][0]["sets"][0]["rest_seconds"] = 30.5
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_nan_rpe_rejected(self):
        data = self.sample()
        data["sessions"][0]["exercises"][0]["sets"][0]["rpe"] = float("nan")
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_inf_load_rejected(self):
        data = self.sample()
        data["sessions"][0]["exercises"][0]["sets"][0]["load_kg"] = float("inf")
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_negative_load_rejected(self):
        data = self.sample()
        data["sessions"][0]["exercises"][0]["sets"][0]["load_kg"] = -0.5
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_rpe_out_of_range(self):
        data = self.sample()
        data["sessions"][0]["exercises"][0]["sets"][0]["rpe"] = 11
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_bad_controls(self):
        data = self.sample()
        data["title"] = "bad\nline"
        with self.assertRaisesRegex(DataValidationError, "control"):
            parse_program(data)

    def test_trim_spaces(self):
        data = self.sample()
        data["title"] = "  trim me "
        with self.assertRaises(DataValidationError):
            parse_program(data)

    def test_malformed_json(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text('{not json', encoding="utf-8")
            with self.assertRaises(DataValidationError):
                read_program(path)

    def test_duplicate_json_object_keys_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "duplicate.json"
            path.write_text('{"weeks": 4, "weeks": 8}', encoding="utf-8")
            with self.assertRaisesRegex(DataValidationError, "duplicate key"):
                read_program(path)

    def test_file_too_large(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "big.json"
            path.write_bytes(b"X" * 2_000_001)
            with self.assertRaisesRegex(DataValidationError, "exceeds"):
                read_program(path)

    def test_cli_validate(self):
        self.assertEqual(main(["validate", str(ROOT / "examples/strength_program.json")]), 0)

    def test_cli_invalid_file_returns_2(self):
        self.assertEqual(main(["validate", "/path/that/does/not/exist.json"]), 2)

    def test_cli_export_guard_and_force(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.csv"
            src = str(ROOT / "examples/strength_program.json")
            self.assertEqual(main(["export-csv", src, "-o", str(dest)]), 0)
            self.assertTrue(dest.is_file())
            self.assertEqual(main(["export-csv", src, "-o", str(dest)]), 2)
            self.assertEqual(main(["export-csv", src, "-o", str(dest), "--force"]), 0)


if __name__ == "__main__":
    unittest.main()
