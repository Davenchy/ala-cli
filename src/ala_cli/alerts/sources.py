import time
from datetime import date, datetime
from urllib.request import urlopen

import feedparser
import html2text

from ala_cli.alerts.models import Alert, AlertType
from ala_cli.errors import AlertsError

NEWS_FEED_URL = "https://archlinux.org/feeds/news/"
SECURITY_FEED_URL = "https://security.archlinux.org/advisory/feed.atom"
FEED_TIMEOUT = 10

html_parser = html2text.HTML2Text()
html_parser.ignore_links = False
html_parser.body_width = 0


def _fetch_feed(url: str) -> feedparser.FeedParserDict:
    try:
        with urlopen(url, timeout=FEED_TIMEOUT) as res:
            raw = res.read()
    except Exception as err:
        raise AlertsError(f"Failed to fetch {url}: {err}") from err

    feed = feedparser.parse(raw)
    if feed.bozo and not feed.entries:
        raise AlertsError(f"Failed to parse feed: {url}")

    return feed


def _parse_summary(entry: dict) -> str:
    try:
        return html_parser.handle(entry["summary"]).strip()
    except Exception as err:
        raise AlertsError(f"Failed to parse summary: {err}") from err


def _parse_date(entry: dict, label: str) -> date:
    try:
        return datetime.fromtimestamp(time.mktime(entry[label])).date()
    except Exception as err:
        raise AlertsError(f"Failed to parse date: {err}") from err


def fetch_news_feed() -> list[Alert]:
    alerts = []
    feed = _fetch_feed(NEWS_FEED_URL)

    for entry in feed["entries"]:
        alerts.append(
            Alert(
                entry["title"],
                entry["link"],
                entry["author"],
                _parse_summary(entry),
                _parse_date(entry, "published_parsed"),
                AlertType.NEWS,
            )
        )

    return alerts


def fetch_security_feed() -> list[Alert]:
    alerts = []
    feed = _fetch_feed(SECURITY_FEED_URL)

    for entry in feed["entries"]:
        alerts.append(
            Alert(
                entry["title"],
                entry["link"],
                entry["author"],
                _parse_summary(entry),
                _parse_date(entry, "updated_parsed"),
                AlertType.SECURITY,
            )
        )

    return alerts
