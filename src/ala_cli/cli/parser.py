import argparse
from argparse import ArgumentParser
from datetime import date, timedelta
from importlib.metadata import version

from ala_cli.cli.utils import parse_cli_date


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ala",
        description="Manage Arch Linux Archive snapshots.",
    )
    parser.add_argument(
        "--version", action="version", version=f"ala-cli {version('ala-cli')}"
    )

    define_commands(parser)

    return parser


def define_commands(parser: ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="command")

    # the `current` command
    commands.add_parser(
        "current",
        aliases=["c", "get"],
        help="Show the currently configured ALA snapshot.",
    )

    # the "completions" command
    completion_cmd_parser = commands.add_parser(
        "completion",
        help="Print shell completion script",
    )
    define_completions_cmd(completion_cmd_parser)

    # the `set` command
    set_cmd_parser = commands.add_parser(
        "set", aliases=["s"], help="Set the ALA snapshot date. By default yesterday"
    )
    define_set_cmd(set_cmd_parser)

    # the `verify` command
    verify_cmd_parser = commands.add_parser(
        "verify", aliases=["v"], help="Verify that the configured snapshot is reachable"
    )
    verify_cmd_parser.add_argument(
        "date",
        help="The snapshot date to verify. By default the current snapshot.",
        nargs="?",
        type=parse_cli_date,
    )

    # the `status` command
    commands.add_parser(
        "status",
        aliases=["st"],
        help="Show system information, e.g. snapshot, mirrorlist, package manager, etc",
    )

    # the `alerts` command
    alerts_cmd_parser = commands.add_parser(
        "alerts", aliases=["a"], help="Show official Arch announcements"
    )
    define_alerts_cmd(alerts_cmd_parser)

    # the `sync` command
    commands.add_parser(
        "sync",
        aliases=["sy"],
        help="Trigger paru/pacman to update local databases.",
    )

    # the `updates` command
    updates_cmd_parser = commands.add_parser(
        "updates",
        aliases=["u", "new"],
        help="List current updates",
    )
    updates_cmd_parser.add_argument(
        "--json", action="store_true", help="Print updates in JSON format"
    )

    # the `upgrade` command
    commands.add_parser(
        "upgrade",
        aliases=["up"],
        help="Trigger Paru/Pacman to sync and do full system upgrade",
    )


def define_set_cmd(parser: ArgumentParser) -> None:
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument(
        "--sync",
        action="store_true",
        help="Trigger paru/pacman to update the local databases.",
    )
    grp.add_argument(
        "--upgrade",
        action="store_true",
        help="Trigger paru/pacman to sync and run a system upgrade.",
    )

    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Force setting the valid snapshot date and skip remote verification.",
    )
    parser.add_argument(
        "date",
        help='The date to set snapshot to. By default yesterday. E.g.: "2 days ago", "2026/11/11", "yesterday", ...',
        nargs="?",
        default=date.today() - timedelta(days=1),
        type=parse_cli_date,
    )


def define_alerts_cmd(parser: ArgumentParser) -> None:
    parser.add_argument(
        "date",
        help="Check alerts for specific snapshot. By default the current snapshot",
        nargs="?",
        type=parse_cli_date,
    )
    parser.add_argument(
        "--json", action="store_true", help="Show JSON formatted output"
    )

    alerts_filter_grp = parser.add_mutually_exclusive_group()
    alerts_filter_grp.add_argument("--news", action="store_true", help="Show news only")
    alerts_filter_grp.add_argument(
        "--security", action="store_true", help="Show security announcements only"
    )


def define_completions_cmd(parser: ArgumentParser) -> None:
    completion_grp = parser.add_mutually_exclusive_group(required=True)
    shells = ["Bash", "ZSH", "Fish", "TCSH"]
    for shell in shells:
        completion_grp.add_argument(
            f"--{shell.lower()}",
            action="store_true",
            help=f"Generate completions for {shell} shell",
        )
