import os
import sys

from src.auth_and_setup import MCPTokenVerifier
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastmcp import FastMCP

from src.server import (
    app_lifespan,
    fetch_jwt_public_key,
    send_message_with_context_values,
)

PORT: int = int(os.getenv("PORT", "8080"))

jwt_public_key = fetch_jwt_public_key()
# mcp_name, mcp_command, send_message_tool_description = fetch_mcp_settings(
#     SCENARIO_ID, API_KEY
# )

mcp = FastMCP(lifespan=app_lifespan, auth=MCPTokenVerifier(public_key=jwt_public_key))

# if mcp_command:
#     send_message_with_context_values.__name__ = mcp_command
# else:
send_message_with_context_values.__name__ = "send_message"

# Register tools by hand
mcp.tool(
    send_message_with_context_values,
    name=send_message_with_context_values.__name__,
    # description=send_message_tool_description,
    
)
# mcp.add_middleware(LoadSessionState())


def run():
    print("Starting Quickchat mcp server")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=PORT,
    )
