# Using the Alita SDK

This project can integrate with the official **Alita SDK** to run agents on the Alita Platform. The SDK builds on top of Langchain and provides tools for authentication, project management, and a Streamlit-based chat interface.

## Installation

Install the SDK alongside this project using pip:

```bash
pip install alita-sdk
```

## Environment Configuration

Create a `.env` file with your platform credentials. The required variables are:

```
AUTH_TOKEN=<your_api_token>
PROJECT_ID=<your_project_id>
INTEGRATION_UID=<your_integration_uid>
```

These values allow the SDK to connect your agents to the Alita Platform.

## Streamlit Demo App

Once installed, you can launch the SDK's demo interface:

```bash
streamlit run alita_local.py
```

This web app lets you authenticate, manage agents, and chat with them directly through your browser.

## Example Script

An example integration is provided in `examples/alita_sdk_demo.py` which lists applications available to your project using `AlitaClient`.

For more details see the [Alita SDK on PyPI](https://pypi.org/project/alita-sdk/).
