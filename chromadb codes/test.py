import chromadb

client = chromadb.Client()
collection = client.create_collection("demo")

collection.add(
    ids=["1"],
    documents=["ChromaDB installation is successful!"]
)

result = collection.query(
    query_texts=["successful"],
    n_results=1
)

print(result)