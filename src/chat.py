from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

from src.client import QuickchatClient


@dataclass
class AppContext:
    conv_id: str | None


def fetch_mcp_settings(client: QuickchatClient) -> tuple[str, str, str]:
    """Fetch MCP settings from the Quickchat API.

    Returns (name, command, description).
    """
    data = client.get("/v1/api/mcp/settings")

    try:
        mcp_active, mcp_name, mcp_command, mcp_description = (
            data["active"],
            data["name"],
            data["command"],
            data["description"],
        )
    except KeyError:
        raise ValueError("Configuration error")

    if not mcp_active:
        raise ValueError("Quickchat MCP not active.")

    if any(not len(x) > 0 for x in (mcp_name, mcp_description)):
        raise ValueError("MCP name and description cannot be empty.")

    return mcp_name, mcp_command, mcp_description


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext(conv_id=None)


async def send_message(message: str, context: Context, client: QuickchatClient) -> str:
    """Send a message to the Quickchat AI agent and return its reply."""
    mcp_client_name = context.request_context.session.client_params.clientInfo.name

    data = client.post(
        "/v1/api/mcp/chat",
        json={
            "conv_id": context.request_context.lifespan_context.conv_id,
            "text": message,
            "mcp_client_name": mcp_client_name,
        },
    )

    if context.request_context.lifespan_context.conv_id is None:
        context.request_context.lifespan_context.conv_id = data["conv_id"]

    return data["reply"]


def register_chat_tool(
    mcp: FastMCP,
    client: QuickchatClient,
    command: str,
    description: str,
) -> None:
    """Register the chat tool with a dynamic name from MCP settings."""
    from functools import partial

    tool_fn = partial(send_message, client=client)
    tool_name = command if command else "send_message"
    tool_fn.__name__ = tool_name

    mcp.add_tool(fn=tool_fn, name=tool_name, description=description)
