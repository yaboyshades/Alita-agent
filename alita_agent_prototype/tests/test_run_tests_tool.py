import sys
from pathlib import Path
from unittest.mock import patch
import importlib

# Ensure the repository root (where the cortex package lives) is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

execute = importlib.import_module("alita_agent.tools.run_tests_tool").execute


def test_execute_invokes_cortex_automation_with_default_path():
    """The tool should call PythonTestAutomation with the provided path."""
    with patch("alita_agent.tools.run_tests_tool.PythonTestAutomation") as mock_auto:
        instance = mock_auto.return_value
        instance.run_pytest_with_coverage.return_value = {"success": True}

        result = execute()

        instance.run_pytest_with_coverage.assert_called_once_with("tests/")
        assert result == {"success": True}


def test_execute_uses_custom_path_when_provided():
    with patch("alita_agent.tools.run_tests_tool.PythonTestAutomation") as mock_auto:
        instance = mock_auto.return_value
        instance.run_pytest_with_coverage.return_value = {"success": False}

        params = {"test_path": "pkg/tests"}
        result = execute(params)

        instance.run_pytest_with_coverage.assert_called_once_with("pkg/tests")
        assert result == {"success": False}
