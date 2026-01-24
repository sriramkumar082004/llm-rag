import faiss
import pickle
from embeddings import generate_embeddings
from config import INDEX_FILE

# Load the pre-built FAISS index
try:
    index = faiss.read_index(INDEX_FILE)
    with open("crime_texts.pkl", "rb") as f:
        texts = pickle.load(f)
    print(f"✅ Loaded FAISS index with {index.ntotal} vectors")
except FileNotFoundError:
    print("❌ Index files not found!")
    print("🔨 Please run: python build_index.py")
    raise


def search_similar(query, top_k=3):
    """Search for similar crime records based on the query."""
    query_embedding = generate_embeddings([query])
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        results.append(
            {"text": texts[idx], "distance": float(distances[0][i]), "rank": i + 1}
        )

    return results
