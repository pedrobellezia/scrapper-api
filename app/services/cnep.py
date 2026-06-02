from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout
from app.config import logger
from app.exceptions import ScrapError
from pathlib import Path


class Cnep:
    @staticmethod
    async def execute_scrap(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting CNEP scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://certidoes-apf.apps.tcu.gov.br/",
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            await page.locator("//input[@id='numero-cnpj']").fill(cnpj)
            await page.locator("//button[@type='button']").click()

            async with page.expect_download(timeout=30_000) as download_info:
                await page.locator("//button[@type='button']").nth(1).click()

            download = await download_info.value
            download_path = await download.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF da certidao CNEP para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"CNEP scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="CNEP",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CNEP",
                cnpj=cnpj,
                tipo_cnd="CNEP",
                url=page.url,
            ) from e
