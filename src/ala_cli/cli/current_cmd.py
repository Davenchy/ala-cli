from argparse import ArgumentParser, Namespace

from ala_cli.snapshot import get_current_snapshot


def current_cmd(_parser: ArgumentParser, _args: Namespace) -> None:
    snapshot = get_current_snapshot()
    print(f"Current ALA snapshot: {snapshot:%Y/%m/%d}")
