from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
import numpy as np

model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embeddings(texts):
    """Generate embeddings for a list of texts."""
    embeddings = model.encode(texts)
    return np.array(embeddings, dtype="float32")
