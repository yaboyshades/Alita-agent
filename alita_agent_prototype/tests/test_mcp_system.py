def test_mcp_system_tool_creation_and_execution():
    import asyncio
    import logging
    from alita_agent.config.settings import AlitaConfig
    from alita_agent.core.web_agent import WebAgent, SearchResult
    from alita_agent.core.mcp_system import MCPSystem

    config = AlitaConfig()
    web_agent = WebAgent(config)

    # Enable debug logging
    logging.getLogger("SandboxExecutor").setLevel(logging.DEBUG)

    # Mock the web search to avoid network calls
    async def mock_search(query):
        return SearchResult(
            query=query, results=[{"title": "Mock result", "snippet": "Mock snippet"}]
        )

    web_agent.search = mock_search

    from alita_agent.core.tool_registry import ToolRegistry

    registry = ToolRegistry(config.get_workspace_path("tools"))
    mcp = MCPSystem(config, web_agent, registry)

    # Use a local generator for tests to avoid real API calls
    async def mock_gen(name, desc, ctx):
        return f"""#!/usr/bin/env python3
import sys
import json

def execute(params: dict):
    result_data = {{
        'status': 'success',
        'message': f"Tool '{name}' executed successfully with mock logic.",
        'received_params': params,
    }}
    return result_data

if __name__ == '__main__':
    try:
        input_data = sys.stdin.read().strip()
        if input_data:
            input_params = json.loads(input_data)
            result = execute(input_params)
            print(json.dumps(result))
        else:
            print(json.dumps({{"error": "No input provided"}}))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
"""

    mcp.llm_code_generator = mock_gen
    tool_name = "TestEchoTool"
    task_description = "A tool that echoes its input."

    async def run():
        await mcp.create_tool(tool_name, task_description)
        assert registry.tool_exists(tool_name)
        result = await mcp.execute_tool(tool_name, {"echo": "hello"})
        print(f"DEBUG: result.success = {result.success}")
        print(f"DEBUG: result.result = {result.result}")
        print(f"DEBUG: result.error = {result.error}")
        assert result.success
        assert result.result["status"] == "success"
        assert result.result["received_params"]["echo"] == "hello"

    asyncio.run(run())
