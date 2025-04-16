# 🚀 Product Hunt MCP Server

A blazing-fast, plug-and-play [MCP](https://modelcontextprotocol.io/) server for Product Hunt, built with [FastMCP](https://github.com/jlowin/fastmcp).

---

## What is this?

**Product Hunt MCP Server** connects Product Hunt's API to any LLM or agent that speaks the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). Perfect for AI assistants, chatbots, or your own automations!

- 🔍 Get posts, collections, topics, users
- 🗳️ Get votes, comments, and more
- 🛠️ Use with Claude Desktop, Cursor, or any MCP client

---

## Quick Start

1. **Get a Product Hunt API token** ([instructions](https://www.producthunt.com/v2/docs/authentication))
2. **Install**: `pip install -e .` or use Docker
3. **Run**: `python -m product_hunt_mcp` or use Docker
4. **Configure** with your LLM/agent (see README)

---

## Features

- Get info on posts, comments, collections, topics, users
- Search/filter by topic, date, votes, etc.
- Paginated comments, user upvotes, and more
- Built for speed and compatibility

---

## Links

- [Full README & Usage](./README.md)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Product Hunt API Docs](https://www.producthunt.com/v2/docs)

---

MIT Licensed. PRs welcome! 