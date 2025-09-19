import os

BASE_URL: str = os.getenv("BASE_URL", "https://app.quickchat.ai")
GENERATE_MCP_TOKEN_ENDPOINT = f"{BASE_URL}/v1/api/mcp/token/private"
MCP_SETTINGS_ENDPOINT = f"{BASE_URL}/v1/api/mcp/settings"
MCP_STATUS_ENDPOINT = f"{BASE_URL}/v1/api/mcp/status"
CHAT_ENDPOINT = f"{BASE_URL}/v1/api/mcp/chat"

SEND_MESSAGE_TIMEOUT_SECONDS = 30.0
