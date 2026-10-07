import json
from graph.workflow import graph

print("=== Test 1: Valid Knowledge Query ===")
q1 = "What is the policy for the WFH stipend?"
res1 = graph.invoke({"raw_input": q1})
print(f"Query: {q1}")
print("Answer:", res1.get("final_answer"))
print("Trace:", json.dumps(res1.get("trace", []), indent=2))

print("\n=== Test 2: Valid Action Query ===")
q2 = "Create a high priority ticket for user emp_1042 about a broken monitor"
res2 = graph.invoke({"raw_input": q2})
print(f"Query: {q2}")
print("Answer:", res2.get("final_answer"))
print("Trace:", json.dumps(res2.get("trace", []), indent=2))
