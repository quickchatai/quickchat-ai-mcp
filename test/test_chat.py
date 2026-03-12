from unittest.mock import AsyncMock, MagicMock

import pytest

from src.chat import AppContext, app_lifespan, fetch_mcp_settings, send_message
from src.client import QuickchatClient


@pytest.fixture
def mock_client():
    client = MagicMock(spec=QuickchatClient)
    return client


@pytest.fixture
def mock_context():
    context = MagicMock()
    context.request_context.session.client_params.clientInfo.name = "Test Client"
    context.request_context.session.send_log_message = AsyncMock()
    context.request_context.lifespan_context.conv_id = None
    return context


def test_fetch_mcp_settings_success(mock_client):
    mock_client.get.return_value = {
        "active": True,
        "name": "Test MCP",
        "command": "test_command",
        "description": "Test Description",
    }

    name, command, description = fetch_mcp_settings(mock_client)

    mock_client.get.assert_called_once_with("/v1/api/mcp/settings")
    assert name == "Test MCP"
    assert command == "test_command"
    assert description == "Test Description"


def test_fetch_mcp_settings_inactive(mock_client):
    mock_client.get.return_value = {
        "active": False,
        "name": "Test MCP",
        "command": "test_command",
        "description": "Test Description",
    }

    with pytest.raises(ValueError, match="Quickchat MCP not active"):
        fetch_mcp_settings(mock_client)


def test_fetch_mcp_settings_empty_name(mock_client):
    mock_client.get.return_value = {
        "active": True,
        "name": "",
        "command": "test_command",
        "description": "Test Description",
    }

    with pytest.raises(ValueError, match="MCP name and description cannot be empty"):
        fetch_mcp_settings(mock_client)


def test_fetch_mcp_settings_missing_keys(mock_client):
    mock_client.get.return_value = {"active": True}

    with pytest.raises(ValueError, match="Configuration error"):
        fetch_mcp_settings(mock_client)


def test_fetch_mcp_settings_api_error(mock_client):
    mock_client.get.side_effect = ValueError("Unauthorized")

    with pytest.raises(ValueError, match="Unauthorized"):
        fetch_mcp_settings(mock_client)


@pytest.mark.asyncio
async def test_send_message_success(mock_client, mock_context):
    mock_client.post.return_value = {
        "conv_id": "test-conv-id",
        "reply": "Hello from AI",
    }

    result = await send_message("Hello", mock_context, mock_client)

    mock_client.post.assert_called_once_with(
        "/v1/api/mcp/chat",
        json={
            "conv_id": None,
            "text": "Hello",
            "mcp_client_name": "Test Client",
        },
    )
    assert result == "Hello from AI"
    assert mock_context.request_context.lifespan_context.conv_id == "test-conv-id"


@pytest.mark.asyncio
async def test_send_message_preserves_conv_id(mock_client, mock_context):
    mock_context.request_context.lifespan_context.conv_id = "existing-id"
    mock_client.post.return_value = {
        "conv_id": "existing-id",
        "reply": "Response",
    }

    result = await send_message("Hi", mock_context, mock_client)

    assert result == "Response"
    assert mock_context.request_context.lifespan_context.conv_id == "existing-id"


@pytest.mark.asyncio
async def test_send_message_api_error(mock_client, mock_context):
    mock_client.post.side_effect = ValueError("API error 500")

    with pytest.raises(ValueError, match="API error 500"):
        await send_message("Hello", mock_context, mock_client)


@pytest.mark.asyncio
async def test_app_lifespan():
    mock_server = MagicMock()
    async with app_lifespan(mock_server) as context:
        assert isinstance(context, AppContext)
        assert context.conv_id is None
