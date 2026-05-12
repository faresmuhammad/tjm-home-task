
from pathlib import Path


POSTS_API_URL = "https://jsonplaceholder.typicode.com/posts"
POSTS_CACHE_PATH = Path(__file__).parent / "posts.json"
DESKTOP_DIR = Path.home() / "Desktop"
PROJECT_DIR = DESKTOP_DIR / "tjm-project"
ANNOTATION_DIR = Path(__file__).parent / "screenshots"