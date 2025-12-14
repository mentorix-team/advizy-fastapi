from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from config import settings
client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, prefer_grpc=False)

client.recreate_collection(
    collection_name="experts",
    vectors_config=VectorParams(
        size=384,               # embedding dimension
        distance=Distance.COSINE
    )
)

print("Qdrant collection created successfully!")
