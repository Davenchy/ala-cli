class AlaError(Exception):
    """Base exception for all ala-cli errors."""


# Snapshots
class SnapshotError(AlaError):
    """Base exception for snapshot-related errors."""


class MirrorlistNotFoundError(SnapshotError):
    """Raised when ALA mirrorlist doesn't exist."""


class SnapshotNotFoundError(SnapshotError):
    """Raised when no valid ALA snapshot URL is found."""


class InvalidSnapshotDateError(SnapshotError):
    """Raised when an ALA URL contains an invalid snapshot date."""


class ConflictingSnapshotsError(SnapshotError):
    """Raised when mirrorlist entries use different snapshots."""


# System
class PrivilegeError(AlaError):
    """Raised when privilege escalation fails"""


class SystemCommandError(AlaError):
    """Raised when an external command fails."""


# Alerts
class AlertsError(AlaError):
    """Raised when fetching or parsing Arch announcements fails."""
