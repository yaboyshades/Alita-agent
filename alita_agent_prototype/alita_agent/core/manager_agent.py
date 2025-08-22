"""The Manager Agent: Central orchestrator for the Alita Framework."""

from typing import Dict, Any
from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging
from .web_agent import WebAgent
from .mcp_system import MCPSystem
from .memory import HierarchicalMemorySystem
from .planning import HybridPlanner
from .tool_registry import ToolRegistry
from ..exceptions import ToolCreationError, ToolExecutionError
from ..utils.llm_client import LLMClient


class ManagerAgent:
    """Orchestrates task processing, planning, and tool creation."""

    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("ManagerAgent")
        self.web_agent = WebAgent(config)
        self.tool_registry = ToolRegistry(
            self.config.get_workspace_path("tools")
        )
        self.mcp_system = MCPSystem(config, self.web_agent, self.tool_registry)
        self.memory = HierarchicalMemorySystem(config)
        self.planner = HybridPlanner(config)
        self.llm = LLMClient(config)
        self.logger.info("Manager Agent initialized.")

    async def process_task(self, user_query: str) -> Dict[str, Any]:
        self.logger.info(f"Received task: '{user_query}'")
        try:
            await self.planner.plan(user_query, [])
            # 1. Determine the name and description of the required tool
            existing = self.tool_registry.find_tool_by_description(user_query)
            if existing:
                tool_name = existing
                tool_description = self.tool_registry.tools[existing]
                self.logger.info(f"Found existing tool by description: '{tool_name}'")
            else:
                tool_name = self._generate_tool_name_from_query(user_query)
                tool_description = f"A tool that can: {user_query}"
                if not await self.mcp_system.tool_exists(tool_name):
                    self.logger.info(
                        f"Tool '{tool_name}' not found. Initiating creation..."
                    )
                    await self.mcp_system.create_tool(
                        name=tool_name,
                        task_description=tool_description,
                    )
                else:
                    self.logger.info(f"Found existing tool: '{tool_name}'")

            # 3. Execute the tool. For this prototype, we'll pass the user query as the main parameter.
            self.logger.info(f"Executing tool '{tool_name}'...")
            execution_result = await self.mcp_system.execute_tool(
                tool_name, parameters={"task_query": user_query}
            )

            if not execution_result.success:
                raise ToolExecutionError(
                    f"Tool execution failed: {execution_result.error}"
                )

            self.logger.info("Task processed successfully.")
            await self.memory.store_episode(
                {
                    "query": user_query,
                    "tool": tool_name,
                    "result": execution_result.result,
                }
            )
            return {"success": True, "result": execution_result.result}

        except (ToolCreationError, ToolExecutionError) as e:
            self.logger.error(f"Task processing failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred in the manager: {e}", exc_info=True
            )
            return {"success": False, "error": f"An unexpected error occurred: {e}"}

    def _generate_tool_name_from_query(self, query: str) -> str:
        """Generates a simple, deterministic tool name from a query."""
        import re

        sanitized = re.sub(r"[^a-zA-Z0-9\s]", "", query).title().replace(" ", "")
        return f"{sanitized[:50]}Tool"  # Limit name length
