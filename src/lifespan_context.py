from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()


@dataclass
class AppContext:
    mcp_jwt_token_by_session_id: dict[str, str] = field(default_factory=dict)
    conv_id_by_session_id: dict[str, str] = field(default_factory=dict)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext(
        mcp_jwt_token_by_session_id=MCP_JWT_TOKEN_BY_SESSION_ID,
        conv_id_by_session_id=CONV_ID_BY_SESSION_ID,
    )


CONV_ID_BY_SESSION_ID: dict[str, str] = {}
MCP_JWT_TOKEN_BY_SESSION_ID: dict[str, str] = {}
