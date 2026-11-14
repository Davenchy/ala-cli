import argparse
from datetime import date

import dateparser


def parse_cli_date(value: str) -> date:
    parsed = dateparser.parse(value)
    if not parsed:
        raise argparse.ArgumentTypeError(f"Invalid date: {value}")
    return parsed.date()
