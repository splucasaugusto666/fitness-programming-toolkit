"""Generate local MCP client configuration without installing or editing clients."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

CLIENTS = ("claude-desktop", "cursor", "vscode", "mcpservers")


def mcp_config(client: str) -> dict[str, Any]:
    """Return a fresh configuration fragment for the current Python environment."""
    if client not in CLIENTS:
        raise ValueError(f"Unknown MCP client profile: {client!r}")
    if not sys.executable or not Path(sys.executable).is_absolute():
        raise RuntimeError("An absolute Python executable is required")
    # Do not resolve symlinks: a virtual environment's interpreter must stay intact.
    # Isolated mode excludes the working directory and PYTHONPATH from imports.
    server = {
        "command": sys.executable,
        "args": ["-I", "-m", "fitness_programming_toolkit.mcp_server"],
    }
    if client == "vscode":
        return {"servers": {"fptk": {"type": "stdio", **server}}}
    return {"mcpServers": {"fptk": server}}
