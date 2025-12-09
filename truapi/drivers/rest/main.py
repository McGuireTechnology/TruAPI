"""Main application entry point.

Minimal FastAPI app loading title/version via Pydantic settings.
"""
from fastapi import FastAPI

from ...settings import settings
from .exception_handlers import exception_container
from .routers.users import router as users_router


def create_api_app() -> FastAPI:
    api = FastAPI(title=settings.NAME, version=settings.VERSION)

    api.include_router(users_router)

    return api


app = create_api_app()

exception_container(app)
