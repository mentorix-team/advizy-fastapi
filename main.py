# ...existing code...
import uuid
import logging
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient, models
from config import settings
from embedder import generate_embedding

# -------------------------------------------
# Logging
# -------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------------------
# FastAPI App
# -------------------------------------------
app = FastAPI(title="Advizy Embedding Service", version="1.0.0")

# -------------------------------------------
# Qdrant Client (Production Safe)
# -------------------------------------------

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

print(client.get_collection("experts"))

# -------------------------------------------
# Request Models
# -------------------------------------------
class EmbedExpertRequest(BaseModel):
    expertId: str
    summary: str


class EmbedExpertResponse(BaseModel):
    success: bool
    message: str
    mongoId: str
    qdrantId: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

# -------------------------------------------
# Health Check
# -------------------------------------------
@app.get("/ping")
async def ping():
    return {"status": "ok", "service": "advizy-embedding-service"}


# -------------------------------------------
# Store Embedding into Qdrant
# -------------------------------------------
@app.post("/embed", response_model=EmbedExpertResponse)
async def embed_expert(request: EmbedExpertRequest):
    try:
        logger.info(f"Embedding request received for Expert: {request.expertId}")

        # 1️⃣ Generate embedding
        vector = generate_embedding(request.summary)

        if not isinstance(vector, list):
            raise ValueError("Embedding generation failed. Expected list vector.")

        # 2️⃣ Create Qdrant-Compatible UUID (use UUID object)
        qdrant_uuid = uuid.uuid4()

        # 3️⃣ Upsert vector into Qdrant (use upsert)
        # Use `upsert` which accepts collection_name and points list
        client.upsert(
            collection_name="experts",
            points=[
                models.PointStruct(
                    id=qdrant_uuid,
                    vector=vector,
                    payload={
                        "mongoId": request.expertId,
                        "summary": request.summary
                    }
                )
            ]
        )

        logger.info(f"Embedding stored. QdrantId={qdrant_uuid}")

        return EmbedExpertResponse(
            success=True,
            message="Embedding stored in Qdrant",
            mongoId=request.expertId,
            qdrantId=str(qdrant_uuid)
        )

    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ----
# generate embedding for user query
@app.post("/embed-user-query")
async def embed_user_query(query: str = Body(...)):
    try:
        logger.info("Generating embedding for user query.")

        # Generate embedding
        vector = generate_embedding(query)

        if not isinstance(vector, list):
            raise ValueError("Embedding generation failed. Expected list vector.")

        logger.info("User query embedding generated successfully.")

        return JSONResponse(content={"embedding": vector})

    except Exception as e:
        logger.error(f"User query embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ---------- SEARCH ENDPOINT ----------
@app.post("/search-experts")
async def search_experts(request: SearchRequest):

    try:
        logger.info(f"Searching experts for query: {request.query}")

        # 1️⃣ Generate embedding for user query
        query_vector = generate_embedding(request.query)

        if not isinstance(query_vector, list):
            raise ValueError("Embedding generation failed. Expected list vector.")

        # 2️⃣ Perform similarity search in Qdrant using query_points (preferred method)
        # query_points accepts pre-computed vectors and is the modern API for similarity search
        try:
            hits = client.query_points(
                collection_name="experts",
                query=query_vector,
                limit=request.top_k,
                with_payload=True
            )
        except Exception as e:
            logger.warning(f"query_points failed ({str(e)}), trying alternatives...")
            # Fallback to other methods if query_points doesn't work
            candidates = [
                ("search", {"collection_name": "experts", "query_vector": query_vector, "limit": request.top_k, "with_payload": True}),
                ("search_points", {"collection_name": "experts", "query_vector": query_vector, "limit": request.top_k, "with_payload": True}),
                ("query", {"collection_name": "experts", "query": query_vector, "limit": request.top_k, "with_payload": True}),
            ]
            hits = None
            for method_name, kwargs in candidates:
                if hasattr(client, method_name):
                    try:
                        hits = getattr(client, method_name)(**kwargs)
                        logger.info(f"Successfully used fallback method: {method_name}")
                        break
                    except Exception as fallback_err:
                        logger.debug(f"Fallback method {method_name} failed: {fallback_err}")
                        continue
            
            if hits is None:
                raise RuntimeError(
                    "qdrant-client missing or failed on all search methods. "
                    "Check installed version: run 'python -m pip show qdrant-client' and ensure Qdrant is running."
                )

        # 3️⃣ Normalize response and extract matched expert MongoDB IDs + scores
        # Qdrant client may return a QueryResponse with attribute `points` (list of ScoredPoint),
        # or other structures. Normalize to a plain list of point-like objects/dicts.
        points_list = None
        if hasattr(hits, "points"):
            points_list = hits.points
        elif hasattr(hits, "result"):
            points_list = getattr(hits, "result", None)
        elif isinstance(hits, dict) and "result" in hits:
            points_list = hits.get("result")
        elif isinstance(hits, list):
            points_list = hits
        else:
            try:
                maybe = list(hits)
                if len(maybe) == 2 and isinstance(maybe[1], list):
                    points_list = maybe[1]
                else:
                    points_list = maybe
            except Exception:
                points_list = []

        if points_list is None:
            points_list = []

        results = []
        for hit in points_list:
            # If hit is a tuple like ('points', [ScoredPoint,...]) skip to inner list
            if isinstance(hit, tuple) and len(hit) == 2 and isinstance(hit[1], list):
                inner = hit[1]
                for h in inner:
                    payload = getattr(h, "payload", {}) if not isinstance(h, dict) else h.get("payload", {})
                    score = getattr(h, "score", None) if not isinstance(h, dict) else h.get("score")
                    mongo_id = payload.get("mongoId") if isinstance(payload, dict) else None
                    results.append({"mongoId": mongo_id, "score": score})
                continue

            if isinstance(hit, dict):
                payload = hit.get("payload") or {}
                score = hit.get("score")
            else:
                payload = getattr(hit, "payload", {}) or {}
                score = getattr(hit, "score", None)

            mongo_id = payload.get("mongoId") if isinstance(payload, dict) else None
            results.append({"mongoId": mongo_id, "score": score})

        logger.info(f"Top {request.top_k} matches: {results}")

        # 4️⃣ Return matched IDs to Node.js
        return JSONResponse(content={
            "success": True,
            "matches": results
        })

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------
# Debug Endpoint: Send message to Node.js
# (Useful only during development)
# -------------------------------------------
@app.get("/send-to-node")
async def send_to_node():
    import httpx

    url = "http://localhost:5030/api/v1/fastapi/from-fastapi"
    payload = {"msg": "Hello from FastAPI!"}

    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(url, json=payload)

        logger.info(f"NodeJS Response: {response.text}")
        return JSONResponse(content=response.json())

    except Exception as e:
        logger.error(f"Failed to reach NodeJS: {str(e)}")
        return {"success": False, "error": str(e)}