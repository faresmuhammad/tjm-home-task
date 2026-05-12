import requests
import json
from config import POSTS_API_URL, POSTS_CACHE_PATH

def fetch_posts(limit: int = 10) -> list[dict]:
    try:
        r = requests.get(POSTS_API_URL, timeout=5)
        r.raise_for_status()
        return r.json()[:limit]
    except Exception as e:
        print(f"[api_client] API unavailable ({e}), loading from cache.")
        with open(POSTS_CACHE_PATH) as f:
            return json.load(f)[:limit]