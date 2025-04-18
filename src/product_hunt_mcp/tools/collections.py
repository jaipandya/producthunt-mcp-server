"""
Collection-related tools for the Product Hunt MCP server.
"""

import logging
from typing import Any, Dict
from product_hunt_mcp.api.client import execute_graphql_query
from product_hunt_mcp.api.queries import COLLECTION_QUERY, COLLECTIONS_QUERY
from product_hunt_mcp.schemas.validation import COLLECTION_SCHEMA, COLLECTIONS_SCHEMA
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


def register_collection_tools(mcp):
    """Register collection-related tools with the MCP server."""

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(COLLECTION_SCHEMA)
    def get_collection(id: str = None, slug: str = None) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific collection by ID or slug.

        Parameters:
        - id (str, optional): The collection's unique ID.
        - slug (str, optional): The collection's slug (e.g., "best-productivity-apps").

        At least one of `id` or `slug` must be provided.

        Returns:
        - success (bool)
        - data (dict): If successful, contains collection details:
            - id, name, description, follower_count, posts, etc.
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - Returns an error if neither `id` nor `slug` is provided, or if the collection is not found.
        """
        params = {k: v for k, v in {"id": id, "slug": slug}.items() if v is not None}
        logger.info("collections.get_collection called", extra=params)

        variables = {}
        add_id_or_slug(variables, id, slug)

        # Execute the query and check if collection exists
        id_or_slug = id or slug
        collection_data, rate_limits, error = execute_and_check_query(
            COLLECTION_QUERY, variables, "collection", id_or_slug
        )

        if error:
            return format_response(False, error=error, rate_limits=rate_limits)

        return format_response(True, data=collection_data, rate_limits=rate_limits)

    @mcp.tool()
    @require_token
    @handle_errors
    @validate_with_schema(COLLECTIONS_SCHEMA)
    def get_collections(
        featured: bool = None,
        user_id: str = None,
        post_id: str = None,
        order: str = "FOLLOWERS_COUNT",
        count: int = 10,
        after: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a list of collections with optional filters.

        Parameters:
        - featured (bool, optional): Only return featured collections if True.
        - user_id (str, optional): Filter to collections created by this user ID.
        - post_id (str, optional): Filter to collections that include this post ID.
        - order (str, optional): Sorting order. Valid values: FOLLOWERS_COUNT (default), NEWEST.
        - count (int, optional): Number of collections to return (default: 10, max: 20).
        - after (str, optional): Pagination cursor for next page.

        Returns:
        - success (bool)
        - data (dict): If successful, contains:
            - collections (list): List of collection objects (id, name, etc.)
            - pagination (dict): { end_cursor, has_next_page }
        - error (dict, optional)
        - rate_limits (dict)

        Notes:
        - If no collections match, `collections` will be an empty list.
        """
        params = {
            k: v
            for k, v in {
                "featured": featured,
                "user_id": user_id,
                "post_id": post_id,
                "order": order,
                "count": count,
                "after": after,
            }.items()
            if v is not None
        }
        logger.info("collections.get_collections called", extra=params)

        # Apply pagination defaults
        variables = apply_pagination_defaults(count, after)

        # Add order parameter
        variables["order"] = order

        # Add optional filters
        if featured is not None:
            variables["featured"] = featured
        if user_id:
            variables["userId"] = user_id
        if post_id:
            variables["postId"] = post_id

        result, rate_limits, error = execute_graphql_query(COLLECTIONS_QUERY, variables)

        if error:
            return format_response(False, error=error, rate_limits=rate_limits)

        # Extract collections
        collections_data = result["data"]["collections"]

        return format_response(
            True,
            data={
                "collections": collections_data["edges"],
                "pagination": extract_pagination(collections_data["pageInfo"]),
            },
            rate_limits=rate_limits,
        )
