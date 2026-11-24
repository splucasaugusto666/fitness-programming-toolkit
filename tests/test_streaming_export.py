"""Streaming CSV contract and failure isolation."""
from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fitness_programming_toolkit import export_csv, read_program, write_csv
from fitness_programming_toolkit.cli import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/csv_contract_input.json"


class StreamingExportTests(unittest.TestCase):
    def test_golden_stream_bytes(self):
        program = read_program(FIXTURE)
        stream = io.StringIO(newline="")
        write_csv(program, stream)
        expected = (ROOT / "tests/fixtures/csv_contract_expected.csv").read_bytes()
        self.assertEqual(stream.getvalue().encode("utf-8"), expected)
        self.assertEqual(stream.getvalue(), export_csv(program))
        self.assertFalse(stream.closed)

    def test_rows_are_written_incrementally(self):
        class CountingStream(io.StringIO):
            def __init__(self):
                super().__init__(newline="")
                self.calls = 0

            def write(self, value):
                self.calls += 1
                return super().write(value)

        stream = CountingStream()
        write_csv(read_program(FIXTURE), stream)
        self.assertEqual(stream.calls, 9)  # header + eight rows

    def test_stream_failure_preserves_destination(self):
        def broken_write(program, stream):
            stream.write("partial")
            raise OSError("simulated write failure")

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "output.csv"
            output.write_bytes(b"original")
            with (
                patch("fitness_programming_toolkit.cli.write_csv", side_effect=broken_write),
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(main(["export-csv", str(FIXTURE), "-o", str(output), "--force"]), 2)
                self.assertEqual(main(["export-csv", str(FIXTURE), "-o", str(folder / "new.csv")]), 2)
            self.assertEqual(output.read_bytes(), b"original")
            self.assertEqual(list(folder.iterdir()), [output])
