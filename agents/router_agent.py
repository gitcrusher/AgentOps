import os
import json
from config.settings import LLM_PROVIDER, GROQ_MODEL
from config.prompts import ROUTER_SYSTEM_PROMPT

def get_router_completion(query: str) -> dict:
    query = query.strip()
    if not query:
        return {"intents": ["zero_intent"], "sub_tasks": []}
        
    # Zero-intent / small talk fallback
    small_talk = ["hello", "hi", "thanks", "thank you", "hello there!"]
    if query.lower() in small_talk:
        return {"intents": ["zero_intent"], "sub_tasks": []}
        
    if LLM_PROVIDER == "groq":
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                model=GROQ_MODEL,
                temperature=0.0,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            # Failure mode: default to treating as a single knowledge_query
            return {"intents": ["knowledge_query"], "sub_tasks": [{"type": "knowledge_query", "text": query}]}
    else:
        return {"intents": ["knowledge_query"], "sub_tasks": [{"type": "knowledge_query", "text": query}]}

if __name__ == "__main__":
    print(get_router_completion("I need to open a ticket for my VPN and also how much is the WFH stipend?"))
