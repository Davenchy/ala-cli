import sys
from argparse import ArgumentParser, Namespace

import argcomplete
import shtab

from ala_cli.cli.alerts_cmd import alerts_cmd
from ala_cli.cli.current_cmd import current_cmd
from ala_cli.cli.other_cmds import sync_cmd, upgrade_cmd
from ala_cli.cli.parser import create_parser
from ala_cli.cli.set_cmd import set_cmd
from ala_cli.cli.status_cmd import status_cmd
from ala_cli.cli.updates_cmd import updates_cmd
from ala_cli.cli.verify_cmd import verify_cmd
from ala_cli.errors import AlaError


def completion_cmd(parser: ArgumentParser, args: Namespace):
    shell = None
    if args.bash:
        shell = "bash"
    elif args.zsh:
        shell = "zsh"
    elif args.fish:
        shell = "fish"
    elif args.tcsh:
        shell = "tcsh"

    if not shell:
        parser.exit(1, "Error: Unsupported shell\n")

    print(shtab.complete(parser, shell=shell))


def run_cli() -> None:
    parser = create_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    cmds = [
        [current_cmd, ("current", "get", "c")],
        [verify_cmd, ("verify", "v")],
        [set_cmd, ("set", "s")],
        [status_cmd, ("status", "st")],
        [alerts_cmd, ("alerts", "a")],
        [upgrade_cmd, ("upgrade", "up")],
        [sync_cmd, ("sync", "sy")],
        [updates_cmd, ("updates", "u", "new")],
        [completion_cmd, ("completion")],
    ]

    if args.command:
        for cmd, triggers in cmds:
            if args.command in triggers:
                try:
                    cmd(parser, args)
                except AlaError as err:
                    parser.exit(1, f"Error: {err}\n")
                sys.exit(0)

    parser.print_help()
