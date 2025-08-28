from fastmcp import Context, FastMCP
from fastmcp.tools import Tool
from src.consts import SEND_MESSAGE_DEFAULT_TOOL_NAME
from src.mcp_server.lifespan_context import (
    get_conv_id_from_fastmcp_context,
    set_conv_id,
)
from src.requests import send_message
from src.schemas import MCPSettingsSchema
from src.utils import get_tools_for_scenario_id


def _get_send_message_tool_name_from_mcp_command(
    mcp_command: str,
    scenario_id: str,
) -> str:
    send_message_tool_name = SEND_MESSAGE_DEFAULT_TOOL_NAME
    if mcp_command:
        send_message_tool_name = mcp_command
    send_message_tool_name += f"__{scenario_id}"
    return send_message_tool_name


async def create_send_message_tool_for_scenario_id(
    scenario_id: str,
    mcp_settings: MCPSettingsSchema,
    mcp_jwt_token: str,
    fastmcp: FastMCP,
) -> Tool:
    try:
        send_message_tools: list[Tool] = await get_tools_for_scenario_id(
            scenario_id=scenario_id,
            fastmcp=fastmcp
        )
    except Exception as e:
        print(f"Error when gett tools for scenario_id: {scenario_id}")
        raise e

    if len(send_message_tools) > 0:
        print(f"Send_message tools found for scenario_id: {scenario_id}")
        raise ValueError("Send_message tools found")

    async def send_message_for_scenario_id(
        message: str, context: Context
    ) -> str:
        conv_id = get_conv_id_from_fastmcp_context(context)
        reply, new_conv_id = await send_message(
            message=message,
            context=context,
            scenario_id=scenario_id,
            conv_id=conv_id,
            mcp_jwt_token=mcp_jwt_token
        )
        set_conv_id(context=context, conv_id=conv_id)
        return reply

    send_message_tool_name = _get_send_message_tool_name_from_mcp_command(
        mcp_command=mcp_settings.mcp_command,
        scenario_id=scenario_id
    )
    send_message_for_scenario_id.__name__ = send_message_tool_name

    return fastmcp.tool(
        send_message_for_scenario_id,
        name=send_message_for_scenario_id.__name__,
        description=mcp_settings.mcp_description,
        tags={scenario_id},
    )


async def update_send_message_tool_for_scenario_id(
    scenario_id: str,
    mcp_settings: MCPSettingsSchema,
    fastmcp: FastMCP,
) -> Tool:
    send_message_tools: list[Tool] = await get_tools_for_scenario_id(
        scenario_id=scenario_id,
        fastmcp=fastmcp
    )

    if len(send_message_tools) == 0:
        print(f"No send_message tool found for scenario_id: {scenario_id}")
        raise ValueError("No send_message tool found")

    if len(send_message_tools) > 1:
        print(f"Multiple send_message tools found for scenario_id: {scenario_id}")
        raise ValueError("Multiple send_message tools found")

    send_message_tool: Tool = send_message_tools[0]

    expected_send_message_tool_name = _get_send_message_tool_name_from_mcp_command(
        mcp_command=mcp_settings.mcp_command,
        scenario_id=scenario_id,
    )
    if send_message_tool.name != expected_send_message_tool_name:
        print("Send message tool name changed, updating")
        send_message_tool.name = expected_send_message_tool_name

    if send_message_tool.description != mcp_settings.mcp_description:
        print("Send message tool description changed, updating")
        send_message_tool.description = mcp_settings.mcp_description

    return send_message_tool
