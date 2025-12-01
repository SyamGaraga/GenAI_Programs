import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

# ------------------------------
# 1️⃣ Text data
student_info = """
Alexandra Thompson, a 19-year-old computer science sophomore with a 3.7 GPA,
is a member of the programming and chess clubs who enjoys pizza, swimming, and hiking
in her free time in hopes of working at a tech company after graduating from the University of Washington.
"""

club_info = """
The university chess club provides an outlet for students to come together and enjoy playing
the classic strategy game of chess. Members of all skill levels are welcome, from beginners learning
the rules to experienced tournament players. The club typically meets a few times per week to play casual games,
participate in tournaments, analyze famous chess matches, and improve members' skills.
"""

university_info = """
The University of Washington, founded in 1861 in Seattle, is a public research university
with over 45,000 students across three campuses in Seattle, Tacoma, and Bothell.
As the flagship institution of the six public universities in Washington state,
UW encompasses over 500 buildings and 20 million square feet of space,
including one of the largest library systems in the world.
"""

documents = [
    ("student_info", student_info),
    ("club_info", club_info),
    ("university_info", university_info)
]

# ------------------------------
# 2️⃣ Connect to SQLite
conn = sqlite3.connect("semantic_db.db")
c = conn.cursor()

# ------------------------------
# 3️⃣ Create table
c.execute('''
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    embedding BLOB
)
''')
conn.commit()

# ------------------------------
# 4️⃣ Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# ------------------------------
# 5️⃣ Helper functions for storing/retrieving embeddings
def adapt_array(arr):
    """Convert numpy array to bytes for SQLite"""
    return arr.tobytes()

def convert_array(blob):
    """Convert bytes from SQLite back to numpy array"""
    return np.frombuffer(blob, dtype=np.float32)

# Register adapter (storing)
sqlite3.register_adapter(np.ndarray, adapt_array)

# ------------------------------
# 6️⃣ Insert documents with embeddings
for title, content in documents:
    emb = model.encode(content).astype(np.float32)
    c.execute("INSERT INTO documents (title, content, embedding) VALUES (?, ?, ?)", (title, content, emb))

conn.commit()

# ------------------------------
# 7️⃣ Semantic search function
def semantic_search(query, top_k=2):
    query_emb = model.encode(query).astype(np.float32)
    c.execute("SELECT title, content, embedding FROM documents")
    results = []
    for title, content, emb_blob in c.fetchall():
        emb = np.frombuffer(emb_blob, dtype=np.float32)
        sim = np.dot(query_emb, emb) / (norm(query_emb) * norm(emb))  # cosine similarity
        results.append((title, content, sim))
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]

# ------------------------------
# 8️⃣ Example search
query = "chess club"
results = semantic_search(query, top_k=3)

for i, (title, content, score) in enumerate(results, 1):
    print(f"Result {i}: {title} (score: {score:.4f})\n{content}\n")
