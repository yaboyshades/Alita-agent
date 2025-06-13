# Getting Started

Follow these steps to configure Alita Agent and run the example scripts.

## 1. Install Dependencies

```bash
python alita_agent_prototype/install.py
```

This script creates a virtual environment in `.venv`, installs all required packages, and writes a `.env` file if one does not exist.

## 2. Configure API Keys

Edit the generated `.env` file and add credentials for your preferred LLM provider:

```bash
OPENAI_API_KEY="your_openai_key_here"
GEMINI_API_KEY="your_gemini_key_here"
LLM_PROVIDER="gemini"
LLM_MODEL="gemini-pro"
```

If you omit these values, the system will prompt for them on first run and save them automatically.

## 3. Run Examples

Activate the environment and launch one of the example scripts:

```bash
source .venv/bin/activate
python examples/basic_usage.py
```

See `docs/examples.md` for more details about available demos.
