"""
Rate limit management utilities
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger("ph_mcp")


class RateLimitManager:
    """Manages API rate limits"""

    # Rate limit tracking
    rate_limit_remaining = 6250  # Complexity-based for GraphQL
    rate_limit_reset = 0  # When the rate limit resets

    @classmethod
    def get_rate_limit_info(cls) -> Dict[str, Any]:
        """Get current rate limit information"""
        now = int(time.time())
        reset_in = max(0, cls.rate_limit_reset - now)

        # Format reset time
        reset_at = None
        if cls.rate_limit_reset > 0:
            try:
                reset_at = datetime.fromtimestamp(now + reset_in).isoformat()
            except (ValueError, OverflowError):
                # Fallback if there was an issue with the timestamp
                reset_at = None

        return {
            "remaining": cls.rate_limit_remaining,
            "reset_at": reset_at,
            "reset_in_seconds": reset_in,
        }

    @classmethod
    def update_from_headers(cls, headers: Dict[str, str]) -> None:
        """Update rate limit info from response headers"""
        # Define exact header names to look for based on the API response
        remaining_header = "x-rate-limit-remaining"
        reset_header = "x-rate-limit-reset"

        # Debug: Print all headers
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Headers received: {list(headers.keys())}")

        # Check for the exact headers we need
        if remaining_header in headers:
            try:
                cls.rate_limit_remaining = int(headers[remaining_header])
                logger.debug(f"Updated rate limit remaining: {cls.rate_limit_remaining}")
            except (ValueError, TypeError):
                logger.warning(f"Could not parse rate limit remaining: {headers[remaining_header]}")
        else:
            logger.debug(f"Rate limit remaining header not found: {remaining_header}")

        if reset_header in headers:
            try:
                # The reset value is the number of seconds remaining until reset
                reset_seconds = int(headers[reset_header])
                # Calculate the absolute timestamp
                current_time = int(time.time())
                cls.rate_limit_reset = current_time + reset_seconds
                logger.debug(
                    f"Updated rate limit reset: {cls.rate_limit_reset} (from {reset_seconds} seconds from now)"
                )
            except (ValueError, TypeError):
                logger.warning(f"Could not parse rate limit reset: {headers[reset_header]}")
        else:
            logger.debug(f"Rate limit reset header not found: {reset_header}")

        # Also try to print all rate limit related headers for debugging
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("All rate limit headers found:")
            for header, value in headers.items():
                if "rate" in header.lower() or "limit" in header.lower():
                    logger.debug(f"  {header}: {value}")
