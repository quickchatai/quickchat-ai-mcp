import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from mcp.server import FastMCP

from src import ai_actions, conversations, imports, knowledge_base
from src.chat import app_lifespan, fetch_mcp_settings, register_chat_tool
from src.client import QuickchatClient

load_dotenv()

API_TOKEN: str = os.getenv("API_TOKEN")

if API_TOKEN is None:
    raise ValueError("Please provide API_TOKEN.")

BASE_URL: str = os.getenv("BASE_URL", "https://app.quickchat.ai")
TRANSPORT: str = os.getenv("TRANSPORT", "stdio")

client = QuickchatClient(api_token=API_TOKEN, base_url=BASE_URL)

mcp_name, mcp_command, chat_description = fetch_mcp_settings(client)

if TRANSPORT == "streamable-http":
    from mcp.server.auth.settings import AuthSettings

    from src.auth import PresenceTokenVerifier

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    mcp = FastMCP(
        mcp_name,
        lifespan=app_lifespan,
        host=HOST,
        port=PORT,
        auth=AuthSettings(
            issuer_url="https://app.quickchat.ai",
            resource_server_url=None,
        ),
        token_verifier=PresenceTokenVerifier(),
    )
else:
    mcp = FastMCP(mcp_name, lifespan=app_lifespan)

register_chat_tool(mcp, client, mcp_command, chat_description)
knowledge_base.register_tools(mcp, client)
conversations.register_tools(mcp, client)
ai_actions.register_tools(mcp, client)
imports.register_tools(mcp, client)


def run():
    print("Starting Quickchat mcp server")
    mcp.run(transport=TRANSPORT)
