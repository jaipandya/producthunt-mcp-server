"""
Server-related tools for the Product Hunt MCP server.
"""

import logging
import importlib.metadata
from typing import Any, Dict
from product_hunt_mcp.api.client import execute_graphql_query
from product_hunt_mcp.api.queries import VIEWER_QUERY
from product_hunt_mcp.utils.common import format_response, handle_errors, require_token
from product_hunt_mcp.utils.token import check_token

logger = logging.getLogger("ph_mcp")


def register_server_tools(mcp):
    """Register server-related tools with the MCP server."""

    @mcp.tool()
    # No @handle_errors here as we want to return specific status messages
    def check_server_status() -> Dict[str, Any]:
        """
        Check the status of the Product Hunt MCP server and authentication.

        Returns:
        - status (str): "Ready", "Not initialized", "Token invalid", or "Error".
        - authenticated (bool, optional): True if authenticated, False otherwise.
        - user (dict, optional): User details if authenticated.
        - rate_limits (dict, optional): API rate limit information.
        - message (str, optional): Additional status or error message.
        """
        logger.info("server.check_server_status called")

        # 1. Check if token exists
        token_error = check_token() # Uses relative import from ..utils.token
        if token_error:
            # Use format_response for consistency, but keep specific status/message
            response = format_response(False, error=token_error)
            response["status"] = "Not initialized"
            response["message"] = token_error["message"]
            return response

        # 2. Try a simple query to check if token is valid
        try:
            # Uses relative imports from ..api.client and ..api.queries
            result, rate_limits, error = execute_graphql_query(VIEWER_QUERY)

            if error:
                response = format_response(False, error=error, rate_limits=rate_limits)
                response["status"] = "Error"
                response["message"] = f"Unable to authenticate with Product Hunt API: {error.get('message', 'Unknown error')}"
                return response

            # Check if viewer data is present (indicates successful auth)
            from ..utils.common import check_data_exists # Local import to avoid circular dependency at module level
            is_valid = check_data_exists(result.get("data", {}), "viewer")
            viewer_data = result.get("data", {}).get("viewer") if is_valid else None

            response = format_response(True, data=viewer_data, rate_limits=rate_limits)
            response["status"] = "Ready" if is_valid else "Token invalid"
            response["authenticated"] = is_valid
            if not is_valid:
                response["message"] = "Authentication successful, but no viewer data returned."
            if viewer_data and "user" in viewer_data: # Handle nested user structure if present
                response["user"] = viewer_data["user"]
            elif viewer_data:
                response["user"] = viewer_data # Assume viewer is the user object

            return response

        except Exception as e:
            logger.error(f"Unexpected error in check_server_status: {str(e)}", exc_info=True)
            response = format_response(False, error={"code": "INTERNAL_ERROR", "message": str(e)})
            response["status"] = "Error"
            response["message"] = f"Unexpected error checking API connection: {str(e)}"
            return response

