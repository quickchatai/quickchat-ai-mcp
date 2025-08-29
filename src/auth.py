import os

from fastmcp.server.auth import AccessToken, JWTVerifier

from src.utils import get_scenario_id_from_jwt_token

SCENARIO_ID: str = os.getenv("SCENARIO_ID")


class QuickchatJWTVerifier(JWTVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        token_scenario_id = get_scenario_id_from_jwt_token(token)
        if token_scenario_id != SCENARIO_ID:
            print(
                f"QuickchatJWTVerifier verify_token failed: request and server scenario_id mismatch, token_scenario_id: {token_scenario_id}, server_scenario_id: {SCENARIO_ID}"
            )
            raise ValueError(
                "Configuration error. Please check your API key and scenario ID."
            )

        return await super().verify_token(token)
