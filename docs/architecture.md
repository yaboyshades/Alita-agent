# Architecture

Alita Agent is organized around a small set of cooperating modules:

- **ManagerAgent** – Orchestrates tasks, selects or creates tools, and drives the overall ReAct loop.
- **WebAgent** – Performs internet searches and GitHub lookups to gather reference material for new tools.
- **MCP System** – Generates, tests, and registers tools in a sandboxed environment.
- **Memory System** – Persists episodic experiences and tool metadata in the workspace.
- **Planner** – Uses ReAct-style reasoning to evaluate and select actions during a task.

The ManagerAgent interacts with these components to continuously expand the agent's capabilities. Generated tools live inside the `workspace/tools` directory and can be called in future tasks.
