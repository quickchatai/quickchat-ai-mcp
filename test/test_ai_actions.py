from unittest.mock import MagicMock

import pytest

from src.ai_actions import register_tools
from src.client import QuickchatClient


@pytest.fixture
def mock_client():
    return MagicMock(spec=QuickchatClient)


@pytest.fixture
def tools(mock_client):
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_tools(mcp, mock_client)
    return {tool.name: tool.fn for tool in mcp._tool_manager._tools.values()}


@pytest.mark.asyncio
async def test_create_ai_action(tools, mock_client):
    mock_client.post.return_value = {"id": "action-1"}
    result = await tools["create_ai_action"](action={"name": "Test Action"})
    mock_client.post.assert_called_once_with(
        "/v1/api/ai_actions/knowledge_base", json={"name": "Test Action"}
    )
    assert result == {"id": "action-1"}


@pytest.mark.asyncio
async def test_get_ai_action(tools, mock_client):
    mock_client.get.return_value = {"id": "action-1", "name": "Test Action"}
    result = await tools["get_ai_action"](action_id="action-1")
    mock_client.get.assert_called_once_with(
        "/v1/api/ai_actions/action-1/knowledge_base"
    )
    assert result["id"] == "action-1"


@pytest.mark.asyncio
async def test_update_ai_action(tools, mock_client):
    mock_client.put.return_value = {"id": "action-1", "name": "Updated"}
    result = await tools["update_ai_action"](
        action_id="action-1", action={"name": "Updated"}
    )
    mock_client.put.assert_called_once_with(
        "/v1/api/ai_actions/action-1/knowledge_base", json={"name": "Updated"}
    )
    assert result["name"] == "Updated"
