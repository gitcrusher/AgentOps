import json
from agents.knowledge_agent import get_knowledge_answer

test_queries = [
    "How much is the WFH stipend?",
    "Tell me about the universe." # Should be low confidence
]

for q in test_queries:
    print(f"\n--- Testing Query: {q} ---")
    res = get_knowledge_answer(q)
    print(f"Confidence: {res['confidence']:.4f}")
    print(f"Sources: {res['source_chunks']}")
    print(f"Answer:\n{res['answer']}\n")
