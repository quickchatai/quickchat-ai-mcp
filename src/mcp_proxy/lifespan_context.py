from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from fastmcp import FastMCP


@dataclass
class MCPSettings:
    mcp_name: str
    mcp_command: str
    mcp_description: str


@dataclass
class MCPConfiguration:
    jwt_token: str
    settings: MCPSettings


@dataclass
class ProxyContext:
    mcp_configuration_by_session_id: dict[str, MCPConfiguration | None] = field(default_factory=dict)


MCP_CONFIGURATION_BY_SESSION_ID: dict[str, MCPConfiguration | None] = {}


@asynccontextmanager
async def proxy_lifespan_context(server: FastMCP) -> AsyncIterator[ProxyContext]:
    yield ProxyContext(
        mcp_configuration_by_session_id=MCP_CONFIGURATION_BY_SESSION_ID
    )
