"""
Common utility functions
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, cast

from product_hunt_mcp.utils.rate_limit import RateLimitManager
from product_hunt_mcp.utils.token import get_token, check_token

logger = logging.getLogger("ph_mcp")

# Type variables for function decorators
F = TypeVar("F", bound=Callable[..., Dict[str, Any]])


def require_token(func: F) -> F:
    """Decorator to check if Product Hunt token exists before executing function"""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        error = check_token()
        if error:
            return format_response(False, error=error)
        return func(*args, **kwargs)

    return cast(F, wrapper)


def handle_errors(func: F) -> F:
    """Decorator to handle exceptions in tool functions"""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return format_response(False, error={"code": "INTERNAL_ERROR", "message": str(e)})

    return cast(F, wrapper)


def format_response(
    success: bool, data: Any = None, error: Any = None, rate_limits: Any = None, warning: Any = None
) -> Dict[str, Any]:
    """Format a standard response for MCP tools"""
    response = {"success": success}

    if data is not None:
        response["data"] = data

    if error is not None:
        response["error"] = error

    if warning is not None:
        response["warning"] = warning

    if rate_limits is not None:
        response["rate_limits"] = rate_limits
    else:
        response["rate_limits"] = RateLimitManager.get_rate_limit_info()

    return response


def apply_pagination_defaults(
    count: Optional[int] = None, after: Optional[str] = None
) -> Dict[str, Any]:
    """Apply default values for pagination parameters"""
    return {
        "first": min(count or 10, 20),  # API has a max of 20 per request
        "after": after,
    }


def check_data_exists(result: Dict[str, Any], path_segments: str or List[str]) -> bool:
    """
    Check if data exists at the given path in the result

    Args:
        result: The result dictionary to check
        path_segments: String path or list of keys representing the path to check

    Returns:
        True if the path exists and contains non-null data, False otherwise
    """
    current = result
    # Convert string path to list if needed
    if isinstance(path_segments, str):
        path_segments = [path_segments]

    for segment in path_segments:
        if not current or segment not in current or current[segment] is None:
            return False
        current = current[segment]
    return True


def extract_pagination(page_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract pagination data from GraphQL page info

    Args:
        page_info: The pageInfo object from a GraphQL response

    Returns:
        Dictionary with end_cursor and has_next_page fields
    """
    return {
        "end_cursor": page_info.get("endCursor"),
        "has_next_page": page_info.get("hasNextPage", False),
    }


def execute_and_check_query(
    query: str,
    variables: Dict[str, Any],
    resource_type: str,
    id_or_slug_value: Optional[str] = None,
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Execute a GraphQL query and check if the requested resource exists

    Args:
        query: The GraphQL query to execute
        variables: Variables to send with the query
        resource_type: The type of resource being requested (e.g., "post", "user")
        id_or_slug_value: The ID or slug value for error messages

    Returns:
        Tuple containing:
        - The resource data if found, None otherwise
        - Rate limit information
        - Error information if any, None otherwise
    """
    from ..api.client import execute_graphql_query

    # Execute the query
    result, rate_limits, error = execute_graphql_query(query, variables)

    if error:
        return None, rate_limits, error

    # Check if the resource exists in the response
    path = ["data", resource_type]
    if not check_data_exists(result, path):
        id_msg = f" with {id_or_slug_value}" if id_or_slug_value else ""
        return (
            None,
            rate_limits,
            {"code": "NOT_FOUND", "message": f"{resource_type.capitalize()} not found{id_msg}"},
        )

    return result["data"][resource_type], rate_limits, None


def add_id_or_slug(variables: Dict[str, Any], id: str = None, slug: str = None) -> None:
    """
    Add 'id' and/or 'slug' to the variables dict if provided.
    Args:
        variables: The dict to update.
        id: The id value (optional).
        slug: The slug value (optional).
    """
    if id:
        variables["id"] = id
    if slug:
        variables["slug"] = slug
