"""Core application settings - Compatibility shim.

DEPRECATED: This module is kept for backward compatibility.
New code should import from api.core.settings package:

    from api.core.settings import settings, AppSettings, CORSSettings, etc.

Settings are now organized into submodules:
    - api.core.settings.app: Application settings
    - api.core.settings.cors: CORS configuration
    - api.core.settings.security: Security settings
    - api.core.settings.base: Settings aggregation
"""
from __future__ import annotations

# Re-export everything from the new structure for backward compatibility
from truapi.core.settings import (
    AppSettings,
    CORSSettings,
    DatabaseSettings,
    SecuritySettings,
    Settings,
    settings,
)

__all__ = [
    "settings",
    "Settings",
    "AppSettings",
    "DatabaseSettings",
    "CORSSettings",
    "SecuritySettings",
]
