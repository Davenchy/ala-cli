import time
from datetime import date, datetime

import feedparser
import html2text

from ala_cli.alerts.models import Alert, AlertType
from ala_cli.errors import AlertsError

NEWS_FEED_URL = "https://archlinux.org/feeds/news/"
SECURITY_FEED_URL = "https://security.archlinux.org/advisory/feed.atom"

html_parser = html2text.HTML2Text()
html_parser.ignore_links = False
html_parser.body_width = 0


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
    feed = feedparser.parse(NEWS_FEED_URL)

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
    feed = feedparser.parse(SECURITY_FEED_URL)

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
