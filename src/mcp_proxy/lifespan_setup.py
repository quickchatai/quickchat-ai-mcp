from fastmcp.exceptions import ClientError

from src.requests import generate_mcp_jwt_token
from src.utils import get_bearer_token, get_scenario_id


async def get_mcp_jwt_token():
    auth_bearer_header: str | None = get_bearer_token()
    scenario_id = get_scenario_id()
    try:
        validated_token = await generate_mcp_jwt_token(scenario_id=scenario_id, jwt_token=auth_bearer_header)
    except ClientError as e:
        print(f"Error while validating token, scenario_id: {scenario_id}, jwt_token: {auth_bearer_header}")
        raise e

    print("Validation request successful, saving new token")
    return validated_token
