from unittest.mock import MagicMock

import pytest

from src.client import QuickchatClient
from src.knowledge_base import register_tools


@pytest.fixture
def mock_client():
    return MagicMock(spec=QuickchatClient)


@pytest.fixture
def tools(mock_client):
    """Register tools and return a dict mapping tool name -> async fn."""
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_tools(mcp, mock_client)
    return {tool.name: tool.fn for tool in mcp._tool_manager._tools.values()}


@pytest.mark.asyncio
async def test_get_knowledge_base_settings(tools, mock_client):
    mock_client.get.return_value = {"setting": "value"}
    result = await tools["get_knowledge_base_settings"]()
    mock_client.get.assert_called_once_with("/v1/api/knowledge_base/")
    assert result == {"setting": "value"}


@pytest.mark.asyncio
async def test_update_knowledge_base_settings(tools, mock_client):
    mock_client.patch.return_value = {"updated": True}
    result = await tools["update_knowledge_base_settings"](settings={"key": "val"})
    mock_client.patch.assert_called_once_with(
        "/v1/api/knowledge_base/", json={"key": "val"}
    )
    assert result == {"updated": True}


@pytest.mark.asyncio
async def test_create_article(tools, mock_client):
    mock_client.post.return_value = {"id": "art-1"}
    result = await tools["create_article"](article={"title": "Test"})
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/articles/", json={"title": "Test"}
    )
    assert result == {"id": "art-1"}


@pytest.mark.asyncio
async def test_list_articles(tools, mock_client):
    mock_client.get.return_value = {"articles": []}
    result = await tools["list_articles"]()
    mock_client.get.assert_called_once_with(
        "/v1/api/knowledge_base/articles/", params=None
    )
    assert result == {"articles": []}


@pytest.mark.asyncio
async def test_list_articles_with_filters(tools, mock_client):
    mock_client.get.return_value = {"articles": []}
    await tools["list_articles"](type="faq", tags="tag1")
    mock_client.get.assert_called_once_with(
        "/v1/api/knowledge_base/articles/", params={"type": "faq", "tags": "tag1"}
    )


@pytest.mark.asyncio
async def test_get_article(tools, mock_client):
    mock_client.get.return_value = {"id": "art-1", "title": "Test"}
    result = await tools["get_article"](article_id="art-1")
    mock_client.get.assert_called_once_with("/v1/api/knowledge_base/articles/art-1")
    assert result["id"] == "art-1"


@pytest.mark.asyncio
async def test_update_article(tools, mock_client):
    mock_client.patch.return_value = {"id": "art-1"}
    await tools["update_article"](article_id="art-1", article={"title": "Updated"})
    mock_client.patch.assert_called_once_with(
        "/v1/api/knowledge_base/articles/art-1", json={"title": "Updated"}
    )


@pytest.mark.asyncio
async def test_delete_articles(tools, mock_client):
    mock_client.delete.return_value = {}
    await tools["delete_articles"](article_ids=["art-1", "art-2"])
    mock_client.delete.assert_called_once_with(
        "/v1/api/knowledge_base/articles/", json={"ids": ["art-1", "art-2"]}
    )


@pytest.mark.asyncio
async def test_search_articles(tools, mock_client):
    mock_client.get.return_value = {"results": []}
    await tools["search_articles"](query="test query")
    mock_client.get.assert_called_once_with(
        "/v1/api/knowledge_base/articles/search", params={"query": "test query"}
    )


@pytest.mark.asyncio
async def test_list_paragraphs(tools, mock_client):
    mock_client.get.return_value = {"paragraphs": []}
    await tools["list_paragraphs"]()
    mock_client.get.assert_called_once_with(
        "/v1/api/knowledge_base/articles/paragraphs", params=None
    )


@pytest.mark.asyncio
async def test_get_article_language_url(tools, mock_client):
    mock_client.get.return_value = {"url": "https://example.com"}
    await tools["get_article_language_url"](article_id="art-1", language="en")
    mock_client.get.assert_called_once_with(
        "/v1/api/knowledge_base/articles/art-1/lang_urls/en"
    )


@pytest.mark.asyncio
async def test_create_article_language_url(tools, mock_client):
    mock_client.post.return_value = {"url": "https://example.com"}
    await tools["create_article_language_url"](
        article_id="art-1", language="en", url_data={"url": "https://example.com"}
    )
    mock_client.post.assert_called_once_with(
        "/v1/api/knowledge_base/articles/art-1/lang_urls/en",
        json={"url": "https://example.com"},
    )


@pytest.mark.asyncio
async def test_delete_article_language_url(tools, mock_client):
    mock_client.delete.return_value = {}
    await tools["delete_article_language_url"](article_id="art-1", language="en")
    mock_client.delete.assert_called_once_with(
        "/v1/api/knowledge_base/articles/art-1/lang_urls/en"
    )


@pytest.mark.asyncio
async def test_list_tags(tools, mock_client):
    mock_client.get.return_value = {"tags": ["tag1", "tag2"]}
    result = await tools["list_tags"]()
    mock_client.get.assert_called_once_with("/v1/api/knowledge_base/tags/")
    assert result == {"tags": ["tag1", "tag2"]}
