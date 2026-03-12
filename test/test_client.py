from unittest.mock import MagicMock, patch

import pytest

from src.client import QuickchatClient

TEST_TOKEN = "test-token"


@pytest.fixture
def client():
    return QuickchatClient(api_token=TEST_TOKEN, base_url="https://test.example.com")


@pytest.fixture
def mock_success_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.ok = True
    mock.content = b'{"result": "ok"}'
    mock.json.return_value = {"result": "ok"}
    return mock


@pytest.fixture
def mock_204_response():
    mock = MagicMock()
    mock.status_code = 204
    mock.ok = True
    mock.content = b""
    return mock


@pytest.fixture
def mock_401_response():
    mock = MagicMock()
    mock.status_code = 401
    mock.ok = False
    mock.text = "Unauthorized"
    return mock


@pytest.fixture
def mock_500_response():
    mock = MagicMock()
    mock.status_code = 500
    mock.ok = False
    mock.text = "Internal Server Error"
    return mock


def test_client_headers(client):
    assert client.headers == {"Authorization": "Bearer test-token"}
    assert client.base_url == "https://test.example.com"


@patch("requests.get")
def test_get_success(mock_get, client, mock_success_response):
    mock_get.return_value = mock_success_response
    result = client.get("/v1/test", params={"key": "val"})

    mock_get.assert_called_once_with(
        url="https://test.example.com/v1/test",
        headers={"Authorization": "Bearer test-token"},
        params={"key": "val"},
    )
    assert result == {"result": "ok"}


@patch("requests.post")
def test_post_success(mock_post, client, mock_success_response):
    mock_post.return_value = mock_success_response
    result = client.post("/v1/test", json={"data": "value"})

    mock_post.assert_called_once_with(
        url="https://test.example.com/v1/test",
        headers={"Authorization": "Bearer test-token"},
        json={"data": "value"},
    )
    assert result == {"result": "ok"}


@patch("requests.patch")
def test_patch_success(mock_patch, client, mock_success_response):
    mock_patch.return_value = mock_success_response
    result = client.patch("/v1/test", json={"data": "value"})
    assert result == {"result": "ok"}


@patch("requests.put")
def test_put_success(mock_put, client, mock_success_response):
    mock_put.return_value = mock_success_response
    result = client.put("/v1/test", json={"data": "value"})
    assert result == {"result": "ok"}


@patch("requests.delete")
def test_delete_success(mock_delete, client, mock_success_response):
    mock_delete.return_value = mock_success_response
    result = client.delete("/v1/test", json={"ids": ["1"]})
    assert result == {"result": "ok"}


@patch("requests.get")
def test_get_204_no_content(mock_get, client, mock_204_response):
    mock_get.return_value = mock_204_response
    result = client.get("/v1/test")
    assert result == {}


@patch("requests.get")
def test_get_401_unauthorized(mock_get, client, mock_401_response):
    mock_get.return_value = mock_401_response
    with pytest.raises(ValueError, match="Unauthorized"):
        client.get("/v1/test")


@patch("requests.post")
def test_post_500_server_error(mock_post, client, mock_500_response):
    mock_post.return_value = mock_500_response
    with pytest.raises(ValueError, match="API error 500"):
        client.post("/v1/test")
