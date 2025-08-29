import os

BASE_URL: str = os.getenv("BASE_URL", "https://app.quickchat.ai")
JWT_PUBLIC_KEY_ENDPOINT = f"{BASE_URL}/v1/api/auth/public_key"
GENERATE_MCP_TOKEN_ENDPOINT = f"{BASE_URL}/v1/api/mcp/token/private"
SETTINGS_ENDPOINT = f"{BASE_URL}/v1/api/mcp/settings"
CHAT_ENDPOINT = f"{BASE_URL}/v1/api/mcp/chat"

SEND_MESSAGE_TIMEOUT_SECONDS = 30.0
