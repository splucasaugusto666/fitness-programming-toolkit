"""Failure-injection tests for transactional CSV publication."""
from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fitness_programming_toolkit import export_csv, read_program
from fitness_programming_toolkit.cli import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "strength_program.json"


class AtomicExportTests(unittest.TestCase):
    def run_export(self, output: Path, *, force: bool = False) -> int:
        args = ["export-csv", str(EXAMPLE), "-o", str(output)]
        if force:
            args.append("--force")
        with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
            return main(args)

    def test_sync_failure_preserves_existing_and_absent_destinations(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            existing = folder / "existing.csv"
            existing.write_bytes(b"previous\r\n")
            absent = folder / "absent.csv"
            with patch("fitness_programming_toolkit.cli.os.fsync", side_effect=OSError("disk")):
                self.assertEqual(self.run_export(existing, force=True), 2)
                self.assertEqual(self.run_export(absent), 2)
            self.assertEqual(existing.read_bytes(), b"previous\r\n")
            self.assertFalse(absent.exists())
            self.assertEqual(list(folder.iterdir()), [existing])

    def test_publish_failure_preserves_original_and_cleans_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "output.csv"
            output.write_bytes(b"original")
            with patch("fitness_programming_toolkit.cli.os.replace", side_effect=OSError("io")):
                self.assertEqual(self.run_export(output, force=True), 2)
            self.assertEqual(output.read_bytes(), b"original")
            self.assertEqual(list(folder.iterdir()), [output])

    def test_concurrent_creation_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "out.csv"

            def competing_writer(source, destination):
                Path(destination).write_bytes(b"competitor")
                raise FileExistsError(str(destination))

            with patch("fitness_programming_toolkit.cli.os.link", side_effect=competing_writer):
                self.assertEqual(self.run_export(output), 2)
            self.assertEqual(output.read_bytes(), b"competitor")
            self.assertEqual(list(folder.iterdir()), [output])

    def test_success_preserves_csv_contract_and_cleans_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "out.csv"
            expected = export_csv(read_program(EXAMPLE)).encode("utf-8")
            self.assertEqual(self.run_export(output), 0)
            self.assertEqual(output.read_bytes(), expected)
            self.assertEqual(self.run_export(output, force=True), 0)
            self.assertEqual(output.read_bytes(), expected)
            self.assertEqual(list(folder.iterdir()), [output])

    def test_force_replaces_symlink_entry_without_writing_through(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            target = folder / "target.csv"
            output = folder / "out.csv"
            target.write_bytes(b"unrelated")
            try:
                output.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            self.assertEqual(self.run_export(output, force=True), 0)
            self.assertFalse(output.is_symlink())
            self.assertEqual(target.read_bytes(), b"unrelated")
            self.assertEqual(output.read_bytes(), export_csv(read_program(EXAMPLE)).encode())
