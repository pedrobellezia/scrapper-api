from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

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
    from app.router import trabalhista, fgts, estadual, municipal

    app.include_router(trabalhista.router)
    app.include_router(fgts.router)
    app.include_router(estadual.router)
    app.include_router(municipal.router)


def add_middlewares(app: FastAPI):
    from app.config.middlewares import auth

    app.middleware("http")(auth)
