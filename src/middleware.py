from typing import Any

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult

from src.errors import RemoteMcpConnectionError
from src.lifespan_helpers import (
    check_if_session_id_has_failed_validation_from_fastmcp_context,
    set_mcp_jwt_token,
)
from src.requests import generate_mcp_jwt_token
from src.status_check import check_server_status
from src.utils import get_session_id_and_lifespan_context_from_fastmcp_context


class SetupMiddleware(Middleware):

    async def _setup_from_middleware_context(
        self, context: MiddlewareContext
    ) -> None:
        session_id, lifespan_context = (
            get_session_id_and_lifespan_context_from_fastmcp_context(
                fastmcp_context=context.fastmcp_context
            )
        )
        check_server_status()
        if check_if_session_id_has_failed_validation_from_fastmcp_context(context.fastmcp_context):
            print("Session_id has failed validation")
            raise RemoteMcpConnectionError()

        lifespan_mcp_jwt_token_by_session_id = (
            lifespan_context.mcp_jwt_token_by_session_id
        )
        if session_id not in lifespan_mcp_jwt_token_by_session_id:
            print(f"MCPJWTToken not found in lifespan_context, loading for session_id: {session_id}")
            try:
                mcp_jwt_token = await generate_mcp_jwt_token(
                    fastmcp_context=context.fastmcp_context
                )
            except Exception as e:
                print(f"Loading MCP JWT Token failed: {e}")
                raise e

            set_mcp_jwt_token(
                fastmcp_context=context.fastmcp_context, mcp_jwt_token=mcp_jwt_token
            )
            print("MCPJWTToken setup successful")

    async def on_list_tools(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        await self._setup_from_middleware_context(context)
        return await call_next(context)

    async def on_call_tool(
        self,
        context: MiddlewareContext,
        call_next: CallNext,
    ) -> ToolResult:
        await self._setup_from_middleware_context(context)
        return await call_next(context)
