from typing import List, Optional

from ...domain.entities.settings import Setting, SettingsScope
from ...domain.value_objects.id import ID


class SettingsRepository:
    async def save(self, setting: Setting) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    async def get(self, *, scope: SettingsScope, key: str, user_id: Optional[ID] = None) -> Optional[Setting]:
        raise NotImplementedError

    async def delete(self, setting_id: ID) -> None:
        raise NotImplementedError

    async def list(self, *, scope: Optional[SettingsScope] = None, user_id: Optional[ID] = None) -> List[Setting]:
        raise NotImplementedError
