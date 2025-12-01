# operations.py
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="fruits", embedding_function=embedding_function)

# Add
print("=== Adding Data ===")
collection.add(
    documents=[
        "Apples are red and crisp fruits.",
        "Bananas are yellow and curved.",
        "Oranges are juicy citrus fruits.",
        "Grapes grow in bunches and are sweet."
    ],
    ids=["fruit1", "fruit2", "fruit3", "fruit4"]
)
print("Added 4 fruit documents.")

# Query
print("\n=== Querying ===")
query_results = collection.query(
    query_texts=["What is a sweet, juicy fruit?"],
    n_results=2
)
print("Query Results:")
print(f"IDs: {query_results['ids']}")
print(f"Documents: {query_results['documents']}")
print(f"Distances: {query_results['distances']}")

# Get specific
print("\n=== Getting Specific ===")
get_result = collection.get(ids=["fruit1"])
print(f"Got fruit1: {get_result['documents']}")

# Update
print("\n=== Updating ===")
collection.update(
    ids=["fruit2"],
    documents=["Bananas are yellow, curved, and great for smoothies."]
)
updated_get = collection.get(ids=["fruit2"])
print(f"Updated fruit2: {updated_get['documents']}")

# Delete
print("\n=== Deleting ===")
collection.delete(ids=["fruit4"])
print("Deleted fruit4.")
remaining = collection.get()
print(f"Remaining IDs: {remaining['ids']}")
