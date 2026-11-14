# ala-cli

[![CI](https://github.com/Davenchy/ala-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/Davenchy/ala-cli/actions/workflows/ci.yml)

A small command-line tool for pinning Arch Linux to a specific
[Arch Linux Archive](https://archive.archlinux.org/) (ALA) snapshot.

It rewrites `/etc/pacman.d/ala-mirrorlist` so `pacman` and `paru` install
packages from the snapshot date you choose, instead of from the live
repositories. Useful for reproducible installs, reproducing bugs, or staying
on a known-good set of package versions.

## Features

- Pin pacman to any ALA snapshot date.
- Accepts natural-language dates (`yesterday`, `2 days ago`, `2026/11/11`).
- Verifies the snapshot exists on `archive.archlinux.org` before writing.
- Shows the current snapshot and whether it is reachable.
- Lists pending updates as `old -> new` (plain text or `--json`).
- Shows Arch news and security advisories published since your snapshot.
- Detects `doas`/`sudo` and prefers `paru` over `pacman`.
- Shell completions for bash, zsh, fish, and tcsh.

## Requirements

- Arch Linux (or an Arch-based distribution)
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- `pacman`, and optionally `paru`
- `sudo` or `doas` for writing the mirrorlist

## Installation

From source:

```bash
git clone https://github.com/Davenchy/ala-cli.git
cd ala-cli
uv sync
uv run ala --help
```

Install the `ala` command globally:

```bash
uv tool install .
# or directly from GitHub:
uv tool install git+https://github.com/Davenchy/ala-cli.git
```

## Setup

Point your repositories at the ALA mirrorlist in `/etc/pacman.conf`:

```ini
[core]
Include = /etc/pacman.d/ala-mirrorlist

[extra]
Include = /etc/pacman.d/ala-mirrorlist

[multilib]
Include = /etc/pacman.d/ala-mirrorlist
```

The file contains a single `Server` line; `$repo` and `$arch` are expanded by
pacman, so all three repositories share it:

```ini
# Arch Linux Archive snapshot
Server = https://archive.archlinux.org/repos/2026/11/13/$repo/os/$arch/
```

## Usage

```text
ala current                 Show the configured snapshot
ala set [date]              Set the snapshot (default: yesterday)
ala verify [date]           Check that a snapshot is reachable
ala status                  Snapshot, reachability, alerts, tooling
ala alerts [date]           News/security since a snapshot
ala sync                    Refresh pacman databases
ala updates                 List pending updates
ala upgrade                 Full system upgrade
ala completion --bash       Print shell completion script
```

Aliases: `current` = `c`/`get`, `set` = `s`, `verify` = `v`, `status` = `st`,
`alerts` = `a`, `sync` = `sy`, `updates` = `u`/`new`, `upgrade` = `up`.

### Examples

```bash
# Pin to yesterday's snapshot
ala set

# Pin to a specific date
ala set 2026/11/11

# Pin and immediately refresh databases
ala set yesterday --sync

# Check what is currently configured
ala current
ala status

# See announcements that appeared after your snapshot
ala alerts
ala alerts 2026/10/01 --security
```

### JSON output

```bash
ala updates --json
ala alerts --json
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success (including "no alerts" / "no updates") |
| 1 | Error: invalid input, write failure, or snapshot not reachable in `set` |
| 10 | `ala verify`: the snapshot is not reachable |
| 130 | Interrupted with Ctrl-C |

## Shell completions

```bash
# bash
ala completion --bash > /usr/share/bash-completion/completions/ala

# zsh
ala completion --zsh > "${fpath[1]}/_ala"

# fish
ala completion --fish > ~/.config/fish/completions/ala.fish
```

## How it works

`ala set` renders a mirrorlist containing one ALA `Server` URL and writes it to
`/etc/pacman.d/ala-mirrorlist` through `sudo`/`doas`. Every repository that
`Include`s that file then resolves packages from the same snapshot. All other
logic (status, updates, alerts) only reads local state and public Arch feeds.

## Notes and caveats

- ALA snapshots are frozen. Packages installed from an old snapshot do not
  receive security fixes until you move the snapshot forward.
- A stale `archlinux-keyring` can cause signature failures when jumping far
  forward; update the keyring first if pacman complains.
- AUR builds (`paru`) compile against the installed system, which may be older
  than what the AUR expects. Prefer repository packages while pinned.
- Back up `/etc/pacman.d/ala-mirrorlist` if you have custom entries; `ala set`
  replaces the file.
- `ala set` writes to `/etc`, so it must not be run as a user without
  `sudo`/`doas`.

## License

[MIT](LICENSE) © 2026 Davenchy
