
"""The MCP System: Handles dynamic tool creation, validation, and execution."""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging
from ..exceptions import ToolCreationError
from .web_agent import WebAgent
from ..utils.security import SandboxExecutor

class MCPSystem:
    """Manages the lifecycle of Model Context Protocols (Tools)."""
    def __init__(self, config: AlitaConfig, web_agent: WebAgent):
        self.config = config
        self.logger = setup_logging("MCPSystem")
        self.web_agent = web_agent
        self.tools_dir = self.config.get_workspace_path("tools")
        self.sandbox = SandboxExecutor(config)
        # NOTE: This would eventually call a real LLM API
        self.llm_code_generator = self._mock_llm_code_generation

    async def create_tool(self, name: str, task_description: str) -> None:
        self.logger.info(f"Initiating creation for tool: '{name}'")
        
        search_query = f"Simple Python script for '{task_description}'"
        search_results = await self.web_agent.search(search_query)
        
        # Use a placeholder for context, as web search is also mocked for now
        context_str = "Context: No external context available in this prototype."
        if search_results and search_results.results:
            context_str = json.dumps(search_results.results[0], indent=2)

        code = self.llm_code_generator(name, task_description, context_str)
        
        if await self.sandbox.validate_code(code):
            self._save_tool_to_disk(name, code, task_description)
            self.logger.info(f"Tool '{name}' created and saved successfully.")
        else:
            raise ToolCreationError(f"Generated code for '{name}' failed syntax validation.")

    def _mock_llm_code_generation(self, name: str, description: str, context: str) -> str:
        self.logger.warning(f"Using MOCK code generation for tool '{name}'")
        return f'''
#!/usr/bin/env python3
import sys
import json

def execute(params: dict):
    """
    Generated Tool: {name}
    Description: {description}
    Context used for generation:
    {context}
    """
    # print(f"Executing MOCK tool '{name}' with parameters: {{params}}")
    
    # MOCK IMPLEMENTATION: A real tool would perform the actual task.
    # This one just acknowledges the request and returns a success message.
    result_data = {{
        "status": "success",
        "message": f"Tool '{name}' executed successfully with mock logic.",
        "received_params": params
    }}
    return result_data

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line
    # It reads parameters from stdin and prints the result to stdout
    if not sys.stdin.isatty():
        input_params = json.load(sys.stdin)
        result = execute(input_params)
        print(json.dumps(result, indent=2))
    else:
        print("This script should be run with JSON input via stdin.")

'''

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
