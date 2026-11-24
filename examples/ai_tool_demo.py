"""Offline integration demonstration for every supported provider profile."""
from __future__ import annotations

import json
from pathlib import Path

from fitness_programming_toolkit.ai import PROFILES, call_tool, tool_definitions

ROOT = Path(__file__).resolve().parent


def main():
    text = (ROOT / "strength_program.json").read_text(encoding="utf-8")
    result = call_tool("fptk_summary", {"plan_json": text})
    if not result["ok"]:
        raise RuntimeError("Synthetic example failed validation")
    print(json.dumps({
        "provider_profiles": {profile: tool_definitions(profile) for profile in PROFILES},
        "simulated_tool_result": result,
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
