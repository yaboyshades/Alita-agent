#!/usr/bin/env python3
"""Command line interface for the Alita Agent Framework."""

import argparse
import asyncio
import json
from typing import Optional

from .config.settings import AlitaConfig
from .core.manager_agent import ManagerAgent


async def _run_task(task: str, config: Optional[AlitaConfig] = None) -> dict:
    """Process a single task with the ManagerAgent."""
    cfg = config or AlitaConfig()
    agent = ManagerAgent(cfg)
    return await agent.process_task(task)


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point for the ``alita-agent`` command."""
    parser = argparse.ArgumentParser(description="Run tasks with the Alita Agent")
    parser.add_argument(
        "task",
        nargs="?",
        help="Task for the agent to process. Leave empty for interactive mode.",
    )
    args = parser.parse_args(argv)

    async def run_and_print(task: str) -> None:
        result = await _run_task(task)
        print(json.dumps(result, indent=2))

    if args.task:
        asyncio.run(run_and_print(args.task))
    else:
        try:
            while True:
                try:
                    task = input("alita> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not task:
                    continue
                if task.lower() in {"exit", "quit"}:
                    break
                asyncio.run(run_and_print(task))
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
