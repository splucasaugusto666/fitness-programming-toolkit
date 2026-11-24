"""Provider-neutral, read-only tool bridge. No model SDK or network calls."""
from __future__ import annotations

import json
from typing import Any

from .core import MAX_BYTES, DataValidationError, _unique_json_pairs, parse_program, summarize_program
from .schema import get_program_schema

PROFILES = ("openai-responses", "openai-chat", "anthropic", "gemini")
_DESCRIPTIONS = {
    "fptk_schema": "Return the versioned structural workout JSON schema.",
    "fptk_validate": "Validate workout JSON structure, not exercise safety or suitability.",
    "fptk_summary": "Validate workout JSON and compute planned session, set and repetition counts.",
}


def tool_definitions(profile: str) -> list[dict[str, Any]]:
    """Return fresh function declarations for one documented API profile."""
    if profile not in PROFILES:
        raise ValueError(f"Unknown tool profile: {profile!r}")
    definitions = []
    for name, description in _DESCRIPTIONS.items():
        properties = {} if name == "fptk_schema" else {
            "plan_json": {"type": "string", "description": "Complete FPTK 1.0 workout JSON text."}
        }
        parameters = {
            "type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False,
        }
        if profile == "anthropic":
            definitions.append({"name": name, "description": description, "input_schema": parameters})
        elif profile == "openai-responses":
            definitions.append({
                "type": "function", "name": name, "description": description,
                "parameters": parameters, "strict": True,
            })
        elif profile == "openai-chat":
            definitions.append({
                "type": "function",
                "function": {"name": name, "description": description, "parameters": parameters},
            })
        else:
            # Keep the GenerateContent declaration within the common schema subset.
            parameters.pop("additionalProperties")
            definitions.append({"name": name, "description": description, "parameters": parameters})
    if profile == "gemini":
        return [{"function_declarations": definitions}]
    return definitions


def _reject_constant(value: str) -> None:
    raise DataValidationError("Non-finite JSON number is not allowed")


def _parse_text(text: str):
    if type(text) is not str or len(text) > MAX_BYTES:
        raise DataValidationError("Expected JSON text within the 2 MB limit")
    try:
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise DataValidationError("JSON text exceeds the 2 MB limit")
        data = json.loads(text, object_pairs_hook=_unique_json_pairs, parse_constant=_reject_constant)
    except DataValidationError:
        raise
    except (ValueError, RecursionError) as exc:
        raise DataValidationError("Malformed UTF-8 JSON text") from exc
    return parse_program(data)


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute only allow-listed, side-effect-free operations on supplied JSON text."""
    if type(name) is not str or name not in _DESCRIPTIONS:
        return {"ok": False, "error": {"code": "unknown_tool", "message": "Unknown FPTK tool"}}
    expected = set() if name == "fptk_schema" else {"plan_json"}
    if type(arguments) is not dict or set(arguments) != expected:
        return {"ok": False, "error": {"code": "invalid_arguments", "message": "Unexpected arguments"}}
    if name == "fptk_schema":
        return {"ok": True, "schema": get_program_schema()}
    try:
        program = _parse_text(arguments["plan_json"])
    except DataValidationError as exc:
        # Bound model-visible diagnostics and escape non-printable characters.
        message = str(exc)[:512]
        message = "".join(c if c.isprintable() else ascii(c)[1:-1] for c in message)
        return {"ok": False, "error": {"code": "invalid_plan", "message": message}}
    if name == "fptk_validate":
        return {"ok": True, "valid": True, "schema_version": program.schema_version}
    return {"ok": True, "summary": summarize_program(program)}
