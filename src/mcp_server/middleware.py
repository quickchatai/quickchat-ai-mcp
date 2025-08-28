from typing import Any

from fastmcp.exceptions import ClientError
from fastmcp.server.middleware import Middleware, MiddlewareContext, CallNext
from fastmcp.tools import Tool

from src.mcp_server.lifespan_schemas import AppContext
from src.mcp_server.tools import (
    create_send_message_tool_for_scenario_id,
    update_send_message_tool_for_scenario_id,
)
from src.schemas import MCPSettingsSchema
from src.utils import (
    get_bearer_token,
    get_mcp_settings,
    get_scenario_id,
    get_session_id_and_lifespan_context_from_fastmcp_context, get_scenario_id_from_jwt_token,
)


class ListToolsMiddleware(Middleware):
    async def on_list_tools(
        self,
        context: MiddlewareContext,
        call_next
    ) -> list[Tool]:
        tools = await call_next(context)
        lifespan_context: AppContext
        _, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(
            fastmcp_context=context.fastmcp_context)

        scenario_id = get_scenario_id()
        tools = [tool for tool in tools if scenario_id in tool.tags]

        mcp_settings: MCPSettingsSchema = get_mcp_settings()
        mcp_jwt_token = get_bearer_token()

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


class ValidateScenarioIdMiddleware(Middleware):
    async def on_request(
        self,
        context: MiddlewareContext,
        call_next: CallNext,
    ) -> Any:
        request_scenario_id = get_scenario_id()
        mcp_jwt_token = get_bearer_token()
        token_scenario_id = get_scenario_id_from_jwt_token(mcp_jwt_token)

        if request_scenario_id != token_scenario_id:
            raise ClientError(

            )
