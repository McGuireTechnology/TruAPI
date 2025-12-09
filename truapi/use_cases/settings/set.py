from typing import Optional

from ...domain.entities.settings import Setting, SettingsScope
from ...domain.value_objects.id import ID
from ...ports.repositories.settings import SettingsRepository


async def set_setting(repo: SettingsRepository, *, scope: SettingsScope, key: str, value: str, user_id: Optional[ID] = None) -> Setting:
    setting = Setting.user(user_id, key, value) if scope == SettingsScope.USER and user_id is not None else Setting.app(key, value)
    await repo.save(setting)
    return setting
