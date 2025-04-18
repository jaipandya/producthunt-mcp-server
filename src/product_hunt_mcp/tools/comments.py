"""
Comment-related tools for the Product Hunt MCP server.
"""

import logging
from typing import Any, Dict
from product_hunt_mcp.api.client import execute_graphql_query
from product_hunt_mcp.api.queries import COMMENT_QUERY, COMMENTS_QUERY
from product_hunt_mcp.schemas.validation import COMMENT_SCHEMA, POST_COMMENTS_SCHEMA
from product_hunt_mcp.utils.common import (
    apply_pagination_defaults,
    check_data_exists,
    execute_and_check_query,
    extract_pagination,
    format_response,
    handle_errors,
    require_token,
)
from product_hunt_mcp.utils.validation import validate_with_schema

logger = logging.getLogger("ph_mcp")


def register_comment_tools(mcp):
    """Register comment-related tools with the MCP server."""

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(COMMENT_SCHEMA)
    def get_comment(id: str = None) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific comment by ID.

        Parameters:
        - id (str, required): The comment's unique ID.

        Returns:
        - success (bool)
        - data (dict): If successful, contains comment details:
            - id, content, created_at, user, post, etc.
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - Returns an error if the comment is not found.
        """
        params = {k: v for k, v in {"id": id}.items() if v is not None}
        logger.info("comments.get_comment called", extra=params)

        comment_data, rate_limits, error = execute_and_check_query(
            COMMENT_QUERY, {"id": id}, "comment", id
        )

        if error:
            return format_response(False, error=error, rate_limits=rate_limits)

        return format_response(True, data=comment_data, rate_limits=rate_limits)

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(POST_COMMENTS_SCHEMA)
    def get_post_comments(
        post_id: str = None,
        slug: str = None,
        order: str = None,
        count: int = None,
        after: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve comments for a specific post by post ID or slug, with optional sorting and pagination.

        Parameters:
        - post_id (str, optional): The post's unique ID.
        - slug (str, optional): The post's slug.
        - order (str, optional): Sorting order. Valid values: NEWEST (default), OLDEST, VOTES.
        - count (int, optional): Number of comments to return (default: 10, max: 20).
        - after (str, optional): Pagination cursor for next page.

        Returns:
        - success (bool)
        - data (dict): If successful, contains:
            - comments (list): List of comment objects (id, content, etc.)
            - pagination (dict): { end_cursor, has_next_page }
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - Returns an error if the post is not found.
        """
        params = {
            k: v
            for k, v in {
                "post_id": post_id,
                "slug": slug,
                "order": order,
                "count": count,
                "after": after,
            }.items()
            if v is not None
        }
        logger.info("comments.get_post_comments called", extra=params)

        variables = {}

        # Prepare variables
        if post_id:
            variables["id"] = post_id
        if slug:
            variables["slug"] = slug

        # Apply pagination defaults
        pagination_vars = apply_pagination_defaults(count, after)
        variables.update(pagination_vars)

        # Apply order
        if order:
            variables["order"] = order

        result, rate_limits, error = execute_graphql_query(COMMENTS_QUERY, variables)

        if error:
            return format_response(False, error=error, rate_limits=rate_limits)

        # Check if post exists based on comments data
        post_exists = check_data_exists(result["data"], "post")

        if not post_exists:
            id_or_slug = post_id or slug
            return format_response(
                False,
                error={
                    "code": "NOT_FOUND",
                    "message": f"Post with ID/slug '{id_or_slug}' not found",
                },
                rate_limits=rate_limits,
            )

        # Extract comments
        comments_data = result["data"]["post"]["comments"]

        return format_response(
            True,
            data={
                "comments": comments_data["edges"],
                "pagination": extract_pagination(comments_data["pageInfo"]),
            },
            rate_limits=rate_limits,
        )
