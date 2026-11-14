from argparse import ArgumentParser, Namespace

from ala_cli.snapshot import (
    check_remote_snapshot,
    generate_snapshot_url,
    get_current_snapshot,
)


def verify_cmd(parser: ArgumentParser, args: Namespace) -> None:

    snapshot = args.date or get_current_snapshot()

    url = generate_snapshot_url(snapshot, "core", "x86_64")
    template = f"Snapshot server {{}} reachable: {snapshot:%Y/%m/%d}.\nServer = {url}\n"

    if not check_remote_snapshot(snapshot):
        parser.exit(10, template.format("isn't"))
    print(template.format("is"))
