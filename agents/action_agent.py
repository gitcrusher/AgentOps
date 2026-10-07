"""Action Agent (AGENTS.md Section 3).

Acts as the MCP *host*: it gets the available tools from the MCP server
(`tools/list`), lets the LLM pick one and extract parameters, validates them
against the server-provided JSON Schema, then runs the tool via `tools/call`.

Tool names, descriptions and schemas are NOT hard-coded here; they come from
the server, so adding a tool to tools/mcp_server.py needs no change here.
"""
import json

from config.llm import chat, LLMUnavailable
from tools.mcp_client import get_mcp_client, MCPToolError

ACTION_SYSTEM_PROMPT = """You are an action-taking agent. Given the user's request, decide which single tool to call from the tools listed below. Extract the required parameters from the request.

CRITICAL RULE: NEVER guess or hallucinate any parameter. If a required parameter is not explicitly stated in the user's request, you MUST set "success": false, set "reason" to explain what is missing, and omit "parameters".

For example, if the request is "Create a ticket for my broken monitor", it is missing priority and user_id. You MUST output:
{{"tool_called": "create_ticket", "success": false, "reason": "Missing priority and user_id"}}

Return ONLY JSON matching this format (when successful):
{{
  "tool_called": "<tool name>",
  "parameters": {{"<param>": "<value>"}},
  "success": true
}}

Available tools (from the MCP server):
{tool_specs}
"""


def _describe_tools(tools: dict) -> str:
    """Render MCP tool schemas (from tools/list) into prompt text."""
    lines = []
    for name, tool in tools.items():
        schema = tool.input_schema or {}
        required = set(schema.get("required", []))
        params = []
        for pname, pschema in schema.get("properties", {}).items():
            ptype = pschema.get("type", "any")
            if "enum" in pschema:
                ptype = "one of " + "/".join(pschema["enum"])
            flag = "required" if pname in required else "optional"
            params.append(f"{pname} ({ptype}, {flag})")
        desc = " ".join((tool.description or "").split())
        lines.append(f"- {name}: {desc}\n  params: {', '.join(params) or 'none'}")
    return "\n".join(lines)


def _validate(params: dict, schema: dict) -> str | None:
    """Check params against the tool's JSON Schema. Returns a reason, or None if valid.

    Enforces AGENTS.md rule 3: never call a tool with missing/guessed params.
    """
    props = schema.get("properties", {})
    missing = [p for p in schema.get("required", [])
               if p not in params or params[p] in (None, "")]
    if missing:
        return f"Missing required parameters: {', '.join(missing)}"
    for pname, value in params.items():
        allowed = props.get(pname, {}).get("enum")
        if allowed and value not in allowed:
            return f"Invalid value for {pname}: {value!r} (expected one of {allowed})"
    return None


def _failure(tool, params, reason, result=None) -> dict:
    return {"tool_called": tool, "parameters": params, "result": result,
            "success": False, "reason": reason}


def get_action_result(query: str) -> dict:
    # 1. Discover tools over MCP (cached in the client after `tools/list`).
    try:
        client = get_mcp_client()
    except MCPToolError as e:
        return _failure(None, None, f"tool_server_unavailable: {e}")
    tools = client.tools

    # 2. LLM picks the tool + extracts parameters.
    system = ACTION_SYSTEM_PROMPT.format(tool_specs=_describe_tools(tools))
    try:
        raw = chat(system, query, temperature=0.0, max_tokens=250, json_mode=True)
        decision = json.loads(raw)
    except (LLMUnavailable, json.JSONDecodeError, TypeError):
        return _failure(None, None, "llm_unavailable")

    tool = decision.get("tool_called")
    params = decision.get("parameters") or {}

    if decision.get("success") is False:
        return _failure(tool, params or None, decision.get("reason", "Missing parameters"))
    if tool not in tools:
        return _failure(tool, params, f"Unknown tool: {tool}")

    # 3. Validate against the server-provided schema before calling.
    problem = _validate(params, tools[tool].input_schema or {})
    if problem:
        return _failure(tool, params, problem)

    # 4. Run the tool over MCP (`tools/call`).
    try:
        result = client.call_tool(tool, params)
    except MCPToolError as e:
        return _failure(tool, params, f"tool_call_failed: {e}")

    # 5. Treat tool-level failures as failures, not false positives.
    if result.get("found") is False:
        return _failure(tool, params, "Record not found", result)
    if result.get("status") == "failed":
        return _failure(tool, params, result.get("reason", "Tool reported failure"), result)

    return {"tool_called": tool, "parameters": params, "result": result, "success": True}
