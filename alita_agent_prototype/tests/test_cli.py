import json
from alita_agent import cli
import pytest


@pytest.mark.asyncio
async def test_cli_run(monkeypatch, capsys):
    async def mock_process(self, task):
        return {"success": True, "result": {"echo": task}}

    monkeypatch.setattr(
        "alita_agent.core.manager_agent.ManagerAgent.process_task", mock_process
    )

    result = await cli._run_task("echo hello")
    print(json.dumps(result))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["result"]["echo"] == "echo hello"
