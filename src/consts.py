import os

BASE_URL: str = os.getenv("BASE_URL", "https://grzegorz.quickchat.dev")
CHAT_ENDPOINT = f"{BASE_URL}/v1/api/mcp/chat"
SETTINGS_ENDPOINT = f"{BASE_URL}/v1/api/mcp/settings"
JWT_PUBLIC_KEY_ENDPOINT = f"{BASE_URL}/v1/api/auth/public_key"
VALIDATE_MCP_TOKEN_ENDPOINT = f"{BASE_URL}/v1/api/mcp/validate"

SEND_MESSAGE_TIMEOUT_SECONDS = 30.0
