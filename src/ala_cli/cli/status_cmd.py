from argparse import ArgumentParser, Namespace
from collections import Counter

from ala_cli.alerts.service import fetch_alerts
from ala_cli.errors import AlertsError
from ala_cli.snapshot import (
    DEFAULT_MIRRORLIST,
    check_remote_snapshot,
    get_current_snapshot,
)
from ala_cli.system import (
    get_package_manager_cmd,
    get_privilege_cmd,
)


def status_cmd(_parser: ArgumentParser, _args: Namespace) -> None:
    snapshot = get_current_snapshot()

    is_reachable = check_remote_snapshot(snapshot)
    reachable_report = "REACHABLE" if is_reachable else "UNREACHABLE"

    alerts_report = "No reports"
    if is_reachable:
        try:
            alerts = [alert.type.value for alert in fetch_alerts(snapshot)]
        except AlertsError:
            alerts_report = "Unavailable (feed error)"
        else:
            if alerts:
                counts = Counter(alerts)
                alerts_report = ", ".join(
                    [f"{k.title()}: {v}" for (k, v) in counts.items()]
                )

    data = [
        ("Snapshot", snapshot),
        ("Mirrorlist", DEFAULT_MIRRORLIST),
        ("Reachable", reachable_report),
        ("Alerts", alerts_report),
        ("PackageManager", get_package_manager_cmd()),
        ("PrivilegeTool", get_privilege_cmd()),
    ]

    print("ALA CLI Status:\n")
    for key, value in data:
        print(f"{key + ':':<20}{value}")
