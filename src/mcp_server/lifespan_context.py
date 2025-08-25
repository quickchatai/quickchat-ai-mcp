from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ClientError

from src.mcp_server.lifespan_schemas import AppContext, MCPSettings
from src.requests import fetch_mcp_settings_for_scenario_id, generate_mcp_jwt_token
from src.schemas import MCPSettingsSchema
from src.utils import (
    get_bearer_token,
    get_scenario_id,
    get_scenario_id_from_jwt_token,
    get_session_id_and_lifespan_context_from_fastmcp_context,
)

MCP_JWT_TOKEN_BY_SESSION_ID: dict[str, str] = {}
MCP_SETTINGS_BY_SESSION_ID: dict[str, MCPSettings] = {}
CONV_ID_BY_SESSION_ID: dict[str, str] = {}
SCENARIO_IDS_WITH_TOOL: set[str] = set()


@asynccontextmanager
async def app_lifespan_context(server: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext(
        mcp_jwt_token_by_session_id=MCP_JWT_TOKEN_BY_SESSION_ID,
        mcp_settings_by_session_id=MCP_SETTINGS_BY_SESSION_ID,
        conv_id_by_session_id=CONV_ID_BY_SESSION_ID,
        scenario_ids_with_tool=SCENARIO_IDS_WITH_TOOL,
    )


def set_conv_id_for_session(context: Context, conv_id: str):
    session_id, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(context)
    if session_id in lifespan_context.conv_id_by_session_id:
        return

    print(f"Setting conv_id in lifespan_context for session_id: {session_id}")
    lifespan_context.conv_id_by_session_id[session_id] = conv_id
    return


def get_conv_id_from_fastmcp_context(fastmcp_context: Context) -> str | None:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return lifespan_context.conv_id_by_session_id.get(session_id)


async def set_mcp_jwt_token() -> str:
    auth_bearer_header: str | None = get_bearer_token()
    scenario_id = get_scenario_id()

    try:
        mcp_jwt_token = await generate_mcp_jwt_token(scenario_id=scenario_id, jwt_token=auth_bearer_header)
    except ClientError as e:
        print(f"Error while validating token, scenario_id: {scenario_id}, jwt_token: {auth_bearer_header}")
        raise e

    scenario_id = get_scenario_id()
    token_scenario_id = get_scenario_id_from_jwt_token(mcp_jwt_token)

    if scenario_id != token_scenario_id:
        print(
            f"Scenario id mismatch, aborting, request_scenario_id: {scenario_id}, token_scenario_id: {token_scenario_id}")
        raise ClientError(
            "Configuration error. Please check your MCP token and scenario ID"
        )
    print("MCP JWT token successful")
    return mcp_jwt_token


def get_mcp_jwt_token_from_fastmcp_context(fastmcp_context: Context) -> str | None:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return lifespan_context.mcp_jwt_token_by_session_id.get(session_id)


async def set_mcp_settings(
    scenario_id: str | None = None,
    mcp_jwt_token: str | None = None,
) -> MCPSettings:
    print("Loading MCP Settings")
    if scenario_id is None:
        scenario_id = get_scenario_id()
    if mcp_jwt_token is None:
        mcp_jwt_token = await set_mcp_jwt_token()

    try:
        mcp_settings: MCPSettingsSchema = await fetch_mcp_settings_for_scenario_id(
            scenario_id=scenario_id,
            mcp_jwt_token=mcp_jwt_token
        )
    except Exception as e:
        print(f"Loading MCP Settings failed: {e}")
        raise ClientError(
            "Configuration error. Please check your MCP token and scenario ID"
        )
    return MCPSettings(
        mcp_name=mcp_settings.mcp_name,
        mcp_command=mcp_settings.mcp_command,
        mcp_description=mcp_settings.mcp_description,
    )


def get_mcp_settings_from_fastmcp_context(fastmcp_context: Context) -> MCPSettings | None:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return lifespan_context.mcp_settings_by_session_id.get(session_id)
