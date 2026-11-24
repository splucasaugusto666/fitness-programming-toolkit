"""Configuration profiles are pure, deterministic and isolated from the caller's cwd."""
from __future__ import annotations

import io
import json
import sys
import unittest
from unittest.mock import patch

from fitness_programming_toolkit.ai_cli import main
from fitness_programming_toolkit.mcp_config import CLIENTS, mcp_config


class MCPConfigTests(unittest.TestCase):
    def test_profiles_preserve_current_interpreter_and_safe_args(self):
        for profile in CLIENTS:
            with self.subTest(profile=profile):
                config = mcp_config(profile)
                group = "servers" if profile == "vscode" else "mcpServers"
                self.assertEqual(set(config), {group})
                entry = config[group]["fptk"]
                self.assertEqual(entry["command"], sys.executable)
                self.assertEqual(entry["args"], [
                    "-I", "-m", "fitness_programming_toolkit.mcp_server",
                ])
                self.assertEqual(set(entry), {"command", "args", "type"} if profile == "vscode"
                                 else {"command", "args"})
                if profile == "vscode":
                    self.assertEqual(entry["type"], "stdio")

    def test_config_is_fresh(self):
        config = mcp_config("cursor")
        config["mcpServers"]["fptk"]["args"].clear()
        self.assertEqual(mcp_config("cursor")["mcpServers"]["fptk"]["args"][0], "-I")

    def test_cli_emits_json_without_reading_stdin_or_writing_files(self):
        for profile in CLIENTS:
            with self.subTest(profile=profile):
                output = io.StringIO()
                with patch("sys.stdin") as stdin, patch("builtins.open") as opener:
                    status = main(["mcp-config", profile], stdout=output)
                    stdin.buffer.read.assert_not_called()
                    opener.assert_not_called()
                self.assertEqual(status, 0)
                self.assertEqual(json.loads(output.getvalue()), mcp_config(profile))

    def test_invalid_profile_and_missing_executable(self):
        with self.assertRaises(ValueError):
            mcp_config("unknown")
        with patch("sys.executable", ""), self.assertRaises(RuntimeError):
            mcp_config("cursor")

    def test_interpreter_with_spaces_is_preserved(self):
        # The profile preserves the path, not a shell-quoted command string.
        path = sys.executable.rsplit("/", 1)[0] + "/a path/python"
        if sys.platform == "win32":
            path = r"C:\Program Files\FPTK\python.exe"
        with patch("sys.executable", path):
            self.assertEqual(mcp_config("cursor")["mcpServers"]["fptk"]["command"], path)
