import requests
from typing import Tuple
from .config import DEVTO_API_KEY, is_token_valid

DEVTO_URL = "https://dev.to/api/articles"


def publish_to_devto(title: str, body_markdown: str, tags=None) -> Tuple[bool, object]:
    """Publish article to dev.to. Returns (success, response_or_error)."""
    if tags is None:
        tags = ["tech"]
    if not is_token_valid(DEVTO_API_KEY):
        return False, "DEVTO_API_KEY not set or is placeholder; skipping publish."

    payload = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": True,
            "tags": tags,
        }
    }
    headers = {"api-key": DEVTO_API_KEY, "Content-Type": "application/json"}
    try:
        resp = requests.post(DEVTO_URL, json=payload, headers=headers, timeout=15)
        if resp.status_code in (200, 201):
            return True, resp.json()
        return False, f"Dev.to API returned {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)
