from __future__ import annotations

from playwright.async_api import async_playwright, Playwright
from fastapi import FastAPI
from contextlib import asynccontextmanager
import app.utils.dependencies as deps
from app.config import (
    HEADLESS,
    PLAYWRIGHT_ARGS,
    setup_logging,
)
from app.config import add_routes, add_exceptions_handlers, add_middlewares

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação: inicializa e fecha o browser."""
    playwright: Playwright | None = None

    try:
        playwright = await async_playwright().start()
        deps.browser = await playwright.chromium.launch(
            args=PLAYWRIGHT_ARGS,
            headless=HEADLESS,
        )
        yield
    finally:
        if deps.browser:
            await deps.browser.close()
        if playwright:
            await playwright.stop()


app = FastAPI(
    title="Scrapper API",
    description="API para web scraping de dados públicos brasileiros",
    version="0.1.0",
    lifespan=lifespan,
)

add_routes(app)
add_exceptions_handlers(app)
add_middlewares(app)
