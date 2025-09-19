from fastmcp import Context
from fastmcp.server.dependencies import get_http_headers
from mcp.shared.context import LifespanContextT

from src.lifespan_context import AppContext


def get_bearer_token() -> str | None:
    headers = get_http_headers()
    auth_bearer_header = next(
        (headers.get(key) for key in headers if key.lower() == "authorization"),
        None,
    )

    token = None
    if auth_bearer_header is not None:
        token = auth_bearer_header[7:]  # Remove "Bearer " prefix
    return token


def get_session_id_and_lifespan_context_from_fastmcp_context(
    fastmcp_context: Context,
) -> tuple[str, LifespanContextT]:
    lifespan_context: AppContext = fastmcp_context.request_context.lifespan_context
    session_id = fastmcp_context.session_id
    return session_id, lifespan_context
