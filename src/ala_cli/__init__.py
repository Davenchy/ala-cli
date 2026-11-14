import sys

from ala_cli.cli import run_cli


def main() -> None:
    try:
        run_cli()
    except KeyboardInterrupt:
        sys.exit(130)
