import json
from argparse import ArgumentParser, Namespace

from ala_cli.system import get_detailed_updates


def updates_cmd(_parser: ArgumentParser, args: Namespace) -> None:
    updates = get_detailed_updates()

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "name": name,
                        "new_version": new,
                        "old_version": old,
                    }
                    for name, (new, old) in updates.items()
                ],
                indent=2,
            )
        )
        return

    for name, (new, old) in updates.items():
        print(f"{name}: {old} -> {new}")
