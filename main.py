from fastapi import FastAPI
from redis_cache import redis_client
from rag import rag_answer

app = FastAPI(title="Crime RAG System")

@app.get("/ask")
def ask(question: str):

    # 1️⃣ Redis Cache
    cached = redis_client.get(question)
    if cached:
        return {
            "source": "redis-cache",
            "answer": cached
        }

    # 2️⃣ RAG Pipeline
    answer = rag_answer(question)

    # 3️⃣ Store in Redis (30 minutes)
    redis_client.setex(question, 1800, answer)

    return {
        "source": "rag-faiss-ollama",
        "answer": answer
    }
