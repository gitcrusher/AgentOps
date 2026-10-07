import json
from config.llm import chat, LLMUnavailable
from config.prompts import ROUTER_SYSTEM_PROMPT

def get_router_completion(query: str) -> dict:
    query = query.strip()
    if not query:
        return {"intents": ["zero_intent"], "sub_tasks": []}
        
    # Zero-intent / small talk fallback
    small_talk = ["hello", "hi", "thanks", "thank you", "hello there!"]
    if query.lower() in small_talk:
        return {"intents": ["zero_intent"], "sub_tasks": []}
        
    try:
        raw = chat(ROUTER_SYSTEM_PROMPT, query, temperature=0.0, max_tokens=300, json_mode=True)
        return json.loads(raw)
    except (LLMUnavailable, json.JSONDecodeError, TypeError) as e:
        print(f"ROUTER ERROR: {e}")
        # Failure mode: default to treating as a single knowledge_query
        return {"intents": ["knowledge_query"], "sub_tasks": [{"type": "knowledge_query", "text": query}]}

if __name__ == "__main__":
    print(get_router_completion("I need to open a ticket for my VPN and also how much is the WFH stipend?"))
