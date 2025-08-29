from typing import Any

from fastmcp.exceptions import ClientError
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

from src.lifespan_helpers import set_mcp_jwt_token
from src.requests import generate_mcp_jwt_token
from src.utils import get_session_id_and_lifespan_context_from_fastmcp_context


class SetupMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        session_id, lifespan_context = (
            get_session_id_and_lifespan_context_from_fastmcp_context(
                fastmcp_context=context.fastmcp_context
            )
        )
        lifespan_mcp_jwt_token_by_session_id = (
            lifespan_context.mcp_jwt_token_by_session_id
        )
        if session_id not in lifespan_mcp_jwt_token_by_session_id:
            print("MCPJWTToken not found in lifespan_context, loading")
            lifespan_mcp_jwt_token_by_session_id[session_id] = None

            print("Loading MCP JWT Token")
            try:
                mcp_jwt_token = await generate_mcp_jwt_token()
            except Exception as e:
                print(f"Loading MCP JWT Token failed: {e}")
                raise ClientError(
                    "Configuration error. Please check your MCP token and scenario ID"
                )
            set_mcp_jwt_token(
                fastmcp_context=context.fastmcp_context, mcp_jwt_token=mcp_jwt_token
            )
            print("MCPJWTToken setup successful")

        return await call_next(context)
