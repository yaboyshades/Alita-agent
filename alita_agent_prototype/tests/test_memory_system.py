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


def test_memory_recent_episodes(tmp_path):
    config = AlitaConfig()
    config.workspace_dir = str(tmp_path)
    memory = HierarchicalMemorySystem(config)

    async def run():
        for i in range(6):
            await memory.store_episode({"query": f"q{i}", "result": "ok"})
        recent = await memory.get_recent_episodes(3)
        assert [e["query"] for e in recent] == ["q3", "q4", "q5"]

    asyncio.run(run())
