from alita_agent.core.manager_agent import ManagerAgent
from alita_agent.config.settings import AlitaConfig
import asyncio


async def main():
    config = AlitaConfig()
    agent = ManagerAgent(config)
    # Simulate a sequence of tasks
    tasks = [
        "Create a tool to validate email addresses",
        "Create a tool to summarize text",
        "Create a tool to fetch data from an API",
    ]
    for task in tasks:
        result = await agent.process_task(task)
        print(f"Task: {task}\nResult: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())
