from typing import Optional

from ...domain.entities.settings import Setting, SettingsScope
from ...domain.value_objects.id import ID
from ...ports.repositories.settings import SettingsRepository


async def get_setting(repo: SettingsRepository, *, scope: SettingsScope, key: str, user_id: Optional[ID] = None) -> Optional[Setting]:
    return await repo.get(scope=scope, key=key, user_id=user_id)
