from mcp.server.fastmcp import FastMCP

from src.client import QuickchatClient

CONV_BASE = "/v1/api_core/conversations"


def register_tools(mcp: FastMCP, client: QuickchatClient) -> None:
    @mcp.tool(
        name="list_conversations",
        description="List conversations. Optionally filter by page.",
    )
    async def list_conversations(
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict:
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        return client.get(CONV_BASE, params=params or None)

    @mcp.tool(
        name="get_conversation",
        description="Get a specific conversation by ID.",
    )
    async def get_conversation(conversation_id: str) -> dict:
        return client.get(f"{CONV_BASE}/{conversation_id}/")

    @mcp.tool(
        name="get_conversation_metadata",
        description="Get metadata for a conversation.",
    )
    async def get_conversation_metadata(conversation_id: str) -> dict:
        return client.get(f"{CONV_BASE}/{conversation_id}/metadata")

    @mcp.tool(
        name="set_conversation_metadata",
        description="Set metadata for a conversation.",
    )
    async def set_conversation_metadata(conversation_id: str, metadata: dict) -> dict:
        return client.post(f"{CONV_BASE}/{conversation_id}/metadata", json=metadata)
