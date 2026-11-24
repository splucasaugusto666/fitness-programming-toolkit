"""Machine-readable CLI for the optional provider-neutral AI bridge."""
from __future__ import annotations

import argparse
import json
import sys
from typing import BinaryIO, TextIO

from .ai import PROFILES, call_tool, tool_definitions
from .core import MAX_BYTES


def main(
    argv: list[str] | None = None,
    *,
    stdin: BinaryIO | None = None,
    stdout: TextIO | None = None,
) -> int:
    """Emit JSON only; read bounded UTF-8 input for read-only plan operations."""
    parser = argparse.ArgumentParser(prog="fptk-ai", description="Offline FPTK AI tools")
    commands = parser.add_subparsers(dest="command", required=True)
    tools = commands.add_parser("tools", help="Print provider tool declarations")
    tools.add_argument("profile", choices=PROFILES)
    invoke = commands.add_parser("call", help="Run a read-only tool locally")
    invoke.add_argument("name", choices=("fptk_schema", "fptk_validate", "fptk_summary"))
    args = parser.parse_args(argv)
    output = sys.stdout if stdout is None else stdout
    if args.command == "tools":
        result = tool_definitions(args.profile)
    elif args.name == "fptk_schema":
        result = call_tool(args.name, {})
    else:
        source = sys.stdin.buffer if stdin is None else stdin
        try:
            raw = source.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                result = call_tool(args.name, {"plan_json": None})
            else:
                result = call_tool(args.name, {"plan_json": raw.decode("utf-8")})
        except (OSError, UnicodeError):
            result = {
                "ok": False,
                "error": {"code": "invalid_plan", "message": "Cannot read UTF-8 JSON input"},
            }
    print(json.dumps(result, ensure_ascii=True, allow_nan=False), file=output)
    return 2 if isinstance(result, dict) and not result.get("ok") else 0


if __name__ == "__main__":
    raise SystemExit(main())
