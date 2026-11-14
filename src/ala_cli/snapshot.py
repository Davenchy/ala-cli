import re
from datetime import date
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ala_cli.errors import (
    ConflictingSnapshotsError,
    InvalidSnapshotDateError,
    MirrorlistNotFoundError,
    SnapshotNotFoundError,
)
from ala_cli.system import write_privilege

DEFAULT_MIRRORLIST = Path("/etc/pacman.d/ala-mirrorlist")
SNAPSHOT_PATTERN = re.compile(
    r"^Server\s*=\s*https?://archive\.archlinux\.org/repos/"
    r"(\d{4}/\d{2}/\d{2})/"
)


def get_current_snapshot(mirrorlist: Path = DEFAULT_MIRRORLIST) -> date:
    snapshots: set[date] = set()

    try:
        content = mirrorlist.read_text(encoding="utf-8")
    except Exception as err:
        raise MirrorlistNotFoundError(
            f"ALA mirrorlist not found: {mirrorlist}"
        ) from err

    for line_num, line in enumerate(content.splitlines(), start=1):
        line = line.strip()

        if line.startswith("#"):
            continue

        match = SNAPSHOT_PATTERN.search(line)
        if not match:
            continue

        snapshot_str = match.group(1).replace("/", "-")

        try:
            snapshot = date.fromisoformat(snapshot_str)
        except ValueError as err:
            raise InvalidSnapshotDateError(
                f"Invalid snapshot date on line {line_num}: {match.group(1)}"
            ) from err

        snapshots.add(snapshot)

    if not snapshots:
        raise SnapshotNotFoundError(f"No valid ALA snapshot URL found in {mirrorlist}")

    if len(snapshots) > 1:
        formatted = ", ".join(
            snapshot.strftime("%Y/%m/%d") for snapshot in sorted(snapshots)
        )
        raise ConflictingSnapshotsError(f"Multiple ALA snapshots found: {formatted}")

    return snapshots.pop()


def generate_snapshot_url(snapshot: date, repo="$repo", arch="$arch") -> str:
    formatted_date = snapshot.strftime("%Y/%m/%d")
    return f"https://archive.archlinux.org/repos/{formatted_date}/{repo}/os/{arch}/"


def generate_mirrorlist(snapshot: date) -> str:
    server_url = generate_snapshot_url(snapshot)
    return f"# Arch Linux Archive snapshot\nServer = {server_url}\n"


def check_remote_snapshot(snapshot: date) -> bool:
    url = generate_snapshot_url(snapshot, "core", "x86_64")
    req = Request(url, method="HEAD")

    try:
        with urlopen(req, timeout=10) as res:
            return res.status == 200
    except HTTPError as err:
        if err.code == 404:
            return False
        raise


def set_snapshot(snapshot: date, mirrorlist: Path = DEFAULT_MIRRORLIST) -> None:
    content = generate_mirrorlist(snapshot)
    write_privilege(mirrorlist, content)
