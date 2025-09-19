import os

from fastmcp import Context
import httpx
from pydantic import ValidationError

import requests
from src.consts import (
    CHAT_ENDPOINT,
    GENERATE_MCP_TOKEN_ENDPOINT,
    MCP_SETTINGS_ENDPOINT,
    MCP_STATUS_ENDPOINT,
    SEND_MESSAGE_TIMEOUT_SECONDS,
)
from src.errors import RemoteMcpConnectionError
from src.lifespan_helpers import register_session_id_with_failed_validation
from src.schemas import MCPSettingsSchema, MCPStatus, SendMessageResponse
from src.utils import get_bearer_token

SCENARIO_ID: str = os.getenv("SCENARIO_ID")
if SCENARIO_ID is None:
    raise ValueError("Please provide SCENARIO_ID.")

def fetch_mcp_status(
    scenario_id: str
) -> MCPStatus:
    response = requests.get(
        url=MCP_STATUS_ENDPOINT,
        headers={"scenario-id": scenario_id},
    )

    if response.status_code != 200:
        print(
            f"Fetch mcp status failed, status_code: {response.status_code}, url: {MCP_STATUS_ENDPOINT}"
        )
        raise RemoteMcpConnectionError()

    try:
        mcp_status = MCPStatus.model_validate(response.json())
    except (ValidationError, ValueError) as e:
        print(f"MCP Status validation error: {e}")
        raise RemoteMcpConnectionError()

    print(f"MCP Status fetch successful, url: {MCP_STATUS_ENDPOINT}")
    return mcp_status


def fetch_mcp_settings(
    scenario_id: str, token: str | None = None
) -> MCPSettingsSchema:
    response = requests.get(
        url=MCP_SETTINGS_ENDPOINT,
        headers={"scenario-id": scenario_id, "Authorization": f"Bearer {token}"},
    )

    if response.status_code != 200:
        print(
            f"Fetch mcp settings failed, status_code: {response.status_code}, url: {MCP_SETTINGS_ENDPOINT}"
        )
        raise ValueError(
            "Configuration error. Please check your auth token and scenario."
        )

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
    fastmcp_context: Context,
    scenario_id: str | None = None,
    jwt_token: str | None = None,
) -> str:
    if jwt_token is None:
        try:
            jwt_token = get_bearer_token()
        except Exception as e:
            print(f"Getting jwt token from headers failed: {e}")

    headers = {"scenario-id": SCENARIO_ID}
    if jwt_token:
        headers["authorization"] = f"Bearer {jwt_token}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=GENERATE_MCP_TOKEN_ENDPOINT,
            headers=headers,
        )

    if response.status_code == 401:
        print("Invalid auth token provided, marking session_id as invalid")
        register_session_id_with_failed_validation(fastmcp_context=fastmcp_context)
        raise RemoteMcpConnectionError()

    if response.status_code != 200:
        print(
            f"MCP Server token generation failed, scenario_id: {scenario_id}, status_code: {response.status_code}"
        )
        raise RemoteMcpConnectionError()

    try:
        token = response.json()["token"]
    except KeyError:
        print("Generate MCP JWT Token failed: invalid response json, marking session_id as invalid")
        register_session_id_with_failed_validation(fastmcp_context=fastmcp_context)
        raise RemoteMcpConnectionError()
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
        print(f"Unauthorized access. Double-check your scenario_id and auth token, scenario_id: {scenario_id}, auth token: {mcp_jwt_token}, session_id: {context.session_id}")
        raise ValueError("Configuration error.")
    elif response.status_code != 200:
        print(f"Server error: {response.content}")
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
