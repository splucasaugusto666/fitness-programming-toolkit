"""Golden-byte and import-safety contract for the public CSV exporter."""

from __future__ import annotations

import csv
import io
import tempfile
import unittest
from pathlib import Path

from fitness_programming_toolkit import export_csv, read_program
from fitness_programming_toolkit.cli import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
SOURCE = FIXTURES / "csv_contract_input.json"
GOLDEN = FIXTURES / "csv_contract_expected.csv"


class CsvContractTests(unittest.TestCase):
    def test_exact_utf8_bytes_match_golden_file(self):
        actual = export_csv(read_program(SOURCE)).encode("utf-8")
        self.assertEqual(actual, GOLDEN.read_bytes())

    def test_cli_writes_identical_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "result.csv"
            self.assertEqual(main(["export-csv", str(SOURCE), "--output", str(output)]), 0)
            self.assertEqual(output.read_bytes(), GOLDEN.read_bytes())

    def test_crlf_unicode_and_deterministic_expansion(self):
        raw = GOLDEN.read_bytes()
        self.assertIn("São Paulo".encode(), raw)
        self.assertIn("Ñ".encode(), raw)
        self.assertEqual(raw.count(b"\r\n"), 9)  # header + 2 weeks * 4 sets
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))
        records = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        self.assertEqual(len(records), 8)
        self.assertEqual([record["week"] for record in records], ["1"] * 4 + ["2"] * 4)
        self.assertEqual([record["set_number"] for record in records[:4]], ["1", "2", "1", "1"])
        self.assertEqual(records[0]["load_kg"], "")
        self.assertEqual(records[0]["rpe"], "")
        self.assertEqual(records[1]["load_kg"], "12.5")
        self.assertEqual(records[3]["load_kg"], "0.0")
        self.assertEqual(records[3]["rpe"], "1.0")
        self.assertEqual(records[0]["exercise_name"], "'=HYPERLINK(\"https://example.invalid\")")

    def test_formula_like_user_text_is_neutralized(self):
        records = list(csv.DictReader(io.StringIO(GOLDEN.read_text(encoding="utf-8"))))
        first = records[0]
        for key in ("program_id", "program_title", "session_id", "session_name",
                    "exercise_id", "exercise_name"):
            self.assertTrue(first[key].startswith("'"), key)
        self.assertEqual(records[3]["exercise_name"], "'@CMD")
        self.assertEqual(records[2]["exercise_name"], "Leg press, pés juntos")


if __name__ == "__main__":
    unittest.main()
