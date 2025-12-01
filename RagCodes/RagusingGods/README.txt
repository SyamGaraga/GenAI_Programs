# Streamlit RAG Chatbot – ChromaDB + distilgpt2 (Final Version)

This is the final working example for a local RAG chatbot that answers questions
about Lord Dakshinamurthy and Maha Vishnu using:

- Streamlit UI
- ChromaDB (PersistentClient, local `chroma_db/` folder)
- SentenceTransformer (`all-MiniLM-L6-v2`) for embeddings
- `distilgpt2` as a small local language model

## Folder Structure

streamlit_rag_chroma_chatbot_final/
├─ app.py
├─ requirements.txt
├─ README.txt
└─ data/
   └─ deities_knowledge.txt

ChromaDB will create its own local folder at runtime:

└─ chroma_db/

## How to Run

1. Open a terminal in this folder:

   ```powershell
   cd path\to\streamlit_rag_chroma_chatbot_final
   ```

2. Create and activate a virtual environment (example with Python 3.13):

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate
   ```

3. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. Run the app:

   ```powershell
   streamlit run app.py
   ```

Then open the URL shown in the terminal (usually http://localhost:8501) and
ask questions like:

- "Who is Maha Vishnu and what is his role in the Hindu trinity?"
- "Why is Lord Dakshinamurthy called the supreme teacher?"
