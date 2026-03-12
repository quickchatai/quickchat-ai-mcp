from mcp.server.fastmcp import FastMCP

from src.client import QuickchatClient

IMPORT_BASE = "/v1/api/knowledge_base/import_external"
SOURCES_BASE = "/v1/api/knowledge_base/sources"
INTERCOM_BASE = "/v1/api/knowledge_base/intercom"


def register_tools(mcp: FastMCP, client: QuickchatClient) -> None:
    @mcp.tool(
        name="scrape_website",
        description="Scrape a website and import content into the Knowledge Base.",
    )
    async def scrape_website(url: str, **kwargs) -> dict:
        body = {"url": url, **kwargs}
        return client.post(f"{IMPORT_BASE}/website", json=body)

    @mcp.tool(
        name="import_youtube_transcript",
        description="Import a YouTube video transcript into the Knowledge Base.",
    )
    async def import_youtube_transcript(url: str, **kwargs) -> dict:
        body = {"url": url, **kwargs}
        return client.post(f"{IMPORT_BASE}/youtube", json=body)

    @mcp.tool(
        name="import_sitemap",
        description="Import pages from a sitemap URL into the Knowledge Base.",
    )
    async def import_sitemap(url: str, **kwargs) -> dict:
        body = {"url": url, **kwargs}
        return client.post(f"{IMPORT_BASE}/site-map", json=body)

    @mcp.tool(
        name="scrape_link_list",
        description="Scrape a list of URLs and import content into the Knowledge Base.",
    )
    async def scrape_link_list(urls: list[str], **kwargs) -> dict:
        body = {"urls": urls, **kwargs}
        return client.post(f"{IMPORT_BASE}/scrape-list", json=body)

    @mcp.tool(
        name="import_source_articles",
        description="Import articles from a connected source into the Knowledge Base.",
    )
    async def import_source_articles(source: str, data: dict | None = None) -> dict:
        return client.post(f"{SOURCES_BASE}/{source}/import", json=data)

    @mcp.tool(
        name="delete_source_articles",
        description="Delete articles imported from a connected source.",
    )
    async def delete_source_articles(source: str, data: dict | None = None) -> dict:
        return client.post(f"{SOURCES_BASE}/{source}/delete", json=data)

    @mcp.tool(
        name="diff_source_articles",
        description="Show differences between source articles and Knowledge Base articles.",
    )
    async def diff_source_articles(source: str, data: dict | None = None) -> dict:
        return client.post(f"{SOURCES_BASE}/{source}/articles_diff", json=data)

    @mcp.tool(
        name="refresh_intercom_articles",
        description="Refresh the list of available Intercom articles.",
    )
    async def refresh_intercom_articles() -> dict:
        return client.post(f"{INTERCOM_BASE}/refresh_articles")

    @mcp.tool(
        name="import_intercom_articles",
        description="Import Intercom articles into the Knowledge Base.",
    )
    async def import_intercom_articles(data: dict | None = None) -> dict:
        return client.post(f"{INTERCOM_BASE}/import", json=data)

    @mcp.tool(
        name="delete_intercom_articles",
        description="Delete Intercom articles from the Knowledge Base.",
    )
    async def delete_intercom_articles(data: dict | None = None) -> dict:
        return client.post(f"{INTERCOM_BASE}/delete", json=data)

    @mcp.tool(
        name="diff_intercom_articles",
        description="Show differences between Intercom articles and Knowledge Base articles.",
    )
    async def diff_intercom_articles() -> dict:
        return client.get(f"{INTERCOM_BASE}/articles_diff")
