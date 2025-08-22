"""Tool Registry: persists and retrieves MCP tools."""

from __future__ import annotations

import json
import difflib
from pathlib import Path
from typing import Dict, Optional

from ..utils.logging import setup_logging


class ToolRegistry:
    """Manages stored tools and supports simple similarity search."""

    def __init__(self, tools_dir: Path):
        self.logger = setup_logging("ToolRegistry")
        self.tools_dir = Path(tools_dir)
        self.tools: Dict[str, str] = {}
        self._load_tools()

    def _load_tools(self) -> None:
        """Load existing tools from disk."""
        if not self.tools_dir.exists():
            return
        for meta_file in self.tools_dir.glob("*.meta.json"):
            try:
                data = json.loads(meta_file.read_text())
                name = data.get("name")
                desc = data.get("description", "")
                if name:
                    self.tools[name] = desc
            except Exception as e:
                self.logger.warning(f"Failed to load {meta_file}: {e}")

    def register_tool(self, name: str, description: str) -> None:
        """Register a newly created tool."""
        self.logger.info(f"Registering tool '{name}'")
        self.tools[name] = description

    def tool_exists(self, name: str) -> bool:
        return name in self.tools

    def find_tool_by_description(self, description: str) -> Optional[str]:
        """Return the name of the most similar tool by description."""
        if not self.tools:
            return None
        best_name = None
        best_score = 0.0
        for name, desc in self.tools.items():
            score = difflib.SequenceMatcher(None, desc, description).ratio()
            if score > best_score:
                best_score = score
                best_name = name
        return best_name if best_score > 0.6 else None
