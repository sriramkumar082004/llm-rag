from rag import rag_answer, query_ollama
from tools.duckduckgo_search import live_search
from tools.student_api import query_students_natural

from mcp.intent_classifier import classify_intent
import logging

logger = logging.getLogger(__name__)


def query_ollama_direct(question: str) -> str:
    """
    Query Ollama directly for general knowledge questions.
    No RAG context, no web search - just pure LLM.
    """
    prompt = f"""You are a helpful AI assistant. Answer the following question clearly and accurately.

Question: {question}

Answer:"""

    return query_ollama(prompt)


def route_question(question: str) -> tuple[str, str]:
    """
    Routes a question to the appropriate data source using four-way classification:
    1. 'student' - Student data → PostgreSQL database
    2. 'web' - Live/current data → DuckDuckGo search
    3. 'rag' - Domain-specific data → Crime database
    4. 'general' - General knowledge → Direct Ollama query

    Returns:
        (context/answer, source_type) tuple
    """
    intent = classify_intent(question)
    logger.info(f"Question: '{question}' | Intent: {intent}")

    if intent == "student":
        # Student data - query PostgreSQL database
        logger.info("Routing to STUDENT database")
        answer = query_students_natural(question)
        return answer, "student"

    elif intent == "web":
        # Live data - search the web
        logger.info("Routing to WEB search")
        search_results = live_search(question, max_results=5)
        context = "\n".join(search_results)
        return context, "web"

    elif intent == "rag":
        # Domain-specific - use RAG database
        logger.info("Routing to RAG database")
        answer = rag_answer(question)
        return answer, "rag"

    else:  # intent == "general"
        # General knowledge - direct Ollama query
        logger.info("Routing to GENERAL Ollama")
        answer = query_ollama_direct(question)
        return answer, "general"
