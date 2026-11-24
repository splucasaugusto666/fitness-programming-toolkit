"""Test schema discovery for installed and offline consumers."""
from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator

from fitness_programming_toolkit import get_program_schema, parse_program
from fitness_programming_toolkit.cli import main

ROOT = Path(__file__).resolve().parents[1]


class SchemaDiscoveryTests(unittest.TestCase):
    def test_bundled_schema_matches_public_contract(self):
        resource = files("fitness_programming_toolkit").joinpath("program-1.0.schema.json")
        self.assertEqual(resource.read_bytes(), (ROOT / "schemas/program-1.0.schema.json").read_bytes())
        Draft202012Validator.check_schema(get_program_schema())

    def test_schema_is_independent_and_usable(self):
        first = get_program_schema()
        first["properties"].clear()
        second = get_program_schema()
        self.assertIn("schema_version", second["properties"])
        payload = json.loads((ROOT / "examples/strength_program.json").read_text(encoding="utf-8"))
        Draft202012Validator(second).validate(payload)
        self.assertEqual(parse_program(payload).schema_version, "1.0")

    def test_cli_schema_matches_api(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["schema"]), 0)
        self.assertEqual(json.loads(output.getvalue()), get_program_schema())
