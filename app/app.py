from playwright.async_api import async_playwright
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
    global playwright

    playwright = await async_playwright().start()
    deps.browser = await playwright.chromium.launch(
        args=PLAYWRIGHT_ARGS,
        headless=HEADLESS,
    )
    yield
    await deps.browser.close()
    await playwright.stop()


app = FastAPI(lifespan=lifespan)
add_routes(app)
add_exceptions_handlers(app)
add_middlewares(app)
