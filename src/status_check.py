import os

from fastmcp.exceptions import ClientError

from src.requests import fetch_mcp_status
from src.schemas import MCPStatus

SCENARIO_ID: str = os.getenv("SCENARIO_ID")
if SCENARIO_ID is None:
    raise ValueError("Please provide SCENARIO_ID.")

def check_server_status() -> None:
    mcp_status: MCPStatus = fetch_mcp_status(SCENARIO_ID)
    if not mcp_status.is_active:
        raise ClientError("Configuration error. Provided scenario-id does not have active MCP.")
    if not mcp_status.is_valid:
        raise ClientError("Configuration error. Provided scenario-id has active MCP but with incorrect configuration.")
