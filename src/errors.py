from fastmcp.exceptions import ClientError


class RemoteMcpConnectionError(ClientError):
    def __init__(self, *args, **kwargs):
        super().__init__("Configuration error. Please check your MCP token and scenario-id")
