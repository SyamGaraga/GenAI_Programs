
import os
import textwrap

import streamlit as st
from transformers.pipelines import pipeline  # fixed import
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# -------------------------------------------------------------------
# 1. Streamlit page configuration
# -------------------------------------------------------------------
st.set_page_config(
    page_title="RAG Chatbot – Dakshinamurthy & Maha Vishnu",
    page_icon="🕉️",
)

st.title("🕉️ RAG Chatbot with ChromaDB (Lord Dakshinamurthy & Maha Vishnu)")
st.write(
    "This chatbot answers questions **only** from your local knowledge file "
    "about Lord Dakshinamurthy and Maha Vishnu using a small local model "
    "(`distilgpt2`) and ChromaDB."
)

# -------------------------------------------------------------------
# 2. Paths and constants
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_FILE = os.path.join(DATA_DIR, "deities_knowledge.txt")

CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "deities_rag_collection2"


# -------------------------------------------------------------------
# 3. Utilities: load knowledge file and chunk it
# -------------------------------------------------------------------
def load_knowledge_text(path: str) -> str:
    """Read the full text file with Dakshinamurthy + Maha Vishnu content."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Knowledge file not found at: {path}\n"
            "Make sure data/deities_knowledge.txt exists."
        )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def simple_chunk_text(text: str, max_chars: int = 600):
    """
    Very simple chunking: split by blank lines, then further split long
    paragraphs into smaller pieces.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []

    for para in paragraphs:
        if len(para) <= max_chars:
            chunks.append(para)
        else:
            # wrap long paragraph into smaller parts
            wrapped = textwrap.wrap(para, width=max_chars)
            chunks.extend(wrapped)

    # ensure uniqueness and non-empty
    cleaned = []
    for c in chunks:
        c = c.strip()
        if c and c not in cleaned:
            cleaned.append(c)

    return cleaned


# -------------------------------------------------------------------
# 4. Cache: embedding model + Chroma collection (PersistentClient)
# -------------------------------------------------------------------
@st.cache_resource
def get_chroma_collection():
    """
    Create / load a ChromaDB collection and populate it with chunks from
    deities_knowledge.txt (Dakshinamurthy & Maha Vishnu).

    Uses the NEW Chroma persistent client API.
    """
    # SentenceTransformer embedding function used by Chroma
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # NEW: use PersistentClient for local on-disk storage
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    # Only populate if empty
    if collection.count() == 0:
        full_text = load_knowledge_text(KNOWLEDGE_FILE)
        chunks = simple_chunk_text(full_text, max_chars=600)

        ids = [f"chunk-{i}" for i in range(len(chunks))]
        metadatas = [{"source": "deities_knowledge.txt"} for _ in chunks]

        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas,
        )

    return collection


# -------------------------------------------------------------------
# 5. Cache: local text-generation model
# -------------------------------------------------------------------
@st.cache_resource
def load_model():
    """Load a smaller local text-generation model (distilgpt2) once and cache it."""
    generator = pipeline(
        "text-generation",
        model="distilgpt2",  # smaller & faster than DialoGPT-medium
    )
    return generator


# -------------------------------------------------------------------
# 6. RAG helper: retrieve relevant chunks from Chroma
# -------------------------------------------------------------------
def retrieve_context(query: str, top_k: int = 3):
    """Query ChromaDB to get top_k relevant chunks for the given user query."""
    collection = get_chroma_collection()
    result = collection.query(
        query_texts=[query],
        n_results=top_k,
    )

    # result["documents"] is a list of lists: [[chunk1, chunk2, ...]]
    documents = result.get("documents", [[]])[0] if result.get("documents") else []
    return documents


# -------------------------------------------------------------------
# 7. Prompt construction (strict RAG)
# -------------------------------------------------------------------
def build_prompt_from_history(history, user_message, used_context):
    """Build a strict prompt that forces the model to use only RAG context."""
    lines = []

    # Strict instructions
    lines.append(
        "You are a question-answering assistant.\n"
        "You MUST answer ONLY using the context below about Lord Dakshinamurthy and Maha Vishnu.\n"
        "If the answer is not clearly present in the context, reply exactly with:\n"
        "\"I don't know from this text.\"\n"
        "\n"
        "Context:\n"
    )

    # Add RAG context (chunks from ChromaDB)
    for i, ctx in enumerate(used_context, start=1):
        lines.append(f"[Chunk {i}] {ctx}\n")

    lines.append("\nConversation so far:\n")

    # Add previous chat history
    for msg in history:
        if msg["role"] == "user":
            lines.append(f"User: {msg['text']}\n")
        else:
            lines.append(f"Bot: {msg['text']}\n")

    # Add latest user message + ask for bot answer
    lines.append(f"User: {user_message}\n")
    lines.append("Bot:")

    return "\n".join(lines)


# -------------------------------------------------------------------
# 8. Generation with low creativity (less hallucination)
# -------------------------------------------------------------------
def generate_bot_reply(history, user_message, used_context, generator):
    """Generate a reply using the strict RAG prompt and low creativity."""
    prompt = build_prompt_from_history(history, user_message, used_context)

    # Safer settings: deterministic + shorter answers
    outputs = generator(
        prompt,
        do_sample=False,        # greedy decoding (no randomness)
        max_new_tokens=40,      # shorter, more precise
    )

    full_text = outputs[0]["generated_text"]

    # Keep only text after the last "Bot:" to avoid repeating the prompt
    if "Bot:" in full_text:
        bot_part = full_text.split("Bot:")[-1].strip()
    else:
        bot_part = full_text.strip()

    # Cut at any extra "User:" or "Bot:" markers the model might generate
    for stop_token in ["User:", "Bot:"]:
        if stop_token in bot_part:
            bot_part = bot_part.split(stop_token)[0].strip()

    if len(bot_part) == 0:
        bot_part = "I don't know from this text."

    return bot_part


# -------------------------------------------------------------------
# 9. Session state initialization
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "bot",
            "text": (
                "Namaste 🙏 I am a RAG-based chatbot. I answer only from the local "
                "knowledge file about Lord Dakshinamurthy and Maha Vishnu.\n\n"
                "Ask me something like:\n"
                "- Who is Maha Vishnu and what is his role in the Hindu trinity?\n"
                "- Why is Lord Dakshinamurthy called the supreme teacher?"
            ),
        }
    ]

if "last_used_context" not in st.session_state:
    st.session_state["last_used_context"] = []


# -------------------------------------------------------------------
# 10. Sidebar: info + clear chat
# -------------------------------------------------------------------
st.sidebar.header("⚙️ Chat Settings")

if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state["messages"] = [
        {
            "role": "bot",
            "text": (
                "Chat cleared. I will again use only the knowledge about "
                "Lord Dakshinamurthy and Maha Vishnu from your local file."
            ),
        }
    ]
    st.session_state["last_used_context"] = []
    st.rerun()

with st.sidebar.expander("ℹ️ How this works", expanded=False):
    st.markdown(
        "- Uses **ChromaDB** for vector search (RAG).\n"
        "- Uses **SentenceTransformer all-MiniLM-L6-v2** for embeddings.\n"
        "- Uses **distilgpt2** local model for answer generation.\n"
        "- Prompt is **strict**: answers only from context or says:\n"
        "  `I don't know from this text.`"
    )

# -------------------------------------------------------------------
# 11. Load model (cached)
# -------------------------------------------------------------------
generator = load_model()

# -------------------------------------------------------------------
# 12. Display conversation so far
# -------------------------------------------------------------------
st.subheader("🗣️ Conversation")

for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(
            f"""
<div style="background-color:#e3f2fd; padding:8px 12px; border-radius:8px; margin-bottom:6px;">
    <strong>You:</strong> {msg['text']}
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div style="background-color:#f1f8e9; padding:8px 12px; border-radius:8px; margin-bottom:6px;">
    <strong>Bot:</strong> {msg['text']}
</div>
""",
            unsafe_allow_html=True,
        )

# -------------------------------------------------------------------
# 13. User input form
# -------------------------------------------------------------------
st.subheader("✉️ Ask a question")

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Type your question about Lord Dakshinamurthy or Maha Vishnu:",
        "",
        placeholder="Example: Who is Maha Vishnu and what is his role in the Hindu trinity?",
    )
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip() != "":
    question = user_input.strip()

    # 1) Retrieve RAG context from Chroma
    with st.spinner("🔍 Retrieving relevant context from ChromaDB..."):
        used_context = retrieve_context(question, top_k=3)

    # 2) Generate answer
    history = st.session_state["messages"]
    with st.spinner("🤖 Generating answer from context..."):
        reply = generate_bot_reply(
            history=history,
            user_message=question,
            used_context=used_context,
            generator=generator,
        )

    # 3) Update session state
    st.session_state["messages"].append({"role": "user", "text": question})
    st.session_state["messages"].append({"role": "bot", "text": reply})
    st.session_state["last_used_context"] = used_context

    st.rerun()

# -------------------------------------------------------------------
# 14. Show context used for the last answer
# -------------------------------------------------------------------
if st.session_state.get("last_used_context"):
    with st.expander("📚 Context used from knowledge base (RAG)", expanded=False):
        for i, c in enumerate(st.session_state["last_used_context"], start=1):
            st.markdown(f"**Chunk {i}:** {c}")
