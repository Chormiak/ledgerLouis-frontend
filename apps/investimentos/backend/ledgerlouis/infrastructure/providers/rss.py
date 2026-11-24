import calendar
from dataclasses import dataclass
from datetime import UTC, datetime

import feedparser
import httpx


@dataclass(frozen=True)
class FeedItem:
    title: str
    url: str
    published_at: datetime


def fetch_feed(url: str, now: datetime, http: httpx.Client | None = None) -> list[FeedItem]:
    """Lê um feed RSS/Atom. Guarda só título, link e data, nunca o texto."""
    r = (http or httpx.Client(timeout=20, follow_redirects=True)).get(url)
    r.raise_for_status()
    items = []
    for e in feedparser.parse(r.content).entries:
        if not e.get("link") or not e.get("title"):
            continue
        parsed = e.get("published_parsed") or e.get("updated_parsed")
        published = datetime.fromtimestamp(calendar.timegm(parsed), UTC) if parsed else now
        items.append(FeedItem(title=e.title.strip()[:500], url=e.link, published_at=published))
    return items
