from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import json
import os

from dotenv import load_dotenv
from fastmcp import Context, FastMCP
import requests

load_dotenv()

BASE_URL: str = os.getenv("BASE_URL", "https://app.quickchat.ai")
SCENARIO_ID_TO_CONV_ID: dict[str, str] = {}

SCENARIO_ID: str = os.getenv("SCENARIO_ID")
if SCENARIO_ID is None:
    raise ValueError("Please provide SCENARIO_ID.")
API_KEY: str = os.getenv("API_KEY")

CHAT_ENDPOINT = f"{BASE_URL}/v1/api/mcp/chat"
SETTINGS_ENDPOINT = f"{BASE_URL}/v1/api/mcp/settings"


def fetch_mcp_settings(scenario_id: str, api_key: str | None = None) -> tuple[str | None, str | None, str | None]:
    response = requests.get(
        url=SETTINGS_ENDPOINT,
        headers={"scenario-id": scenario_id, "X-API-Key": api_key},
    )

    if response.status_code != 200:
        raise ValueError(
            "Configuration error. Please check your API key and scenario ID."
        )

    data = json.loads(response.content)

    try:
        mcp_active, mcp_name, mcp_command, mcp_description = (
            data["active"],
            data["name"],
            data["command"],
            data["description"],
        )
    except KeyError:
        raise ValueError("Configuration error")

    if not mcp_active:
        raise ValueError("Quickchat MCP not active.")

    if any(not len(x) > 0 for x in (mcp_name, mcp_description)):
        raise ValueError("MCP name and description cannot be empty.")

    return mcp_name, mcp_command, mcp_description


@dataclass
class AppContext:
    scenario_to_conv_id: dict[str, str] = field(default_factory=dict)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext(scenario_to_conv_id=SCENARIO_ID_TO_CONV_ID)


async def send_message(
    message: str, context: Context, scenario_id: str, api_key: str | None = None
) -> str:
    mcp_client_name = context.request_context.session.client_params.clientInfo.name

    response = requests.post(
        url=CHAT_ENDPOINT,
        headers={"scenario-id": scenario_id, "X-API-Key": api_key},
        json={
            "conv_id": context.request_context.lifespan_context.scenario_to_conv_id.get(
                scenario_id
            ),
            "text": message,
            "mcp_client_name": mcp_client_name,
        },
    )

    if response.status_code == 401:
        await context.request_context.session.send_log_message(
            level="error",
            data="Unauthorized access. Double-check your scenario_id and api_key.",
        )
        raise ValueError("Configuration error.")
    elif response.status_code != 200:
        await context.request_context.session.send_log_message(
            level="error", data=f"Server error: {response.content}"
        )
        raise ValueError("Server error. Please try again.")
    else:
        data = json.loads(response.content)

        if (
            context.request_context.lifespan_context.scenario_to_conv_id.get(
                scenario_id
            )
            is None
        ):
            context.request_context.lifespan_context.scenario_to_conv_id[
                scenario_id
            ] = data["conv_id"]

        return data["reply"]


async def send_message_with_default_values(
    message: str, context: Context
) -> str:
    return await send_message(
        message=message,
        context=context,
        scenario_id=SCENARIO_ID,
        api_key=API_KEY
    )
