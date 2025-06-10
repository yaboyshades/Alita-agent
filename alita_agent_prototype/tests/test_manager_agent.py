import asyncio
from alita_agent.config.settings import AlitaConfig
from alita_agent.core.manager_agent import ManagerAgent


def test_manager_agent_process_task(tmp_path):
    config = AlitaConfig(workspace_dir=str(tmp_path))
    manager = ManagerAgent(config)

    async def run():
        query = "echo test"
        result = await manager.process_task(query)
        assert result["success"] is True
        tool_name = manager._generate_tool_name_from_query(query)
        tool_file = config.get_workspace_path("tools") / f"{tool_name}.py"
        assert tool_file.exists()

    asyncio.run(run())

