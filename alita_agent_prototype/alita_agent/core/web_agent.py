"""The Web Agent: information retrieval using DuckDuckGo."""

from __future__ import annotations

import requests
from typing import Dict, Any, List
from dataclasses import dataclass

from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging

@dataclass
class SearchResult:
    query: str
    results: List[Dict[str, Any]]

class WebAgent:
    """Simple web search powered by DuckDuckGo's instant answer API."""

    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("WebAgent")
        self.logger.info("Web Agent ready.")

    async def search(self, query: str) -> SearchResult:
        """Perform a real web search."""

        self.logger.info(f"Searching the web for: {query}")
        params = {"q": query, "format": "json", "no_html": 1, "no_redirect": 1}
        try:
            resp = requests.get("https://api.duckduckgo.com/", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results: List[Dict[str, Any]] = []
            for item in data.get("RelatedTopics", []):
                if isinstance(item, dict) and "FirstURL" in item:
                    results.append({
                        "title": item.get("Text", ""),
                        "url": item.get("FirstURL"),
                        "snippet": item.get("Text", "")
                    })
            return SearchResult(query=query, results=results)
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            return SearchResult(query=query, results=[])
