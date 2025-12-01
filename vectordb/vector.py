import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Sample embeddings
docs = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])  # Document vectors
query = np.array([[0.2, 0.3]])  # Query vector

# Compute similarities
similarities = cosine_similarity(query, docs)[0]
ranked_indices = np.argsort(similarities)[::-1]
print("Top matches:", ranked_indices)