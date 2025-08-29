from fastmcp import Context, FastMCP

from src.lifespan_helpers import (
    get_conv_id_from_fastmcp_context,
    get_mcp_jwt_token_from_fastmcp_context,
    set_conv_id,
)
from src.requests import send_message
from src.schemas import MCPSettingsSchema, SendMessageResponse


def create_send_message_tool_for_scenario_id(
    scenario_id: str,
    fastmcp: FastMCP,
    mcp_settings: MCPSettingsSchema,
) -> None:
    send_message_tool_name = mcp_settings.mcp_command or "send_message"
    send_message_tool_description = mcp_settings.mcp_description

    @fastmcp.tool(
        name=send_message_tool_name, description=send_message_tool_description
    )
    async def send_message_for_scenario_id(message: str, context: Context) -> str:
        conv_id = get_conv_id_from_fastmcp_context(context)
        mcp_jwt_token = get_mcp_jwt_token_from_fastmcp_context(context)

        send_message_response: SendMessageResponse = await send_message(
            message=message,
            context=context,
            scenario_id=scenario_id,
            conv_id=conv_id,
            mcp_jwt_token=mcp_jwt_token,
        )
        set_conv_id(fastmcp_context=context, conv_id=send_message_response.conv_id)
        return send_message_response.reply
