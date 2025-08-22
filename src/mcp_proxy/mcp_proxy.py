from fastmcp import Client, Context
from fastmcp.client import StreamableHttpTransport
from fastmcp.exceptions import ClientError
from fastmcp.server.dependencies import get_context
from fastmcp.server.proxy import FastMCPProxy, ProxyClient

from src.mcp_proxy.lifespan_context import (
    MCPConfiguration,
    MCPSettings,
    proxy_lifespan_context,
)
from src.mcp_proxy.lifespan_setup import get_mcp_jwt_token
from src.requests import fetch_mcp_settings_for_scenario_id
from src.schemas import MCPSettingsSchema
from src.utils import (
    get_scenario_id,
    get_session_id_and_lifespan_context_from_fastmcp_context,
)


async def client_factory() -> Client:
    context: Context = get_context()
    session_id, lifespan_context = get_session_id_and_lifespan_context_from_fastmcp_context(
        fastmcp_context=context
    )

    lifespan_mcp_configuration_by_session_id = lifespan_context.mcp_configuration_by_session_id
    if session_id not in lifespan_mcp_configuration_by_session_id:
        print("MCPSettings not found in lifespan_context, loading")
        lifespan_mcp_configuration_by_session_id[session_id] = None

        print("Loading MCP JWT Token")
        try:
            mcp_jwt_token = await get_mcp_jwt_token()
        except Exception as e:
            print(f"Loading MCP JWT Token failed: {e}")
            raise ClientError(
                "Configuration error. Please check your MCP token and scenario ID"
            )

        print("Loading MCP Settings")
        scenario_id = get_scenario_id()
        try:
            mcp_settings: MCPSettingsSchema = await fetch_mcp_settings_for_scenario_id(
                scenario_id=scenario_id,
                mcp_jwt_token=mcp_jwt_token
            )
        except Exception as e:
            print(f"Loading MCP Settings failed: {e}")
            raise ClientError(
                "Configuration error. Please check your MCP token and scenario ID"
            )

        print(lifespan_mcp_configuration_by_session_id)
        lifespan_mcp_configuration_by_session_id[session_id] = MCPConfiguration(
            jwt_token=mcp_jwt_token,
            settings=MCPSettings(
                mcp_name=mcp_settings.mcp_name,
                mcp_command=mcp_settings.mcp_command,
                mcp_description=mcp_settings.mcp_description,
            ),
        )
        print("MCPSettings setup successful")

    mcp_configuration: MCPConfiguration = lifespan_mcp_configuration_by_session_id[session_id]

    if mcp_configuration is None:
        print("MCP Configuration not found")
        raise ClientError(
            "Configuration error. Please check your MCP token and scenario ID"
        )

    scenario_id = get_scenario_id()
    print(f"JWT Token: {mcp_configuration.jwt_token}")
    url = f"http://localhost:8080/mcp/{scenario_id}"
    transport = StreamableHttpTransport(
        url=url,
        headers={
            "authorization": f"Bearer {mcp_configuration.jwt_token}",
            "mcp_name": mcp_configuration.settings.mcp_name,
            "mcp_command": mcp_configuration.settings.mcp_command,
            "mcp_description": mcp_configuration.settings.mcp_description,
        }
    )
    return ProxyClient(transport=transport)


mcp_proxy = FastMCPProxy(
    client_factory=client_factory,
    lifespan=proxy_lifespan_context,
    name="RoutingProxy"
)
