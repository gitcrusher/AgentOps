import os
import json
from datetime import datetime
from config.settings import CONFIDENCE_THRESHOLD

def escalate(knowledge_results: list, action_results: list, trace: list) -> list:
    escalations = []
    
    for kr in knowledge_results:
        conf = kr.get("confidence", 0.0)
        if conf < CONFIDENCE_THRESHOLD:
            reason = f"Retrieval confidence below threshold ({conf:.2f}) — no matching policy section found."
            escalations.append({"type": "knowledge", "status": "needs_human_review", "reason": reason})
            log_escalation(reason, "knowledge")
            
    for ar in action_results:
        if not ar.get("success", False):
            reason = ar.get("reason", "Action failed or missing required parameters.")
            escalations.append({"type": "action", "status": "needs_human_review", "reason": reason})
            log_escalation(reason, "action")
            
    return escalations

def log_escalation(reason, req_type):
    os.makedirs("logs", exist_ok=True)
    with open("logs/escalations.jsonl", "a") as f:
        f.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "type": req_type, "reason": reason}) + "\n")
