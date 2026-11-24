"""Optional local MCP server. Import the SDK only when launching."""
from __future__ import annotations

from typing import Any

from .ai import call_tool


def main() -> None:
    try:
        from mcp.server import MCPServer
    except ImportError as exc:
        raise SystemExit("Install the optional MCP extra: pip install '.[mcp]'") from exc

    server = MCPServer("Fitness Programming Toolkit")

    @server.tool(structured_output=True)
    def fptk_schema() -> dict[str, Any]:
        """Return the versioned structural workout JSON schema."""
        return call_tool("fptk_schema", {})

    @server.tool(structured_output=True)
    def fptk_validate(plan_json: str) -> dict[str, Any]:
        """Validate workout JSON structure, not exercise safety or suitability."""
        return call_tool("fptk_validate", {"plan_json": plan_json})

    @server.tool(structured_output=True)
    def fptk_summary(plan_json: str) -> dict[str, Any]:
        """Validate workout JSON and compute planned session, set and repetition counts."""
        return call_tool("fptk_summary", {"plan_json": plan_json})

    server.run()


if __name__ == "__main__":
    main()
