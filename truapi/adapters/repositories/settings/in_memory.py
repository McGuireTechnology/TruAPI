from typing import Dict, List, Optional

from ....domain.entities.settings import Setting, SettingsScope
from ....domain.value_objects.id import ID
from ....ports.repositories.settings import SettingsRepository


class InMemorySettingsRepository(SettingsRepository):
    def __init__(self) -> None:
        self._items: Dict[str, Setting] = {}

    async def save(self, setting: Setting) -> None:
        self._items[str(setting.id)] = setting

    async def get(self, *, scope: SettingsScope, key: str, user_id: Optional[ID] = None) -> Optional[Setting]:
        for s in self._items.values():
            if s.scope != scope:
                continue
            if s.key != key:
                continue
            if scope == SettingsScope.USER and s.user_id != user_id:
                continue
            return s
        return None

    async def delete(self, setting_id: ID) -> None:
        self._items.pop(str(setting_id), None)

    async def list(self, *, scope: Optional[SettingsScope] = None, user_id: Optional[ID] = None) -> List[Setting]:
        out: List[Setting] = []
        for s in self._items.values():
            if scope is not None and s.scope != scope:
                continue
            if scope == SettingsScope.USER and user_id is not None and s.user_id != user_id:
                continue
            out.append(s)
        return out
