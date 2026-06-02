from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import logger
from app.exceptions.errors import CaptchaError, ScrapError


def _log_error(
    exc: Exception,
    *,
    cnpj: str | None,
    tipo_cnd: str | None,
    message: str | None = None,
    **kwargs,
) -> None:
    logger.error(
        f"[{type(exc).__name__}] {exc}" if not message else message,
        extra={
            "extra": {
                "cnpj": cnpj,
                "tipo_cnd": tipo_cnd,
                **kwargs,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        },
        exc_info=(type(exc), exc, exc.__traceback__),
    )


async def handle_request_validation_error(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(
        "[RequestValidationError] payload invalido",
        extra={
            "extra": {
                "error_type": "RequestValidationError",
                "errors": [
                    {k: v for k, v in i.items() if k != "ctx"} for i in exc.errors()
                ],
            }
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "message": "Erro de validacao nos dados enviados.",
            "error": "request_validation_error",
            "details": [i.get("msg") for i in exc.errors()],
        },
    )


async def handle_scrap_error(_: Request, exc: ScrapError) -> JSONResponse:
    original_exc = exc.__cause__ if exc.__cause__ else exc
    _log_error(
        original_exc,
        cnpj=exc.cnpj,
        tipo_cnd=exc.tipo_cnd,
        url=exc.url,
        message=exc.message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error": exc.error_code,
            "cnd_type": exc.tipo_cnd,
            "cnpj": exc.cnpj,
        },
    )


async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    _log_error(exc, cnpj=None, tipo_cnd=None)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno inesperado.", "error": "internal_error"},
    )


__all__ = [
    "CaptchaError",
    "ScrapError",
    "handle_request_validation_error",
    "handle_scrap_error",
    "handle_unexpected_error",
]
