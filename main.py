from fastapi import FastAPI
from redis_cache import redis_client
from mcp.tool_router import route_question
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hybrid RAG + AI System")


@app.get("/ask")
def ask(question: str):
    """
    Main endpoint that intelligently routes queries to:
    - Student API (for student data)
    - Web search (for live/current data)
    - RAG database (for crime data)
    - Direct Ollama (for general knowledge)
    """

    # 1️⃣ Check Redis Cache
    cached = redis_client.get(question)
    if cached:
        logger.info(f"Cache HIT: {question}")
        return {"source": "redis-cache", "answer": cached, "cached": True}

    # 2️⃣ Route to appropriate source (Web / RAG / General)
    logger.info(f"Processing question: {question}")
    answer, source_type = route_question(question)

    # 3️⃣ Cache the result with appropriate TTL
    # student: 10 min | web: 5 min | rag: 30 min | general: 15 min
    cache_ttl = {"student": 600, "web": 300, "rag": 1800, "general": 900}.get(
        source_type, 1800
    )

    redis_client.setex(question, cache_ttl, answer)
    logger.info(f"Response from {source_type}, cached for {cache_ttl}s")

    return {"source": source_type, "answer": answer, "cached": False}
