"""Demo of integrating the official Alita SDK."""

import asyncio
import os
from alita_sdk.clients.client import AlitaClient


async def main() -> None:
    base_url = os.environ.get("DEPLOYMENT_URL", "https://app.alita.ai")
    auth_token = os.environ.get("AUTH_TOKEN")
    project_id = os.environ.get("PROJECT_ID")
    if not (auth_token and project_id):
        print("Missing AUTH_TOKEN or PROJECT_ID environment variables")
        return

    client = AlitaClient(
        base_url=base_url, project_id=int(project_id), auth_token=auth_token
    )
    apps = client.get_list_of_apps()
    print("Available applications:")
    for app in apps:
        print(f"- {app['name']} (id={app['id']})")


if __name__ == "__main__":
    asyncio.run(main())
