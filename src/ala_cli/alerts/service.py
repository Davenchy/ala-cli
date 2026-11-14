from datetime import date

from ala_cli.alerts.models import Alert, AlertType
from ala_cli.alerts.sources import fetch_news_feed, fetch_security_feed


def fetch_alerts(snapshot: date, alert_type: AlertType | None = None) -> list[Alert]:
    alerts: list[Alert] = []

    if alert_type in (None, AlertType.NEWS):
        alerts.extend(fetch_news_feed())
    if alert_type in (None, AlertType.SECURITY):
        alerts.extend(fetch_security_feed())

    alerts = [alert for alert in alerts if alert.date >= snapshot]

    return sorted(alerts, key=lambda x: x.date, reverse=True)
