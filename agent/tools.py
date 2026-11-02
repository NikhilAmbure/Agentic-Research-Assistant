import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def search_web(query: str, max_results: int = 4) -> list[dict]:
    res = _client.search(query=query, max_results=max_results)
    return [
        {"url": r["url"], "title": r["title"], "content": r["content"]}
        for r in res["results"]
    ]