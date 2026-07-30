import os
import json
from config.settings import LLM_PROVIDER, GROQ_MODEL

ACTION_SYSTEM_PROMPT = """You are an action-taking agent. Given the user's request, decide which single tool to call from: create_ticket, send_notification, lookup_status.

CRITICAL RULE: NEVER guess or hallucinate any parameter. If a required parameter is not explicitly stated in the user's request, you MUST set "success": false and set "reason" to explain what is missing, and omit "parameters". 

For example, if the request is "Create a ticket for my broken monitor", it is missing priority and user_id. You MUST output:
{"tool_called": "create_ticket", "success": false, "reason": "Missing priority and user_id"}

Return ONLY JSON matching this format (when successful):
{
  "tool_called": "create_ticket",
  "parameters": {"issue": "VPN connectivity", "priority": "medium", "user_id": "emp_1042"},
  "success": true
}

Tools schemas:
create_ticket: issue (str), priority (low/medium/high), user_id (str)
send_notification: to (str), subject (str), message (str)
lookup_status: record_type (ticket_status/stipend_eligibility), identifier (str)
"""

def execute_create_ticket(params):
    ticket_id = 4501
    os.makedirs("logs", exist_ok=True)
    with open("logs/tickets.jsonl", "a") as f:
        f.write(json.dumps({"ticket_id": ticket_id, **params}) + "\n")
    return {"status": "created", "ticket_id": ticket_id}

def execute_lookup_status(params):
    try:
        with open("data/mock_records.json", "r") as f:
            records = json.load(f)
    except:
        return {"found": False}
        
    rt = params.get("record_type")
    ident = params.get("identifier")
    if rt in records and ident in records[rt]:
        return {"found": True, "result": records[rt][ident]}
    return {"found": False}

def execute_send_notification(params):
    import smtplib
    from email.mime.text import MIMEText
    sender = os.getenv("GMAIL_ADDRESS")
    pwd = os.getenv("GMAIL_APP_PASSWORD")
    if not sender or not pwd:
        return {"status": "failed", "reason": "Missing email credentials"}
    try:
        msg = MIMEText(params.get("message", ""))
        msg["Subject"] = params.get("subject", "")
        msg["From"] = sender
        msg["To"] = params.get("to", "")
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender, pwd)
            server.send_message(msg)
        return {"status": "sent"}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}

def get_action_result(query: str) -> dict:
    if LLM_PROVIDER == "groq":
        import time
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": ACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                model=GROQ_MODEL,
                temperature=0.0,
                max_tokens=250,
                response_format={"type": "json_object"}
            )
        except Exception as e:
            if "429" in str(e):
                time.sleep(2)
                try:
                    response = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": ACTION_SYSTEM_PROMPT},
                            {"role": "user", "content": query}
                        ],
                        model=GROQ_MODEL,
                        temperature=0.0,
                        max_tokens=250,
                        response_format={"type": "json_object"}
                    )
                except Exception as e2:
                    return {"success": False, "reason": "llm_unavailable"}
            else:
                return {"success": False, "reason": "llm_unavailable"}
        
        try:
            decision = json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"success": False, "reason": "llm_unavailable"}
    else:
        return {"success": False, "reason": "llm_unavailable"}

    if decision.get("success") is False:
        return {
            "tool_called": decision.get("tool_called"),
            "parameters": decision.get("parameters"),
            "result": None,
            "success": False,
            "reason": decision.get("reason", "Missing parameters")
        }

    tool = decision.get("tool_called")
    params = decision.get("parameters", {})
    
    if tool == "create_ticket":
        if "issue" not in params or "priority" not in params or "user_id" not in params:
             return {"tool_called": tool, "success": False, "reason": "Missing required parameters for create_ticket"}
        res = execute_create_ticket(params)
        return {"tool_called": tool, "parameters": params, "result": res, "success": True}
        
    elif tool == "lookup_status":
        if "record_type" not in params or "identifier" not in params:
             return {"tool_called": tool, "success": False, "reason": "Missing required parameters for lookup_status"}
        res = execute_lookup_status(params)
        if not res.get("found"):
             return {"tool_called": tool, "parameters": params, "result": res, "success": False, "reason": "Record not found"}
        return {"tool_called": tool, "parameters": params, "result": res, "success": True}
        
    elif tool == "send_notification":
        if "to" not in params or "subject" not in params or "message" not in params:
             return {"tool_called": tool, "success": False, "reason": "Missing required parameters for send_notification"}
        res = execute_send_notification(params)
        if res.get("status") == "failed":
             return {"tool_called": tool, "parameters": params, "result": res, "success": False, "reason": res.get("reason")}
        return {"tool_called": tool, "parameters": params, "result": res, "success": True}
        
    return {"success": False, "reason": f"Unknown tool: {tool}"}
