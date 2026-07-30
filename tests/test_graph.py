import json
from graph.workflow import graph

test_queries = [
    "How much is the WFH stipend?",
    "Create a high priority ticket for user emp_1042 about broken VPN.",
    "What is the refund policy for hardware, and also open a ticket for my defective monitor for emp_1042 with high priority.",
    "Tell me about the universe.",
    "Create a ticket for my broken monitor." 
]

for q in test_queries:
    print(f"\n========== TESTING: {q} ==========")
    initial_state = {"raw_input": q}
    result = graph.invoke(initial_state)
    
    print("\nFINAL ANSWER:")
    print(result.get("final_answer"))
    
    print("\nTRACE:")
    print(json.dumps(result.get("trace"), indent=2))
