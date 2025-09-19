from fastmcp import Context, FastMCP

from src.lifespan_helpers import (
    get_mcp_jwt_token_from_fastmcp_context,
)
from src.requests import send_message
from src.schemas import MCPSettingsSchema, SendMessageResponse


def enhance_send_message_tool_description(
    mcp_description: str
) -> str:
    return f"""{mcp_description}
    
In response, you will receive reply and conv_id. If you wish to make further tool calls within the same 
'thread', please pass conv_id in the following requests."""

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
    async def send_message_for_scenario_id(message: str, context: Context, conv_id: str | None = None) -> SendMessageResponse:
        mcp_jwt_token = get_mcp_jwt_token_from_fastmcp_context(context)
        send_message_response: SendMessageResponse = await send_message(
            message=message,
            context=context,
            scenario_id=scenario_id,
            conv_id=conv_id,
            mcp_jwt_token=mcp_jwt_token,
        )
        print("Send message successful, returning")
        return send_message_response
