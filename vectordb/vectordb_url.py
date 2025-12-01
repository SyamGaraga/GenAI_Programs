from flask import Flask, render_template, request, send_file, redirect, url_for, Blueprint
import os, json, uuid, io
import numpy as np
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import pymupdf
from docx import Document
from datetime import datetime
import sqlite3 

# ---------------- CONFIG ----------------
CHROMA_DIR = "./chroma_db"
UPLOAD_DIR = "./uploads"
EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
client = PersistentClient(path=CHROMA_DIR)
model = SentenceTransformer(EMB_MODEL)


# ---------------- HELPERS ----------------
def get_col(name):
    """Get or create a Chroma collection."""
    try:
        return client.get_collection(name)
    except Exception:
        try:
             return client.get_collection(name)
        except:
             return client.create_collection(name)


def extract_text_from_file(path):
    """Extract text from txt, pdf, docx."""
    ext = os.path.splitext(path)[1].lower()
    text = ""

    if ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    elif ext == ".pdf":
        try:
            pdf = pymupdf.open(path)
            for page in pdf:
                text += page.get_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")

    elif ext == ".docx":
        try:
            doc = Document(path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX: {e}")

    return text.strip()


def get_summary():
    """Dashboard stats for the home page."""
    collections = client.list_collections()
    total_docs = 0
    recent = []

    for c in collections:
        col = client.get_collection(c.name)
        try:
            count = col.count()
        except:
            count = 0

        total_docs += count
        recent.append({"name": c.name, "count": count})

    return {
        "total_collections": len(collections),
        "total_documents": total_docs,
        "collections": recent[-5:]
    }


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    """Home/Dashboard view."""
    stats = get_summary()
    return render_template("index.html", stats=stats)


# ---------- COLLECTION MANAGEMENT ----------
@app.route("/collections", methods=["GET", "POST"])
def collections():
    """Handles listing and creation of collections."""
    if request.method == "POST":
        name = request.form["collectionName"].strip()
        if name:
            try:
                client.create_collection(name)
            except Exception as e:
                print(f"Error creating collection: {e}") 

    cols = [c.name for c in client.list_collections()]
    return render_template("collections.html", collections=cols)


@app.route("/delete_collection/<string:col_name>")
def delete_collection(col_name):
    """Deletes a collection by name."""
    try:
        client.delete_collection(col_name)
    except Exception as e:
        print("Error deleting collection:", e)

    return redirect(url_for("collections"))


# ---------- EXPORT FUNCTION ----------
@app.route("/export_collection/<string:col_name>")
def export_collection(col_name):
    """Exports all data from a collection as a JSON file."""
    col = client.get_collection(col_name)
    
    data = col.get(
        include=["documents", "metadatas", "embeddings"]
    )

    export_data = []

    docs = data.get("documents", [])
    metadatas = data.get("metadatas", [])
    embeddings = data.get("embeddings", [])
    ids = data.get("ids", [])

    for doc, meta, emb, item_id in zip(docs, metadatas, embeddings, ids):

        if hasattr(emb, "tolist"):
            emb = emb.tolist()

        export_data.append({
            "id": item_id,
            "document": doc,
            "metadata": meta,
            "embedding": emb
        })

    buf = io.BytesIO(json.dumps(export_data, indent=2).encode("utf-8"))
    buf.seek(0)

    return send_file(
        buf, 
        as_attachment=True, 
        download_name=f"{col_name}_export.json",
        mimetype='application/json'
    )


# ---------- UPLOAD (FIXED WITH TRY/EXCEPT) ----------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Handles uploading text or files, and embedding."""
    cols = [c.name for c in client.list_collections()]

    if request.method == "POST":
        # Start comprehensive try/except block to ensure a return statement is always hit
        try:
            col_name = request.form["collection"]
            input_type = request.form["input_type"]
            
            if col_name not in [c.name for c in client.list_collections()]:
                 return "Error: Collection does not exist.", 400

            col = client.get_collection(col_name)

            metadata_raw = request.form.get("metadata", "")
            try:
                metadata = json.loads(metadata_raw) if metadata_raw else {}
            except:
                metadata = {}

            text = ""
            if input_type == "text":
                text = request.form.get("text", "").strip()

            elif input_type == "file":
                uploaded = request.files.get("file")
                if uploaded and uploaded.filename:
                    save_path = os.path.join(UPLOAD_DIR, uploaded.filename)
                    uploaded.save(save_path)
                    text = extract_text_from_file(save_path)
                    os.remove(save_path) # Clean up

            if not text:
                return "No text provided or extracted.", 400

            # Embed and upload
            emb = model.encode([text])[0].tolist()
            
            col.add(
                ids=[str(uuid.uuid4())],
                documents=[text],
                metadatas=[{**metadata, "timestamp": str(datetime.now())}],
                embeddings=[emb],
            )
            
            return redirect(url_for("search"))

        except Exception as e:
            # Catch-all: If any error occurred during the POST process, return a 500 error
            print(f"UPLOAD PROCESSING ERROR: {e}")
            return f"An unhandled error occurred during processing: {e}", 500


    return render_template("upload.html", collections=cols)


# ---------- SEARCH (FIXED: REMOVED "ids" from include list) ----------
@app.route("/search", methods=["GET", "POST"])
def search():
    """Handles vector similarity search and keyword/hybrid filtering."""
    cols = [c.name for c in client.list_collections()]
    results = None
    selected_col = None

    if request.method == "POST":
        selected_col = request.form["collection"]
        query = request.form["query"].strip()
        topk = int(request.form.get("topk", 5))
        mode = request.form.get("mode", "vector")
        where_raw = request.form.get("filter", "")

        col = client.get_collection(selected_col)

        where = None
        try:
            where = json.loads(where_raw) if where_raw else None
        except:
            where = None

        query_emb = model.encode([query])[0].tolist()

        # FIX: Removed "ids" from the include list, as they are returned by default.
        res = col.query(
            query_embeddings=[query_emb],
            n_results=topk,
            include=["documents", "metadatas", "distances"], 
            where=where
        )

        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dists = res["distances"][0]
        ids = res["ids"][0] # IDs are still available here

        results = []
        for doc, meta, dist, doc_id in zip(docs, metas, dists, ids):
            score = 1 / (1 + dist)
            keyword_match = query.lower() in doc.lower()

            if mode == "keyword" and not keyword_match:
                continue
            if mode == "hybrid" and not keyword_match:
                continue

            results.append({
                "id": doc_id,
                "text": doc,
                "metadata": meta,
                "score": score
            })

    return render_template(
        "search.html",
        collections=cols,
        results=results,
        selected_col=selected_col
    )


# ---------- DELETE DOCUMENT ----------
@app.route("/delete_document/<string:col_name>/<string:doc_id>")
def delete_document(col_name, doc_id):
    """Deletes a specific document (chunk) from a collection."""
    col = client.get_collection(col_name)
    try:
        col.delete(ids=[doc_id])
    except Exception as e:
        print("Error deleting document:", e)

    return redirect(url_for("search"))


# ---------- VISUALIZATION ----------
@app.route("/visualize", methods=["GET", "POST"])
def visualize():
    """
    Provides a 2D PCA visualization of document embeddings from a selected Chroma collection.
    """
    cols = [c.name for c in client.list_collections()]
    selected_col = request.form.get("collection") if request.method == "POST" else None
    chart_data = None
    error = None

    if request.method == "POST" and selected_col:
        
        try:
            col = client.get_collection(selected_col)
            
            data = col.get(
                include=["documents", "metadatas", "embeddings"]
            )
            
            vectors = data.get("embeddings", [])
            doc_ids = data.get("ids", [])
            documents = data.get("documents", [])
            metadatas = data.get("metadatas", [])
            
        except Exception as e:
            error = f"Error retrieving data from collection '{selected_col}': {e}"
            vectors = [] 

        
        if len(vectors) < 2:
            error = f"Need at least 2 documents in collection '{selected_col}' for PCA visualization (found {len(vectors)})."
            
        else:
            vectors = np.array(vectors)
            pca = PCA(n_components=2)
            
            try:
                reduced = pca.fit_transform(vectors)
                x_vals = reduced[:, 0].tolist()
                y_vals = reduced[:, 1].tolist()

                chart_data = []
                for i in range(len(doc_ids)):
                    chart_data.append({
                        "id": doc_ids[i],
                        "x": x_vals[i],
                        "y": y_vals[i],
                        "meta": metadatas[i],
                        "snippet": documents[i][:80] + "..." if documents[i] else "No text"
                    })
            except ValueError as e:
                error = f"PCA fitting failed. Check embedding dimensions. Error: {e}"


    return render_template(
        "visualize.html",
        collections=cols,
        selected_col=selected_col,
        chart_data=chart_data,
        error=error
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)