from ddgs import DDGS
import logging

logger = logging.getLogger(__name__)


def live_search(query: str, max_results=5):
    """
    Performs live web search using DuckDuckGo.
    Returns formatted search results as a list of strings.
    """
    results = []

    try:
        logger.info(f"Performing DuckDuckGo search for: {query}")

        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=max_results))

            if not search_results:
                logger.warning(f"No results found for query: {query}")
                return ["No web results found for your query."]

            for idx, r in enumerate(search_results, 1):
                # Format each result with title, body, and URL
                title = r.get("title", "No title")
                body = r.get("body", "No description")
                url = r.get("href", "")

                formatted_result = f"[{idx}] {title}\n{body}\nSource: {url}\n"
                results.append(formatted_result)

            logger.info(f"Found {len(results)} results")

    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return [f"Error performing web search: {str(e)}"]

    return results
