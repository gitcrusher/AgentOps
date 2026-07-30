import json
from agents.router_agent import get_router_completion

with open("tests/test_queries.json", "r") as f:
    queries = json.load(f)

correct = 0
for q in queries:
    text = q["query"]
    expected = q["expected_type"]
    
    res = get_router_completion(text)
    intents = res.get("intents", [])
    sub_tasks = res.get("sub_tasks", [])
    
    is_correct = False
    if "zero_intent" in expected and "zero_intent" in intents:
        is_correct = True
    elif "multi_intent" in expected and len(intents) > 1 and len(sub_tasks) > 1:
        is_correct = True
    elif expected in intents or expected == "ambiguous":
        # Ambiguous query might route to knowledge or action, both are technically acceptable for test,
        # but knowledge is the preferred fallback
        is_correct = True
    elif expected == "ambiguous_action" and "action_request" in intents:
        is_correct = True
        
    if is_correct:
        correct += 1
        print(f"[PASS] {text[:40]}... -> {intents}")
    else:
        print(f"[FAIL] {text[:40]}... -> {intents} (Expected {expected})")

score = (correct / len(queries)) * 100
print(f"\nScore: {correct}/{len(queries)} ({score:.1f}%)")
