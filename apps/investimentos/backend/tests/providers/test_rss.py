from datetime import UTC, datetime

import httpx
import respx

from ledgerlouis.infrastructure.providers.rss import fetch_feed

FEED = """<?xml version="1.0"?><rss version="2.0"><channel><title>Economia</title>
<item><title>PETR4 sobe após resultado</title><link>https://n/1</link><pubDate>Wed, 28 Oct 2026 12:00:00 +0000</pubDate></item>
<item><title>Sem data</title><link>https://n/2</link></item>
</channel></rss>"""


@respx.mock
def test_fetch_feed_parses_items():
    respx.get("https://feed.example/rss").mock(return_value=httpx.Response(200, text=FEED))
    items = fetch_feed("https://feed.example/rss", now=datetime(2026, 10, 29, tzinfo=UTC))
    assert [(i.title, i.url) for i in items] == [("PETR4 sobe após resultado", "https://n/1"), ("Sem data", "https://n/2")]
    assert items[0].published_at == datetime(2026, 10, 28, 12, tzinfo=UTC)
    assert items[1].published_at == datetime(2026, 10, 29, tzinfo=UTC)
