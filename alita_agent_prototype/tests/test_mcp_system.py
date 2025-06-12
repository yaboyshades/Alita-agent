def test_mcp_system_tool_creation_and_execution():
    import asyncio
    from alita_agent.config.settings import AlitaConfig
    from alita_agent.core.web_agent import WebAgent
    from alita_agent.core.mcp_system import MCPSystem

    config = AlitaConfig()
    web_agent = WebAgent(config)
    mcp = MCPSystem(config, web_agent)
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
    if not sys.stdin.isatty():
        input_params = json.load(sys.stdin)
        result = execute(input_params)
        print(json.dumps(result, indent=2))
    else:
        print('This script should be run with JSON input via stdin.')
"""
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
