# AGENTS.md

`ala` is an Arch-only Python CLI that pins pacman to an [Arch Linux Archive](https://archive.archlinux.org/) snapshot by rewriting `/etc/pacman.d/ala-mirrorlist`. `pacman.conf` must `Include` that file for any change to matter. One `Server = .../repos/YYYY/MM/DD/$repo/os/$arch/` line serves `core`, `extra`, and `multilib` via `$repo`.

## Commands

- `uv sync` — provision `.venv` (uv only; the system `python3` is 3.14, project is 3.12).
- `uv run ala <cmd>` — run from source (editable install).
- `uv run pytest` — full suite (~0.5s, offline).
- `uv run pytest tests/test_snapshot.py::test_get_current_snapshot -q` — single test.
- `uv run ruff check .` — lint (config in `pyproject.toml`).
- `uv build` — sdist + wheel via `uv_build` (src layout, module `ala_cli`).
- CI (`.github/workflows/ci.yml`) runs `uv sync --frozen`, `uv run ruff check .`, and `uv run pytest` on pushes and PRs.

## Layout

- `src/ala_cli/snapshot.py` — mirrorlist parsing, URL generation, reachability check. `DEFAULT_MIRRORLIST` is hardcoded to `/etc/pacman.d/ala-mirrorlist`.
- `src/ala_cli/system.py` — `doas`/`sudo` and `paru`/`pacman` wrappers; parses `-Sup`/`-Q` output.
- `src/ala_cli/alerts/` — Arch news + security advisory feeds (live network).
- `src/ala_cli/cli/` — argparse setup and one module per command; `errors.py` defines the `AlaError` tree.

## Non-obvious wiring

- Command dispatch is a hand-written table in `cli/__init__.py` (`cmds = [[fn, aliases], ...]`), not `argparse.set_defaults`. A new command needs an entry in `cli/parser.py`, that table, and a `cli/<name>_cmd.py`.
- `AlaError` is caught once in `run_cli` and becomes `Error: ...` + exit 1. Anything outside that hierarchy (`HTTPError`, feed `KeyError`, etc.) escapes as a raw traceback.
- Early exits use `parser.exit(code, msg)`, which writes `msg` to **stderr**. Only `verify` uses exit code 10 (unreachable); everything else uses 0/1. `main()` maps Ctrl-C to 130.
- Library functions in `snapshot.py` accept a `mirrorlist` path, but the CLI commands always hit the hardcoded default. Pointing the CLI elsewhere requires a code change.
- Writing the mirrorlist shells out to `<doas|sudo> tee /etc/...`; `upgrade`/`sync` shell out to the package manager. Never invoke these in tests.
- The `ala_cli.cli.<name>_cmd` submodule names are shadowed by same-named functions imported in `cli/__init__.py`; use `importlib.import_module` to get the module in tests.

## Testing

- Tests live at the repo root in `tests/` (not in the package) and are excluded from the wheel.
- Existing coverage is only `get_current_snapshot` with `tmp_path`. For new tests, monkeypatch `ala_cli.system.shutil.which`, `subprocess.run`, `urllib.request.urlopen`, or `feedparser.parse`; do not touch `/etc`, pacman, or the network.
- `alerts/sources.py` fetches feeds with a 10s timeout and raises `AlertsError` on failure; monkeypatch `ala_cli.alerts.sources.urlopen` (not the real network) when testing it.

## Known issues (verified 2026-11, safe to delete once fixed)

- `parse_cli_date` uses `dateparser` with an ambivalent date order (`"11/12"` → Nov 12). Prefer/document ISO `YYYY/MM/DD`.
- `alerts/sources.py` feeds UTC `*_parsed` structs into `time.mktime`, which treats them as local time and shifts dates by the TZ offset.
- `set` swallows every `SnapshotError` as "no current snapshot", so a conflicting or corrupt mirrorlist is silently overwritten.
- `check_remote_snapshot` only maps 404 to `False`; other `HTTPError`/`URLError` escape as tracebacks (not `AlaError`).
