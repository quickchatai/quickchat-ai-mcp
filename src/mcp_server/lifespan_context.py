from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastmcp import Context, FastMCP

from src.mcp_server.lifespan_schemas import AppContext
from src.utils import get_session_id_and_lifespan_context_from_fastmcp_context

CONV_ID_BY_SESSION_ID: dict[str, str] = {}
SCENARIO_IDS_WITH_TOOL: set[str] = set()


@asynccontextmanager
async def app_lifespan_context(server: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext(
        conv_id_by_session_id=CONV_ID_BY_SESSION_ID,
        scenario_ids_with_tool=SCENARIO_IDS_WITH_TOOL,
    )


def set_conv_id(context: Context, conv_id: str):
    session_id, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(context)
    if session_id in lifespan_context.conv_id_by_session_id:
        return

    print(f"Setting conv_id in lifespan_context for session_id: {session_id}")
    lifespan_context.conv_id_by_session_id[session_id] = conv_id
    return


def get_conv_id_from_fastmcp_context(fastmcp_context: Context) -> str | None:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return lifespan_context.conv_id_by_session_id.get(session_id)
