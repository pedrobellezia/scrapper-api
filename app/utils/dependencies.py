from typing import Optional
from playwright.async_api import Browser
import asyncio

# Global state
browser: Optional[Browser] = None
semaphore = asyncio.Semaphore(3)


async def get_tools():
    if browser is None:
        raise RuntimeError(
            "Browser nao inicializado. Verifique o lifespan da aplicacao."
        )

    async with semaphore:
        context = None
        page = None
        try:
            context = await browser.new_context()

            page = await context.new_page()
            yield page, context
        finally:
            if page:
                await page.close()
            if context:
                await context.close()


def get_browser() -> Browser:
    global browser
    if browser is None:
        raise RuntimeError(
            "Browser nao inicializado. Verifique o lifespan da aplicacao."
        )
    return browser
