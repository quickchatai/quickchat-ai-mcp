from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import json
import os

from dotenv import load_dotenv
from fastmcp import Context, FastMCP
from fastmcp.server.auth import AccessToken
from fastmcp.server.dependencies import get_access_token
import httpx
import requests

from src.consts import (
    CHAT_ENDPOINT,
    JWT_PUBLIC_KEY_ENDPOINT,
    SEND_MESSAGE_TIMEOUT_SECONDS,
)
from src.helpers import get_scenario_id_from_jwt_token

load_dotenv()


SCENARIO_ID_TO_CONV_ID: dict[str, str] = {}

SCENARIO_ID: str = os.getenv("SCENARIO_ID")
if SCENARIO_ID is None:
    raise ValueError("Please provide SCENARIO_ID.")




def fetch_jwt_public_key() -> str:
    response = requests.get(url=JWT_PUBLIC_KEY_ENDPOINT)
    if response.status_code != 200:
        raise ValueError(
            "Configuration error. Please check your MCP token"
        )

    return response.json()["key"]


@dataclass
class AppContext:
    scenario_to_conv_id: dict[str, str] = field(default_factory=dict)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext(scenario_to_conv_id=SCENARIO_ID_TO_CONV_ID)


async def send_message(
    message: str, context: Context, scenario_id: str, jwt_token: str
) -> str:
    mcp_client_name = context.request_context.session.client_params.clientInfo.name

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=CHAT_ENDPOINT,
            headers={"scenario-id": scenario_id, "Authorization": f"Bearer {jwt_token}"},
            json={
                "conv_id": context.request_context.lifespan_context.scenario_to_conv_id.get(
                    scenario_id
                ),
                "text": message,
                "mcp_client_name": mcp_client_name,
            },
            timeout=SEND_MESSAGE_TIMEOUT_SECONDS
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


async def send_message_with_context_values(
    message: str, context: Context
) -> str:
    access_token: AccessToken | None = get_access_token()
    scenario_id = get_scenario_id_from_jwt_token(access_token.token)
    return await send_message(
        message=message,
        context=context,
        scenario_id=scenario_id,
        jwt_token=access_token.token
    )
