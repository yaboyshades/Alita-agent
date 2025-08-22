"""
Alita Agent Framework - A Self-Evolving AI Agent System.
"""

__version__ = "0.1.0"
from .core.manager_agent import ManagerAgent
from .core.web_agent import WebAgent
from .core.memory import HierarchicalMemorySystem
from .core.planning import HybridPlanner
from .core.mcp_system import MCPSystem
from .core.tool_registry import ToolRegistry

__all__ = [
    "ManagerAgent",
    "WebAgent",
    "HierarchicalMemorySystem",
    "HybridPlanner",
    "MCPSystem",
    "ToolRegistry",
]
