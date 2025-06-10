def test_config_import():
    from alita_agent.config.settings import AlitaConfig
    config = AlitaConfig()
    assert config.workspace_dir == "workspace"

def test_llm_client_config():
    from alita_agent.config.settings import AlitaConfig
    from alita_agent.utils.llm_client import LLMClient
    config = AlitaConfig()
    llm = LLMClient(config)
    assert llm.provider in {"openai", "gemini", "deepseek"}
    assert isinstance(llm.model, str)
