import os
import pytest

from alita_agent.config.settings import AlitaConfig
from alita_agent.utils.llm_client import LLMClient


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
async def test_llm_client_gemini_generates_text():
    config = AlitaConfig(
        llm_provider="gemini",
        gemini_api_key=os.environ.get("GEMINI_API_KEY"),
        llm_model="gemini-pro",
    )
    client = LLMClient(config)
    response = await client.generate("Say hello")
    assert isinstance(response, str)
    assert response
