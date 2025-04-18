#!/usr/bin/env python3
"""
Product Hunt MCP Server CLI Entry Point

Command-line interface entry point for the Product Hunt MCP server.
"""

import logging
import os
from product_hunt_mcp.tools.collections import register_collection_tools
from product_hunt_mcp.tools.comments import register_comment_tools
from product_hunt_mcp.tools.posts import register_post_tools
from product_hunt_mcp.tools.server import register_server_tools
from product_hunt_mcp.tools.topics import register_topic_tools
from product_hunt_mcp.tools.users import register_user_tools

# fastmcp is an external dependency
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ph_mcp.cli") # Adjusted logger name

__version__ = "0.1.0" # Consider getting this from the package metadata later

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