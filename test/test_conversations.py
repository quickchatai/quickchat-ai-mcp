from unittest.mock import MagicMock

import pytest

from src.client import QuickchatClient
from src.conversations import register_tools


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
async def test_list_conversations(tools, mock_client):
    mock_client.get.return_value = {"conversations": []}
    result = await tools["list_conversations"]()
    mock_client.get.assert_called_once_with("/v1/api_core/conversations", params=None)
    assert result == {"conversations": []}


@pytest.mark.asyncio
async def test_list_conversations_with_page(tools, mock_client):
    mock_client.get.return_value = {"conversations": []}
    await tools["list_conversations"](page=2, page_size=10)
    mock_client.get.assert_called_once_with(
        "/v1/api_core/conversations", params={"page": 2, "page_size": 10}
    )


@pytest.mark.asyncio
async def test_get_conversation(tools, mock_client):
    mock_client.get.return_value = {"id": "conv-1", "messages": []}
    result = await tools["get_conversation"](conversation_id="conv-1")
    mock_client.get.assert_called_once_with("/v1/api_core/conversations/conv-1/")
    assert result["id"] == "conv-1"


@pytest.mark.asyncio
async def test_get_conversation_metadata(tools, mock_client):
    mock_client.get.return_value = {"key": "value"}
    result = await tools["get_conversation_metadata"](conversation_id="conv-1")
    mock_client.get.assert_called_once_with(
        "/v1/api_core/conversations/conv-1/metadata"
    )
    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_set_conversation_metadata(tools, mock_client):
    mock_client.post.return_value = {"key": "new_value"}
    await tools["set_conversation_metadata"](
        conversation_id="conv-1", metadata={"key": "new_value"}
    )
    mock_client.post.assert_called_once_with(
        "/v1/api_core/conversations/conv-1/metadata", json={"key": "new_value"}
    )
