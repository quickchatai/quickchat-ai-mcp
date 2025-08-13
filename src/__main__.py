from functools import partial
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server import FastMCP
from fastmcp import FastMCP as FastMCP2

from src.server import (
    app_lifespan,
    fetch_mcp_settings,
    send_message,
)

SCENARIO_ID: str = os.getenv("SCENARIO_ID")

if SCENARIO_ID is None:
    raise ValueError("Please provide SCENARIO_ID.")

API_KEY: str = os.getenv("API_KEY")

mcp_name, mcp_command, send_message_tool_description = fetch_mcp_settings(
    SCENARIO_ID, API_KEY
)

mcp = FastMCP(mcp_name, lifespan=app_lifespan)

send_message = partial(send_message, scenario_id=SCENARIO_ID, api_key=API_KEY)
if mcp_command:
    send_message.__name__ = mcp_command
else:
    send_message.__name__ = "send_message"

# Register tools by hand
mcp.add_tool(
    fn=send_message,
    name=send_message.__name__,
    description=send_message_tool_description,
)


def run():
    print("Starting Quickchat mcp server")
    # mcp.run()
    mcp_proxy = FastMCP2.as_proxy(mcp, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
    mcp_proxy.run(transport="streamable-http")
