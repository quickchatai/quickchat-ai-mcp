from pydantic import BaseModel, constr


class MCPSettingsSchema(BaseModel):
    mcp_name: constr(min_length=1)
    mcp_command: str
    mcp_description: constr(min_length=1)
