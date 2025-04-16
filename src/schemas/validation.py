"""
Validation schemas for API parameters
"""

# Post schemas
POST_SCHEMA = {"requires_one_of": [["id", "slug"]], "id": {"type": str}, "slug": {"type": str}}

POSTS_SCHEMA = {
    "featured": {"type": bool},
    "topic": {"type": str},
    "order": {"type": str, "valid_values": ["RANKING", "NEWEST", "VOTES", "FEATURED_AT"]},
    "count": {"type": int, "min_value": 1, "max_value": 20},
    "after": {"type": str},
    "url": {"type": str},
    "twitter_url": {"type": str},
    "posted_before": {"type": str, "is_iso8601": True},
    "posted_after": {"type": str, "is_iso8601": True},
}

# Comment schemas
COMMENT_SCHEMA = {"id": {"required": True, "type": str}}

POST_COMMENTS_SCHEMA = {
    "requires_one_of": [["post_id", "slug"]],
    "post_id": {"type": str},
    "slug": {"type": str},
    "order": {"type": str, "valid_values": ["NEWEST", "OLDEST", "TOP"]},
    "count": {"type": int, "min_value": 1, "max_value": 20},
    "after": {"type": str},
}

# Collection schemas
COLLECTION_SCHEMA = {
    "requires_one_of": [["id", "slug"]],
    "id": {"type": str},
    "slug": {"type": str},
}

COLLECTIONS_SCHEMA = {
    "featured": {"type": bool},
    "user_id": {"type": str},
    "post_id": {"type": str},
    "order": {"type": str, "valid_values": ["FOLLOWERS_COUNT", "NEWEST", "FEATURED_AT"]},
    "count": {"type": int, "min_value": 1, "max_value": 20},
    "after": {"type": str},
}

# Topic schemas
TOPIC_SCHEMA = {"requires_one_of": [["id", "slug"]], "id": {"type": str}, "slug": {"type": str}}

TOPICS_SCHEMA = {
    "query": {"type": str},
    "followed_by_user_id": {"type": str},
    "order": {"type": str, "valid_values": ["FOLLOWERS_COUNT", "NEWEST", "NAME"]},
    "count": {"type": int, "min_value": 1, "max_value": 20},
    "after": {"type": str},
}

# User schemas
USER_SCHEMA = {
    "requires_one_of": [["id", "username"]],
    "id": {"type": str},
    "username": {"type": str},
    "posts_type": {"type": str, "valid_values": ["MADE", "VOTED"]},
    "posts_count": {"type": int, "min_value": 1, "max_value": 20},
    "posts_after": {"type": str},
}
