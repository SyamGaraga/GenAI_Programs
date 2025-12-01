import json
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from openai import OpenAI

HF_TOKEN = "enter_your_huggingface_token_here"

# ======================
# HF CLIENT
# ======================
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# ======================
# FIX JSON FUNCTION
# ======================
def clean_json(raw):
    """
    Removes code blocks and ensures valid JSON.
    """
    raw = raw.strip()

    # Remove ```json or ``` wrappers
    if raw.startswith("```"):
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

    # Try to parse
    try:
        return json.loads(raw)
    except Exception:
        print("⚠ JSON Parse Failed! Raw content returned.")
        return None


# ======================
# METADATA GENERATOR
# ======================
def generate_metadata(letter: str, word: str):
    prompt = f"""
You must return ONLY a valid JSON object. No explanations. No code blocks.

Generate metadata for the following:

Alphabet: {letter}
Word: {word}

Return JSON with these exact fields:

{{
    "alphabet": "{letter}",
    "type": "",
    "category": "",
    "color": "",
    "is_living": "",
    "origin_country": "",
    "description": ""
}}
"""

    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    raw = response.choices[0].message.content
    meta = clean_json(raw)

    # fallback
    if meta is None:
        return {
            "alphabet": letter,
            "description": raw
        }

    return meta


# ======================
# SETUP CHROMA DB
# ======================
chroma_client = chromadb.Client(
    Settings(persist_directory="./chroma_ai_store")
)

embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="dictionary_ai",
    embedding_function=embedder
)


# ======================
# READ DATA FILE
# ======================
records = []

print("\n📖 Reading data.txt ...\n")

with open("data.txt", "r") as f:
    for line in f:
        if ":" in line:
            letter, word = line.split(":")
            records.append((letter.strip(), word.strip()))

print(f"✔ Loaded {len(records)} records.\n")


# ======================
# PROCESS + STORE
# ======================
ids = []
documents = []
metadatas = []

print("⚙ Generating metadata and storing in Chroma...\n")

for i, (letter, word) in enumerate(records):
    print(f"➡ Processing '{word}' ...")

    meta = generate_metadata(letter, word)

    ids.append(str(i))

    # Better embedding → combine word + metadata
    doc_text = f"{word}. {meta.get('description', '')}"
    documents.append(doc_text)

    metadatas.append(meta)

# Store everything
collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

print("\n🎉 ALL DATA STORED SUCCESSFULLY in chroma_ai_store/")
print("--------------------------------------------------------\n")


# ======================
# TEST QUERY
# ======================
print("🔎 Testing semantic search for: 'fruit'\n")

results = collection.query(
    query_texts=["cricket"],
    n_results=3
)

print(results["metadatas"])
print("\n✅ Done.\n")
