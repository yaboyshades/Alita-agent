#!/usr/bin/env python3
"""
Demonstration script showing the Alita Agent working end-to-end.
This bypasses LLM API calls to show the framework functionality.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alita_agent import ManagerAgent  # noqa: E402
from alita_agent.config.settings import AlitaConfig  # noqa: E402
from alita_agent.core.web_agent import SearchResult  # noqa: E402


async def demo_framework():
    """Demonstrate the Alita framework working end-to-end."""
    print("🚀 Alita Agent Framework - Working Demo 🚀")
    print("=" * 50)

    # 1. Initialize configuration
    config = AlitaConfig()
    print("✅ Configuration loaded.")

    # 2. Initialize the Manager Agent
    manager = ManagerAgent(config)
    print("🤖 Alita Manager Agent is online.")

    # 3. Mock external dependencies for demo
    async def mock_search(query):
        return SearchResult(
            query=query,
            results=[
                {
                    "title": "Python String Reversal",
                    "snippet": "Simple string reversal in Python",
                }
            ],
        )

    manager.mcp_system.web_agent.search = mock_search

    # 4. Mock LLM code generation for demo
    async def mock_code_generator(name, desc, ctx):
        return f"""#!/usr/bin/env python3
import sys
import json

def execute(params: dict):
    \"\"\"
    Generated Tool: {name}
    Description: {desc}
    \"\"\"
    # Demo implementation for string reversal
    if 'text' in params:
        reversed_text = params['text'][::-1]
        return {{
            'status': 'success',
            'original': params['text'],
            'reversed': reversed_text,
            'tool_name': '{name}'
        }}
    else:
        return {{
            'status': 'success',
            'message': f'Tool {name} executed successfully',
            'received_params': params
        }}

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

    manager.mcp_system.llm_code_generator = mock_code_generator

    # 5. Process a sample task
    task_query = "Create a tool to reverse a given string"
    print(f"\n▶️  Processing task: '{task_query}'")

    try:
        result = await manager.process_task(task_query)

        print("\n--- Task Result ---")
        if result.get("success"):
            print("✅ Success!")
            print("📦 Tool Creation Result:")
            import json

            print(json.dumps(result.get("result"), indent=2))
        else:
            print("❌ Failure!")
            print(f"Error: {result.get('error')}")
        print("-------------------")

        # 6. Test the created tool with actual input
        print("\n▶️  Testing the created tool with sample input...")
        tool_name = manager._generate_tool_name_from_query(task_query)
        test_result = await manager.mcp_system.execute_tool(
            tool_name, {"text": "Hello World"}
        )

        if test_result.success:
            print("✅ Tool execution successful!")
            print("📦 Tool Execution Result:")
            print(json.dumps(test_result.result, indent=2))
        else:
            print("❌ Tool execution failed!")
            print(f"Error: {test_result.error}")

    except Exception as e:
        print(f"\n💥 An error occurred: {e}")

    # 7. Show memory stats
    memory_stats = await manager.memory.get_memory_stats()
    print(f"\n📊 Memory Stats: {memory_stats}")

    # 8. Check workspace
    tools_dir = config.get_workspace_path("tools")
    print(f"\n📁 Created tools in: {tools_dir}")
    if tools_dir.exists():
        tool_files = list(tools_dir.glob("*.py"))
        print(f"   Found {len(tool_files)} tool files:")
        for tool_file in tool_files:
            print(f"   - {tool_file.name}")

    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(demo_framework())
