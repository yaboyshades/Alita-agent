"""The Web Agent: Information retrieval from external sources."""
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging

@dataclass
class SearchResult:
    query: str
    results: List[Dict[str, Any]]

class WebAgent:
    """A placeholder for a real web search agent."""
    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("WebAgent")
        self.logger.info("Placeholder Web Agent initialized.")

    async def search(self, query: str) -> SearchResult:
        """MOCK: Simulates a web search."""
        self.logger.warning(f"Using MOCK web search for query: '{query}'")
        mock_results = [
            {"title": "Python Official Documentation", "url": "https://docs.python.org", "snippet": "The official source for Python documentation."},
            {"title": "Stack Overflow - Python", "url": "https://stackoverflow.com/questions/tagged/python", "snippet": "Questions and answers about Python programming."}
        ]
        return SearchResult(query=query, results=mock_results)
