import os
import sys

from fastmcp import FastMCP

from src.lifespan_context import app_lifespan_context
from src.middleware import (
    ListToolsMiddleware,
    SetupMiddleware,
)
from src.server import (
    fetch_jwt_public_key,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

IS_MCP_PUBLIC: bool = bool(os.getenv("IS_MCP_PUBLIC", "False") == "True")
PORT: int = int(os.getenv("PORT", "8080"))

if IS_MCP_PUBLIC:
    mcp = FastMCP(lifespan=app_lifespan_context)
else:
    jwt_public_key = fetch_jwt_public_key()
    mcp = FastMCP(lifespan=app_lifespan_context, auth=MCPTokenVerifier(public_key=jwt_public_key))

mcp.add_middleware(SetupMiddleware())
mcp.add_middleware(ListToolsMiddleware())

def run():
    print("Starting Quickchat mcp server")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=PORT,
        path="/mcp/{mcp_id}"
    )
