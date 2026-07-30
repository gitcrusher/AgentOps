from agents.action_agent import get_action_result
import json

queries = [
    "Create a high priority ticket for user emp_1042 about broken VPN.",
    "Lookup ticket status for TKT-1001.",
    "Lookup ticket status for TKT-9999.",
    "Send an email to noreplyaayushsoni@gmail.com with subject 'Hello' and message 'Test'.",
    "Create a ticket for my broken monitor."
]

for q in queries:
    print(f"\n--- Testing Query: {q} ---")
    res = get_action_result(q)
    print(json.dumps(res, indent=2))
