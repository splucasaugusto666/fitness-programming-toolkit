# AI agent integration: MCP and function calling

FPTK offers a local, deterministic tool layer for workout JSON validation and
planned volume calculation. No model SDK, API key, network request or model
inference is required to execute the tools. This does not generate training
prescriptions or verify clinical suitability. Do not send personal or health
records to a model provider without appropriate authorization.

## Provider profiles

The standard-library adapter returns fresh tool declarations. It does not call
provider APIs or manage authentication, billing, conversation state or retries.

| API or host | Profile / route |
| --- | --- |
| OpenAI Responses, compatible endpoints | openai-responses |
| OpenAI Chat Completions; compatible DeepSeek, Mistral, Groq, Ollama endpoints | openai-chat |
| Anthropic Claude Messages | anthropic |
| Gemini GenerateContent (Python SDK tool declarations) | gemini |
| Claude Desktop, Claude Code, Cursor, VS Code and other local MCP clients | Optional stdio MCP |
| Other AI systems, including models without tool support | JSON schema + application-side validation |

Compatibility is at the documented tool-declaration level, not a claim of live
provider certification. Model/endpoint support varies. The ChatGPT consumer app
and other hosted chat products do not automatically gain access to local stdio;
they may require separately authorized hosting or connectors. No remote server is deployed.

```python
from fitness_programming_toolkit.ai import call_tool, tool_definitions

tools = tool_definitions("openai-responses")
# Pass tools to the provider request using your own SDK and credentials.
# On receipt of a tool call, decode its arguments and dispatch locally:
result = call_tool("fptk_validate", {"plan_json": "{}"})
assert result["ok"] is False
```

For Chat Completions, pass the openai-chat list as tools; for Claude Messages,
pass the anthropic list. For Gemini GenerateContent with the Python SDK, pass
the gemini list as config.tools. Return the JSON result as the matching tool
response with its original call ID/name as required by the provider. The host
must handle provider errors, and must not execute arbitrary tool names.

All three tools are read-only: fptk_schema, fptk_validate, fptk_summary.
The latter two take a single string plan_json (maximum 2 MB UTF-8).
The portable argument envelope avoids requiring each model to support the full
workout schema's JSON Schema dialect. Retrieve the schema separately. Invalid
input yields a bounded diagnostic with a stable error code. No file paths,
arbitrary code, shell commands, or CSV writes are exposed.

## Offline command-line integration (any language)

The default branch includes a standalone entry point for applications that
cannot import Python directly. From the installed environment:

```sh
fptk-ai tools openai-responses
fptk-ai tools openai-chat
fptk-ai tools anthropic
fptk-ai tools gemini
fptk-ai call fptk_schema
fptk-ai call fptk_summary < examples/strength_program.json
```

The last command uses shell input redirection (POSIX shells or cmd.exe).
For PowerShell or other languages, launch the process with binary UTF-8
standard input and capture standard output. The module is also executable
as `python -m fitness_programming_toolkit.ai_cli`.

The call interface accepts raw workout JSON on stdin (not an argument
envelope), and reads at most 2 MB plus one byte. All tool results are JSON
on stdout; invalid plan/input returns exit code 2. Provider declarations
are emitted as JSON arrays. Argument parsing errors use argparse's normal
stderr and exit code 2. There is no file-path parameter, network access,
model inference, or CSV write operation in this interface.

The synthetic [offline provider example](../examples/ai_tool_demo.py)
can be run with `python examples/ai_tool_demo.py`. It prints declarations
for every profile and a simulated result from the same local dispatcher;
it does not send any API request. A host still needs to implement its
provider's message and tool-result protocol.

## Optional local MCP server

From a checkout, use a separate environment:

```sh
python -m pip install '.[mcp]'
python -m fitness_programming_toolkit.mcp_server
```

Generate the configuration from the same environment where the MCP extra is installed:

```sh
fptk-ai mcp-config claude-desktop
fptk-ai mcp-config cursor
fptk-ai mcp-config vscode
fptk-ai mcp-config mcpservers
```

The first two use the standard `mcpServers` object; the VS Code profile uses
the editor-managed `servers` object. The generic profile is intended for
compatible local clients. Merge the single FPTK entry into your existing
configuration manually, following the client's instructions; do not overwrite
unrelated settings. The generator does not modify files, install anything,
include credentials or start a server. A missing MCP extra must be installed
before launching the server. These configurations are based on the clients'
documented formats; individual desktop applications are not exercised in CI.

The generated command uses the current Python executable (including the virtual
environment path) and isolated mode (`-I`). This reduces import shadowing by
the current directory or PYTHONPATH. It is not an OS sandbox and does not
protect against a compromised Python environment. Install into a trusted virtual
environment rather than relying on user-site packages, which isolated mode
excludes. The config should not be committed if it contains a machine-specific path.

Example for clients accepting mcpServers JSON:

```json
{
  "mcpServers": {
    "fptk": {
      "command": "/absolute/path/to/python",
      "args": ["-I", "-m", "fitness_programming_toolkit.mcp_server"]
    }
  }
}
```

This starts a local stdio process; it does not open a network listener.
The MCP SDK is optional and is never imported by the core. Run the
protocol smoke test with python tools/check_mcp.py after installing the extra.
Cloud API calls may incur charges; the local validation itself is free.

## Optional authenticated HTTP adapter / OpenAPI for remote agents

The default branch includes a separate WSGI application factory. It does not
start a server, deploy anything or expose the local filesystem. Export the
OpenAPI 3.1 contract:

```sh
fptk-ai openapi
fptk-ai openapi --server-url https://your-operator-controlled-host.example
```

A deployment operator can create the callable in their own WSGI entry point:

```python
import os
from fitness_programming_toolkit.http_tools import create_app

application = create_app(os.environ["FPTK_HTTP_TOKEN"])
```

Generate a cryptographically random token (for example with Python's secrets
module); never commit it or put it in the OpenAPI document. Use a production
WSGI server behind HTTPS, with request limits, timeouts, rate limiting and
access control. The application requires an Authorization: Bearer header on
every route and does not log request bodies. It accepts uncompressed JSON with
Content-Length; the transport envelope is bounded to 12,000,128 bytes, and the
inner plan remains limited to 2,000,000 UTF-8 bytes. The host must enforce its
own transport limits and ensure upstream request framing is correct. This is
not a multi-tenant service, OAuth implementation or hardened public gateway.

The three routes are GET /v1/schema, POST /v1/validate and POST /v1/summary.
POST bodies are objects with a plan_json string. There are no file-path,
shell or write operations. An invalid plan yields HTTP 422; missing or
incorrect credentials yield HTTP 401. Response data is marked no-store.

For hosted GPT Actions and other OpenAPI consumers, deploy and review the
service first, then configure the real HTTPS URL and bearer authentication in
the client. Hosted apps cannot connect to this code merely by importing the
contract. No live vendor or public-host compatibility has been certified.

## References

- OpenAPI 3.1: https://spec.openapis.org/oas/v3.1.0
- GPT Actions: https://help.openai.com/en/articles/9442513-configuring-actions-in-gpts
- WSGI: https://peps.python.org/pep-3333/
- OpenAI: https://developers.openai.com/api/docs/guides/function-calling
- Claude: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- Gemini: https://ai.google.dev/gemini-api/docs/function-calling
- Cursor MCP configuration: https://cursor.com/docs/mcp
- VS Code editor-managed MCP configuration: https://code.visualstudio.com/docs/agents/reference/mcp-configuration
- MCP Python SDK: https://py.sdk.modelcontextprotocol.io/get-started/real-host/
- DeepSeek: https://api-docs.deepseek.com/guides/tool_calls/
- Mistral: https://docs.mistral.ai/inference/conversations/function-calling
- Groq: https://console.groq.com/docs/tool-use/overview
- Ollama: https://ollama.com/blog/tool-support

The core validator remains authoritative. Use synthetic data in public examples.
