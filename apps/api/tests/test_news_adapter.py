from unittest import TestCase
from unittest.mock import patch

from app.infrastructure.providers.adapters import GoogleNewsRssAdapter


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Fed cut hopes pressure the dollar outlook in Asia - Reuters</title>
      <link>https://news.google.com/rss/articles/example-1</link>
      <pubDate>Fri, 20 Mar 2026 10:12:00 GMT</pubDate>
      <description><![CDATA[<a href="https://news.google.com/rss/articles/example-1">Fed cut hopes pressure the dollar outlook in Asia</a>]]></description>
      <source url="https://www.reuters.com">Reuters</source>
    </item>
  </channel>
</rss>
"""


class _FakeResponse:
    text = SAMPLE_RSS

    def raise_for_status(self) -> None:
        return None


class _FakeClient:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def get(self, url: str) -> _FakeResponse:
        self.url = url
        return _FakeResponse()


class GoogleNewsRssAdapterTests(TestCase):
    @patch("app.infrastructure.providers.adapters.httpx.Client", _FakeClient)
    def test_fetch_latest_parses_google_news_rss_items(self) -> None:
        adapter = GoogleNewsRssAdapter(default_queries=("Fed OR dollar when:2d",), max_queries=1, max_items=5)

        items = adapter.fetch_latest("Fed, dollar")

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Fed cut hopes pressure the dollar outlook in Asia")
        self.assertEqual(items[0].source_name, "Reuters")
        self.assertTrue(items[0].url.startswith("https://news.google.com/rss/articles/"))
        self.assertGreater(items[0].credibility_score, 0.9)
