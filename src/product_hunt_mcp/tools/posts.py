"""
Post-related tools for the Product Hunt MCP server.
"""

import logging
from typing import Any, Dict
from product_hunt_mcp.api.client import execute_graphql_query
from product_hunt_mcp.api.queries import POST_QUERY, POSTS_QUERY
from product_hunt_mcp.schemas.validation import POST_SCHEMA, POSTS_SCHEMA
from product_hunt_mcp.utils.common import (
    add_id_or_slug,
    apply_pagination_defaults,
    execute_and_check_query,
    extract_pagination,
    format_response,
    handle_errors,
    require_token,
)
from product_hunt_mcp.utils.validation import validate_with_schema

logger = logging.getLogger("ph_mcp")


def register_post_tools(mcp):
    """Register post-related tools with the MCP server."""

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(POST_SCHEMA)
    def get_post_details(
        id: str = None, slug: str = None, comments_count: int = 10, comments_after: str = None
    ) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific Product Hunt post by ID or slug.

        Parameters:
        - id (str, optional): The post's unique ID.
        - slug (str, optional): The post's slug (e.g., "product-hunt-api").
        - comments_count (int, optional): Number of comments to return (default: 10, max: 20).
        - comments_after (str, optional): Pagination cursor for fetching the next page of comments.

        At least one of `id` or `slug` must be provided.

        Returns:
        - success (bool): Whether the request was successful.
        - data (dict): If successful, contains:
            - id, name, description, tagline, votes, makers, topics, media, and
            - comments (paginated): { edges: [...], pageInfo: { endCursor, hasNextPage } }
        - error (dict, optional): If unsuccessful, contains error code and message.
        - rate_limits (dict): API rate limit information.

        Notes:
        - If neither `id` nor `slug` is provided, an error is returned.
        - If the post is not found, an error is returned.
        - The dedicated `get_post_comments` tool is deprecated; use this tool for paginated comments.
        """
        params = {
            k: v
            for k, v in {
                "id": id,
                "slug": slug,
                "comments_count": comments_count,
                "comments_after": comments_after,
            }.items()
            if v is not None
        }
        logger.info("posts.get_post_details called", extra=params)

        variables = {}
        add_id_or_slug(variables, id, slug)
        # Add pagination for comments if requested
        if comments_count is not None:
            variables["commentsCount"] = min(comments_count, 20)
        if comments_after:
            variables["commentsAfter"] = comments_after

        # Use the utility function to execute the query and check if post exists
        id_or_slug = id or slug
        post_data, rate_limits, error = execute_and_check_query(
            POST_QUERY, variables, "post", id_or_slug
        )

        if error:
            return format_response(False, error=error, rate_limits=rate_limits)

        return format_response(True, data=post_data, rate_limits=rate_limits)

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(POSTS_SCHEMA)
    def get_posts(
        featured: bool = None,
        topic: str = None,
        order: str = "RANKING",
        count: int = 10,
        after: str = None,
        url: str = None,
        twitter_url: str = None,
        posted_before: str = None,
        posted_after: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a list of Product Hunt posts with various filtering and sorting options.

        Parameters:
        - featured (bool, optional): Only return featured posts if True.
        - topic (str, optional): Filter by topic slug.
        - order (str, optional): Sorting order. Valid values: RANKING (default), NEWEST, VOTES, FEATURED_AT.
        - count (int, optional): Number of posts to return (default: 10, max: 20).
        - after (str, optional): Pagination cursor for next page.
        - url (str, optional): Filter posts by URL.
        - twitter_url (str, optional): Filter posts by Twitter URL.
        - posted_before (str, optional): ISO datetime to filter posts posted before this date.
        - posted_after (str, optional): ISO datetime to filter posts posted after this date.

        Returns:
        - success (bool)
        - data (dict): If successful, contains:
            - posts (list): List of post objects (id, name, description, etc.)
            - pagination (dict): { end_cursor, has_next_page }
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - This is not a keyword search; use filters to narrow results.
        - If no posts match, `posts` will be an empty list.
        - Invalid date formats return a user-friendly error.
        """
        params = {
            k: v
            for k, v in {
                "featured": featured,
                "topic": topic,
                "order": order,
                "count": count,
                "after": after,
                "url": url,
                "twitter_url": twitter_url,
                "posted_before": posted_before,
                "posted_after": posted_after,
            }.items()
            if v is not None
        }
        logger.info("posts.get_posts called", extra=params)

        # Apply pagination defaults
        variables = apply_pagination_defaults(count, after)

        # Add order parameter
        variables["order"] = order

        # Add optional filters
        if featured is not None:
            variables["featured"] = featured
        if topic:
            variables["topic"] = topic
        if url:
            variables["url"] = url
        if twitter_url:
            variables["twitterUrl"] = twitter_url
        if posted_before:
            variables["postedBefore"] = posted_before
        if posted_after:
            variables["postedAfter"] = posted_after

        result, rate_limits, error = execute_graphql_query(POSTS_QUERY, variables)

        if error:
            # If there's a GraphQL error related to date format, provide a more user-friendly message
            if (
                "code" in error
                and error["code"] == "GRAPHQL_ERROR"
                and any(
                    "postedBefore" in str(e) or "postedAfter" in str(e)
                    for e in error.get("details", [])
                )
            ):
                return format_response(
                    False,
                    error={
                        "code": "INVALID_DATE_FORMAT",
                        "message": "The provided date format is invalid. Please use ISO 8601 format (e.g., 2023-01-01T00:00:00Z)",
                    },
                    rate_limits=rate_limits,
                )
            return format_response(False, error=error, rate_limits=rate_limits)

        # Extract posts
        posts_data = result["data"]["posts"]

        return format_response(
            True,
            data={
                "posts": posts_data["edges"],
                "pagination": extract_pagination(posts_data["pageInfo"]),
            },
            rate_limits=rate_limits,
        )
