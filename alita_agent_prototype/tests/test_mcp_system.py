def test_mcp_system_tool_creation_and_execution():
    import asyncio
    from alita_agent.config.settings import AlitaConfig
    from alita_agent.core.web_agent import WebAgent
    from alita_agent.core.mcp_system import MCPSystem

    config = AlitaConfig()
    web_agent = WebAgent(config)
    mcp = MCPSystem(config, web_agent)
    # Use the mock generator for tests to avoid real API calls
    async def mock_gen(name, desc, ctx):
        return mcp._mock_llm_code_generation(name, desc, ctx)
    mcp.llm_code_generator = mock_gen
    tool_name = "TestEchoTool"
    task_description = "A tool that echoes its input."
    async def run():
        await mcp.create_tool(tool_name, task_description)
        result = await mcp.execute_tool(tool_name, {"echo": "hello"})
        assert result.success
        assert result.result["status"] == "success"
        assert result.result["received_params"]["echo"] == "hello"
    asyncio.run(run())
