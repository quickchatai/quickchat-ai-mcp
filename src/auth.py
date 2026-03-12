from mcp.server.auth.provider import AccessToken, TokenVerifier


class PresenceTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        if not token or not token.strip():
            return None
        return AccessToken(token=token, client_id="user", scopes=[])
