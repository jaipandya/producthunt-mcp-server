# 🚀 Product Hunt MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue)](Dockerfile)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-brightgreen)](https://modelcontextprotocol.io/)

> **A blazing-fast, plug-and-play [MCP](https://modelcontextprotocol.io/) server for Product Hunt, built with [FastMCP](https://github.com/jlowin/fastmcp).**

---

## ✨ What is this?

**Product Hunt MCP Server** connects Product Hunt's API to any LLM or agent that speaks the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). Perfect for AI assistants, chatbots, or your own automations!

- 🔍 Get posts, collections, topics, users
- 🗳️ Get votes, comments, and more
- 🛠️ Use with Claude Desktop, Cursor, or any MCP client

---

## 🛠️ Features

- Get detailed info on posts, comments, collections, topics, users
- Search/filter by topic, date, votes, etc.
- Paginated comments, user upvotes, and more
- Built with [FastMCP](https://github.com/jlowin/fastmcp) for speed and compatibility

---

## 🧑‍💻 Who is this for?

- **AI/LLM users**: Plug into Claude Desktop, Cursor, or your own agent
- **Developers**: Build bots, dashboards, or automations with Product Hunt data
- **Tinkerers**: Explore the MCP ecosystem and build your own tools

---

## 🏁 Setup

### Prerequisites

- Python 3.10+
- Product Hunt API token ([get one here](https://www.producthunt.com/v2/docs/authentication))
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Installation

```bash
pip install uv
uv pip install -e .
```

---

## 🚀 Usage with Claude Desktop & Cursor

Add to your Claude Desktop or Cursor configuration:

```json
{
  "mcpServers": {
    "product-hunt": {
      "command": "uv",
      "args": ["run", "product-hunt-mcp"],
      "env": {
        "PRODUCT_HUNT_TOKEN": "your_token_here"
      }
    }
  }
}
```

- Replace `your_token_here` with your actual Product Hunt API token.
- The token must be set as an environment variable in your Claude Desktop or Cursor config. 
- Always restart your client after editing the config file.

### Docker

You can also run the server in STDIO mode using Docker:

```bash
docker build -t product-hunt-mcp .
docker run -i --rm -e PRODUCT_HUNT_TOKEN=your_token_here product-hunt-mcp
```

---

## 🛠️ MCP Tools

| Tool                | Description                                 |
|---------------------|---------------------------------------------|
| get_post_details    | Get info about a specific post              |
| get_posts           | Get posts with filters                      |
| get_comment         | Get info about a specific comment           |
| get_post_comments   | Get comments for a post                     |
| get_collection      | Get info about a collection                 |
| get_collections     | Get collections with filters                |
| get_topic           | Get info about a topic                      |
| search_topics       | Search topics                               |
| get_user            | Get info about a user                       |
| get_viewer          | Get info about the authenticated user       |
| check_server_status | Check server/API status                     |

---

## 🏗️ Project Structure

```
product-hunt-mcp/
├── main.py             # Entry point
├── pyproject.toml      # Project metadata and dependencies
├── Dockerfile          # Docker configuration
└── src/                # Source code
    ├── api/            # API clients
    ├── schemas/        # Data models
    ├── tools/          # MCP tools
    └── utils/          # Utility functions
```

---

## 🤝 Contributing

- PRs and issues welcome!
- Please follow [PEP8](https://peps.python.org/pep-0008/) and use [ruff](https://github.com/charliermarsh/ruff) for linting.
- See `pyproject.toml` for dev dependencies.

---

## 🌐 Links

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Product Hunt API Docs](https://www.producthunt.com/v2/docs)
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

---

## 📜 License

MIT
