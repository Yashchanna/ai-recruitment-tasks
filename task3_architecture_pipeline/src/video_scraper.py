import feedparser
import re
from typing import List, Dict

def clean_html(raw_html: str) -> str:
    """Remove HTML tags from summary strings."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def get_trending_news(limit: int = 10) -> List[Dict[str, str]]:
    """Fetch top trending news from Google News RSS feed."""
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    trending = []
    for entry in feed.entries[:limit]:
        title = entry.title
        clean_title = re.sub(r' - [^-]+$', '', title).strip()
        summary = getattr(entry, "summary", "")
        clean_summary = clean_html(summary)
        
        trending.append({
            "title": clean_title,
            "original_title": title,
            "link": entry.link,
            "summary": clean_summary,
            "published": getattr(entry, "published", "")
        })
    return trending
