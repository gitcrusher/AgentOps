import os
from config.settings import LLM_PROVIDER, GROQ_MODEL
from rag.retriever import retrieve

KNOWLEDGE_SYSTEM_PROMPT = """Answer the user's question using ONLY the provided context below. If the context does not contain enough information to answer confidently, say so explicitly rather than guessing.
Cite which document/section your answer came from.

Context:
{retrieved_chunks}

Question:
{query}
"""

def get_knowledge_answer(query: str) -> dict:
    chunks = retrieve(query, k=3)
    
    if not chunks:
        return {
            "answer": "insufficient_context",
            "source_chunks": [],
            "confidence": 0.0
        }
        
    best_distance = min(chunk["distance"] for chunk in chunks)
    confidence = max(0, 1 - (best_distance / 2))
    
    context_text = "\n\n".join([f"Source: {c['source']}\n{c['text']}" for c in chunks])
    prompt = KNOWLEDGE_SYSTEM_PROMPT.format(retrieved_chunks=context_text, query=query)
    
    if LLM_PROVIDER == "groq":
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=GROQ_MODEL,
                temperature=0.2,
                max_tokens=400
            )
            answer = response.choices[0].message.content
        except Exception as e:
            return {
                "answer": "llm_unavailable",
                "source_chunks": [],
                "confidence": 0.0
            }
    else:
        answer = "llm_unavailable"
        
    return {
        "answer": answer,
        "source_chunks": [c["source"] for c in chunks],
        "confidence": confidence
    }
