from argparse import ArgumentParser, Namespace

from ala_cli.errors import SnapshotError
from ala_cli.snapshot import check_remote_snapshot, get_current_snapshot, set_snapshot
from ala_cli.system import sync, upgrade


def set_cmd(parser: ArgumentParser, args: Namespace) -> None:
    snapshot = args.date

    try:
        current = get_current_snapshot()
    except SnapshotError:
        current = None

    if current == snapshot:
        parser.exit(0, f"ALA snapshot already set to {snapshot:%Y/%m/%d}\n")

    if not args.no_verify and not check_remote_snapshot(snapshot):
        parser.exit(1, "Error: Requested snapshot server isn't reachable.\n")

    set_snapshot(snapshot)
    prev = f" (Old snapshot: {current:%Y/%m/%d})" if current else ""
    print(f"ALA snapshot updated to {snapshot:%Y/%m/%d}{prev}")

    if args.sync:
        sync()
    elif args.upgrade:
        upgrade()
