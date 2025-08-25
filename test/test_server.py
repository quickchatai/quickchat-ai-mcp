import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.requests import send_message
from src.mcp_server.lifespan_context import app_lifespan_context, set_mcp_settings

TEST_SCENARIO_ID = "test_scenario_id"
TEST_API_KEY = "test_api_key"


@pytest.fixture(scope="session", autouse=True)
def mock_env():
    os.environ["API_KEY"] = "test_api_key"
    os.environ["SCENARIO_ID"] = "test_scenario"


@pytest.fixture
def mock_response():
    """Fixture to create a mock response object"""
    mock = MagicMock()
    mock.status_code = 200
    mock.content = json.dumps(
        {
            "active": True,
            "name": "Test MCP",
            "command": "Test Command",
            "description": "Test Description",
            "conv_id": "test-conv-id",
            "reply": "This is a test reply",
        }
    ).encode()
    return mock


@pytest.fixture
def mock_error_response():
    """Fixture for error responses"""
    mock = MagicMock()
    mock.status_code = 400
    mock.content = json.dumps({"error": "Test Error"}).encode()
    return mock


@pytest.fixture
def mock_unauthorized_response():
    """Fixture for unauthorized responses"""
    mock = MagicMock()
    mock.status_code = 401
    mock.content = json.dumps({"error": "Unauthorized"}).encode()
    return mock


@pytest.fixture
def mock_context():
    """Fixture to create a mock context object for MCP"""
    context = MagicMock()
    context.request_context.session.client_params.clientInfo.name = "Test Client"
    context.request_context.session.send_log_message = AsyncMock()
    context.request_context.lifespan_context.scenario_to_conv_id = {}
    return context


# Tests for the fetch_mcp_settings_for_scenario_id function
@patch("requests.get")
def test_fetch_mcp_settings_for_scenario_id_success(mock_get, mock_response):
    """Test successful MCP settings fetch"""
    mock_get.return_value = mock_response
    name, command, description = set_mcp_settings("test-scenario", "test-key")

    mock_get.assert_called_once()
    assert name == "Test MCP"
    assert command == "Test Command"
    assert description == "Test Description"


@patch("requests.get")
def test_fetch_mcp_settings_for_scenario_id_error_response(mock_get, mock_error_response):
    """Test error response handling"""
    mock_get.return_value = mock_error_response

    with pytest.raises(ValueError, match="Configuration error"):
        set_mcp_settings("test-scenario", "test-key")

    mock_get.assert_called_once()


@patch("requests.get")
def test_fetch_mcp_settings_for_scenario_id_inactive_mcp(mock_get, mock_response):
    """Test when MCP is not active"""
    mock_response.content = json.dumps(
        {
            "active": False,
            "name": "Test MCP",
            "command": "Test Command",
            "description": "Test Description",
        }
    ).encode()
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="Quickchat MCP not active"):
        set_mcp_settings("test-scenario", "test-key")

    mock_get.assert_called_once()


@patch("requests.get")
def test_fetch_mcp_settings_for_scenario_id_empty_name_description(mock_get, mock_response):
    """Test when name or description is empty"""
    mock_response.content = json.dumps(
        {
            "active": True,
            "name": "",
            "command": "Test Command",
            "description": "Test Description",
        }
    ).encode()
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="MCP name and description cannot be empty"):
        set_mcp_settings("test-scenario", "test-key")

    mock_get.assert_called_once()


# Tests for the send_message function
@pytest.mark.asyncio
@patch("requests.post")
async def test_send_message_success(mock_post, mock_response, mock_context):
    """Test successful message sending"""
    mock_post.return_value = mock_response

    result = await send_message("Hello", mock_context, TEST_SCENARIO_ID, TEST_API_KEY)

    mock_post.assert_called_once()
    assert result == "This is a test reply"
    assert (
        mock_context.request_context.lifespan_context.scenario_to_conv_id.get(
            TEST_SCENARIO_ID
        )
        == "test-conv-id"
    )


@pytest.mark.asyncio
@patch("requests.post")
async def test_send_message_unauthorized(
    mock_post, mock_unauthorized_response, mock_context
):
    """Test unauthorized error handling"""
    mock_post.return_value = mock_unauthorized_response

    with pytest.raises(ValueError, match="Configuration error"):
        await send_message("Hello", mock_context, TEST_SCENARIO_ID, TEST_API_KEY)

    mock_post.assert_called_once()
    mock_context.request_context.session.send_log_message.assert_called_once()


@pytest.mark.asyncio
@patch("requests.post")
async def test_send_message_server_error(mock_post, mock_error_response, mock_context):
    """Test server error handling"""
    mock_post.return_value = mock_error_response

    with pytest.raises(ValueError, match="Server error"):
        await send_message("Hello", mock_context, TEST_SCENARIO_ID, TEST_API_KEY)

    mock_post.assert_called_once()
    mock_context.request_context.session.send_log_message.assert_called_once()


# Tests for the app_lifespan context manager
@pytest.mark.asyncio
async def test_app_lifespan():
    """Test the app_lifespan context manager"""
    mock_server = MagicMock()

    async with app_lifespan_context(mock_server) as context:
        assert context.scenario_to_conv_id == {}


@pytest.mark.asyncio
@patch("requests.post")
async def test_multiple_conv_ids(mock_post, mock_response, mock_context):
    """Test correct handling of requests with multiple scenario_ids and conv_ids"""
    assert mock_context.request_context.lifespan_context.scenario_to_conv_id == {}

    mock_response.content = json.dumps(
        {
            "conv_id": "conv_id1",
            "reply": "This is a test reply",
        }
    ).encode()
    mock_post.return_value = mock_response
    await send_message("Hello", mock_context, "scenario_id1", TEST_API_KEY)
    assert mock_context.request_context.lifespan_context.scenario_to_conv_id == {
        "scenario_id1": "conv_id1"
    }

    mock_response.content = json.dumps(
        {
            "conv_id": "conv_id2",
            "reply": "This is a test reply",
        }
    ).encode()
    mock_post.return_value = mock_response
    await send_message("Hello", mock_context, "scenario_id2", TEST_API_KEY)
    assert mock_context.request_context.lifespan_context.scenario_to_conv_id == {
        "scenario_id1": "conv_id1",
        "scenario_id2": "conv_id2",
    }
