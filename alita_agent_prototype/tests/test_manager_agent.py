import asyncio
from alita_agent.config.settings import AlitaConfig
from alita_agent.core.manager_agent import ManagerAgent


def test_manager_agent_process_task():
    config = AlitaConfig()
    agent = ManagerAgent(config)

    # Patch MCPSystem generator to avoid real API calls
    async def mock_gen(name, desc, ctx):
        return agent.mcp_system._mock_llm_code_generation(name, desc, ctx)
    agent.mcp_system.llm_code_generator = mock_gen

    async def run():
        result = await agent.process_task("echo this text")
        assert result["success"]
        assert "success" in result["result"]["status"]
    asyncio.run(run())
