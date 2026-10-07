import itertools
import json
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TICKETS_LOG = PROJECT_ROOT / "logs" / "tickets.jsonl"

# AGENTS.md Section 3: sequential IDs starting at 4500, in-memory, reset each
# session. The MCP server is a long-lived process, so this lives for the session.
_ticket_ids = itertools.count(4500)
_lock = threading.Lock()


def execute_create_ticket(params: dict) -> dict:
    with _lock:
        ticket_id = next(_ticket_ids)
    TICKETS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(TICKETS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ticket_id": ticket_id, **params}) + "\n")
    return {"status": "created", "ticket_id": ticket_id}
