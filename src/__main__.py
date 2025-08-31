import os
import sys

from src.mcp_server.mcp_server import mcp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run():
    print("Starting Quickchat mcp server")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8080,
        path="/mcp/{mcp_id}"
    )
