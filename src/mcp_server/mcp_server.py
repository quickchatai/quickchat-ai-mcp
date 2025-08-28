import os

from fastmcp import FastMCP
from fastmcp.server.auth import JWTVerifier

from src.mcp_server.lifespan_context import app_lifespan_context
from src.mcp_server.middleware import ListToolsMiddleware
from src.requests import fetch_jwt_public_key

IS_MCP_PUBLIC: bool = bool(os.getenv("IS_MCP_PUBLIC", "False") == "True")
PORT: int = int(os.getenv("PORT", "8080"))

if IS_MCP_PUBLIC:
    mcp = FastMCP(lifespan=app_lifespan_context)
else:
    jwt_public_key = fetch_jwt_public_key()
    mcp = FastMCP(lifespan=app_lifespan_context, auth=JWTVerifier(public_key=jwt_public_key))

mcp.add_middleware(ListToolsMiddleware())
