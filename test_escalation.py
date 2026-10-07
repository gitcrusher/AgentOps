import json
from graph.workflow import graph

query = "What is the company policy for bringing pets into the office and taking them for walks?"
print(f"Testing Query: {query}")
result = graph.invoke({"raw_input": query})

print("\n--- Final Answer ---")
print(result.get("final_answer"))
print("\n--- Trace ---")
print(json.dumps(result.get("trace", []), indent=2))
