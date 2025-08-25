import os

BASE_URL: str = os.getenv("BASE_URL", "https://app.quickchat.ai")
CHAT_ENDPOINT = f"{BASE_URL}/v1/api/mcp/chat"
SETTINGS_ENDPOINT = f"{BASE_URL}/v1/api/mcp/settings"
JWT_PUBLIC_KEY_ENDPOINT = f"{BASE_URL}/v1/api/auth/public_key"
GENERATE_MCP_TOKEN_ENDPOINT = f"{BASE_URL}/v1/api/mcp/token/private"

SEND_MESSAGE_DEFAULT_TOOL_NAME = "send_message"
SEND_MESSAGE_TIMEOUT_SECONDS = 30.0
SCENARIO_ID_PATH_PARAM_NAME = "mcp_id"
