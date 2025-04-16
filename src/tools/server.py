"""
Server status tools for the Product Hunt MCP server.
"""

import logging
from typing import Any, Dict

from src.api.client import execute_graphql_query
from src.api.queries import VIEWER_QUERY
from src.utils.token import check_token

logger = logging.getLogger("ph_mcp")


def register_server_tools(mcp):
    """Register server-related tools with the MCP server."""

    @mcp.tool()
    def check_server_status() -> Dict[str, Any]:
        """
        Check the status of the Product Hunt MCP server and current authentication.

        Parameters:
        - None

        Returns:
        - status (str): "Ready", "Not initialized", "Token invalid", or "Error".
        - authenticated (bool, optional): True if authenticated, False otherwise.
        - user (dict, optional): User details if authenticated.
        - rate_limit (dict, optional): API rate limit information.
        - message (str, optional): Additional status or error message.

        Notes:
        - Returns "Not initialized" if the token is missing.
        - Returns "Token invalid" or "Error" if authentication fails.
        """
        logger.info("server.check_server_status called")

        # Check token
        token_error = check_token()
        if token_error:
            return {
                "status": "Not initialized",
                "message": "PRODUCT_HUNT_TOKEN not found in environment. Please set it as an environment variable to continue.",
            }

        # Try a simple query to check if token is still valid
        try:
            result, rate_limits, error = execute_graphql_query(VIEWER_QUERY)

            if error:
                return {
                    "status": "Error",
                    "message": "Unable to authenticate with Product Hunt API.",
                }

            is_valid = "data" in result and result["data"]["viewer"] is not None

            return {
                "status": "Ready" if is_valid else "Token invalid",
                "authenticated": is_valid,
                "user": result.get("data", {}).get("viewer", {}) if is_valid else None,
                "rate_limit": rate_limits,
            }
        except Exception:
            return {
                "status": "Error",
                "message": "Error checking API connection. Please check your token and network connection.",
            }
