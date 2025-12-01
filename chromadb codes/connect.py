# connect.py
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="my_first_collection",
    embedding_function=embedding_function
)

print("Connected to Chroma and got/created collection 'my_first_collection'!")
