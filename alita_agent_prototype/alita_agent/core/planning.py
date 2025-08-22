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
        """Generates a direct, single-step plan for the prototype."""
        self.logger.info(f"Generating plan for: {user_query}")
        if available_tools:
            tool = available_tools[0]
        else:
            tool = None
        return PlanningResult(action_sequence=[{"tool": tool, "query": user_query}])
