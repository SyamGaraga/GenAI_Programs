import chromadb
from sentence_transformers import SentenceTransformer

# 1. Load embedding model (small, fast)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Start ChromaDB client (in-memory)
chroma_client = chromadb.Client()

# 3. Create a collection (like a table)
collection = chroma_client.create_collection(name="ittechgenie_docs")

# 4. Some example documents (replace with your own text if you like)
documents = [
    "Databricks is a unified analytics platform built on top of Apache Spark.",
    "Spark is an open-source distributed computing system for big data processing.",
    "ChromaDB is a vector database used to store and search embeddings.",
    "RAG stands for Retrieval-Augmented Generation. It combines search and generation.",
]

# 5. Create embeddings for these documents
embeddings = embed_model.encode(documents).tolist()

# 6. Add them to the Chroma collection
ids = [f"doc-{i}" for i in range(len(documents))]

collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=ids
)

print("✅ Indexed", len(documents), "documents in ChromaDB.")