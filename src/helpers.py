import jwt


def get_scenario_id_from_jwt_token(token: str) -> str:
    scenario_id = jwt.get_unverified_header(token).get("scenario_id")
    if scenario_id is None:
        raise ValueError("Invalid mcp token, no scenario_id found")
    return scenario_id
