"""Persistent hierarchical memory system.

This module implements a very small persistent memory store used by the
``ManagerAgent`` to keep track of past task executions.  Episodes are stored as
JSON lines on disk so they survive across runs and can be inspected easily.

The implementation is intentionally lightweight but fully functional.
"""
from __future__ import annotations

import json
from typing import Dict, Any, List
from pathlib import Path

from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging

class HierarchicalMemorySystem:
    """Simple persistent episodic memory."""

    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("HierarchicalMemorySystem")

        self.memory_dir = self.config.get_workspace_path("memory")
        self.episodes_file = self.memory_dir / "episodic.jsonl"

        self.episodic_memory: List[Dict[str, Any]] = []
        self._load_from_disk()
        self.logger.info("Memory System initialized.")

    async def store_episode(self, experience: Dict[str, Any]):
        """Persist a task experience to memory."""
        self.logger.info(
            f"Storing experience for task: {experience.get('query', 'unknown')}"
        )
        self.episodic_memory.append(experience)
        self._append_to_disk(experience)

        if len(self.episodic_memory) > self.config.memory.get("max_episodes", 1000):
            self.episodic_memory.pop(0)
            self._rewrite_disk()

    async def get_memory_stats(self) -> Dict[str, int]:
        return {"episodic_episodes": len(self.episodic_memory)}

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _load_from_disk(self) -> None:
        if not self.episodes_file.exists():
            return
        try:
            for line in self.episodes_file.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    self.episodic_memory.append(json.loads(line))
                except json.JSONDecodeError:
                    self.logger.warning("Skipping malformed memory line")
        except Exception as e:
            self.logger.error(f"Failed loading memory: {e}")

    def _append_to_disk(self, experience: Dict[str, Any]) -> None:
        try:
            with self.episodes_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(experience) + "\n")
        except Exception as e:
            self.logger.error(f"Failed writing memory: {e}")

    def _rewrite_disk(self) -> None:
        try:
            with self.episodes_file.open("w", encoding="utf-8") as f:
                for ep in self.episodic_memory:
                    f.write(json.dumps(ep) + "\n")
        except Exception as e:
            self.logger.error(f"Failed rewriting memory: {e}")
