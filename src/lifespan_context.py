from contextlib import asynccontextmanager
import json
from typing import AsyncIterator

from fastmcp import Context, FastMCP
import httpx

from src.consts import SETTINGS_ENDPOINT
from src.helpers import (
    get_jwt_token_from_fastmcp_context,
    get_scenario_id_from_fastmcp_context,
    get_session_id_and_lifespan_context_from_fastmcp_context,
)
from src.lifespan_schemas import AppContext, MCPSettings

CONV_ID_BY_SESSION_ID: dict[str, str] = {}
JWT_TOKEN_BY_SESSION_ID: dict[str, str | None] = {}
SCENARIO_IDS_WITH_TOOL: set[str] = set()


@asynccontextmanager
async def app_lifespan_context(server: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext(
        conv_id_by_session_id=CONV_ID_BY_SESSION_ID,
        jwt_token_by_session_id=JWT_TOKEN_BY_SESSION_ID,
        scenario_ids_with_tool=SCENARIO_IDS_WITH_TOOL,
    )


def set_conv_id(context: Context, conv_id: str):
    session_id, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(context)
    if session_id in lifespan_context.conv_id_by_session_id:
        return

    print(f"Setting conv_id in lifespan_context for session_id: {session_id}")
    lifespan_context.conv_id_by_session_id[session_id] = conv_id
    return


async def get_mcp_settings(fastmcp_context: Context) -> MCPSettings:
    scenario_id = get_scenario_id_from_fastmcp_context(fastmcp_context)
    if scenario_id is None:
        print("Invalid scenario_id")
        raise ValueError("Invalid scenario_id")

    jwt_token = get_jwt_token_from_fastmcp_context(fastmcp_context)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=SETTINGS_ENDPOINT,
            headers={"scenario-id": scenario_id, "Authorization": f"Bearer {jwt_token}"},
        )

    if response.status_code != 200:
        print(f"Configuration error. Please check your API key and scenario ID, status_code: {response.status_code}")
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
        print("Configuration error")
        raise ValueError("Configuration error")

    if not mcp_active:
        print("Quickchat MCP not active.")
        raise ValueError("Quickchat MCP not active.")

    if any(not len(x) > 0 for x in (mcp_name, mcp_description)):
        print("MCP name and description cannot be empty.")
        raise ValueError("MCP name and description cannot be empty.")

    mcp_settings = MCPSettings(
        mcp_name=mcp_name,
        mcp_command=mcp_command,
        mcp_description=mcp_description,
    )
    return mcp_settings
