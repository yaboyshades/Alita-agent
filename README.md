# Alita Agent

This repository contains the prototype of the Alita agent framework. The working code lives inside the `alita_agent_prototype` directory.

## Quick Start

1. Install dependencies and set up a virtual environment:

```bash
python alita_agent_prototype/install.py
```

2. Activate the environment and run an example:

```bash
# On Linux/macOS
source alita_agent_prototype/.venv/bin/activate

# Run the basic example
python alita_agent

Alternatively you can `cd alita_agent_prototype` and run `python install.py` followed by `python examples/basic_usage.py` from inside that directory.
=======
Alternatively you can `cd alita_agent_prototype` and run `python install.py` followed by `python examples/basic_usage.py` 

For full documentation and advanced usage, see [alita_agent_prototype/README.md](alita_agent_prototype/README.md).

# Alita Agent Framework

A minimalist dual-agent architecture that enables autonomous tool creation and self-evolution through symbolic learning and dynamic planning.

The Python sources and tests live in the `alita_agent_prototype` directory.
## 🚀 Features

- **Self-Evolving Architecture**: Creates and optimizes tools autonomously based on task needs.
- **Dual-Agent Design**: A `ManagerAgent` for orchestration and a `WebAgent` for research.
- **Dynamic Tool Creation**: Uses a Model Context Protocol (MCP) system to generate, test, and save new capabilities on-the-fly.
- **Security-First**: Includes provisions for code validation and sandboxed execution to run generated tools safely.

## 📋 Requirements

- Python 3.10 or higher
- Docker (for secure sandboxed code execution)
- API keys for an LLM provider (OpenAI or Gemini)

## ⚡ Quick Start

### 1. Setup Environment

First, create a virtual environment and install the required dependencies using the provided script.

```bash
# This script creates a .venv, installs packages, and creates a .env file
python install.py
```

### 2. Configure API Keys

Edit the `.env` file that was created in the root directory and add your API keys. If you
skip this step, the first time you run any example the system will prompt for the missing
provider, model, and key and persist them to `.env` for future runs.

```bash
# .env file
OPENAI_API_KEY="your_openai_key_here"
GEMINI_API_KEY="your_gemini_key_here"
LLM_PROVIDER="gemini"
LLM_MODEL="gemini-pro"
AUTH_TOKEN="your_auth_token"
PROJECT_ID="your_project_id"
INTEGRATION_UID="your_integration_uid"
```

### 3. Run the Examples

Activate the virtual environment and run the example scripts to see Alita in action.

```bash
# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Run the basic example to see a simple task processed
python examples/basic_usage.py

# Run the advanced demo to see learning and tool creation over time
python examples/advanced_demo.py

# Launch the GUI chat interface
python examples/gui_chat.py

# Launch the Streamlit demo for the Alita SDK
streamlit run alita_local.py

# List your Alita applications using the SDK
python examples/alita_sdk_demo.py
```

Task results are logged in `workspace/memory/episodic.json` for future reference.

## 🏗️ Architecture

The framework is built on a modular design:

- **Manager Agent**: The central orchestrator. It analyzes tasks, plans execution, and triggers tool creation.
- **Web Agent**: Gathers information from the internet, including searching for code on GitHub.
- **MCP System**: The factory for tools. It generates, tests (in a sandbox), and manages the lifecycle of tools.
- **Memory System**: A hierarchical memory to store experiences (episodic), general knowledge (semantic), and successful action sequences (procedural).
- **Planning System**: A hybrid planner that uses ReAct-style reasoning to generate and evaluate potential action plans.

## 🧪 Testing

To run the test suite, use `pytest`:



For full documentation and advanced usage, see [alita_agent_prototype/README.md](alita_agent_prototype/README.md).

## 📚 Additional Documentation

The `docs/` directory contains extended guides on architecture, setup, and usage examples. Start with [docs/overview.md](docs/overview.md) for a high-level look at the project.
For Alita Platform integration, see [docs/alita_sdk.md](docs/alita_sdk.md).
