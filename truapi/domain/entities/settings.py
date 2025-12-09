from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ..value_objects.id import ID


class SettingsScope(str, Enum):
    APP = "app"
    USER = "user"


@dataclass(frozen=True)
class Setting:
    id: ID
    scope: SettingsScope
    key: str
    value: str
    user_id: Optional[ID] = None

    @staticmethod
    def app(key: str, value: str) -> "Setting":
        return Setting(id=ID.new(), scope=SettingsScope.APP, key=key, value=value)

    @staticmethod
    def user(user_id: ID, key: str, value: str) -> "Setting":
        return Setting(id=ID.new(), scope=SettingsScope.USER, key=key, value=value, user_id=user_id)
