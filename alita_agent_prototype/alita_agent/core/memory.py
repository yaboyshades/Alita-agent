"""
Hierarchical Memory System (Placeholder)
A simplified in-memory store for this prototype.
"""

from typing import Dict, Any, List
from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging


class HierarchicalMemorySystem:
    """Simple persistent episodic memory stored on disk."""

    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("HierarchicalMemorySystem")
        memory_dir = self.config.get_workspace_path("memory")
        self.memory_file = memory_dir / "episodic.json"
        self.episodic_memory: List[Dict[str, Any]] = self._load_memory()
        self.logger.info("Memory System initialized.")

    async def store_episode(self, experience: Dict[str, Any]):
        """Stores a task experience."""
        self.logger.info(f"Storing experience for task: {experience.get('query')}")
        self.episodic_memory.append(experience)
        if len(self.episodic_memory) > self.config.memory.get("max_episodes", 100):
            self.episodic_memory.pop(0)  # Keep memory from growing indefinitely
        self._save_memory()

    async def get_memory_stats(self) -> Dict[str, int]:
        return {"episodic_episodes": len(self.episodic_memory)}

    def _load_memory(self) -> List[Dict[str, Any]]:
        if self.memory_file.exists():
            try:
                import json

                return json.loads(self.memory_file.read_text())
            except Exception:
                return []
        return []

    def _save_memory(self) -> None:
        import json

        self.memory_file.write_text(json.dumps(self.episodic_memory, indent=2))
