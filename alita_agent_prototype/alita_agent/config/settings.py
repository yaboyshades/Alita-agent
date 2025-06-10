"""Configuration settings for the Alita Agent Framework."""
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
import sys
from dotenv import load_dotenv, set_key

# Load environment variables from a .env file
load_dotenv()

@dataclass
class AlitaConfig:
    """Main configuration class for the Alita Agent Framework."""

    # API Configuration
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv('OPENAI_API_KEY'))
    gemini_api_key: Optional[str] = field(default_factory=lambda: os.getenv('GEMINI_API_KEY'))
    llm_provider: Optional[str] = field(default_factory=lambda: os.getenv('LLM_PROVIDER', 'openai'))
    llm_model: Optional[str] = field(default_factory=lambda: os.getenv('LLM_MODEL', 'gpt-4'))

    # Workspace Configuration
    workspace_dir: str = "workspace"

    # Core System Settings
    memory: Dict[str, Any] = field(default_factory=dict)
    planning: Dict[str, Any] = field(default_factory=dict)
    mcp: Dict[str, Any] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set default nested configurations after initialization."""
        self.memory.setdefault('max_episodes', 1000)
        self.planning.setdefault('max_react_steps', 10)
        self.mcp.setdefault('execution_timeout', 60)
        self.security.setdefault('sandbox_enabled', True)
        self.security.setdefault('allowed_imports', ['json', 'aiohttp', 'math', 'random'])
        self.security.setdefault('use_docker', True)
        self._ensure_credentials()

    def get_workspace_path(self, sub_dir: str) -> Path:
        """Returns the absolute path to a subdirectory in the workspace."""
        path = Path(self.workspace_dir).resolve() / sub_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _ensure_credentials(self) -> None:
        """Prompt the user for missing credentials and persist them."""
        if not sys.stdin or not sys.stdin.isatty() or os.environ.get("PYTEST_CURRENT_TEST"):
            return

        env_path = Path(__file__).resolve().parents[2] / ".env"
        changed = False

        if not self.llm_provider:
            self.llm_provider = input("LLM provider (openai/gemini): ").strip() or "openai"
            changed = True

        if self.llm_provider == "openai" and not self.openai_api_key:
            self.openai_api_key = input("Enter OpenAI API key: ").strip()
            changed = True
        elif self.llm_provider == "gemini" and not self.gemini_api_key:
            self.gemini_api_key = input("Enter Gemini API key: ").strip()
            changed = True

        if not self.llm_model:
            default_model = "gpt-4" if self.llm_provider == "openai" else "gemini-pro"
            self.llm_model = input(f"Model name [{default_model}]: ").strip() or default_model
            changed = True

        if changed:
            env_path.touch(exist_ok=True)
            set_key(str(env_path), "LLM_PROVIDER", self.llm_provider)
            set_key(str(env_path), "LLM_MODEL", self.llm_model)
            if self.llm_provider == "openai" and self.openai_api_key:
                set_key(str(env_path), "OPENAI_API_KEY", self.openai_api_key)
            if self.llm_provider == "gemini" and self.gemini_api_key:
                set_key(str(env_path), "GEMINI_API_KEY", self.gemini_api_key)
