"""MCP client used by the Action Agent.

Spawns tools/mcp_server.py as a subprocess and talks to it over the MCP
protocol (JSON-RPC over stdio):

    initialize  -> handshake, capability negotiation
    tools/list  -> discover tool names, descriptions and JSON Schemas
    tools/call  -> invoke a tool, get a structured result back

The rest of the app is synchronous (Streamlit + LangGraph nodes), while the
MCP SDK is async. So the client runs one long-lived session on a dedicated
background event loop, and exposes plain sync methods that submit work to it.
The server process is started once and reused across requests.
"""
import asyncio
import atexit
import concurrent.futures
import json
import os
import sys
import threading
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config.settings import MCP_TOOL_TIMEOUT_SECONDS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STARTUP_TIMEOUT_SECONDS = 30


class MCPToolError(Exception):
    """The MCP server couldn't be reached or the protocol call itself failed."""


class MCPToolClient:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever, name="mcp-client-loop", daemon=True
        )
        self._thread.start()

        self._session: ClientSession | None = None
        self._shutdown: asyncio.Event | None = None
        self._runner: concurrent.futures.Future | None = None
        self.tools: dict = {}  # name -> mcp.types.Tool, filled by tools/list

        ready = concurrent.futures.Future()
        self._runner = asyncio.run_coroutine_threadsafe(self._run(ready), self._loop)
        try:
            # Fail fast at startup if the server can't start (ARCHITECTURE.md Sec. 9).
            ready.result(timeout=STARTUP_TIMEOUT_SECONDS)
        except Exception as e:
            self.close()
            raise MCPToolError(f"MCP server failed to initialize: {e}") from e

    async def _run(self, ready: concurrent.futures.Future):
        """Owns the transport + session for their whole lifetime.

        The stdio transport uses an anyio task group, which must be entered and
        exited in the same task — so one task holds the contexts open and waits
        for shutdown, while individual requests run as separate tasks.
        """
        self._shutdown = asyncio.Event()
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "tools.mcp_server"],
            cwd=str(PROJECT_ROOT),
            # Pass the full environment explicitly: by default the SDK only
            # forwards a minimal safe set (PATH etc.), which would drop
            # GMAIL_* credentials loaded from .env / Streamlit Secrets.
            env=dict(os.environ),
        )
        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    listed = await session.list_tools()
                    self.tools = {t.name: t for t in listed.tools}
                    self._session = session
                    ready.set_result(True)
                    await self._shutdown.wait()
        except Exception as e:
            if not ready.done():
                ready.set_exception(e)
            else:
                raise
        finally:
            self._session = None

    def call_tool(self, name: str, arguments: dict) -> dict:
        """Invoke a tool over MCP (`tools/call`) and return its result as a dict.

        Raises MCPToolError if the protocol call fails or the server reports a
        tool error, so the caller can route to escalation.
        """
        if self._session is None:
            raise MCPToolError("MCP session is not connected")

        coro = self._session.call_tool(
            name, arguments, read_timeout_seconds=MCP_TOOL_TIMEOUT_SECONDS
        )
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            result = future.result(timeout=MCP_TOOL_TIMEOUT_SECONDS + 5)
        except Exception as e:
            future.cancel()
            raise MCPToolError(f"tools/call {name} failed: {type(e).__name__}: {e}") from e

        text = "".join(
            getattr(block, "text", "") for block in (getattr(result, "content", None) or [])
        )
        if getattr(result, "is_error", False):
            raise MCPToolError(f"tool {name} returned an error: {text or 'no details'}")

        structured = getattr(result, "structured_content", None)
        if isinstance(structured, dict):
            # Non-object return types get wrapped as {"result": ...} by the server.
            if set(structured) == {"result"} and isinstance(structured["result"], dict):
                return structured["result"]
            return structured
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError) as e:
            raise MCPToolError(f"tool {name} returned non-JSON content") from e

    def close(self):
        if self._shutdown is not None and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._shutdown.set)
        if self._runner is not None:
            try:
                self._runner.result(timeout=5)
            except Exception:
                pass
        if not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)


_client: MCPToolClient | None = None
_client_lock = threading.Lock()


def get_mcp_client() -> MCPToolClient:
    """Process-wide singleton: one server subprocess, one session."""
    global _client
    with _client_lock:
        if _client is None or _client._session is None:
            _client = MCPToolClient()
            atexit.register(_client.close)
        return _client
