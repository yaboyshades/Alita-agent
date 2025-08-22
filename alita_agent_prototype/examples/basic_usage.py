#!/usr/bin/env python3
"""
Basic usage example for the Alita Agent Framework.
This script demonstrates the core loop of dynamic tool creation and execution.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alita_agent import ManagerAgent  # noqa: E402
from alita_agent.config.settings import AlitaConfig  # noqa: E402


async def main():
    """Main example function."""
    print("🚀 Alita Agent Framework - Basic Usage Example 🚀")
    print("=" * 50)

    # 1. Initialize configuration from .env file
    config = AlitaConfig()
    print("✅ Configuration loaded.")

    # 2. Initialize the Manager Agent
    manager = ManagerAgent(config)
    print("🤖 Alita Manager Agent is online.")

    # 3. Define a task for the agent
    # This task will trigger the creation of a new tool if it doesn't exist.
    task_query = "Create a tool to reverse a given string"
    print(f"\n▶️  Processing task: '{task_query}'")

    try:
        # 4. Process the task
        result = await manager.process_task(task_query)

        # 5. Display the result
        print("\n--- Task Result ---")
        if result.get("success"):
            print("✅ Success!")
            print("📦 Result Payload:")
            import json

            print(json.dumps(result.get("result"), indent=2))
        else:
            print("❌ Failure!")
            print(f"Error: {result.get('error')}")
        print("-------------------\n")

    except Exception as e:
        print(f"\n💥 An unexpected error occurred during the demonstration: {e}")

    print(
        "🎉 Basic usage example completed. Check the 'workspace/tools' directory for any new tools created."
    )


if __name__ == "__main__":
    asyncio.run(main())
