from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error."""
    status_code: int = 500
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found."


class ValidationError(AppError):
    status_code = 400
    detail = "Invalid request."


class RunnerUnavailableError(AppError):
    status_code = 503
    detail = "Code runner is unavailable."


class RunnerTimeoutError(AppError):
    status_code = 504
    detail = "Code runner timed out."


class LLMUnavailableError(AppError):
    status_code = 502
    detail = "LLM provider is unavailable."


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )
