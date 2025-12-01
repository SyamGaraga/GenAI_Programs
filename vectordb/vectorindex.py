import numpy as np
import faiss

# 1. Suppose these are 5 product embeddings (dimension d = 4)
d = 4  # vector dimension
vectors = np.array([
    [0.9,  0.1,  0.0,  0.0],  # "Red apple"
    [0.85, 0.15, 0.0,  0.0],  # "Green apple"
    [0.1,  0.9,  0.0,  0.0],  # "Banana fruit"
    [0.0,  0.1,  0.9,  0.1],  # "Fresh orange"
    [0.88, 0.12, 0.1,  0.0],  # "Apple juice"
], dtype='float32')

print("vectors.shape =", vectors.shape)  # (5, 4)

# 2. Create an HNSW index using L2 distance
M = 32
index = faiss.IndexHNSWFlat(d, M)

# Optional: tune HNSW parameters
index.hnsw.efConstruction = 40
index.hnsw.efSearch = 50

# 3. Add vectors
index.add(vectors)
print("Index total vectors:", index.ntotal)

# 4. Query vector for "Apple drink"
query = np.array([[0.0,  0.1,  0.9,  0.1]], dtype='float32')

# 5. Search
k = 3
D, I = index.search(query, k)

print("Nearest distances:", D)
print("Nearest indices:", I)
