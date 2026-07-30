import os
import chromadb
from chromadb.utils import embedding_functions

docs_dir = "rag/docs"
db_dir = "data/chroma_db"

def build_index():
    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=db_dir)
    
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Reset collection if it exists to ensure a clean build
    try:
        client.delete_collection("agentops_knowledge")
    except:
        pass
        
    collection = client.create_collection(
        name="agentops_knowledge",
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"} # Use cosine distance
    )
    
    documents = []
    metadatas = []
    ids = []
    
    print("Reading markdown files...")
    for filename in os.listdir(docs_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(docs_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            
            for i, p in enumerate(paragraphs):
                documents.append(p)
                metadatas.append({"source": f"{filename}#chunk-{i}"})
                ids.append(f"{filename}_{i}")
                
    print(f"Adding {len(documents)} chunks to the vector database...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Index built successfully!")

if __name__ == "__main__":
    build_index()
