from typing import Any

from asgiref.sync import async_to_sync, sync_to_async
from fastmcp import Context
from fastmcp.exceptions import ClientError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools import Tool

from src.auth import get_bearer_token_from_context, validate_mcp_token
from src.consts import SEND_MESSAGE_DEFAULT_TOOL_NAME
from src.helpers import (
    get_jwt_token_from_fastmcp_context,
    get_scenario_id_from_fastmcp_context,
    get_session_id_and_lifespan_context_from_fastmcp_context,
)
from src.lifespan_context import get_mcp_settings
from src.lifespan_schemas import MCPSettings
from src.server import send_message


async def load_jwt_token(fastmcp_context: Context):
    session_id, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(
        fastmcp_context
    )
    if session_id in lifespan_context.jwt_token_by_session_id:
        return

    print("JWT Token not in lifespan_context, loading")
    lifespan_context.jwt_token_by_session_id[session_id] = None
    auth_bearer_header: str | None = get_bearer_token_from_context(fastmcp_context=fastmcp_context)
    scenario_id = get_scenario_id_from_fastmcp_context(fastmcp_context=fastmcp_context)
    try:
        validated_token = await validate_mcp_token(scenario_id=scenario_id, jwt_token=auth_bearer_header)
    except ClientError as e:
        print(f"Error while validating token, scenario_id: {scenario_id}, jwt_token: {auth_bearer_header}")
        raise e
    print("Validation request successful, saving new token")
    lifespan_context.jwt_token_by_session_id[session_id] = validated_token
    return


async def setup_tool(fastmcp_context: Context):
    # TODO: Add lock to avoid race conditions / double creation of tool for scenario_id
    scenario_id = get_scenario_id_from_fastmcp_context(fastmcp_context=fastmcp_context)
    session_id, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(
        fastmcp_context=fastmcp_context
    )
    if scenario_id in lifespan_context.scenario_ids_with_tool:
        return

    print("Scenario id not loaded, loading send_message for scenario_id")
    lifespan_context.scenario_ids_with_tool.add(scenario_id)
    mcp_settings: MCPSettings = await get_mcp_settings(fastmcp_context=fastmcp_context)
    print("MCP settings successfully fetched")

    scenario_id = get_scenario_id_from_fastmcp_context(fastmcp_context=fastmcp_context)
    if scenario_id is None:
        print("Scenario id not found")
        raise ValueError("Scenario id not found")
    jwt_token = get_jwt_token_from_fastmcp_context(fastmcp_context=fastmcp_context)

    # Create tool function based on scenario_id and jwt_token
    async def send_message_for_scenario_id(
            message: str, context: Context
    ) -> str:
        return await send_message(
            message=message,
            context=context,
            scenario_id=scenario_id,
            jwt_token=jwt_token
        )

    if mcp_settings.mcp_command:
        send_message_for_scenario_id.__name__ = mcp_settings.mcp_command
    else:
        send_message_for_scenario_id.__name__ = SEND_MESSAGE_DEFAULT_TOOL_NAME

    send_message_for_scenario_id.__name__ += f"__{scenario_id}"

    fastmcp_context.fastmcp.tool(
        send_message_for_scenario_id,
        name=send_message_for_scenario_id.__name__,
        description=mcp_settings.mcp_description,
        tags={scenario_id},
    )
    return


def setup_on_request(fastmcp_context: Context):  # Why? Without this setup_tool was executed while load_jwt_token was awaiting API response
    async_to_sync(load_jwt_token)(fastmcp_context)
    async_to_sync(setup_tool)(fastmcp_context)


class SetupMiddleware(Middleware):
    async def on_request(
        self,
        context: MiddlewareContext,
        call_next,
    ) -> Any:
        await sync_to_async(setup_on_request)(context.fastmcp_context)
        return await call_next(context)


class ListToolsMiddleware(Middleware):
    async def on_list_tools(
        self,
        context: MiddlewareContext,
        call_next
    ) -> list[Tool]:
        tools = await call_next(context)
        _, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(fastmcp_context=context.fastmcp_context)

        scenario_id = get_scenario_id_from_fastmcp_context(fastmcp_context=context.fastmcp_context)
        tools = [tool for tool in tools if scenario_id in tool.tags]
        return tools
