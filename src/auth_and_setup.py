import json

from fastmcp.server.auth import AccessToken, JWTVerifier
import httpx

from src.consts import SETTINGS_ENDPOINT, VALIDATE_MCP_TOKEN_ENDPOINT
from src.helpers import get_scenario_id_from_jwt_token


async def validate_mcp_token(scenario_id: str, jwt_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=VALIDATE_MCP_TOKEN_ENDPOINT,
            headers={"scenario-id": scenario_id, "Authorization": f"Bearer {jwt_token}"},
        )

    if response.status_code != 200:
        raise ValueError(
            f"Configuration error. Please check your MCP token and scenario ID, status_code: {response.status_code}"
        )


async def fetch_mcp_settings(scenario_id: str, jwt_token: str) -> tuple[str | None, str | None, str | None]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=SETTINGS_ENDPOINT,
            headers={"scenario-id": scenario_id, "Authorization": f"Bearer {jwt_token}"},
        )

    if response.status_code != 200:
        raise ValueError(
            "Configuration error. Please check your API key and scenario ID."
        )

    data = json.loads(response.content)

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


class MCPTokenVerifier(JWTVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        scenario_id = get_scenario_id_from_jwt_token(token)
        await validate_mcp_token(
            scenario_id=scenario_id,
            jwt_token=token
        )
        return await super().verify_token(token)


    # async def load_access_token(self, token: str) -> AccessToken | None:
    #     print("Loading access token")
    #     access_token = await super().load_access_token(token)
    #
    #     scenario_id = get_scenario_id_from_jwt_token(token)
    #     mcp_name, mcp_command, send_message_tool_description = fetch_mcp_settings(
    #         scenario_id,
    #     )
