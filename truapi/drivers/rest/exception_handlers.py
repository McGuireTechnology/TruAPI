from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ...adapters.exceptions import ExternalError
from ...use_cases.exceptions import UserNotFoundError


def exception_container(app: FastAPI) -> None:
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_exception_handler(
        request: Request, exc: UserNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc)}
        )

    @app.exception_handler(ExternalError)
    async def external_exception_handler(
        request: Request, exc: ExternalError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Something went wrong. Please try again"},
        )
