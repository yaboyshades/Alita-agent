"""
Hybrid Planning System (Placeholder)
A simplified planner for this prototype.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging


@dataclass
class PlanningResult:
    action_sequence: List[Dict[str, Any]]


class HybridPlanner:
    """Very small planner that selects or creates tools."""

    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("HybridPlanner")
        self.logger.info("Planning system initialized.")

    async def plan(self, user_query: str, available_tools: List[str]) -> PlanningResult:
        """Generates a direct, single-step plan for the prototype.

        Chooses the first tool whose name appears in the query (case-insensitive).
        Falls back to the first available tool when no match is found."""
        self.logger.info(f"Generating plan for: {user_query}")
        chosen_tool = None
        if available_tools:
            query_lower = user_query.lower()
            for tool in available_tools:
                if tool.lower() in query_lower:
                    chosen_tool = tool
                    break
            if chosen_tool is None:
                chosen_tool = available_tools[0]
        return PlanningResult(
            action_sequence=[{"tool": chosen_tool, "query": user_query}]
        )
