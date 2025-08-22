from dataclasses import dataclass, field


@dataclass
class MCPSettings:
    mcp_name: str
    mcp_command: str
    mcp_description: str


@dataclass
class AppContext:
    conv_id_by_session_id: dict[str, str] = field(default_factory=dict)
    scenario_ids_with_tool: set[str] = field(default_factory=set)
