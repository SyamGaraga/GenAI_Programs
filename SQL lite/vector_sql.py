import sqlite3
import numpy as np

# ------------------------------
# SETUP: sample table + vectors
# ------------------------------
conn = sqlite3.connect(":memory:")

conn.execute("""
CREATE TABLE books_vectors (
    id        INTEGER PRIMARY KEY,
    title     TEXT NOT NULL,
    embedding BLOB NOT NULL
);
""")

# ------------------------------
# Function to create fake embeddings
# ------------------------------
def make_vec(value: float) -> bytes:
    """Makes a simple 384-dim vector for demo."""
    return np.array([value] * 384, dtype=np.float32).tobytes()

# Sample embeddings
book1_emb = make_vec(0.10)
book2_emb = make_vec(0.80)
book3_emb = make_vec(0.14)
book4_emb = make_vec(0.25)  # <-- Added this, it was missing

# Insert sample data
conn.executemany(
    "INSERT INTO books_vectors (id, title, embedding) VALUES (?, ?, ?)",
    [
        (1, "Book 1: Intro to AI",       book1_emb),
        (2, "Book 2: Cooking with Love", book2_emb),
        (3, "Book 3: Machine Learning",  book3_emb),
        (4, "Book 4: Ms Dhoni Biopic",   book4_emb),
    ],
)
conn.commit()

# ------------------------------
# Fake embedding function
# ------------------------------
def fake_text_embedding(text: str) -> np.ndarray:
    """Simulates an embedding generator."""
    return np.array([0.15] * 384, dtype=np.float32)

# ------------------------------
# COSINE SIMILARITY FUNCTION
# ------------------------------
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ------------------------------
# Vector search in Python
# ------------------------------
query_text = input("Enter your search text: ")
query_emb = fake_text_embedding(query_text)

cur = conn.cursor()
cur.execute("SELECT id, title, embedding FROM books_vectors")
results = []

for id_, title, emb_blob in cur.fetchall():
    emb = np.frombuffer(emb_blob, dtype=np.float32)
    sim = cosine_similarity(query_emb, emb)
    results.append((id_, title, sim))

# Sort by similarity (descending) and pick top 2
results.sort(key=lambda x: x[2], reverse=True)
top_results = results[:2]

print("\nTop-2 similar books:")
for id_, title, sim in top_results:
    print(f"{title} (score: {sim:.4f})")
