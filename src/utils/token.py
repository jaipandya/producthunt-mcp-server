"""
Token management utilities
"""
import os

def get_token() -> str:
    """Get token from environment variable"""
    return os.getenv("PRODUCT_HUNT_TOKEN")

def check_token() -> dict:
    """Check if a token exists and return error if not"""
    token = get_token()
    if not token:
        return {
            "code": "MISSING_TOKEN",
            "message": "PRODUCT_HUNT_TOKEN not found in environment. Please set it as an environment variable.",
        }
    return None
