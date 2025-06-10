"""The Web Agent: Information retrieval from external sources."""
from typing import Dict, Any, List
from dataclasses import dataclass
import aiohttp
from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging

@dataclass
class SearchResult:
    query: str
    results: List[Dict[str, Any]]

class WebAgent:
    """A minimal asynchronous web search agent using DuckDuckGo."""

    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("WebAgent")
        self.logger.info("Web Agent initialized.")

    async def search(self, query: str) -> SearchResult:
        """Perform a web search using DuckDuckGo."""
        url = "https://duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "skip_disambig": 1,
        }
        results: List[Dict[str, Any]] = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    data = await resp.json()
                    for item in data.get("RelatedTopics", []):
                        if isinstance(item, dict) and "Text" in item and "FirstURL" in item:
                            results.append(
                                {
                                    "title": item["Text"],
                                    "url": item["FirstURL"],
                                    "snippet": item["Text"],
                                }
                            )
        except Exception as exc:
            self.logger.error(f"Web search failed: {exc}")
        return SearchResult(query=query, results=results)
