from fastmcp import Context, FastMCP
import jwt
from mcp.shared.context import LifespanContextT
from starlette.requests import Request

from src.consts import SCENARIO_ID_PATH_PARAM_NAME, SEND_MESSAGE_DEFAULT_TOOL_NAME
from src.lifespan_schemas import AppContext, MCPSettings


def get_scenario_id_from_jwt_token(token: str) -> str:
    scenario_id = jwt.get_unverified_header(token).get("scenario_id")
    if scenario_id is None:
        raise ValueError("Invalid mcp token, no scenario_id found")
    return scenario_id


def get_session_id_and_lifespan_context_from_fastmcp_context(fastmcp_context: Context) -> tuple[str, LifespanContextT]:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return session_id, lifespan_context


def get_scenario_id_from_fastmcp_context(fastmcp_context: Context) -> str | None:
    request: Request = fastmcp_context.request_context.request
    scenario_id = request.path_params.get(SCENARIO_ID_PATH_PARAM_NAME)
    return scenario_id


def get_conv_id_from_fastmcp_context(fastmcp_context: Context) -> str | None:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return lifespan_context.conv_id_by_session_id.get(session_id)


def get_jwt_token_from_fastmcp_context(fastmcp_context: Context) -> str | None:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return lifespan_context.jwt_token_by_session_id.get(session_id)


async def set_up_send_message_tool_for_scenario_id(context: Context, mcp_settings: MCPSettings):
    fastmcp: FastMCP = context.fastmcp
    tool = await fastmcp.get_tool(key=SEND_MESSAGE_DEFAULT_TOOL_NAME)
    tool.name = mcp_settings.mcp_command
    tool.description = mcp_settings.mcp_description
