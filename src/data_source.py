import requests
import json
from config import POSTS_API_URL, POSTS_CACHE_PATH
from src.log import logger


def fetch_posts(limit: int = 10) -> list[dict]:
    try:
        r = requests.get(POSTS_API_URL, timeout=5)
        r.raise_for_status()
        return r.json()[:limit]
    except Exception as e:
        logger.error(f"Posts API is not available, loading from cache, {e}")
        with open(POSTS_CACHE_PATH) as f:
            return json.load(f)[:limit]