import asyncio

from alita_agent.config.settings import AlitaConfig
from alita_agent.core.planning import HybridPlanner


def test_planner_returns_action_sequence():
    planner = HybridPlanner(AlitaConfig())

    async def run():
        result = await planner.plan("reverse a string", ["ReverseStringTool"])
        assert result.action_sequence

    asyncio.run(run())
