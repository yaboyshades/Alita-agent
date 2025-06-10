"""
Security utilities, including the sandboxed code executor.
WARNING: This is a simplified prototype. A production system requires a robust
containerization solution like Docker with strict resource and network limits.
"""
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
from ..config.settings import AlitaConfig
from ..utils.logging import setup_logging


class ToolExecutionResult(BaseModel):
    success: bool
    result: Any = None
    error: Optional[str] = None

class SandboxExecutor:
    """Execute generated Python code in an isolated environment."""
    def __init__(self, config: AlitaConfig):
        self.config = config
        self.logger = setup_logging("SandboxExecutor")
        # Ensure the venv python is used for sandboxing
        self.python_executable = str(Path(sys.executable))
        self.logger.debug(f"SandboxExecutor using python executable: {self.python_executable}")

    async def execute_code(self, code: str, parameters: Dict[str, Any]) -> ToolExecutionResult:
        """Runs code in a Docker container if available, otherwise subprocess."""
        self.logger.info("Executing code in sandbox...")
        
        # Use a temporary file to run the script
        temp_dir = self.config.get_workspace_path("temp_exec")
        script_path = temp_dir / "temp_tool.py"
        script_path.write_text(code)
        self.logger.debug(f"Writing tool code to: {script_path}")
        
        input_json = json.dumps(parameters)
        self.logger.debug(f"Input JSON: {input_json}")
        
        try:
            if self.config.security.get('use_docker', True) and self._docker_available():
                stdout, stderr, returncode = self._execute_with_docker(script_path, input_json)
            else:
                stdout, stderr, returncode = self._execute_subprocess(script_path, input_json)
            self.logger.debug(f"Sandbox stdout: {stdout}")
            self.logger.debug(f"Sandbox stderr: {stderr}")
            if returncode != 0:
                return ToolExecutionResult(success=False, result=None, error=stderr)

            try:
                parsed = json.loads(stdout)
                return ToolExecutionResult(success=True, result=parsed, error=None)
            except json.JSONDecodeError:
                self.logger.debug("Full stdout is not valid JSON, trying line-by-line.")
            result_lines = stdout.strip().split('\n')
            self.logger.debug(f"Result lines: {result_lines}")
            for idx, line in enumerate(result_lines):
                try:
                    parsed = json.loads(line)
                    self.logger.debug(f"Successfully parsed JSON from line {idx}: {parsed}")
                    return ToolExecutionResult(success=True, result=parsed, error=None)
                except json.JSONDecodeError:
                    self.logger.debug(f"Line {idx} is not valid JSON: {line}")
            return ToolExecutionResult(success=False, result=None, error="Failed to decode tool output as JSON. Full stdout: " + stdout)

        except subprocess.TimeoutExpired:
            return ToolExecutionResult(success=False, result=None, error="Execution timed out.")
        except json.JSONDecodeError:
            return ToolExecutionResult(success=False, result=None, error="Failed to decode tool output as JSON.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during sandbox execution: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def validate_code(self, code: str) -> bool:
        """
        Placeholder for static code analysis (e.g., using AST or bandit).
        For this prototype, it just checks for basic Python syntax.
        """
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    def _docker_available(self) -> bool:
        """Check if the docker CLI is available."""
        try:
            subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception:
            return False

    def _execute_with_docker(self, script_path: Path, input_json: str):
        """Run the code inside a Docker container."""
        cmd = [
            "docker", "run", "--rm", "--network", "none",
            "-v", f"{script_path.parent}:/app", "-w", "/app",
            "python:3.10-slim", "python", str(script_path.name)
        ]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=input_json, timeout=self.config.mcp['execution_timeout'])
        return stdout, stderr, process.returncode

    def _execute_subprocess(self, script_path: Path, input_json: str):
        """Run the code in a local subprocess (fallback)."""
        process = subprocess.Popen(
            [self.python_executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=input_json, timeout=self.config.mcp['execution_timeout'])
        return stdout, stderr, process.returncode
