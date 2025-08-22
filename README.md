<p align="center">
  <img src="https://raw.githubusercontent.com/incentivai/quickchat-ai-mcp/main/img/background.jpg"/>
</p>

# Quickchat AI MCP server

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/incentivai/quickchat-ai-mcp)](https://archestra.ai/mcp-catalog/incentivai__quickchat-ai-mcp)
The [Quickchat AI](https://quickchat.ai) MCP ([Model Context Protocol](https://modelcontextprotocol.io/)) server allows you to let anyone plug in your Quickchat AI Agent into their favourite AI app such as Claude Desktop, Cursor, VS Code, Windsurf and [more](https://modelcontextprotocol.io/clients#feature-support-matrix).

## Quickstart
1. Create a [Quickchat AI account](https://app.quickchat.ai) and start a 7-day trial of any plan.
2. Set up your AI's Knowledge Base, capabilities and settings.
3. Go to the MCP page to activate your MCP. Give it **Name**, **Description** and (optional) **Command**. They are important - AI apps need to understand when to contact your AI, what its capabilities and knowledge are.
4. That's it! Now you're ready to test your Quickchat AI via any AI app and show it to the world!

<p align="center">
  <img src="https://raw.githubusercontent.com/incentivai/quickchat-ai-mcp/main/img/claude_tool_anatomy.png" alt="Claude tool anatomy" width="600"/>
  <br/>
  <sub>Claude tool anatomy</sub>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/incentivai/quickchat-ai-mcp/main/img/cursor_tool_anatomy.png" alt="Cursor tool anatomy" width="600"/>
  <br/>
  <sub>Cursor tool anatomy</sub>
</p>

## Useful links
- Quickstart video [youtube.com/watch?v=JE3dNiyZO8w](https://www.youtube.com/watch?v=JE3dNiyZO8w)
- Quickstart blog post: [quickchat.ai/post/how-to-launch-your-quickchat-ai-mcp](https://www.quickchat.ai/post/how-to-launch-your-quickchat-ai-mcp)
- MCP (Model Context Protocol) explained: [quickchat.ai/post/mcp-explained](https://www.quickchat.ai/post/mcp-explained)
- The Quickchat AI MCP package on PyPI: [pypi.org/project/quickchat-ai-mcp](https://pypi.org/project/quickchat-ai-mcp)
- The Quickchat AI MCP GitHub repo: [github.com/quickchatai/quickchat-ai-mcp](https://github.com/quickchatai/quickchat-ai-mcp)

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
        "SCENARIO_ID": "< QUICKCHAT AI SCENARIO ID >",
        "API_KEY": "< QUICKCHAT AI API KEY >"
      }
    }
  }
}
```

Go to the `Quickchat AI app > MCP > Integration` to find the above snippet with the values of MCP Name, SCENARIO_ID and API_KEY filled out.

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
        "SCENARIO_ID": "< QUICKCHAT AI SCENARIO ID >",
        "API_KEY": "< QUICKCHAT AI API KEY >"
      }
    }
  }
}
```

As before, you can find values for MCP Name, SCENARIO_ID and API_KEY at `Quickchat AI app > MCP > Integration`.

## Test with other AI apps

Other AI apps will most likely require the same configuration but the actual steps to include it in the App itself will be different. We will be expanding this README as we go along.

## Launch your Quickchat AI MCP to the world! 

```
⛔️ Do not publish your Quickchat API key to your users!
```

Once you're ready to let other users connect your Quickchat AI MCP to their AI apps, share configuration snippet with them! However, you need to make sure they can use your Quickchat AI MCP **without your Quickchat API key**. Here is how to do that:
1. On the Quickchat App MCP page, turn the **Require API key** toggle **OFF**.
2. Share the configuration snippet _without the API key_:

```JSON
{
  "mcpServers": {
    "< QUICKCHAT AI MCP NAME >": {
      "command": "uvx",
      "args": ["quickchat-ai-mcp"],
      "env": {
        "SCENARIO_ID": "< QUICKCHAT AI SCENARIO ID >"
      }
    }
  }
}
```
---

## Cool features
- You can control all aspects of your MCP from the Quickchat AI dashboard. _One click and your change is deployed_. That includes the MCP name and description - all your users need to do is refresh their MCP connection.
- View all conversations in the Quickchat Inbox. Remember: those won't be the exact messages your users send to their AI app but rather the transcript of the AI <> AI interaction between their AI app and your Quickchat AI. 🤯
- Unlike most MCP implementations, this isn't a static tool handed to an AI. It's an open-ended way to send messages to Quickchat AI Agents you create. 🙌 

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
        "SCENARIO_ID": "< QUICKCHAT AI SCENARIO ID >",
        "API_KEY": "< QUICKCHAT AI API KEY >"
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

## GitHub Star History

[![Star History Chart](https://api.star-history.com/svg?repos=quickchatai/quickchat-ai-mcp&type=Date)](https://www.star-history.com/#quickchatai/quickchat-ai-mcp&Date)