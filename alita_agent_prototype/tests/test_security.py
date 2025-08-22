import asyncio
from alita_agent.config.settings import AlitaConfig
from alita_agent.utils.security import SandboxExecutor


def test_validate_code_disallows_import(tmp_path):
    config = AlitaConfig(workspace_dir=str(tmp_path))
    executor = SandboxExecutor(config)

    async def run():
        assert not await executor.validate_code("import os\nprint('hi')")

    asyncio.run(run())
