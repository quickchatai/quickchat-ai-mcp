from fastmcp import Context

from src.lifespan_context import AppContext
from src.utils import get_session_id_and_lifespan_context_from_fastmcp_context


def set_conv_id(fastmcp_context: Context, conv_id: str):
    session_id, lifespan_context = (
        get_session_id_and_lifespan_context_from_fastmcp_context(fastmcp_context)
    )
    if session_id in lifespan_context.conv_id_by_session_id:
        return

    print(f"Setting conv_id in lifespan_context for session_id: {session_id}")
    lifespan_context.conv_id_by_session_id[session_id] = conv_id
    return


def get_conv_id_from_fastmcp_context(fastmcp_context: Context) -> str | None:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return lifespan_context.conv_id_by_session_id.get(session_id)


def set_mcp_jwt_token(fastmcp_context: Context, mcp_jwt_token: str):
    session_id, lifespan_context = (
        get_session_id_and_lifespan_context_from_fastmcp_context(fastmcp_context)
    )
    if mcp_jwt_token in lifespan_context.mcp_jwt_token_by_session_id:
        return

    print(f"Setting mcp_jwt_token in lifespan_context for session_id: {session_id}")
    lifespan_context.mcp_jwt_token_by_session_id[session_id] = mcp_jwt_token
    return


def get_mcp_jwt_token_from_fastmcp_context(fastmcp_context: Context) -> str | None:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return lifespan_context.mcp_jwt_token_by_session_id.get(session_id)
