from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_type": exc.__class__.__name__},
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "error_type": "ValidationError"},
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Database constraint violation", "error_type": "IntegrityError"},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": "HTTPException"},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": exc.__class__.__name__},
    )