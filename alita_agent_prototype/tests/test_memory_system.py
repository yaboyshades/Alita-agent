import asyncio
from alita_agent.config.settings import AlitaConfig
from alita_agent.core.memory import HierarchicalMemorySystem


def test_memory_persistence(tmp_path):
    config = AlitaConfig()
    config.workspace_dir = str(tmp_path)
    memory = HierarchicalMemorySystem(config)

    async def run():
        await memory.store_episode({"query": "test", "result": "ok"})
        stats = await memory.get_memory_stats()
        assert stats["episodic_episodes"] == 1
        # Reload and ensure persistence
        new_mem = HierarchicalMemorySystem(config)
        stats2 = await new_mem.get_memory_stats()
        assert stats2["episodic_episodes"] == 1
    asyncio.run(run())
