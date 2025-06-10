"""A very small planning module.

The planner analyses the user's query and the tools currently available and
returns an ordered list of actions for the ``ManagerAgent`` to perform.  This is
not a full-blown planner, but it provides real logic rather than a placeholder
"pass" implementation.
"""

from __future__ import annotations

from typing import Dict, Any, List
from dataclasses import dataclass

from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging

@dataclass
class PlanningResult:
    action_sequence: List[Dict[str, Any]]

class HybridPlanner:
    """Naive rule-based planner."""

    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("HybridPlanner")
        self.logger.info("Planning system ready.")

    async def plan(self, user_query: str, available_tools: List[str]) -> PlanningResult:
        """Generate a minimal plan based on keyword matching."""

        self.logger.info(f"Planning for query: {user_query}")

        chosen_tool = None
        lowered = user_query.lower()
        for tool in available_tools:
            if tool.lower().replace("tool", "") in lowered:
                chosen_tool = tool
                break

        if not chosen_tool and available_tools:
            chosen_tool = available_tools[0]

        actions = []
        if chosen_tool:
            actions.append({"action": "execute_tool", "tool": chosen_tool})

        return PlanningResult(action_sequence=actions)
