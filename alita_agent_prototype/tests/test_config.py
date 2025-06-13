def test_config_import():
    from alita_agent.config.settings import AlitaConfig

    config = AlitaConfig()
    assert config.workspace_dir == "workspace"


def test_llm_client_config():
    from alita_agent.config.settings import AlitaConfig
    from alita_agent.utils.llm_client import LLMClient

    config = AlitaConfig()
    llm = LLMClient(config)
    assert llm.provider in {"openai", "gemini"}
    assert isinstance(llm.model, str)


def test_sdk_env_vars(monkeypatch):
    monkeypatch.setenv("AUTH_TOKEN", "token")
    monkeypatch.setenv("PROJECT_ID", "1")
    monkeypatch.setenv("INTEGRATION_UID", "uid")
    from alita_agent.config.settings import AlitaConfig

    config = AlitaConfig()
    assert config.auth_token == "token"
    assert config.project_id == "1"
    assert config.integration_uid == "uid"
