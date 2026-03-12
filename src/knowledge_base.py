from mcp.server.fastmcp import FastMCP

from src.client import QuickchatClient

KB_BASE = "/v1/api/knowledge_base"


def register_tools(mcp: FastMCP, client: QuickchatClient) -> None:
    @mcp.tool(
        name="get_knowledge_base_settings",
        description="Get Knowledge Base settings.",
    )
    async def get_knowledge_base_settings() -> dict:
        return client.get(f"{KB_BASE}/")

    @mcp.tool(
        name="update_knowledge_base_settings",
        description="Update Knowledge Base settings. Pass only the fields you want to change.",
    )
    async def update_knowledge_base_settings(settings: dict) -> dict:
        return client.patch(f"{KB_BASE}/", json=settings)

    @mcp.tool(
        name="create_article",
        description="Create a new Knowledge Base article.",
    )
    async def create_article(article: dict) -> dict:
        return client.post(f"{KB_BASE}/articles/", json=article)

    @mcp.tool(
        name="list_articles",
        description="List Knowledge Base articles. Filter by type, tags, URL, title, or search by content.",
    )
    async def list_articles(
        type: str | None = None,
        tags: str | None = None,
        url: str | None = None,
        title: str | None = None,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict:
        params = {}
        if type is not None:
            params["type"] = type
        if tags is not None:
            params["tags"] = tags
        if url is not None:
            params["url"] = url
        if title is not None:
            params["title"] = title
        if search is not None:
            params["search"] = search
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        return client.get(f"{KB_BASE}/articles/", params=params or None)

    @mcp.tool(
        name="get_article",
        description="Get a specific Knowledge Base article by ID.",
    )
    async def get_article(article_id: str) -> dict:
        return client.get(f"{KB_BASE}/articles/{article_id}")

    @mcp.tool(
        name="update_article",
        description="Update a Knowledge Base article. Pass the article ID and fields to change.",
    )
    async def update_article(article_id: str, article: dict) -> dict:
        return client.patch(f"{KB_BASE}/articles/{article_id}", json=article)

    @mcp.tool(
        name="delete_articles",
        description="Delete Knowledge Base articles. Pass a list of article IDs.",
    )
    async def delete_articles(article_ids: list[str]) -> dict:
        return client.delete(f"{KB_BASE}/articles/", json={"ids": article_ids})

    @mcp.tool(
        name="search_articles",
        description="Search Knowledge Base articles by content similarity.",
    )
    async def search_articles(
        query: str,
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict:
        params: dict = {"query": query}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        return client.get(f"{KB_BASE}/articles/search", params=params)

    @mcp.tool(
        name="list_paragraphs",
        description="List all paragraphs across Knowledge Base articles.",
    )
    async def list_paragraphs(
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict:
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        return client.get(f"{KB_BASE}/articles/paragraphs", params=params or None)

    @mcp.tool(
        name="get_article_language_url",
        description="Get the language-specific URL for an article.",
    )
    async def get_article_language_url(article_id: str, language: str) -> dict:
        return client.get(f"{KB_BASE}/articles/{article_id}/lang_urls/{language}")

    @mcp.tool(
        name="create_article_language_url",
        description="Create a language-specific URL for an article.",
    )
    async def create_article_language_url(
        article_id: str, language: str, url_data: dict
    ) -> dict:
        return client.post(
            f"{KB_BASE}/articles/{article_id}/lang_urls/{language}", json=url_data
        )

    @mcp.tool(
        name="update_article_language_url",
        description="Update a language-specific URL for an article.",
    )
    async def update_article_language_url(
        article_id: str, language: str, url_data: dict
    ) -> dict:
        return client.patch(
            f"{KB_BASE}/articles/{article_id}/lang_urls/{language}", json=url_data
        )

    @mcp.tool(
        name="delete_article_language_url",
        description="Delete a language-specific URL for an article.",
    )
    async def delete_article_language_url(article_id: str, language: str) -> dict:
        return client.delete(f"{KB_BASE}/articles/{article_id}/lang_urls/{language}")

    @mcp.tool(
        name="list_tags",
        description="List all Knowledge Base tags.",
    )
    async def list_tags() -> dict:
        return client.get(f"{KB_BASE}/tags/")
