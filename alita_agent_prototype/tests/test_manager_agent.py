import asyncio
from alita_agent.config.settings import AlitaConfig
from alita_agent.core.manager_agent import ManagerAgent
from alita_agent.core.web_agent import SearchResult


def test_manager_agent_process_task(tmp_path):
    config = AlitaConfig(workspace_dir=str(tmp_path))
    manager = ManagerAgent(config)

    # Mock web search to avoid network calls
    async def mock_search(query):
        return SearchResult(query=query, results=[{"title": "Mock result", "snippet": "Mock snippet"}])
    manager.mcp_system.web_agent.search = mock_search

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

    manager.mcp_system.llm_code_generator = mock_gen

    async def run():
        query = "echo test"
        result = await manager.process_task(query)
        assert result["success"] is True
        tool_name = manager._generate_tool_name_from_query(query)
        tool_file = config.get_workspace_path("tools") / f"{tool_name}.py"
        assert tool_file.exists()

    asyncio.run(run())


def test_manager_agent_process_task_default():
    config = AlitaConfig()
    agent = ManagerAgent(config)

    # Mock web search to avoid network calls
    async def mock_search(query):
        return SearchResult(query=query, results=[{"title": "Mock result", "snippet": "Mock snippet"}])
    agent.mcp_system.web_agent.search = mock_search

    # Patch MCPSystem generator to avoid real API calls
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
    agent.mcp_system.llm_code_generator = mock_gen

    async def run():
        result = await agent.process_task("echo this text")
        assert result["success"]
        assert "success" in result["result"]["status"]
    asyncio.run(run())
