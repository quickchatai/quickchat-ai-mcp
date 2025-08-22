import os
import sys

from src.mcp_proxy.mcp_proxy import mcp_proxy
from src.mcp_server.mcp_server import mcp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

SERVER_TYPE = "SERVER"  # / "PROXY"

def run():
    print("Starting Quickchat mcp server")
    if SERVER_TYPE == "SERVER":
        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=8080,
            path="/mcp/{mcp_id}"
        )
    else:
        mcp_proxy.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=8088,
            path="/mcp_proxy/{mcp_id}"
        )
