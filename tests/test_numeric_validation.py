"""Regression tests for numeric validation errors and CLI exit codes."""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from fitness_programming_toolkit import DataValidationError, parse_program, read_program
from fitness_programming_toolkit.cli import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "strength_program.json"


def plan_with(field, value):
    plan = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    plan["sessions"][0]["exercises"][0]["sets"][0][field] = value
    return plan


class NumericValidationTests(unittest.TestCase):
    def test_large_integers_raise_field_validation_error(self):
        for field in ("load_kg", "rpe"):
            for value in (10**400, -(10**400)):
                with self.subTest(field=field, sign=value > 0):
                    with self.assertRaisesRegex(
                        DataValidationError,
                        rf"\$\.sessions\[0\]\.exercises\[0\]\.sets\[0\]\.{field}:",
                    ):
                        parse_program(plan_with(field, value))

    def test_nonfinite_and_boolean_values_remain_invalid(self):
        for field in ("load_kg", "rpe"):
            for value in (float("nan"), float("inf"), -float("inf"), True, False):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(DataValidationError):
                        parse_program(plan_with(field, value))

    def test_finite_boundaries_and_null_remain_valid(self):
        for field, values in (("load_kg", (0, 5000, 12.5, None)), ("rpe", (1, 10, 7.5, None))):
            for value in values:
                with self.subTest(field=field, value=value):
                    result = parse_program(plan_with(field, value))
                    actual = getattr(result.sessions[0].exercises[0].sets[0], field)
                    self.assertEqual(actual, None if value is None else float(value))
                    if value is not None:
                        self.assertIs(type(actual), float)

    def test_cli_invalid_numeric_input_never_writes_output(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "invalid.json"
            output = Path(temp) / "out.csv"
            for field in ("load_kg", "rpe"):
                with self.subTest(field=field):
                    source.write_text(json.dumps(plan_with(field, 10**400)), encoding="utf-8")
                    with self.assertRaisesRegex(DataValidationError, field):
                        read_program(source)
                    stderr = io.StringIO()
                    with redirect_stderr(stderr):
                        code = main(["export-csv", str(source), "-o", str(output)])
                    self.assertEqual(code, 2)
                    self.assertIn(field, stderr.getvalue())
                    self.assertNotIn("Traceback", stderr.getvalue())
                    self.assertFalse(output.exists())
                    output.write_bytes(b"existing file\n")
                    with redirect_stderr(io.StringIO()):
                        code = main(["export-csv", str(source), "-o", str(output), "--force"])
                    self.assertEqual(code, 2)
                    self.assertEqual(output.read_bytes(), b"existing file\n")
                    output.unlink()
