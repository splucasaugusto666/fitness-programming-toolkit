"""Contract checks for the local machine-readable AI CLI."""
from __future__ import annotations

import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from fitness_programming_toolkit.ai import PROFILES, call_tool, tool_definitions
from fitness_programming_toolkit.ai_cli import main
from fitness_programming_toolkit.core import MAX_BYTES

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "examples/strength_program.json").read_bytes()


class AICLITests(unittest.TestCase):
    def invoke(self, args, raw=b""):
        output = io.StringIO()
        status = main(args, stdin=io.BytesIO(raw), stdout=output)
        return status, json.loads(output.getvalue())

    def test_all_provider_declarations_match_api(self):
        for profile in PROFILES:
            with self.subTest(profile=profile):
                self.assertEqual(self.invoke(["tools", profile]), (0, tool_definitions(profile)))

    def test_schema_needs_no_stdin(self):
        with patch("sys.stdin") as stdin:
            stdin.buffer.read.side_effect = AssertionError("unexpected stdin read")
            output = io.StringIO()
            self.assertEqual(main(["call", "fptk_schema"], stdout=output), 0)
            self.assertEqual(json.loads(output.getvalue()), call_tool("fptk_schema", {}))

    def test_summary_matches_dispatcher(self):
        expected = call_tool("fptk_summary", {"plan_json": SOURCE.decode("utf-8")})
        self.assertEqual(self.invoke(["call", "fptk_summary"], SOURCE), (0, expected))

    def test_malformed_unicode_duplicate_and_nonfinite(self):
        for raw in (b"{}", b"\xff", b'{"x":1,"x":2}', b"NaN"):
            with self.subTest(raw=raw):
                status, result = self.invoke(["call", "fptk_validate"], raw)
                self.assertEqual(status, 2)
                self.assertFalse(result["ok"])
                self.assertEqual(result["error"]["code"], "invalid_plan")

    def test_bounded_read_and_no_input_file_paths(self):
        source = io.BytesIO(b"x" * (MAX_BYTES + 100))
        output = io.StringIO()
        self.assertEqual(main(["call", "fptk_validate"], stdin=source, stdout=output), 2)
        self.assertEqual(source.tell(), MAX_BYTES + 1)
        self.assertFalse(json.loads(output.getvalue())["ok"])

    def test_io_failure_returns_machine_readable_error(self):
        source = io.BytesIO()
        with patch.object(source, "read", side_effect=OSError("simulated failure")):
            output = io.StringIO()
            self.assertEqual(main(["call", "fptk_validate"], stdin=source, stdout=output), 2)
            self.assertFalse(json.loads(output.getvalue())["ok"])
