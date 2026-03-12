<p align="center">
  <img src="img/background.jpg"/>
</p>

# Quickchat AI MCP server

The [Quickchat AI](https://quickchat.ai) MCP ([Model Context Protocol](https://modelcontextprotocol.io/)) server allows you to let anyone plug in your Quickchat AI Agent into their favourite AI app such as Claude Desktop, Cursor, VS Code, Windsurf and [more](https://modelcontextprotocol.io/clients#feature-support-matrix).

## Quickstart
1. Create a [Quickchat AI account](https://app.quickchat.ai) and start a 7-day trial of any plan.
2. Set up your AI's Knowledge Base, capabilities and settings.
3. Go to the MCP page to activate your MCP. Give it **Name**, **Description** and (optional) **Command**. They are important - AI apps need to understand when to contact your AI, what its capabilities and knowledge are.
4. That's it! Now you're ready to test your Quickchat AI via any AI app and show it to the world!

<p align="center">
  <img src="img/claude_tool_anatomy.png" alt="Claude tool anatomy" width="600"/>
  <br/>
  <sub>Claude tool anatomy</sub>
</p>

<p align="center">
  <img src="img/cursor_tool_anatomy.png" alt="Cursor tool anatomy" width="600"/>
  <br/>
  <sub>Cursor tool anatomy</sub>
</p>

## Useful links
- Quickstart video [youtube.com/watch?v=JE3dNiyZO8w](https://www.youtube.com/watch?v=JE3dNiyZO8w)
- Quickstart blog post: [quickchat.ai/post/how-to-launch-your-quickchat-ai-mcp](https://www.quickchat.ai/post/how-to-launch-your-quickchat-ai-mcp)
- MCP (Model Context Protocol) explained: [quickchat.ai/post/mcp-explained](https://www.quickchat.ai/post/mcp-explained)
- The Quickchat AI MCP package on PyPI: [pypi.org/project/quickchat-ai-mcp](https://pypi.org/project/quickchat-ai-mcp)


## Prerequisite
Install `uv` using:
```commandline
curl -LsSf https://astral.sh/uv/install.sh | sh
```

or read more [here](https://docs.astral.sh/uv/getting-started/installation/).

## Test with Claude Desktop

### Configuration
Go to `Settings > Developer > Edit` Config. Open the _claude_desktop_config.json_ file in a text editor. If you're just starting out, the file is going to look like this:

```JSON
{
  "mcpServers": {}
}
```

This is where you can define all the MCPs your Claude Desktop has access to. Here is how you add your Quickchat AI MCP:

```JSON
{
  "mcpServers": {
    "< QUICKCHAT AI MCP NAME >": {
      "command": "uvx",
      "args": ["quickchat-ai-mcp"],
      "env": {
        "API_TOKEN": "< QUICKCHAT AI API TOKEN >"
      }
    }
  }
}
```

Go to the `Quickchat AI app > MCP > Integration` to find the above snippet with the values of MCP Name and API_TOKEN filled out.

## Test with Cursor

### Configuration
Go to `Settings > Cursor Settings > MCP > Add new global MCP server` and include the Quickchat AI MCP snippet:

```JSON
{
  "mcpServers": {
    "< QUICKCHAT AI MCP NAME >": {
      "command": "uvx",
      "args": ["quickchat-ai-mcp"],
      "env": {
        "API_TOKEN": "< QUICKCHAT AI API TOKEN >"
      }
    }
  }
}
```

As before, you can find values for MCP Name and API_TOKEN at `Quickchat AI app > MCP > Integration`.

## Test with other AI apps

Other AI apps will most likely require the same configuration but the actual steps to include it in the App itself will be different. We will be expanding this README as we go along.

## HTTP mode (streamable-http)

The MCP server can also run as an HTTP server using the `streamable-http` transport. In this mode it listens for POST requests on `/mcp` and requires a Bearer token in the `Authorization` header.

### Configuration

Set the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | Set to `streamable-http` to enable HTTP mode |
| `HOST` | `0.0.0.0` | Host to bind the HTTP server to |
| `PORT` | `8000` | Port to listen on |

### Starting the server

```commandline
TRANSPORT=streamable-http PORT=8000 API_TOKEN=<your-token> uv run python -m src
```

### Making requests

All requests must include an `Authorization: Bearer <token>` header. Requests without a token will receive a 401 response.

```commandline
curl -X POST http://localhost:8000/mcp \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

---

## Available tools

This MCP server exposes the following tools:

### Chat
- **send_message** (or custom command name) — Send a message to your Quickchat AI agent

### Knowledge Base
- **get_knowledge_base_settings** — Get Knowledge Base settings
- **update_knowledge_base_settings** — Update Knowledge Base settings
- **create_article** — Create a new Knowledge Base article
- **list_articles** — List Knowledge Base articles with filters
- **get_article** — Get a specific article by ID
- **update_article** — Update an article
- **delete_articles** — Delete articles by IDs
- **search_articles** — Search articles by content similarity
- **list_paragraphs** — List all paragraphs across articles
- **get_article_language_url** — Get language-specific URL for an article
- **create_article_language_url** — Create language-specific URL for an article
- **update_article_language_url** — Update language-specific URL for an article
- **delete_article_language_url** — Delete language-specific URL for an article
- **list_tags** — List all Knowledge Base tags

### Conversations
- **list_conversations** — List conversations
- **get_conversation** — Get a specific conversation by ID
- **get_conversation_metadata** — Get metadata for a conversation
- **set_conversation_metadata** — Set metadata for a conversation

### AI Actions
- **create_ai_action** — Create a new Knowledge Base AI Action
- **get_ai_action** — Get an AI Action by ID
- **update_ai_action** — Update an AI Action

### Import
- **scrape_website** — Scrape a website and import content
- **import_youtube_transcript** — Import a YouTube video transcript
- **import_sitemap** — Import pages from a sitemap URL
- **scrape_link_list** — Scrape a list of URLs and import content
- **import_source_articles** — Import articles from a connected source
- **delete_source_articles** — Delete articles imported from a source
- **diff_source_articles** — Show diff between source and KB articles
- **refresh_intercom_articles** — Refresh the list of Intercom articles
- **import_intercom_articles** — Import Intercom articles
- **delete_intercom_articles** — Delete Intercom articles from KB
- **diff_intercom_articles** — Show diff between Intercom and KB articles

---

## Cool features
- You can control all aspects of your MCP from the Quickchat AI dashboard. _One click and your change is deployed_. That includes the MCP name and description - all your users need to do is refresh their MCP connection.
- View all conversations in the Quickchat Inbox. Remember: those won't be the exact messages your users send to their AI app but rather the transcript of the AI <> AI interaction between their AI app and your Quickchat AI.
- Unlike most MCP implementations, this isn't a static tool handed to an AI. It's an open-ended way to send messages to Quickchat AI Agents you create.

---

## Running from source

### Debugging with the [MCP inspector](https://modelcontextprotocol.io/docs/tools/inspector)

```commandline
uv run mcp dev src/__main__.py
```

### Debugging with Claude Desktop, Cursor or other AI apps

Use the following JSON configuration:

```JSON
{
  "mcpServers": {
    "< QUICKCHAT AI MCP NAME >": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "requests",
        "mcp",
        "run",
        "< YOUR PATH>/quickchat-ai-mcp/src/__main__.py"
      ],
      "env": {
        "API_TOKEN": "< QUICKCHAT AI API TOKEN >"
      }
    }
  }
}
```

### Testing

Make sure your code is properly formatted and all tests are passing:

```commandline
ruff check --fix
ruff format
uv run pytest
```
