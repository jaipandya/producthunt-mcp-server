"""
GraphQL API Client for Product Hunt

This module handles GraphQL queries and API execution.
"""

import logging
import time
from typing import Any, Dict, Optional, Tuple

import requests

from product_hunt_mcp.utils.rate_limit import RateLimitManager
from product_hunt_mcp.utils.token import get_token, check_token

logger = logging.getLogger("ph_mcp")

# API endpoints
API_BASE_URL = "https://api.producthunt.com/v2"
GRAPHQL_URL = f"{API_BASE_URL}/api/graphql"


def execute_graphql_query(
    query: str, variables: Dict[str, Any] = None, operation_name: str = None
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Execute a GraphQL query against Product Hunt API with rate limit handling

    Args:
        query: The GraphQL query string
        variables: Dictionary of query variables
        operation_name: Optional operation name

    Returns:
        tuple: (result, rate_limit_info, error) - only one of result or error will be populated
    """
    # Get developer token
    token = get_token()

    if not token:
        return (
            None,
            None,
            {
                "code": "NO_TOKEN",
                "message": "Developer token not found. Please add PRODUCT_HUNT_TOKEN to your environment variables.",
            },
        )

    # Check rate limits
    current_time = int(time.time())
    rate_limits = RateLimitManager.get_rate_limit_info()

    if (
        current_time < RateLimitManager.rate_limit_reset
        and RateLimitManager.rate_limit_remaining <= 0
    ):
        wait_time = RateLimitManager.rate_limit_reset - current_time
        logger.warning(f"Rate limit reached. Need to wait for {wait_time} seconds.")
        return (
            None,
            rate_limits,
            {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": (
                    f"Rate limit exceeded. Reset in {wait_time} seconds at "
                    f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(RateLimitManager.rate_limit_reset))}."
                ),
                "retry_after": wait_time,
            },
        )

    # Set up headers with auth
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "curl/7.64.1",
    }

    payload = {"query": query}

    if variables:
        payload["variables"] = variables
    if operation_name:
        payload["operationName"] = operation_name

    try:
        response = requests.post(GRAPHQL_URL, headers=headers, json=payload)

        # Always update rate limits if headers are present (regardless of case)
        # This is now handled in the RateLimitManager.update_from_headers method
        RateLimitManager.update_from_headers(response.headers)

        rate_limits = RateLimitManager.get_rate_limit_info()

        if response.status_code == 200:
            result = response.json()
            # Check for GraphQL-level errors
            if "errors" in result:
                error_message = (
                    result["errors"][0]["message"] if result["errors"] else "Unknown GraphQL error"
                )
                error_path = result["errors"][0].get("path", []) if result["errors"] else []
                logger.error(f"GraphQL error: {error_message}")

                # Map known GraphQL errors to more user-friendly messages
                friendly_message = error_message
                error_code = "GRAPHQL_ERROR"

                # Detect common GraphQL error patterns and provide friendly messages
                if "Variable $" in error_message and "was provided invalid value" in error_message:
                    if "DateTime" in error_message:
                        error_code = "INVALID_DATE_FORMAT"
                        friendly_message = "Invalid date format. Dates must be in ISO 8601 format (e.g., 2023-01-01T00:00:00Z)."
                    elif "Int" in error_message:
                        error_code = "INVALID_PARAMETER"
                        friendly_message = "One of the parameters has an invalid value type. Please check numeric parameters."
                    else:
                        friendly_message = (
                            "One of the parameters has an invalid value. Please check your input."
                        )
                elif (
                    "Not found" in error_message
                    or "not found" in error_message.lower()
                    or "doesn't exist" in error_message.lower()
                ):
                    error_code = "NOT_FOUND"
                    if error_path and len(error_path) > 0:
                        friendly_message = f"Resource not found: {error_path[-1]}"
                    else:
                        friendly_message = "The requested resource could not be found."

                return (
                    None,
                    rate_limits,
                    {"code": error_code, "message": friendly_message, "details": result["errors"]},
                )
            return result, rate_limits, None

        elif response.status_code == 429:
            # Rate limited
            # Find the reset header regardless of case
            reset_header = next(
                (h for h in response.headers if h.lower() == "x-rate-limit-reset"), None
            )
            wait_time = int(response.headers.get(reset_header, 900)) if reset_header else 900

            logger.warning(f"Rate limited by API. Reset in {wait_time} seconds.")
            return (
                None,
                rate_limits,
                {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Reset in {wait_time} seconds.",
                    "retry_after": wait_time,
                },
            )
        else:
            error_msg = f"API request failed: {response.status_code} - {response.text}"
            logger.error(error_msg)

            # Provide more user-friendly messages based on status code
            if response.status_code == 401:
                friendly_message = "Authentication failed. Please check your API token."
                error_code = "AUTHENTICATION_ERROR"
            elif response.status_code == 403:
                friendly_message = "You don't have permission to access this resource."
                error_code = "PERMISSION_DENIED"
            elif response.status_code == 404:
                friendly_message = "The requested resource was not found."
                error_code = "NOT_FOUND"
            elif response.status_code >= 500:
                friendly_message = (
                    "The Product Hunt API is currently unavailable. Please try again later."
                )
                error_code = "SERVER_ERROR"
            else:
                friendly_message = (
                    "An error occurred while communicating with the Product Hunt API."
                )
                error_code = "API_ERROR"

            return (
                None,
                rate_limits,
                {
                    "code": error_code,
                    "message": friendly_message,
                    "status_code": response.status_code,
                },
            )

    except requests.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)

        # Provide more user-friendly network error messages
        if "ConnectionError" in str(e.__class__):
            friendly_message = (
                "Could not connect to the Product Hunt API. Please check your internet connection."
            )
        elif "Timeout" in str(e.__class__):
            friendly_message = "The request to Product Hunt API timed out. Please try again later."
        elif "TooManyRedirects" in str(e.__class__):
            friendly_message = (
                "Too many redirects occurred when connecting to the Product Hunt API."
            )
        else:
            friendly_message = "A network error occurred while connecting to the Product Hunt API."

        return (
            None,
            RateLimitManager.get_rate_limit_info(),
            {"code": "NETWORK_ERROR", "message": friendly_message, "details": str(e)},
        )
