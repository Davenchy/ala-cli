from argparse import ArgumentParser, Namespace

from ala_cli.system import sync, upgrade


def sync_cmd(_parser: ArgumentParser, _args: Namespace) -> None:
    sync()


def upgrade_cmd(_parser: ArgumentParser, _args: Namespace) -> None:
    upgrade()
