# 🚀 Product Hunt MCP Server

[![PyPI version](https://img.shields.io/pypi/v/product-hunt-mcp.svg)](https://pypi.org/project/product-hunt-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue)](Dockerfile)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-brightgreen)](https://modelcontextprotocol.io/)

> **A plug-and-play [MCP](https://modelcontextprotocol.io/) server for Product Hunt**

---

## 📦 Quick Install

```bash
pip install product-hunt-mcp
```

## 🏃‍♂️ Quick Start Example

```bash
# Run the MCP server (requires PRODUCT_HUNT_TOKEN environment variable)
export PRODUCT_HUNT_TOKEN=your_token_here
product-hunt-mcp
```

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
- Product Hunt API token ([get one here](https://www.producthunt.com/v2/oauth/applications))
  - You'll need to create an account on Product Hunt
  - Navigate to the API Dashboard and create a new application
  - Use the `Developer Token` for the token

> **Note:** When creating a new application on Product Hunt, you will be asked for a `redirect_uri`. While the MCP server does not use the redirect URI, it is a required field. You can enter any valid URL, such as `https://localhost:8424/callback`.

### Installation

**Preferred: [uv](https://github.com/astral-sh/uv) (fast, modern Python installer)**

```bash
# Install uv if you don't have it
pip install uv
```

#### Install from PyPI (recommended)
```bash
uv pip install product-hunt-mcp
# or
pip install product-hunt-mcp
```

#### Install from GitHub (latest main branch)
```bash
uv pip install 'git+https://github.com/jaipandya/producthunt-mcp-server.git'
# or
pip install 'git+https://github.com/jaipandya/producthunt-mcp-server.git'
```

#### Install locally from source
```bash
uv pip install .
# or
pip install .
```

---

## 🚀 Usage with Claude Desktop & Cursor

Once installed, the `product-hunt-mcp` command will be available. Add it to your Claude Desktop or Cursor configuration:

```json
{
  "mcpServers": {
    "product-hunt": {
      "command": "product-hunt-mcp",
      "env": {
        "PRODUCT_HUNT_TOKEN": "your_token_here"
      }
    }
  }
}
```

- Replace `your_token_here` with your actual Product Hunt API token.
- The token **must** be set as an environment variable in your Claude Desktop or Cursor config for the server to authenticate.
- Always restart your client (Claude Desktop/Cursor) after editing the config file.

> **Tip:** On macOS, Claude Desktop may not always find the `product-hunt-mcp` command if it's not in the default PATH. If you encounter issues, you can provide the full path to the executable. After installing, run:
>
> ```bash
> which product-hunt-mcp
> ```
>
> Use the output path in your Claude Desktop config, replacing `"command": "product-hunt-mcp"` with the full path (e.g., `"command": "/Users/youruser/.local/bin/product-hunt-mcp"`).

### Finding your configuration file

- **Claude Desktop**: 
  - Windows: `%APPDATA%\claude-desktop\config.json`
  - macOS: `~/Library/Application Support/claude-desktop/config.json`
  - Linux: `~/.config/claude-desktop/config.json`

- **Cursor**:
  - Windows: `%APPDATA%\Cursor\User\settings.json`
  - macOS: `~/Library/Application Support/Cursor/User/settings.json`
  - Linux: `~/.config/Cursor/User/settings.json`

### Docker

You can also run the server using Docker:

```bash
# Build the Docker image
docker build -t product-hunt-mcp .

# Run the Docker container (interactive for MCP)
docker run -i --rm -e PRODUCT_HUNT_TOKEN=your_token_here product-hunt-mcp
```

For Claude Desktop/Cursor integration with Docker, use this configuration:

```json
{
  "mcpServers": {
    "product-hunt": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "PRODUCT_HUNT_TOKEN=your_token_here", "product-hunt-mcp"],
      "env": {}
    }
  }
}
```

> **Security Note:** Your `PRODUCT_HUNT_TOKEN` is sensitive. Do not share it or commit it to version control.

---

## 🛠️ MCP Tools

| Tool                | Description                                 | Key Parameters |
|---------------------|---------------------------------------------|----------------|
| get_post_details    | Get info about a specific post              | `id` or `slug`, `comments_count`, `comments_after` |
| get_posts           | Get posts with filters                      | `topic`, `order`, `count`, `featured`, `posted_before`, `posted_after` |
| get_comment         | Get info about a specific comment           | `id` (required) |
| get_post_comments   | Get comments for a post                     | `post_id` or `slug`, `order`, `count`, `after` |
| get_collection      | Get info about a collection                 | `id` or `slug` |
| get_collections     | Get collections with filters                | `featured`, `user_id`, `post_id`, `order`, `count` |
| get_topic           | Get info about a topic                      | `id` or `slug` |
| search_topics       | Search topics                               | `query`, `followed_by_user_id`, `order`, `count` |
| get_user            | Get info about a user                       | `id` or `username`, `posts_type`, `posts_count` |
| get_viewer          | Get info about the authenticated user       | None |
| check_server_status | Check server/API status & authentication    | None |

---

## 🏗️ Project Structure

```
product-hunt-mcp/
├── src/
│   └── product_hunt_mcp/ # Main package directory
│       ├── __init__.py
│       ├── cli.py        # Command-line entry point
│       ├── api/          # API clients & queries
│       ├── schemas/      # Data validation schemas
│       ├── tools/        # MCP tool definitions
│       └── utils/        # Utility functions
├── pyproject.toml      # Project metadata, dependencies, build config
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── Dockerfile
└── ... (config files, etc.)
```

---

## 🔄 Rate Limiting

The Product Hunt API has rate limits that this client respects. If you encounter rate limit errors, the client will inform you when the rate limit resets. You can check your current rate limit status using the `get_api_rate_limits` or `check_server_status` tools.

---

## 🐛 Troubleshooting

- **Missing token**: Ensure your `PRODUCT_HUNT_TOKEN` is correctly set as an environment variable.
- **Connection issues**: Verify your internet connection and that the Product Hunt API is accessible.
- **Rate limiting**: If you hit rate limits, wait until the reset time or reduce your query frequency.
- **Claude Desktop/Cursor not finding the server**: Verify the path to your Python executable and restart the client.

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

## 📝 Notes

- This project is not affiliated with Product Hunt.
- The Product Hunt API is subject to change.

---

## 📜 License

MIT