import shutil
import subprocess
from pathlib import Path

from ala_cli.errors import PrivilegeError, SystemCommandError


def get_privilege_cmd() -> str | None:
    for cmd in ("doas", "sudo"):
        executable = shutil.which(cmd)
        if executable:
            return executable


def get_package_manager_cmd() -> str | None:
    for cmd in ("paru", "pacman"):
        executable = shutil.which(cmd)
        if executable:
            return executable


def write_privilege(path: Path, content: str) -> None:
    privilege_cmd = get_privilege_cmd()
    if not privilege_cmd:
        raise PrivilegeError("Neither doas nor sudo is available")

    try:
        subprocess.run(
            [privilege_cmd, "tee", str(path)],
            input=content,
            text=True,
            check=True,
            stdout=subprocess.DEVNULL,
        )

    except subprocess.CalledProcessError as err:
        raise SystemCommandError(f"Failed to write configuration file: {path}") from err
    except OSError as err:
        raise SystemCommandError(f"Unable to execute privileged writer: {err}") from err


def use_package_manager(task: str, capture=False, *args: tuple[str]) -> str:
    tool = get_package_manager_cmd()
    if not tool:
        raise SystemCommandError("Neither paru nor pacman is available")

    cmd = [tool, *args]
    if Path(tool).name == "pacman":
        privilege_tool = get_privilege_cmd()
        if not privilege_tool:
            raise PrivilegeError()

        cmd.insert(0, privilege_tool)

    try:
        return subprocess.run(cmd, check=True, text=True, capture_output=capture).stdout
    except KeyboardInterrupt:
        return ""
    except Exception as err:
        raise SystemCommandError(f"Unable to {task}: {err}") from err


def sync():
    use_package_manager("sync", False, "-Syy")


def upgrade():
    use_package_manager(
        "start a system upgrade", False, "-Syyu", "--disable-download-timeout"
    )


def _get_packages(task: str, *args: tuple[str]) -> dict[str, str]:
    packages = {}
    results = use_package_manager(task, True, *args)

    for package in results.splitlines():
        if not package.strip():
            continue

        name, version = package.split(" ")
        packages[name.strip()] = version.strip()

    return packages


def get_updates_packages() -> dict[str, str]:
    return _get_packages("get updates", "-Sup", "--print-format", "%n %v")


def get_installed_packages() -> dict[str, str]:
    return _get_packages("get installed packages", "-Q")


def get_detailed_updates() -> dict[str, tuple[str, str]]:
    updates = get_updates_packages()
    installed = get_installed_packages()
    return {name: (new, installed.get(name, new)) for name, new in updates.items()}
