from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
import os

from app.exceptions import ScrapError
from app.exceptions.handlers import (
    handle_request_validation_error,
    handle_scrap_error,
    handle_unexpected_error,
)


def add_exceptions_handlers(app: FastAPI):
    app.add_exception_handler(ScrapError, handle_scrap_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)


def add_routes(app: FastAPI):
    from app.router import trabalhista, fgts, estadual, municipal, log as lg

    app.include_router(trabalhista.router)
    app.include_router(fgts.router)
    app.include_router(estadual.router)
    app.include_router(municipal.router)
    app.include_router(lg.router)


def add_middlewares(app: FastAPI):
    from app.config.middlewares import auth

    app.middleware("http")(auth)

    # CORS seguro: apenas origens especificadas (ou configuráveis via env)
    allowed_origins = os.environ.get(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000"
    ).split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in allowed_origins],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=True,
        max_age=600,
    )
