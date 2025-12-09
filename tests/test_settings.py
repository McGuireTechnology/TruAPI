import asyncio

from truapi.adapters.repositories.settings.in_memory import InMemorySettingsRepository
from truapi.domain.entities.settings import SettingsScope
from truapi.domain.value_objects.id import ID
from truapi.use_cases.settings.get import get_setting
from truapi.use_cases.settings.set import set_setting


def test_app_setting_roundtrip():
    repo = InMemorySettingsRepository()
    setting = asyncio.run(set_setting(repo, scope=SettingsScope.APP, key="theme", value="dark"))
    fetched = asyncio.run(get_setting(repo, scope=SettingsScope.APP, key="theme"))
    assert fetched is not None
    assert fetched.id == setting.id
    assert fetched.value == "dark"


def test_user_setting_scoped():
    repo = InMemorySettingsRepository()
    user1 = ID.new()
    user2 = ID.new()
    asyncio.run(set_setting(repo, scope=SettingsScope.USER, key="theme", value="light", user_id=user1))
    asyncio.run(set_setting(repo, scope=SettingsScope.USER, key="theme", value="dark", user_id=user2))

    s1 = asyncio.run(get_setting(repo, scope=SettingsScope.USER, key="theme", user_id=user1))
    s2 = asyncio.run(get_setting(repo, scope=SettingsScope.USER, key="theme", user_id=user2))

    assert s1 is not None and s1.value == "light"
    assert s2 is not None and s2.value == "dark"
