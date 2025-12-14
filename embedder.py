from sentence_transformers import SentenceTransformer

# Load model once at startup (best practice)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding(text: str):
    # Convert to vector list (Python can't json return numpy array)
    vector = model.encode(text).tolist()
    return vector
