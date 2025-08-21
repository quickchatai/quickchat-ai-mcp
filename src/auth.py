from fastmcp import Context
from fastmcp.exceptions import ClientError
from fastmcp.server.auth import AccessToken, JWTVerifier
from fastmcp.server.dependencies import get_http_headers
import httpx

from src.consts import VALIDATE_MCP_TOKEN_ENDPOINT
from src.helpers import get_scenario_id_from_jwt_token


def get_bearer_token_from_context(fastmcp_context: Context) -> str | None:
    headers = get_http_headers()
    auth_bearer_header = next(
        (headers.get(key) for key in headers if key.lower() == "authorization"),
        None,
    )

    token = None
    if auth_bearer_header is not None:
        token = auth_bearer_header[7:]  # Remove "Bearer " prefix
    return token


async def validate_mcp_token(scenario_id: str, jwt_token: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=VALIDATE_MCP_TOKEN_ENDPOINT,
            json={
                "token": jwt_token,
            },
            headers={"scenario-id": scenario_id},
        )

    if response.status_code != 200:
        print(f"Configuration error. Please check your MCP token and scenario ID, scenario_id: {scenario_id}, status_code: {response.status_code}")
        raise ClientError(
            "Configuration error. Please check your MCP token and scenario ID"
        )

    return response.json()["token"]


class MCPTokenVerifier(JWTVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        scenario_id = get_scenario_id_from_jwt_token(token)
        await validate_mcp_token(
            scenario_id=scenario_id,
            jwt_token=token
        )
        access_token = await super().verify_token(token)
        return access_token
