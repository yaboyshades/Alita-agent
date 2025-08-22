def test_web_agent_search_async():
    import asyncio
    from unittest.mock import patch
    from alita_agent.config.settings import AlitaConfig
    from alita_agent.core.web_agent import WebAgent

    config = AlitaConfig()
    agent = WebAgent(config)

    mock_json = {
        "RelatedTopics": [{"Text": "Example Result", "FirstURL": "http://example.com"}]
    }

    class MockResponse:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def json(self):
            return mock_json

    class MockSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        def get(self, *args, **kwargs):
            return MockResponse()

    async def run():
        with patch("aiohttp.ClientSession", return_value=MockSession()):
            result = await agent.search("example")
        assert result.query == "example"
        assert result.results[0]["url"] == "http://example.com"

    asyncio.run(run())
