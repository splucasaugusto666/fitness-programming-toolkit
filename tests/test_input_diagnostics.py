"""Regression coverage for object keys and exclusive file creation."""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from fitness_programming_toolkit import DataValidationError, parse_program, read_program
from fitness_programming_toolkit.cli import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "strength_program.json"


class InputDiagnosticsTests(unittest.TestCase):
    def test_non_string_object_keys(self):
        for keys in [(1,), (1, "unknown"), (None,)]:
            with self.subTest(keys=keys):
                data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
                data.update(dict.fromkeys(keys, True))
                with self.assertRaisesRegex(DataValidationError, "object keys must be strings"):
                    parse_program(data)

    def test_unknown_and_duplicate_keys_escape_controls(self):
        for key in ("\x1b[31m", "\n", "\ud800"):
            with self.subTest(key=repr(key)), tempfile.TemporaryDirectory() as temp:
                data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
                data[key] = True
                with self.assertRaises(DataValidationError) as caught:
                    parse_program(data)
                self.assertNotIn(key, str(caught.exception))
                path = Path(temp) / "duplicate.json"
                quoted = json.dumps(key)
                path.write_text(f"{{{quoted}: 1, {quoted}: 2}}", encoding="utf-8")
                with self.assertRaisesRegex(DataValidationError, "duplicate key") as caught:
                    read_program(path)
                self.assertNotIn(key, str(caught.exception))

    def test_dangling_output_symlink_is_not_followed_without_force(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "unexpected.csv"
            link = Path(temp) / "output.csv"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = main(["export-csv", str(EXAMPLE), "-o", str(link)])
            self.assertEqual(result, 2)
            self.assertIn("already exists", stderr.getvalue())
            self.assertFalse(target.exists())
            self.assertTrue(link.is_symlink())
            self.assertEqual(stdout.getvalue(), "")
