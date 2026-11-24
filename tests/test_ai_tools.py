"""Offline provider-profile and tool-dispatch contract tests."""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator

from fitness_programming_toolkit import get_program_schema
from fitness_programming_toolkit.ai import PROFILES, call_tool, tool_definitions
from fitness_programming_toolkit.core import MAX_BYTES

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "examples/strength_program.json").read_text(encoding="utf-8")


class AIToolTests(unittest.TestCase):
    def test_profiles_are_valid_and_independent(self):
        for profile in PROFILES:
            with self.subTest(profile=profile):
                tools = tool_definitions(profile)
                declarations = tools[0]["function_declarations"] if profile == "gemini" else tools
                names = []
                for declaration in declarations:
                    fn = declaration["function"] if profile == "openai-chat" else declaration
                    names.append(fn["name"])
                    schema = fn["input_schema"] if profile == "anthropic" else fn["parameters"]
                    Draft202012Validator.check_schema(schema)
                    args = {} if fn["name"] == "fptk_schema" else {"plan_json": TEXT}
                    Draft202012Validator(schema).validate(args)
                    if profile == "openai-responses":
                        self.assertIs(fn["strict"], True)
                    schema["properties"].clear()
                self.assertEqual(set(names), {"fptk_schema", "fptk_validate", "fptk_summary"})
                self.assertNotEqual(tools, tool_definitions(profile))

    def test_dispatch_validates_and_summarizes(self):
        self.assertEqual(call_tool("fptk_schema", {})["schema"], get_program_schema())
        self.assertTrue(call_tool("fptk_validate", {"plan_json": TEXT})["valid"])
        result = call_tool("fptk_summary", {"plan_json": TEXT})
        self.assertEqual(result["summary"]["planned_sets"], 28)
        self.assertEqual(result["summary"]["planned_reps"], 272)

    def test_malformed_and_oversized_inputs(self):
        for text in ("not JSON", '{"a":1,"a":2}', "NaN", "[" * 2000,
                     "x" * (MAX_BYTES + 1), "é" * (MAX_BYTES // 2 + 1), "\ud800"):
            with self.subTest(size=len(text)):
                result = call_tool("fptk_validate", {"plan_json": text})
                self.assertFalse(result["ok"])
                self.assertEqual(result["error"]["code"], "invalid_plan")
                json.dumps(result, ensure_ascii=True)

    def test_allowlist_and_no_file_or_network_access(self):
        with patch("builtins.open", side_effect=AssertionError("unexpected file access")):
            self.assertTrue(call_tool("fptk_summary", {"plan_json": TEXT})["ok"])
            self.assertFalse(call_tool("read_file", {"path": "/etc/passwd"})["ok"])
            self.assertFalse(call_tool("fptk_validate", {"path": "secret.json"})["ok"])
            self.assertFalse(call_tool("fptk_validate", {"plan_json": TEXT, "path": "x"})["ok"])
            self.assertFalse(call_tool("fptk_validate", {"plan_json": None})["ok"])

    def test_unknown_profile(self):
        with self.assertRaises(ValueError):
            tool_definitions("unsupported")
