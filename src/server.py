import json

from dotenv import load_dotenv
from fastmcp import Context
import httpx
import requests

from src.consts import (
    CHAT_ENDPOINT,
    JWT_PUBLIC_KEY_ENDPOINT,
    SEND_MESSAGE_TIMEOUT_SECONDS,
)
from src.helpers import (
    get_conv_id_from_fastmcp_context,
)
from src.lifespan_context import set_conv_id

load_dotenv()



def fetch_jwt_public_key() -> str:
    response = requests.get(url=JWT_PUBLIC_KEY_ENDPOINT)
    if response.status_code != 200:
        print(f"Configuration error. Please check your MCP token, status_code: {response.status_code}")
        raise ValueError(
            "Configuration error. Please check your MCP token"
        )

    return response.json()["key"]


async def send_message(
    message: str, context: Context, scenario_id: str, jwt_token: str
) -> str:
    mcp_client_name = context.request_context.session.client_params.clientInfo.name

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=CHAT_ENDPOINT,
            headers={"scenario-id": scenario_id, "Authorization": f"Bearer {jwt_token}"},
            json={
                "conv_id": get_conv_id_from_fastmcp_context(context),
                "text": message,
                "mcp_client_name": mcp_client_name,
            },
            timeout=SEND_MESSAGE_TIMEOUT_SECONDS
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
    else:
        data = json.loads(response.content)
        set_conv_id(context=context, conv_id=data["conv_id"])

        return data["reply"]
