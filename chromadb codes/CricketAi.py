# CricketAi.py
import chromadb
from chromadb.utils import embedding_functions

# Step 1: Connect to Chroma
client = chromadb.Client()

# Step 2: Load a more powerful embedding model for better accuracy
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"   # more accurate than MiniLM
)

# Step 3: Create or get cricket collection
collection = client.get_or_create_collection(
    name="cricket_info",
    embedding_function=embedding_function
)

# Step 4: Add cricket-related data with metadata
collection.add(
    documents=[
        "Virat Kohli is an Indian batsman known for his aggressive style and match-winning knocks.",
        "MS Dhoni is a calm leader and one of the greatest finishers in world cricket.",
        "Jasprit Bumrah is a world-class Indian fast bowler famous for his yorkers.",
        "Ravindra Jadeja is an Indian all-rounder known for spin bowling and sharp fielding.",
        "AB de Villiers is a South African batsman known as Mr. 360 for his innovative shots.",
        "Australia won the 2023 World Cup final against India at Ahmedabad."
    ],
    ids=["kohli", "dhoni", "bumrah", "jadeja", "abd", "wc2023"],
    metadatas=[
        {"type": "batsman", "team": "India"},
        {"type": "captain", "team": "India"},
        {"type": "bowler", "team": "India"},
        {"type": "allrounder", "team": "India"},
        {"type": "batsman", "team": "South Africa"},
        {"type": "tournament", "year": 2023}
    ]
)

print("✅ Cricket knowledge base created successfully!\n")

# Helper function to ask questions
def ask_cricket(question, filter_type=None):
    """Ask a cricket-related question with optional filtering by role/type."""
    if filter_type:
        result = collection.query(
            query_texts=[question],
            n_results=1,
            where={"type": filter_type}
        )
    else:
        result = collection.query(query_texts=[question], n_results=1)

    if result["documents"]:
        print(f"🟩 Question: {question}")
        print("🟢 Answer:", result["documents"][0][0])
        print("-" * 70)
    else:
        print(f"❌ No result found for: {question}")
        print("-" * 70)


# Step 5: Ask some example questions

# Without filter (semantic search only)
ask_cricket("Who is a calm leader?")
ask_cricket("Who is known for yorkers?")
ask_cricket("Tell me about a player called Mr. 360?")
ask_cricket("Who won the 2023 World Cup?")

# With filters for precise answers
ask_cricket("Who is the best batsman?", filter_type="batsman")
ask_cricket("Who is a great all-rounder?", filter_type="allrounder")
ask_cricket("Who is India's fast bowler?", filter_type="bowler")
ask_cricket("Who is India's captain?", filter_type="captain")

# Update one player info to test update functionality
collection.update(
    ids=["kohli"],
    documents=["Virat Kohli is an Indian cricketer, former captain, and one of the best modern batsmen."],
    metadatas=[{"type": "batsman", "team": "India"}]
)
print("\n✅ Updated Virat Kohli’s latest info.\n")

# Show remaining data
remaining = collection.get()
print("📋 Remaining documents in the collection:", remaining["ids"])
