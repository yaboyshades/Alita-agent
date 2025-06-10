import asyncio

from alita_agent.config.settings import AlitaConfig
from alita_agent.core.memory import HierarchicalMemorySystem


def test_memory_persistence(tmp_path):
    config = AlitaConfig()
    config.workspace_dir = str(tmp_path / "ws")
    memory = HierarchicalMemorySystem(config)

    async def run():
        await memory.store_episode({"query": "hello", "result": "world"})
        stats = await memory.get_memory_stats()
        assert stats["episodic_episodes"] == 1

    asyncio.run(run())
