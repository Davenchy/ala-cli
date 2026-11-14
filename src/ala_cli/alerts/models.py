from dataclasses import dataclass
from datetime import date
from enum import Enum
from json import JSONEncoder


class AlertType(Enum):
    NEWS = "news"
    SECURITY = "security"


@dataclass(frozen=True, slots=True)
class Alert:
    title: str
    url: str
    author: str
    summary: str
    date: date
    type: AlertType


class AlertEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
