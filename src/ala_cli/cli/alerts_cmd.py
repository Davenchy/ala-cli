import json
from argparse import ArgumentParser, Namespace
from dataclasses import asdict

from ala_cli.alerts.models import AlertEncoder, AlertType
from ala_cli.alerts.service import fetch_alerts
from ala_cli.snapshot import get_current_snapshot

MAX_SUMMARY_LEN = 240


def alerts_cmd(_parser: ArgumentParser, args: Namespace) -> None:
    snapshot = args.date or get_current_snapshot()
    alerts_type = None
    if args.news:
        alerts_type = AlertType.NEWS
    elif args.security:
        alerts_type = AlertType.SECURITY

    alerts = fetch_alerts(snapshot, alerts_type)

    if args.json:
        print(
            json.dumps([asdict(alert) for alert in alerts], cls=AlertEncoder, indent=2)
        )
        return

    if not alerts:
        print(f"No alerts found for the snapshot {snapshot:%Y/%m/%d}.")
        return

    for alert in alerts:
        print(f"[{alert.type.value.upper()}] {alert.title}")
        print(f"Published At: {alert.date:%Y/%m/%d}, By: {alert.author}")
        print(f"URL: {alert.url}")
        if alert.summary:
            summary = alert.summary
            if len(summary) > MAX_SUMMARY_LEN:
                summary = summary[: MAX_SUMMARY_LEN - 3].rstrip() + "..."
            print(f"\n{summary}")

        print("=====================")
