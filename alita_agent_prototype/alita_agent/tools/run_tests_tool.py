"""Tool for executing pytest with coverage via Cortex automation."""

from __future__ import annotations

from typing import Any, Dict, Optional

from cortex.automation.python_tests import PythonTestAutomation


def execute(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run the project's test suite using Cortex's automation helpers.

    Parameters
    ----------
    params:
        Optional dictionary that may contain a ``test_path`` specifying
        which test directory to run. Defaults to ``"tests/"``.

    Returns
    -------
    Dict[str, Any]
        The result dictionary returned by ``PythonTestAutomation`` containing
        ``success`` and ``output`` keys, and possibly ``coverage`` or ``error``.
    """
    params = params or {}
    test_path = params.get("test_path", "tests/")
    return PythonTestAutomation().run_pytest_with_coverage(test_path)
