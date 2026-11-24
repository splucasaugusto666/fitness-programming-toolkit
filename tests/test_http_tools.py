"""Exercise authenticated HTTP adapter without binding a network socket."""
from __future__ import annotations

import io
import json
import unittest
from pathlib import Path
from unittest.mock import Mock
from wsgiref.util import setup_testing_defaults
from wsgiref.validate import validator

from jsonschema import Draft202012Validator

from fitness_programming_toolkit.http_tools import MAX_REQUEST_BYTES, create_app, openapi_document

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "test-only-token-" + "a" * 32
PLAN = (ROOT / "examples/strength_program.json").read_text(encoding="utf-8")


class HTTPToolsTests(unittest.TestCase):
    def request(self, path="/v1/summary", method="POST", body=None, auth=None, **overrides):
        raw = json.dumps({"plan_json": PLAN}).encode("utf-8") if body is None else body
        environ = {}
        setup_testing_defaults(environ)
        environ.update({
            "PATH_INFO": path, "REQUEST_METHOD": method, "CONTENT_TYPE": "application/json",
            "CONTENT_LENGTH": str(len(raw)), "wsgi.input": io.BytesIO(raw),
            "HTTP_AUTHORIZATION": "Bearer " + TOKEN if auth is None else auth,
        })
        environ.update(overrides)
        captured = {}

        def start_response(status, headers, exc_info=None):
            captured.update(status=int(status.split()[0]), headers=dict(headers))
            return lambda data: None

        result = validator(create_app(TOKEN))(environ, start_response)
        try:
            data = json.loads(b"".join(result))
        finally:
            result.close()
        return captured["status"], data, captured["headers"]

    def test_summary_and_validate(self):
        status, data, headers = self.request()
        self.assertEqual(status, 200)
        self.assertEqual(data["summary"]["planned_sets"], 28)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertTrue(self.request(path="/v1/validate")[1]["valid"])

    def test_schema_and_openapi_contract(self):
        status, data, _ = self.request(path="/v1/schema", method="GET")
        self.assertEqual(status, 200)
        Draft202012Validator.check_schema(data["schema"])
        spec = openapi_document("https://example.org")
        self.assertEqual(spec["security"], [{"bearerAuth": []}])
        self.assertEqual(set(spec["paths"]), {"/v1/schema", "/v1/validate", "/v1/summary"})
        schema = spec["paths"]["/v1/summary"]["post"]["requestBody"]["content"]["application/json"]["schema"]
        Draft202012Validator(schema).validate({"plan_json": PLAN})
        self.assertNotIn("servers", openapi_document())

    def test_unauthorized_and_oversize_do_not_read_body(self):
        source = Mock()
        self.assertEqual(self.request(auth="", **{"wsgi.input": source})[0], 401)
        self.assertEqual(self.request(auth="Bearer wrong", **{"wsgi.input": source})[0], 401)
        self.assertEqual(self.request(CONTENT_LENGTH=str(MAX_REQUEST_BYTES + 1),
                                      **{"wsgi.input": source})[0], 413)
        source.read.assert_not_called()

    def test_reject_malformed_and_ambiguous_requests(self):
        for raw in (b"{}", b'{"plan_json":"{}","plan_json":"{}"}', b"NaN",
                    b'{"plan_json":null}', b"\xff", b"[" * 2000):
            with self.subTest(raw=raw[:40]):
                self.assertEqual(self.request(body=raw)[0], 400)
        self.assertEqual(self.request(CONTENT_LENGTH="99999999999999999999")[0], 400)
        self.assertEqual(self.request(CONTENT_LENGTH="999999")[0], 400)
        self.assertEqual(self.request(CONTENT_TYPE="text/plain")[0], 415)
        self.assertEqual(self.request(HTTP_CONTENT_ENCODING="gzip")[0], 415)

    def test_invalid_plan_and_allowlist(self):
        self.assertEqual(self.request(body=b'{"plan_json":"{}"}')[0], 422)
        self.assertEqual(self.request(path="/read_file")[0], 404)
        self.assertEqual(self.request(method="DELETE")[0], 405)

    def test_no_default_secret_or_insecure_server_url(self):
        for token in ("", "short", "a" * 32 + "\n"):
            with self.assertRaises(ValueError):
                create_app(token)
        for url in ("http://example.org", "https://user:pass@example.org",
                    "https://example.org?key=secret"):
            with self.assertRaises(ValueError):
                openapi_document(url)
