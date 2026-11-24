"""Optional authenticated WSGI adapter; importing it never opens a socket."""
from __future__ import annotations

import hmac
import json
import re
from http import HTTPStatus
from typing import Any
from urllib.parse import urlsplit

from .ai import call_tool
from .core import MAX_BYTES, DataValidationError, _unique_json_pairs

MAX_REQUEST_BYTES = 6 * MAX_BYTES + 128
_ROUTES = {
    "/v1/schema": ("GET", "fptk_schema"),
    "/v1/validate": ("POST", "fptk_validate"),
    "/v1/summary": ("POST", "fptk_summary"),
}


def _error(code: str, message: str) -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message}}


def _reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON constant")


def _response(description: str) -> dict[str, Any]:
    return {
        "description": description,
        "content": {"application/json": {"schema": {"type": "object"}}},
    }


def openapi_document(server_url: str | None = None) -> dict[str, Any]:
    """Return an OpenAPI 3.1 contract, with no credentials or default public host."""
    document = {
        "openapi": "3.1.0",
        "info": {
            "title": "FPTK read-only workout tools",
            "version": "1.0.0",
            "description": "Structural validation and planned counts, not exercise safety.",
        },
        "security": [{"bearerAuth": []}],
        "components": {"securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer"},
        }},
        "paths": {},
    }
    if server_url is not None:
        parsed = urlsplit(server_url)
        if (
            parsed.scheme != "https" or not parsed.hostname or parsed.username is not None
            or parsed.password is not None or parsed.query or parsed.fragment
            or any(c.isspace() or ord(c) < 32 for c in server_url)
        ):
            raise ValueError("Use an HTTPS server URL without credentials, query or fragment")
        document["servers"] = [{"url": server_url}]
    for path, (method, name) in _ROUTES.items():
        operation = {
            "operationId": name,
            "description": {
                "fptk_schema": "Return the structural workout schema.",
                "fptk_validate": "Validate supplied workout JSON, not physiological suitability.",
                "fptk_summary": "Validate JSON and calculate planned sessions, sets and reps.",
            }[name],
            "x-openai-isConsequential": False,
            "responses": {
                "200": _response("Successful read-only result"),
                "401": _response("Authentication required"),
                "400": _response("Invalid request"),
                "413": _response("Request too large"),
                "415": _response("Unsupported content type or encoding"),
                "422": _response("Invalid workout data"),
            },
        }
        if method == "POST":
            operation["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object", "additionalProperties": False,
                    "required": ["plan_json"],
                    "properties": {"plan_json": {
                        "type": "string", "maxLength": MAX_BYTES,
                        "description": "Complete FPTK 1.0 JSON text, at most 2 MB UTF-8.",
                    }},
                }}},
            }
        document["paths"][path] = {method.lower(): operation}
    return document


def create_app(token: str):
    """Create a read-only WSGI callable with mandatory operator-supplied bearer auth."""
    if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9._~-]{32,512}", token):
        raise ValueError("Use a random URL-safe bearer token of 32 to 512 characters")
    secret = token.encode("ascii")

    def application(environ, start_response):
        def respond(status: int, result: dict[str, Any], extra=()):
            body = json.dumps(result, ensure_ascii=True, allow_nan=False).encode("ascii")
            headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(body))),
                ("Cache-Control", "no-store"),
                ("X-Content-Type-Options", "nosniff"),
            ]
            headers.extend(extra)
            start_response(f"{status} {HTTPStatus(status).phrase}", headers)
            return [body]

        auth = environ.get("HTTP_AUTHORIZATION", "")
        scheme, _, supplied = auth.partition(" ")
        if (
            scheme.lower() != "bearer" or len(supplied) > 512
            or not hmac.compare_digest(supplied.encode("utf-8"), secret)
        ):
            return respond(401, _error("unauthorized", "Authentication required"),
                           (("WWW-Authenticate", "Bearer"),))
        route = _ROUTES.get(environ.get("PATH_INFO"))
        if route is None:
            return respond(404, _error("not_found", "Unknown route"))
        method, name = route
        if environ.get("REQUEST_METHOD") != method:
            return respond(405, _error("method_not_allowed", "Method not allowed"),
                           (("Allow", method),))
        if method == "GET":
            return respond(200, call_tool(name, {}))
        media_type = environ.get("CONTENT_TYPE", "").split(";", 1)[0].strip().lower()
        if media_type != "application/json" or environ.get("HTTP_CONTENT_ENCODING", "identity").lower() != "identity":
            return respond(415, _error("unsupported_media", "Expected uncompressed JSON"))
        length = environ.get("CONTENT_LENGTH", "")
        if not re.fullmatch(r"[0-9]{1,9}", length):
            return respond(400, _error("invalid_request", "Valid Content-Length required"))
        size = int(length)
        if size > MAX_REQUEST_BYTES:
            return respond(413, _error("too_large", "Request exceeds the transport limit"))
        try:
            raw = environ["wsgi.input"].read(size)
            if len(raw) != size:
                raise ValueError("Incomplete body")
            args = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_pairs,
                              parse_constant=_reject_constant)
        except (ValueError, RecursionError, OSError, DataValidationError):
            return respond(400, _error("invalid_request", "Malformed JSON request"))
        if type(args) is not dict or set(args) != {"plan_json"} or type(args["plan_json"]) is not str:
            return respond(400, _error("invalid_request", "Expected a plan_json string"))
        result = call_tool(name, args)
        return respond(200 if result["ok"] else 422, result)

    return application
