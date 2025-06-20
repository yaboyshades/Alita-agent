
"""The MCP System: Handles dynamic tool creation, validation, and execution."""
import json
from typing import Dict, Any
from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging
from ..exceptions import ToolCreationError
from .web_agent import WebAgent
from ..utils.security import SandboxExecutor
from ..utils.llm_client import LLMClient

class MCPSystem:
    """Manages the lifecycle of Model Context Protocols (Tools)."""
    def __init__(self, config: AlitaConfig, web_agent: WebAgent):
        self.config = config
        self.logger = setup_logging("MCPSystem")
        self.web_agent = web_agent
        self.tools_dir = self.config.get_workspace_path("tools")
        self.sandbox = SandboxExecutor(config)
        self.llm = LLMClient(config)
        # Default to using the real LLM for code generation
        self.llm_code_generator = self._generate_tool_code

    async def create_tool(self, name: str, task_description: str) -> None:
        self.logger.info(f"Initiating creation for tool: '{name}'")
        
        search_query = f"Simple Python script for '{task_description}'"
        search_results = await self.web_agent.search(search_query)
        
        # Use a placeholder for context, as web search is also mocked for now
        context_str = "Context: No external context available in this prototype."
        if search_results and search_results.results:
            context_str = json.dumps(search_results.results[0], indent=2)

        code = await self.llm_code_generator(name, task_description, context_str)
        
        if await self.sandbox.validate_code(code):
            self._save_tool_to_disk(name, code, task_description)
            self.logger.info(f"Tool '{name}' created and saved successfully.")
        else:
            raise ToolCreationError(f"Generated code for '{name}' failed syntax validation.")

    async def _generate_tool_code(self, name: str, description: str, context: str) -> str:
        """Generate tool code using the configured LLM provider."""
        prompt = (
            "You are ToolsmithAI. Generate a self-contained Python script that "
            "defines a function 'execute(params: dict)' to accomplish the "
            f"following task: {description}.\nUse this context if helpful:\n{context}\n"
            "Return only the code without markdown."
        )
        return await self.llm.generate(prompt)


    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]):
        tool_path = self.tools_dir / f"{tool_name}.py"
        if not tool_path.exists():
            raise ToolCreationError(f"Tool '{tool_name}' not found at {tool_path}")
        
        code = tool_path.read_text()
        return await self.sandbox.execute_code(code, parameters)
        
    def _save_tool_to_disk(self, name: str, code: str, description: str):
        (self.tools_dir / f"{name}.py").write_text(code)
        metadata = {"name": name, "description": description}
        (self.tools_dir / f"{name}.meta.json").write_text(json.dumps(metadata, indent=2))

    async def tool_exists(self, tool_name: str) -> bool:
        return (self.tools_dir / f"{tool_name}.meta.json").exists()
