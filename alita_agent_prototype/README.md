# Alita Agent Framework

A minimalist dual-agent architecture that enables autonomous tool creation and self-evolution through symbolic learning and dynamic planning.

## 🚀 Features

- **Self-Evolving Architecture**: Creates and optimizes tools autonomously based on task needs.
- **Dual-Agent Design**: A `ManagerAgent` for orchestration and a `WebAgent` for research.
- **Dynamic Tool Creation**: Uses a Model Context Protocol (MCP) system to generate, test, and save new capabilities on-the-fly.
- **Security-First**: Includes provisions for code validation and sandboxed execution to run generated tools safely.

## 📋 Requirements

- Python 3.10 or higher
- Docker (for secure sandboxed code execution)
- API keys for an LLM provider (e.g., OpenAI, Anthropic)

## ⚡ Quick Start

### 1. Setup Environment

First, create a virtual environment and install the required dependencies using the provided script.

```bash
# This script creates a .venv, installs packages, and creates a .env file
python install.py
```


### 2. Configure API Keys

Edit the `.env` file that was created in the root directory and add your API keys.
If you don't provide them ahead of time, running an example will prompt for the
provider, model, and key and write them back to `.env`.

```bash
# .env file
OPENAI_API_KEY="your_openai_key_here"
GEMINI_API_KEY="your_gemini_key_here"
LLM_PROVIDER="openai|gemini"
LLM_MODEL="gpt-4|gemini-pro"
```
=======

### 2. Configure API Keys

Edit the `.env` file that was created in the root directory and add your API keys.
If you don't provide them ahead of time, running an example will prompt for the
provider, model, and key and write them back to `.env`.

```bash
# .env file
OPENAI_API_KEY="your_openai_key_here"
GEMINI_API_KEY="your_gemini_key_here"
LLM_PROVIDER="openai|gemini"
LLM_MODEL="gpt-4|gemini-pro"
```

### 2. Configure API Keys

Edit the `.env` file that was created in the root directory and add your API keys.

```bash
# .env file
OPENAI_API_KEY="your_openai_key_here"
GEMINI_API_KEY="your_gemini_key_here"

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
```

All task results are persisted to `workspace/memory/episodic.json`.

python examples/basic_usage.py

# Run the advanced demo to see learning and tool creation over time
python examples/advanced_demo.py

# Launch the GUI chat interface
python examples/gui_chat.py
```

All task results are persisted to `workspace/memory/episodic.json`.

python examples/basic_usage.py

# Run the advanced demo to see learning and tool creation over time
python examples/advanced_demo.py

# Launch the GUI chat interface
python examples/gui_chat.py
```



All task results are persisted to `workspace/memory/episodic.json`.

## 🏗️ Architecture

The framework is built on a modular design:

- **Manager Agent**: The central orchestrator. It analyzes tasks, plans execution, and triggers tool creation.
- **Web Agent**: Gathers information from the internet, including searching for code on GitHub.
- **MCP System**: The factory for tools. It generates, tests (in a sandbox), and manages the lifecycle of tools.
- **Memory System**: A hierarchical memory to store experiences (episodic), general knowledge (semantic), and successful action sequences (procedural).
- **Planning System**: A hybrid planner that uses ReAct-style reasoning to generate and evaluate potential action plans.

## 🧪 Testing

To run the test suite, use `pytest`:

```bash
pytest
```
