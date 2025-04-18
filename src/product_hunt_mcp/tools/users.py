"""
User-related tools for the Product Hunt MCP server.
"""

import logging
from typing import Any, Dict
from product_hunt_mcp.api.client import execute_graphql_query
from product_hunt_mcp.api.queries import USER_POSTS_QUERY, USER_QUERY, USER_VOTED_POSTS_QUERY, VIEWER_QUERY
from product_hunt_mcp.schemas.validation import USER_SCHEMA
from product_hunt_mcp.utils.common import (
    apply_pagination_defaults,
    check_data_exists,
    execute_and_check_query,
    format_response,
    handle_errors,
    require_token,
)
from product_hunt_mcp.utils.validation import validate_with_schema

logger = logging.getLogger("ph_mcp")


def register_user_tools(mcp):
    """Register user-related tools with the MCP server."""

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(USER_SCHEMA)
    def get_user(
        id: str = None,
        username: str = None,
        posts_type: str = None,
        posts_count: int = None,
        posts_after: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve user information by ID or username, with optional retrieval of their posts.

        Parameters:
        - id (str, optional): The user's unique ID.
        - username (str, optional): The user's username.
        - posts_type (str, optional): Type of posts to retrieve. Valid values: MADE (default), VOTED.
        - posts_count (int, optional): Number of posts to return (default: 10, max: 20).
        - posts_after (str, optional): Pagination cursor for next page of posts.

        At least one of `id` or `username` must be provided.

        Returns:
        - success (bool)
        - data (dict): If successful, contains user details and optionally their posts.
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - Returns an error if neither `id` nor `username` is provided, or if the user is not found.
        """
        params = {
            k: v
            for k, v in {
                "id": id,
                "username": username,
                "posts_type": posts_type,
                "posts_count": posts_count,
                "posts_after": posts_after,
            }.items()
            if v is not None
        }
        logger.info("users.get_user called", extra=params)

        # Determine if posts are being requested
        requesting_posts = posts_type is not None or posts_count is not None

        # Apply sensible defaults if posts are being requested
        if requesting_posts:
            posts_type = posts_type or "MADE"
            posts_count = posts_count or 10
        else:
            posts_type = None
            posts_count = None

        # Set up common variables
        variables = {}
        if id:
            variables["id"] = id
        if username:
            variables["username"] = username

        # Normalize posts_type
        posts_type = posts_type.upper() if posts_type else None

        # Case 1: Basic user info (no posts requested)
        if not requesting_posts:
            result, rate_limits, error = execute_graphql_query(USER_QUERY, variables)
            if error:
                return format_response(False, error=error, rate_limits=rate_limits)
            if not check_data_exists(result["data"], "user"):
                id_or_username = id or username
                return format_response(
                    False,
                    error={
                        "code": "NOT_FOUND",
                        "message": f"User with ID/username '{id_or_username}' not found",
                    },
                    rate_limits=rate_limits,
                )
            return format_response(True, data=result["data"]["user"], rate_limits=rate_limits)

        # Case 2 & 3: Posts requested (made or voted)
        # Set up pagination
        pagination = apply_pagination_defaults(posts_count, posts_after)
        variables.update(pagination)

        # Choose query based on posts_type
        if posts_type == "MADE":
            query = USER_POSTS_QUERY
        elif posts_type == "VOTED":
            query = USER_VOTED_POSTS_QUERY
        else:
            return format_response(
                False,
                error={
                    "code": "INVALID_PARAMETER",
                    "message": f"Invalid posts_type: {posts_type}. Valid values are MADE, VOTED.",
                },
            )

        # Execute the appropriate query
        result, rate_limits, error = execute_graphql_query(query, variables)
        if error:
            return format_response(False, error=error, rate_limits=rate_limits)
        if not check_data_exists(result["data"], "user"):
            id_or_username = id or username
            return format_response(
                False,
                error={
                    "code": "NOT_FOUND",
                    "message": f"User with ID/username '{id_or_username}' not found",
                },
                rate_limits=rate_limits,
            )
        user_data = result["data"]["user"]
        # Format response based on the query type
        if posts_type == "MADE" and check_data_exists(user_data, "madePosts"):
            posts_data = user_data["madePosts"]
            response_data = {
                "id": user_data["id"],
                "posts": posts_data
            }
            return format_response(True, data=response_data, rate_limits=rate_limits)
        elif posts_type == "VOTED" and check_data_exists(user_data, "votedPosts"):
            posts_data = user_data["votedPosts"]
            response_data = {
                "id": user_data["id"],
                "posts": posts_data
            }
            return format_response(True, data=response_data, rate_limits=rate_limits)
        # If we get here, the posts field wasn't in the response, just return what we have
        return format_response(True, data=user_data, rate_limits=rate_limits)

    @mcp.tool()
    @require_token
    @handle_errors
    def get_viewer() -> Dict[str, Any]:
        """
        Retrieve information about the currently authenticated user.

        Parameters:
        - None

        Returns:
        - success (bool)
        - data (dict): If successful, contains user details.
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - Returns an error if the token is invalid or expired.
        """
        logger.info("users.get_viewer called")

        result, rate_limits, error = execute_graphql_query(VIEWER_QUERY)

        if error:
            return format_response(False, error=error, rate_limits=rate_limits)

        # Check if viewer info exists
        viewer_exists = check_data_exists(result["data"], "viewer")

        if not viewer_exists:
            return format_response(
                False,
                error={
                    "code": "AUTHENTICATION_ERROR",
                    "message": "Unable to get viewer information. Token may be invalid or expired.",
                },
                rate_limits=rate_limits,
            )

        # Extract viewer data
        viewer_data = result["data"]["viewer"]

        # Check if the user field exists for nested viewer structure
        if "user" in viewer_data and viewer_data["user"] is not None:
            viewer_data = viewer_data["user"]

        return format_response(True, data=viewer_data, rate_limits=rate_limits)
