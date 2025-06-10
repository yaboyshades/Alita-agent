"""Configuration settings for the Alita Agent Framework."""
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

@dataclass
class AlitaConfig:
    """Main configuration class for the Alita Agent Framework."""

    # API Configuration
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv('OPENAI_API_KEY'))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv('ANTHROPIC_API_KEY'))
    gemini_api_key: Optional[str] = field(default_factory=lambda: os.getenv('GEMINI_API_KEY'))
    deepseek_api_key: Optional[str] = field(default_factory=lambda: os.getenv('DEEPSEEK_API_KEY'))
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
        self.security.setdefault('allowed_imports', ['json', 'requests', 'math', 'random'])

    def get_workspace_path(self, sub_dir: str) -> Path:
        """Returns the absolute path to a subdirectory in the workspace."""
        path = Path(self.workspace_dir).resolve() / sub_dir
        path.mkdir(parents=True, exist_ok=True)
        return path
