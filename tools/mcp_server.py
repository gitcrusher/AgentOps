"""AgentOps MCP tool server.

Runs as its own process and speaks the MCP protocol (JSON-RPC over stdio).
The Action Agent never imports the tool functions — it connects as an MCP
client (see tools/mcp_client.py), discovers tools via `tools/list`, and
invokes them via `tools/call`.

Run standalone (e.g. to inspect with an MCP client):
    python -m tools.mcp_server

IMPORTANT: stdout is the protocol channel. Never print() in this process —
log to stderr instead, or the JSON-RPC stream gets corrupted.
"""
from typing import Literal

from mcp.server.mcpserver import MCPServer

from tools.create_ticket import execute_create_ticket
from tools.lookup_status import execute_lookup_status
from tools.send_notification import execute_send_notification

mcp = MCPServer("agentops-tools")

# Type hints become each tool's JSON Schema `inputSchema` (AGENTS.md Section 3):
# plain `str` params are required strings, `Literal[...]` becomes an enum.


@mcp.tool()
def create_ticket(
    issue: str,
    priority: Literal["low", "medium", "high"],
    user_id: str,
) -> dict:
    """Create a support/IT ticket for a reported issue.

    issue: short description of the issue. user_id: requesting employee's ID.
    """
    return execute_create_ticket({"issue": issue, "priority": priority, "user_id": user_id})


@mcp.tool()
def send_notification(to: str, subject: str, message: str) -> dict:
    """Send a real email notification via Gmail SMTP.

    to: recipient email address.
    """
    return execute_send_notification({"to": to, "subject": subject, "message": message})


@mcp.tool()
def lookup_status(
    record_type: Literal["ticket_status", "stipend_eligibility"],
    identifier: str,
) -> dict:
    """Look up an existing record (e.g. stipend eligibility, ticket status).

    identifier: ticket ID or employee ID.
    """
    return execute_lookup_status({"record_type": record_type, "identifier": identifier})


if __name__ == "__main__":