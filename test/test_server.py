import json
import os
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from src.lifespan_context import app_lifespan
from src.requests import fetch_mcp_settings, send_message
from src.schemas import MCPSettingsSchema

TEST_SCENARIO_ID = "test_scenario_id"
MCP_USER_JWT_TOKEN = "test_mcp_user_jwt_token"


@pytest.fixture(scope="session", autouse=True)
def mock_env():
    os.environ["MCP_USER_JWT_TOKEN"] = "test_mcp_user_jwt_token"
    os.environ["SCENARIO_ID"] = "test_scenario"


def mock_response_from_response_json(
    response_json: dict
) -> Mock:
    """Fixture to create a mock response object"""
    mock = MagicMock()
    mock.status_code = 200
    mock.content = json.dumps(response_json).encode()
    mock.json.return_value = response_json
    return mock


@pytest.fixture
def mock_error_response() -> Mock:
    """Fixture for error responses"""
    mock = MagicMock()
    mock.status_code = 400
    response_json = {"error": "Test Error"}
    mock.content = json.dumps(response_json).encode()
    mock.json.return_value = response_json
    return mock


@pytest.fixture
def mock_unauthorized_response() -> Mock:
    """Fixture for unauthorized responses"""
    mock = MagicMock()
    mock.status_code = 401
    response_json = {"error": "Unauthorized"}
    mock.content = json.dumps(response_json).encode()
    mock.json.return_value = response_json
    return mock


@pytest.fixture
def mock_context() -> Mock:
    """Fixture to create a mock context object for MCP"""
    context = MagicMock()
    context.request_context.session.client_params.clientInfo.name = "Test Client"
    context.request_context.lifespan_context.conv_id_by_session_id = {}
    return context


# Tests for the fetch_mcp_settings function
@patch("requests.get")
def test_fetch_mcp_settings_success(mock_get: Mock) -> None:
    """Test successful MCP settings fetch"""
    mock_get.return_value = mock_response_from_response_json(
        {
            "active": True,
            "name": "Test MCP",
            "command": "Test Command",
            "description": "Test Description",
            "conv_id": "test-conv-id",
            "reply": "This is a test reply",
        }
    )
    mcp_settings: MCPSettingsSchema = fetch_mcp_settings("test-scenario", "test-key")

    mock_get.assert_called_once()
    assert mcp_settings.mcp_name == "Test MCP"
    assert mcp_settings.mcp_command == "Test Command"
    assert mcp_settings.mcp_description == "Test Description"


@patch("requests.get")
def test_fetch_mcp_settings_error_response(mock_get: Mock, mock_error_response: Mock):
    """Test error response handling"""
    mock_get.return_value = mock_error_response

    with pytest.raises(ValueError, match="Configuration error"):
        fetch_mcp_settings("test-scenario", "test-key")

    mock_get.assert_called_once()


@patch("requests.get")
def test_fetch_mcp_settings_inactive_mcp(mock_get: Mock):
    """Test when MCP is not active"""
    mock_get.return_value = mock_response_from_response_json(
        {
            "active": False,
            "name": "Test MCP",
            "command": "Test Command",
            "description": "Test Description",
        }
    )

    with pytest.raises(ValueError, match="Quickchat MCP not active"):
        fetch_mcp_settings("test-scenario", "test-key")

    mock_get.assert_called_once()


@patch("requests.get")
def test_fetch_mcp_settings_empty_name_description(mock_get: Mock):
    """Test when name or description is empty"""
    mock_get.return_value = mock_response_from_response_json(
        {
            "active": True,
            "name": "",
            "command": "Test Command",
            "description": "Test Description",
        }
    )

    with pytest.raises(ValueError, match="MCP Settings validation error"):
        fetch_mcp_settings("test-scenario", "test-key")

    mock_get.assert_called_once()


# Tests for the send_message function
@pytest.mark.asyncio
@patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock)
async def test_send_message_success(
    mock_send_message_post: AsyncMock,
    mock_context: Mock,
):
    """Test successful message sending"""
    mock_send_message_post.return_value = mock_response_from_response_json(
        {
            "conv_id": "test-conv-id",
            "reply": "This is a test reply",
        }
    )

    result = await send_message(
        message="Hello",
        context=mock_context,
        scenario_id=TEST_SCENARIO_ID,
        conv_id="test_conv_id",
        mcp_jwt_token="test_mcp_jwt_token",
    )

    mock_send_message_post.assert_called_once()
    assert result.conv_id == "test-conv-id"
    assert result.reply == "This is a test reply"


@pytest.mark.asyncio
@patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock)
async def test_send_message_unauthorized(
    mock_post: AsyncMock,
    mock_unauthorized_response: Mock,
    mock_context: Mock,
):
    """Test unauthorized error handling"""
    mock_post.return_value = mock_unauthorized_response

    with pytest.raises(ValueError, match="Configuration error"):
        await send_message(
            message="Hello",
            context=mock_context,
            scenario_id=TEST_SCENARIO_ID,
            conv_id="test_conv_id",
            mcp_jwt_token="test_mcp_jwt_token",
        )

    mock_post.assert_called_once()


@pytest.mark.asyncio
@patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock)
async def test_send_message_server_error(
    mock_post: AsyncMock,
    mock_error_response: Mock,
    mock_context: Mock
):
    """Test server error handling"""
    mock_post.return_value = mock_error_response

    with pytest.raises(ValueError, match="Server error"):
        await send_message(
            message="Hello",
            context=mock_context,
            scenario_id=TEST_SCENARIO_ID,
            conv_id="test_conv_id",
            mcp_jwt_token="test_mcp_jwt_token",
        )

    mock_post.assert_called_once()


# Tests for the app_lifespan context manager
@pytest.mark.asyncio
async def test_app_lifespan():
    """Test the app_lifespan context manager"""
    mock_server = MagicMock()

    async with app_lifespan(mock_server) as context:
        assert context.conv_id_by_session_id == {}
