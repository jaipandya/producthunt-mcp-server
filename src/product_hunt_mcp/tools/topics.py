"""
Topic-related tools for the Product Hunt MCP server.
"""

import logging
from typing import Any, Dict
from product_hunt_mcp.api.client import execute_graphql_query
from product_hunt_mcp.api.queries import TOPIC_QUERY, TOPICS_QUERY
from product_hunt_mcp.schemas.validation import TOPIC_SCHEMA, TOPICS_SCHEMA
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


def register_topic_tools(mcp):
    """Register topic-related tools with the MCP server."""

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(TOPIC_SCHEMA)
    def get_topic(id: str = None, slug: str = None) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific topic by ID or slug.

        Parameters:
        - id (str, optional): The topic's unique ID.
        - slug (str, optional): The topic's slug (e.g., "artificial-intelligence").

        At least one of `id` or `slug` must be provided.

        Returns:
        - success (bool)
        - data (dict): If successful, contains topic details:
            - id, name, description, follower_count, posts, etc.
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - Returns an error if neither `id` nor `slug` is provided, or if the topic is not found.
        """
        params = {k: v for k, v in {"id": id, "slug": slug}.items() if v is not None}
        logger.info("topics.get_topic called", extra=params)

        variables = {}
        add_id_or_slug(variables, id, slug)

        # Execute the query and check if topic exists
        id_or_slug = id or slug
        topic_data, rate_limits, error = execute_and_check_query(
            TOPIC_QUERY, variables, "topic", id_or_slug
        )

        if error:
            return format_response(False, error=error, rate_limits=rate_limits)

        return format_response(True, data=topic_data, rate_limits=rate_limits)

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(TOPICS_SCHEMA)
    def search_topics(
        query: str = None,
        followed_by_user_id: str = None,
        order: str = "FOLLOWERS_COUNT",
        count: int = 10,
        after: str = None,
    ) -> Dict[str, Any]:
        """
        Search for topics by name or filter by user following, with optional sorting and pagination.

        Parameters:
        - query (str, optional): Search term to find topics by name.
        - followed_by_user_id (str, optional): Only topics followed by this user ID.
        - order (str, optional): Sorting order. Valid values: FOLLOWERS_COUNT (default), NAME, NEWEST.
        - count (int, optional): Number of topics to return (default: 10, max: 20).
        - after (str, optional): Pagination cursor for next page.

        Returns:
        - success (bool)
        - data (dict): If successful, contains:
            - topics (list): List of topic objects (id, name, etc.)
            - pagination (dict): { end_cursor, has_next_page }
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - If no topics match, `topics` will be an empty list.
        """
        params = {
            k: v
            for k, v in {
                "query": query,
                "followed_by_user_id": followed_by_user_id,
                "order": order,
                "count": count,
                "after": after,
            }.items()
            if v is not None
        }
        logger.info("topics.search_topics called", extra=params)

        # Apply pagination defaults
        variables = apply_pagination_defaults(count, after)

        # Add order parameter
        variables["order"] = order

        # Add optional filters
        if query:
            variables["query"] = query
        if followed_by_user_id:
            variables["followedByUserId"] = followed_by_user_id

        result, rate_limits, error = execute_graphql_query(TOPICS_QUERY, variables)

        if error:
            return format_response(False, error=error, rate_limits=rate_limits)

        # Extract topics
        topics_data = result["data"]["topics"]

        return format_response(
            True,
            data={
                "topics": topics_data["edges"],
                "pagination": extract_pagination(topics_data["pageInfo"]),
            },
            rate_limits=rate_limits,
        )
