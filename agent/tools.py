import os

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

tavily = TavilySearch(api_key=os.getenv("TAVILY_API_KEY", ""))

@tool
def web_search(query: str) -> str:
    """Search the web for current, real-time information using Tavily."""
    try:
        result = tavily.invoke({"query": query})
        
        if isinstance(result, list):
            results = []

            for r in result:
                results.append(
                    f"Source: {r.get('url')}\n"
                    f"Content: {r.get('content')}\n"
                )

            return "\n\n".join(results)

        return str(result)

    except Exception as e:
        return f"Search error: {str(e)}"

tools = [web_search]