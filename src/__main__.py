import os
import sys

from dotenv import load_dotenv
from fastmcp.server import FastMCP

from src.auth import QuickchatJWTVerifier
from src.lifespan_context import app_lifespan
from src.middleware import SetupMiddleware
from src.requests import fetch_jwt_public_key, fetch_mcp_settings
from src.schemas import MCPSettingsSchema
from src.tools import create_send_message_tool_for_scenario_id

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

SCENARIO_ID: str = os.getenv("SCENARIO_ID")
if SCENARIO_ID is None:
    raise ValueError("Please provide SCENARIO_ID.")
API_KEY: str = os.getenv("API_KEY")

jwt_public_key = fetch_jwt_public_key()
mcp_settings: MCPSettingsSchema = fetch_mcp_settings(SCENARIO_ID, API_KEY)
mcp = FastMCP(
    "FastMCP",
    lifespan=app_lifespan,
    auth=QuickchatJWTVerifier(public_key=jwt_public_key),
)

create_send_message_tool_for_scenario_id(
    scenario_id=SCENARIO_ID,
    fastmcp=mcp,
    mcp_settings=mcp_settings,
)
mcp.add_middleware(SetupMiddleware())


def run():
    print("Starting Quickchat mcp server")
    mcp.run(transport="streamable-http", host="127.0.0.1", port=43123, path="/my_mcp")
