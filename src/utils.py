from fastmcp import Context, FastMCP
from fastmcp.exceptions import ClientError
from fastmcp.server.dependencies import get_http_headers, get_http_request
from fastmcp.tools import Tool
import jwt
from mcp.shared.context import LifespanContextT
from pydantic import ValidationError

from src.consts import SCENARIO_ID_PATH_PARAM_NAME
from src.mcp_server.lifespan_schemas import AppContext
from src.schemas import MCPSettingsSchema


def get_scenario_id() -> str:
    return get_http_request().path_params[SCENARIO_ID_PATH_PARAM_NAME]


def get_scenario_id_from_jwt_token(token: str) -> str:
    scenario_id = jwt.get_unverified_header(token).get("scenario_id")
    if scenario_id is None:
        raise ValueError("Invalid mcp token, no scenario_id found")
    return scenario_id


def get_bearer_token() -> str | None:
    headers = get_http_headers()
    auth_bearer_header = next(
        (headers.get(key) for key in headers if key.lower() == "authorization"),
        None,
    )

    token = None
    if auth_bearer_header is not None:
        token = auth_bearer_header[7:]  # Remove "Bearer " prefix
    return token


def get_session_id_and_lifespan_context_from_fastmcp_context(
        fastmcp_context: Context
) -> tuple[str, LifespanContextT]:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return session_id, lifespan_context


async def get_tools_for_scenario_id(scenario_id: str, fastmcp: FastMCP) -> list[Tool]:
    tools_by_name = await fastmcp.get_tools()
    send_message_tools: list[Tool] = [
        tool
        for tool in list(tools_by_name.values())
        if scenario_id in tool.tags
    ]
    return send_message_tools


def get_mcp_settings_from_headers() -> MCPSettingsSchema:
    expected_header_names = {"mcp_name", "mcp_command", "mcp_description"}
    request_headers = get_http_headers()
    request_header_names = set(request_headers.keys())
    if not request_header_names.issuperset(expected_header_names):
        print(
            f"Auth failed: request header names don't contain all expected header names, request_header_names: {request_header_names}, expected_header_names: {expected_header_names}")
        raise ClientError(
            "Configuration error. Please check your MCP token and scenario ID"
        )

    try:
        mcp_settings = MCPSettingsSchema.model_validate(request_headers)
    except ValidationError as e:
        print(f"MCP Settings validation failed: {e}")
        raise e

    return mcp_settings
