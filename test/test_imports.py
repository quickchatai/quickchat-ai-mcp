from unittest.mock import MagicMock

import pytest

from src.client import QuickchatClient
from src.imports import register_tools


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
async def test_scrape_website(tools, mock_client):
    mock_client.post.return_value = {"status": "started"}
    result = await tools["scrape_website"](url="https://example.com")
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/import_external/website",
        json={"url": "https://example.com"},
    )
    assert result == {"status": "started"}


@pytest.mark.asyncio
async def test_import_youtube_transcript(tools, mock_client):
    mock_client.post.return_value = {"status": "started"}
    await tools["import_youtube_transcript"](url="https://youtube.com/watch?v=test")
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/import_external/youtube",
        json={"url": "https://youtube.com/watch?v=test"},
    )


@pytest.mark.asyncio
async def test_import_sitemap(tools, mock_client):
    mock_client.post.return_value = {"status": "started"}
    await tools["import_sitemap"](url="https://example.com/sitemap.xml")
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/import_external/site-map",
        json={"url": "https://example.com/sitemap.xml"},
    )


@pytest.mark.asyncio
async def test_scrape_link_list(tools, mock_client):
    mock_client.post.return_value = {"status": "started"}
    urls = ["https://example.com/1", "https://example.com/2"]
    await tools["scrape_link_list"](urls=urls)
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/import_external/scrape-list",
        json={"urls": urls},
    )


@pytest.mark.asyncio
async def test_import_source_articles(tools, mock_client):
    mock_client.post.return_value = {"imported": 5}
    await tools["import_source_articles"](source="zendesk")
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/sources/zendesk/import", json=None
    )


@pytest.mark.asyncio
async def test_delete_source_articles(tools, mock_client):
    mock_client.post.return_value = {"deleted": 3}
    await tools["delete_source_articles"](source="zendesk")
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/sources/zendesk/delete", json=None
    )


@pytest.mark.asyncio
async def test_diff_source_articles(tools, mock_client):
    mock_client.post.return_value = {"diff": []}
    await tools["diff_source_articles"](source="zendesk")
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/sources/zendesk/articles_diff", json=None
    )


@pytest.mark.asyncio
async def test_refresh_intercom_articles(tools, mock_client):
    mock_client.post.return_value = {"refreshed": True}
    await tools["refresh_intercom_articles"]()
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/intercom/refresh_articles"
    )


@pytest.mark.asyncio
async def test_import_intercom_articles(tools, mock_client):
    mock_client.post.return_value = {"imported": 10}
    await tools["import_intercom_articles"]()
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/intercom/import", json=None
    )


@pytest.mark.asyncio
async def test_delete_intercom_articles(tools, mock_client):
    mock_client.post.return_value = {"deleted": 5}
    await tools["delete_intercom_articles"]()
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/intercom/delete", json=None
    )


@pytest.mark.asyncio
async def test_diff_intercom_articles(tools, mock_client):
    mock_client.get.return_value = {"diff": []}
    await tools["diff_intercom_articles"]()
    mock_client.get.assert_called_once_with(
        "/v1/api/knowledge_base/intercom/articles_diff"
    )
