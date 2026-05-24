# Secure MCP server skeleton (Python)

Copy-paste starting point for a Python MCP server with all six pre-trust checks baked in. Adapt to Node, Rust, Go as needed — the structural commitments are language-agnostic.

## Directory layout

```
my-mcp-server/
├── pyproject.toml
├── uv.lock
├── LICENSE
├── README.md
├── CHANGELOG.md
├── src/
│   └── my_mcp_server/
│       ├── __init__.py
│       ├── server.py            # explicit tool registration; no eval
│       ├── config.py            # env-var-only secret loading
│       └── tools/
│           ├── __init__.py
│           ├── search.py
│           └── get.py
└── tests/
    ├── test_tools.py
    └── test_no_secret_leak.py
```

## pyproject.toml (Checks 1 + 4)

```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
description = "Read-only MCP wrapper for the internal incident database."
license = { text = "MIT" }
requires-python = ">=3.11,<3.14"
dependencies = [
  "mcp==1.2.3",
  "httpx==0.27.2",
  "pydantic==2.8.0",
]

[project.scripts]
my-mcp-server = "my_mcp_server.server:main"
```

Lockfile (`uv.lock`) is committed. Install command in README pins to a SemVer tag.

## config.py (Check 5)

```python
"""Env-var-only secret loading. No fallback to config files."""
import os
import sys


class Config:
    def __init__(self) -> None:
        self.db_url = os.environ.get("INCIDENT_DB_URL")
        self.api_token = os.environ.get("INCIDENT_DB_TOKEN")
        if not self.db_url or not self.api_token:
            # Fail fast — do not silently fall back to unauthenticated mode.
            sys.exit("INCIDENT_DB_URL and INCIDENT_DB_TOKEN env vars required")

    def __repr__(self) -> str:
        # Never include the token in repr / debug output.
        return f"Config(db_url={self.db_url!r}, api_token=<redacted>)"
```

## server.py (Check 6)

```python
"""MCP server with explicit tool registration. No dynamic dispatch."""
from mcp.server import Server
from mcp.types import Tool

from .config import Config
from .tools import search, get


def build_server() -> Server:
    cfg = Config()
    server = Server("my-mcp-server")

    # Explicit tool registration — no loop over user input, no eval.
    server.add_tool(Tool(
        name="search_incidents",
        description="Read-only full-text search over the incident database.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 10},
            },
            "required": ["query"],
        },
        handler=lambda args: search.run(cfg, args),
    ))
    server.add_tool(Tool(
        name="get_incident",
        description="Read a single incident by ID.",
        inputSchema={
            "type": "object",
            "properties": {"incident_id": {"type": "string"}},
            "required": ["incident_id"],
        },
        handler=lambda args: get.run(cfg, args),
    ))
    return server


def main() -> None:
    server = build_server()
    server.run()
```

No catch-all dispatch tool. No `eval()`. No dynamic import. Two read-only tools, both with explicit JSON Schema input contracts.

## Egress documentation (Check 3)

In `README.md`:

```markdown
## Network egress

This MCP makes outbound HTTPS calls to:

- `$INCIDENT_DB_URL` (default `https://incidents.internal.example.com`) — read-only API queries.
  Override by setting `INCIDENT_DB_URL` in your environment.

No telemetry. No update checks. No third-party endpoints.
```

## Test: no secret leak

```python
"""Asserts the secret never appears in any tool result or error message."""
import pytest
from my_mcp_server.config import Config
from my_mcp_server.tools import search


def test_search_error_does_not_leak_token(monkeypatch):
    monkeypatch.setenv("INCIDENT_DB_URL", "https://example.invalid")
    monkeypatch.setenv("INCIDENT_DB_TOKEN", "secret-test-token")
    cfg = Config()
    try:
        search.run(cfg, {"query": "anything"})
    except Exception as e:
        assert "secret-test-token" not in str(e)
        assert "secret-test-token" not in repr(e)
```

## README install snippet (Check 4)

```bash
# Pinned install — never use @latest or unpinned forms
uvx --from "git+https://github.com/you/my-mcp-server@v0.1.0" my-mcp-server
```

Or, after publishing to PyPI:

```bash
uvx --from "my-mcp-server==0.1.0" my-mcp-server
```
