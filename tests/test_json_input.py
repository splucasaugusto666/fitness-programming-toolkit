"""Regression coverage for malformed JSON and non-scalar Unicode."""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from fitness_programming_toolkit import DataValidationError, export_csv, parse_program, read_program
from fitness_programming_toolkit.cli import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "strength_program.json"


def plan():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


class JsonInputTests(unittest.TestCase):
    def test_non_scalar_strings_rejected(self):
        for surrogate in ("\ud800", "\udfff"):
            for field in ("program_id", "title", "session_id", "exercise_id", "name"):
                with self.subTest(field=field, surrogate=repr(surrogate)):
                    data = plan()
                    if field in ("program_id", "title"):
                        target = data
                    elif field == "session_id":
                        target = data["sessions"][0]
                    else:
                        target = data["sessions"][0]["exercises"][0]
                    target[field] = surrogate
                    with self.assertRaisesRegex(DataValidationError, "Unicode scalar"):
                        parse_program(data)

    def test_valid_supplementary_unicode(self):
        data = plan()
        data["title"] = "Treino \U0001f3cb"
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "valid.json"
            source.write_text(json.dumps(data), encoding="utf-8")
            result = read_program(source)
        self.assertEqual(result.title, data["title"])
        self.assertIn(data["title"].encode(), export_csv(result).encode())

    def test_decoder_failures_and_cli_output_integrity(self):
        data = plan()
        data["title"] = "\ud800"
        cases = [
            (json.dumps(data).encode(), "Unicode scalar"),
            (b'{"title": "\xff"}', "malformed UTF-8 JSON"),
            (b'{"title": "x", "title": "y"}', "duplicate key"),
        ]
        limit = sys.get_int_max_str_digits()
        if 0 < limit < 100_000:
            cases.append((b'{"weeks": ' + b"9" * (limit + 1) + b"}", "malformed UTF-8 JSON"))
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "invalid.json"
            output = Path(temp) / "out.csv"
            for raw, message in cases:
                with self.subTest(message=message):
                    source.write_bytes(raw)
                    with self.assertRaisesRegex(DataValidationError, message) as caught:
                        read_program(source)
                    if message == "malformed UTF-8 JSON":
                        self.assertIsNotNone(caught.exception.__cause__)
                    for args in ([], ["--force"]):
                        if args:
                            output.write_bytes(b"existing\r\n")
                        stderr = io.StringIO()
                        with redirect_stderr(stderr):
                            code = main(["export-csv", str(source), "-o", str(output), *args])
                        self.assertEqual(code, 2)
                        self.assertIn(message, stderr.getvalue())
                        self.assertNotIn("Traceback", stderr.getvalue())
                        if args:
                            self.assertEqual(output.read_bytes(), b"existing\r\n")
                            output.unlink()
                        else:
                            self.assertFalse(output.exists())

    def test_recursion_error_from_decoder_is_chained(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "deep.json"
            source.write_text("[]", encoding="utf-8")
            with (
                patch("fitness_programming_toolkit.core.json.loads", side_effect=RecursionError),
                self.assertRaisesRegex(DataValidationError, "malformed UTF-8 JSON") as caught,
            ):
                read_program(source)
            self.assertIsInstance(caught.exception.__cause__, RecursionError)

    def test_deep_invalid_json_is_rejected_cleanly(self):
        # Interpreter versions differ in how the decoder limits nesting.
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "deep.json"
            source.write_bytes(b"[" * 2000 + b"0" + b"]" * 2000)
            with self.assertRaises(DataValidationError):
                read_program(source)
