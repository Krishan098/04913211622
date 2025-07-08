from typing import Dict, List
from datetime import datetime,UTC

# In-memory storage for shortened URLs and click analytics
URL_STORE: Dict[str, dict] = {}
CLICK_STATS: Dict[str, List[dict]] = {}

def save_url(shortcode: str, original_url: str, expiry: datetime):
    URL_STORE[shortcode] = {
        "original_url": original_url,
        "created_at": datetime.now(UTC),
        "expiry": expiry,
        "click_count": 0
    }
    CLICK_STATS[shortcode] = []

def get_url(shortcode: str):
    return URL_STORE.get(shortcode)

def increment_click(shortcode: str, click_info: dict):
    if shortcode in URL_STORE:
        URL_STORE[shortcode]["click_count"] += 1
        CLICK_STATS[shortcode].append(click_info)

def get_clicks(shortcode: str):
    return CLICK_STATS.get(shortcode, [])

def shortcode_exists(shortcode: str):
    return shortcode in URL_STORE