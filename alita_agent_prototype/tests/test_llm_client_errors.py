import builtins
import pytest

from alita_agent.config.settings import AlitaConfig
from alita_agent.utils.llm_client import LLMClient


@pytest.mark.asyncio
async def test_unknown_provider_raises_value_error():
    config = AlitaConfig()
    config.llm_provider = "unknown"
    client = LLMClient(config)
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        await client.generate("hello")


@pytest.mark.asyncio
async def test_missing_openai_package(monkeypatch):
    config = AlitaConfig()
    config.llm_provider = "openai"
    config.openai_api_key = "test-key"
    client = LLMClient(config)

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "openai":
            raise ModuleNotFoundError("No module named 'openai'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ValueError, match="openai package is required"):
        await client.generate("test")
