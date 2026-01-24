import requests
from vector_store import search_similar
from config import OLLAMA_URL, MODEL_NAME


def query_ollama(prompt):
    """Send a prompt to Ollama and get the response."""
    response = requests.post(
        OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]


def rag_answer(question):
    """Answer a question using RAG (Retrieval Augmented Generation)."""
    # Search for similar crime records
    context_results = search_similar(question, top_k=5)

    # Extract text from results
    context_docs = [result["text"] for result in context_results]
    context = "\n\n".join(context_docs)

    prompt = f"""
You are a crime data assistant for Los Angeles crime records.
Answer ONLY using the context below. Be specific and cite details from the records.

Context (Top matching crime records):
{context}

Question:
{question}

Answer:"""

    return query_ollama(prompt)
