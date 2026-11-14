from datetime import date
from pathlib import Path

import pytest

from ala_cli.errors import (
    ConflictingSnapshotsError,
    InvalidSnapshotDateError,
    MirrorlistNotFoundError,
    SnapshotNotFoundError,
)
from ala_cli.snapshot import get_current_snapshot


def test_get_current_snapshot(tmp_path: Path):
    mirrorlist = tmp_path / "ala-mirrorlist"

    mirrorlist.write_text(
        "Server = https://archive.archlinux.org/repos/2026/11/10/$repo/os/$arch\n",
        encoding="utf-8",
    )

    result = get_current_snapshot(mirrorlist)

    assert result == date(2026, 11, 10)


def test_get_current_snapshot_from_missing_path(tmp_path: Path):
    mirrorlist = tmp_path / "missing-ala-mirrorlist"
    with pytest.raises(MirrorlistNotFoundError):
        get_current_snapshot(mirrorlist)


def test_get_current_snapshot_from_invalid_snapshot_date(tmp_path: Path):
    mirrorlist = tmp_path / "invalid_date-ala-mirrorlist"
    mirrorlist.write_text(
        "Server = https://archive.archlinux.org/repos/2026/99/99/$repo/os/$arch\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidSnapshotDateError):
        get_current_snapshot(mirrorlist)


def test_get_current_snapshot_commented_line(tmp_path: Path):
    mirrorlist = tmp_path / "commented-ala-mirrorlist"
    mirrorlist.write_text(
        "# Server = https://archive.archlinux.org/repos/2026/99/99/$repo/os/$arch\n",
        encoding="utf-8",
    )

    with pytest.raises(SnapshotNotFoundError):
        get_current_snapshot(mirrorlist)


def test_get_current_snapshot_multiple_repos(tmp_path: Path):
    mirrorlist = tmp_path / "multi_repo-ala-mirrorlist"
    mirrorlist.write_text(
        "Server = https://archive.archlinux.org/repos/2026/11/10/$repo/os/$arch\n"
        "Server = https://archive.archlinux.org/repos/2026/11/12/$repo/os/$arch\n",
        encoding="utf-8",
    )

    with pytest.raises(ConflictingSnapshotsError):
        get_current_snapshot(mirrorlist)


def test_get_current_snapshot_invalid_url(tmp_path: Path):
    mirrorlist = tmp_path / "invalid_url-ala-mirrorlist"
    mirrorlist.write_text(
        "Server = https://archive.github.com/repos/2026/11/10/$repo/os/$arch\n",
        encoding="utf-8",
    )

    with pytest.raises(SnapshotNotFoundError):
        get_current_snapshot(mirrorlist)


def test_get_current_snapshot_invalid_date_after_valid_entry(tmp_path: Path):
    mirrorlist = tmp_path / "ala-mirrorlist"

    mirrorlist.write_text(
        "Server = https://archive.archlinux.org/repos/2026/11/10/$repo/os/$arch\n"
        "Server = https://archive.archlinux.org/repos/2026/99/99/$repo/os/$arch\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidSnapshotDateError):
        get_current_snapshot(mirrorlist)
