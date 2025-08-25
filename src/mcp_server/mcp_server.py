import os

from fastmcp import FastMCP

from src.mcp_server.lifespan_context import app_lifespan_context
from src.mcp_server.middleware import ListToolsMiddleware, SetupMiddleware

PORT: int = int(os.getenv("PORT", "8080"))

mcp = FastMCP(lifespan=app_lifespan_context)
mcp.add_middleware(ListToolsMiddleware())
mcp.add_middleware(SetupMiddleware())
