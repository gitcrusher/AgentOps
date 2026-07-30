import chromadb
from chromadb.utils import embedding_functions

db_dir = "data/chroma_db"

# Initialize globally so it doesn't reload on every query
client = chromadb.PersistentClient(path=db_dir)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_collection(name="agentops_knowledge", embedding_function=emb_fn)

def retrieve(query: str, k: int = 3) -> list[dict]:
    """
    Retrieve the top-k most relevant chunks for a given query.
    Returns a list of dicts: {"text": str, "source": str, "distance": float}
    """
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    chunks = []
    if results["documents"] and results["documents"][0]:
        for i in range(len(results["documents"][0])):
            chunks.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "distance": results["distances"][0][i]
            })
    return chunks

if __name__ == "__main__":
    test_queries = [
        "How much is the WFH stipend?",
        "Can I expense alcohol on a business trip?",
        "I need to open a ticket because my VPN is broken.",
        "Tell me about the universe.", # Intentional out of domain
        "What laptops are standard issue?"
    ]
    
    for q in test_queries:
        print(f"\nQuery: {q}")
        retrieved = retrieve(q, k=3)
        for chunk in retrieved:
            print(f"  - [Dist: {chunk['distance']:.4f}] {chunk['source']}: {chunk['text'][:75]}...")
