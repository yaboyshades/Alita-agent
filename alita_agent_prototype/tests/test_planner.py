import asyncio
from alita_agent.config.settings import AlitaConfig
from alita_agent.core.planning import HybridPlanner


def test_planner_selects_matching_tool(tmp_path):
    config = AlitaConfig(workspace_dir=str(tmp_path))
    planner = HybridPlanner(config)

    async def run():
        result = await planner.plan("show weather", ["search", "weather"])
        assert result.action_sequence[0]["tool"] == "weather"

    asyncio.run(run())


def test_planner_falls_back_to_first_tool(tmp_path):
    config = AlitaConfig(workspace_dir=str(tmp_path))
    planner = HybridPlanner(config)

    async def run():
        result = await planner.plan("do something", ["search", "weather"])
        assert result.action_sequence[0]["tool"] == "search"

    asyncio.run(run())
