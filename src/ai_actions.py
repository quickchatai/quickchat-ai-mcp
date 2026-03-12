from mcp.server.fastmcp import FastMCP

from src.client import QuickchatClient

ACTIONS_BASE = "/v1/api/ai_actions"


def register_tools(mcp: FastMCP, client: QuickchatClient) -> None:
    @mcp.tool(
        name="create_ai_action",
        description="Create a new Knowledge Base AI Action.",
    )
    async def create_ai_action(action: dict) -> dict:
        return client.post(f"{ACTIONS_BASE}/knowledge_base", json=action)

    @mcp.tool(
        name="get_ai_action",
        description="Get a Knowledge Base AI Action by ID.",
    )
    async def get_ai_action(action_id: str) -> dict:
        return client.get(f"{ACTIONS_BASE}/{action_id}/knowledge_base")

    @mcp.tool(
        name="update_ai_action",
        description="Update a Knowledge Base AI Action.",
    )
    async def update_ai_action(action_id: str, action: dict) -> dict:
        return client.put(f"{ACTIONS_BASE}/{action_id}/knowledge_base", json=action)
