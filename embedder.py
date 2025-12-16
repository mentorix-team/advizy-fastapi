# from sentence_transformers import SentenceTransformer

# # Load model once at startup (best practice)
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# def generate_embedding(text: str):
#     # Convert to vector list (Python can't json return numpy array)
#     vector = model.encode(text).tolist()
#     return vector

import os
from fastembed import TextEmbedding

FASTEMBED_CACHE = os.getenv("FASTEMBED_CACHE", "./model_cache")
os.makedirs(FASTEMBED_CACHE, exist_ok=True)

_model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    cache_dir=FASTEMBED_CACHE
)

def generate_embedding(text: str) -> list[float]:
    embedding = list(_model.embed(text))[0]   # numpy.ndarray
    return embedding.tolist()                 # ✅ convert to list
