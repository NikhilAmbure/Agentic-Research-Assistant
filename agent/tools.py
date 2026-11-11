import os
import re

from dotenv import load_dotenv
from httpx2 import query
from tavily import TavilyClient

load_dotenv()
_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

INJECTION_PATTERNS = re.compile(
    r"ignore (all |any )?(previous|prior|above) instructions|disregard .{0,30}instructions"
    r"|you are now|reveal .{0,20}system prompt",
    re.I,
)
EXCLUDED = ["linkedin.com", "x.com", "twitter.com", "facebook.com", "reddit.com", "quora.com"]

def _clean(text: str, limit: int = 1500) -> str:
    return re.sub(r"\s+", " ", text).strip()[:limit]


def search_web(query: str, max_results: int = 4) -> list[dict]:
    res = _client.search(query=query, max_results=max_results, exclude_domains=EXCLUDED)
    out = []
    for r in res["results"]:
        content = _clean(r["content"])
        if INJECTION_PATTERNS.search(content):
            continue  # skip pages that try to instruct the model
        out.append({"url": r["url"], "title": r["title"], "content": content})
    return out