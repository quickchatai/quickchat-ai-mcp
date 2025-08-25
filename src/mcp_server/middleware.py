from typing import Any

from fastmcp.exceptions import ClientError
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import Tool

from src.mcp_server.lifespan_context import (
    get_mcp_settings_from_fastmcp_context,
    set_mcp_jwt_token,
    set_mcp_settings, get_mcp_jwt_token_from_fastmcp_context,
)
from src.mcp_server.lifespan_schemas import AppContext, MCPSettings
from src.mcp_server.tools import (
    create_send_message_tool_for_scenario_id,
    update_send_message_tool_for_scenario_id,
)
from src.utils import (
    get_bearer_token,
    get_scenario_id,
    get_session_id_and_lifespan_context_from_fastmcp_context,
)


class ListToolsMiddleware(Middleware):
    async def on_list_tools(
        self,
        context: MiddlewareContext,
        call_next
    ) -> list[Tool]:
        tools = await call_next(context)
        tools = tools or []

        lifespan_context: AppContext
        _, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(
            fastmcp_context=context.fastmcp_context)

        scenario_id = get_scenario_id()
        tools = [tool for tool in tools if scenario_id in tool.tags]

        mcp_settings: MCPSettings = get_mcp_settings_from_fastmcp_context(fastmcp_context=context.fastmcp_context)
        mcp_jwt_token: str = get_mcp_jwt_token_from_fastmcp_context(fastmcp_context=context.fastmcp_context)
        if len(tools) == 0:
            print(f"No send_message_tool found for scenario_id: {scenario_id}, creating")
            lifespan_context.scenario_ids_with_tool.add(scenario_id)
            send_message_tool = await create_send_message_tool_for_scenario_id(
                scenario_id=scenario_id,
                mcp_settings=mcp_settings,
                mcp_jwt_token=mcp_jwt_token,
                fastmcp=context.fastmcp_context.fastmcp
            )
            print("Send_message_tool successfully created")
            tools = [send_message_tool]
        elif len(tools) == 1:
            send_message_tool = await update_send_message_tool_for_scenario_id(
                scenario_id=scenario_id,
                mcp_settings=mcp_settings,
                fastmcp=context.fastmcp_context.fastmcp
            )
            tools = [send_message_tool]
        else:
            print(f"Multiple send_message_tools found for scenario_id: {scenario_id}, creating")
            raise ClientError("Multiple send_message_tools found")

        return tools


class SetupMiddleware(Middleware):
    async def on_request(
        self,
        context: MiddlewareContext,
        call_next: CallNext,
    ) -> Any:
        session_id, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(
            fastmcp_context=context.fastmcp_context
        )

        if any([
            session_id not in lifespan_context.mcp_jwt_token_by_session_id,
            session_id not in lifespan_context.mcp_settings_by_session_id,
        ]):
            lifespan_context.mcp_jwt_token_by_session_id[session_id] = None
            lifespan_context.mcp_settings_by_session_id[session_id] = None

            mcp_jwt_token = await set_mcp_jwt_token()
            lifespan_context.mcp_jwt_token_by_session_id[session_id] = mcp_jwt_token

            mcp_settings: MCPSettings = await set_mcp_settings(
                mcp_jwt_token=mcp_jwt_token
            )
            lifespan_context.mcp_settings_by_session_id[session_id] = mcp_settings
        await call_next(context)
