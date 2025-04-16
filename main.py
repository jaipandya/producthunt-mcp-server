#!/usr/bin/env python3
"""
Product Hunt MCP Server

Simple entry point for the Product Hunt MCP server.
"""

import logging
import os

# Import tools
from src.tools.collections import register_collection_tools
from src.tools.comments import register_comment_tools
from src.tools.posts import register_post_tools
from src.tools.server import register_server_tools
from src.tools.topics import register_topic_tools
from src.tools.users import register_user_tools

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ph_mcp")


def main():
    """Run the Product Hunt MCP server."""
    # Create MCP server
    mcp = FastMCP("Product Hunt MCP 🚀")

    # Register all tools
    register_server_tools(mcp)
    register_post_tools(mcp)
    register_comment_tools(mcp)
    register_collection_tools(mcp)
    register_topic_tools(mcp)
    register_user_tools(mcp)

    logger.info("Starting Product Hunt MCP server...")

    # Run server with default transport
    mcp.run()


if __name__ == "__main__":
    main()
