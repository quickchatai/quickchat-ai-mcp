from fastmcp import Context
from fastmcp.exceptions import ClientError
import httpx
from pydantic import ValidationError

import requests
from src.consts import (
    CHAT_ENDPOINT,
    GENERATE_MCP_TOKEN_ENDPOINT,
    JWT_PUBLIC_KEY_ENDPOINT,
    SEND_MESSAGE_TIMEOUT_SECONDS,
    SETTINGS_ENDPOINT,
)
from src.schemas import MCPSettingsSchema, SendMessageResponse
from src.utils import get_bearer_token, get_scenario_id_from_jwt_token


def fetch_jwt_public_key() -> str:
    print(JWT_PUBLIC_KEY_ENDPOINT)
    response = requests.get(url=JWT_PUBLIC_KEY_ENDPOINT)
    if response.status_code != 200:
        print(
            f"Configuration error. Please check your MCP token, status_code: {response.status_code}"
        )
        raise ValueError("Configuration error. Please check your MCP token")

    return response.json()["key"]


def fetch_mcp_settings(
    scenario_id: str, api_key: str | None = None
) -> MCPSettingsSchema:
    response = requests.get(
        url=SETTINGS_ENDPOINT,
        headers={"scenario-id": scenario_id, "X-API-Key": api_key},
    )

    if response.status_code != 200:
        print(
            f"Fetch mcp settings failed, status_code: {response.status_code}, response_json: {response.json()}"
        )
        raise ValueError(
            "Configuration error. Please check your API key and scenario ID."
        )

    if response.json()["active"] is False:
        print("Quickchat MCP not active.")
        raise ValueError("Quickchat MCP not active.")

    try:
        mcp_settings_response = MCPSettingsSchema.model_validate(
            {
                "mcp_name": response.json()["name"],
                "mcp_command": response.json()["command"],
                "mcp_description": response.json()["description"],
            }
        )
    except (ValidationError, ValueError) as e:
        print(f"MCP Settings validation error: {e}")
        raise ValueError(f"MCP Settings validation error: {e}")

    print("MCP Settings fetch successful")
    return mcp_settings_response


async def generate_mcp_jwt_token(
    scenario_id: str | None = None, jwt_token: str | None = None
) -> str:
    if jwt_token is None:
        jwt_token = get_bearer_token()
    if scenario_id is None:
        scenario_id = get_scenario_id_from_jwt_token(token=jwt_token)

    async with httpx.AsyncClient() as client:
        headers = {"scenario-id": scenario_id, "authorization": f"Bearer {jwt_token}"}
        response = await client.post(
            url=GENERATE_MCP_TOKEN_ENDPOINT,
            headers=headers,
        )

    if response.status_code != 200:
        print(
            f"Configuration error. Please check your MCP token and scenario ID, scenario_id: {scenario_id}, status_code: {response.status_code}"
        )
        raise ClientError(
            "Configuration error. Please check your MCP token and scenario ID"
        )

    try:
        token = response.json()["token"]
    except KeyError:
        print("Generate MCP JWT Token failed: invalid response json")
        raise ClientError(
            "Configuration error. Please check your MCP token and scenario ID"
        )
    return token


async def send_message(
    message: str,
    context: Context,
    scenario_id: str,
    conv_id: str | None,
    mcp_jwt_token: str
) -> SendMessageResponse:
    mcp_client_name = context.request_context.session.client_params.clientInfo.name

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=CHAT_ENDPOINT,
            headers={
                "scenario-id": scenario_id,
                "Authorization": f"Bearer {mcp_jwt_token}",
            },
            json={
                "conv_id": conv_id,
                "text": message,
                "mcp_client_name": mcp_client_name,
            },
            timeout=SEND_MESSAGE_TIMEOUT_SECONDS,
        )

    if response.status_code == 401:
        await context.request_context.session.send_log_message(
            level="error",
            data="Unauthorized access. Double-check your scenario_id and api_key.",
        )
        raise ValueError("Configuration error.")
    elif response.status_code != 200:
        await context.request_context.session.send_log_message(
            level="error", data=f"Server error: {response.content}"
        )
        raise ValueError("Server error. Please try again.")

    try:
        send_message_response = SendMessageResponse.model_validate(
            {
                "reply": response.json()["reply"],
                "conv_id": response.json()["conv_id"],
            }
        )
    except (ValidationError, ValueError) as e:
        print(f"MCP Settings validation error: {e}")
        raise ValueError(f"MCP Settings validation error: {e}")

    print("Send message successful")
    return send_message_response
