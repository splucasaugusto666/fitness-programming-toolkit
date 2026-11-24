"""Exercise the optional MCP server over real local stdio, without any model."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parents[1]


async def run() -> None:
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "fitness_programming_toolkit.mcp_server"]
    )
    async with Client(params) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools.tools} == {
            "fptk_schema", "fptk_validate", "fptk_summary",
        }
        source = (ROOT / "examples/strength_program.json").read_text(encoding="utf-8")
        result = await client.call_tool("fptk_summary", {"plan_json": source})
        assert result.structured_content["summary"]["planned_sets"] == 28
        invalid = await client.call_tool("fptk_validate", {"plan_json": "{}"})
        assert invalid.structured_content["ok"] is False
        schema = await client.call_tool("fptk_schema", {})
        assert schema.structured_content["ok"] is True


if __name__ == "__main__":
    asyncio.run(run())
