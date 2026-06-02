from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout
from app.config import logger
from app.exceptions import ScrapError
import asyncio


class Fgts:
    @staticmethod
    async def execute_scrap(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting FGTS scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await page.locator("//input[@id='mainForm:txtInscricao1']").fill(cnpj)

            await page.locator("//input[@id='mainForm:btnConsultar']").click()

            await page.wait_for_load_state("networkidle", timeout=20_000)

            await page.locator("//span[@id='mainForm:linkCertificado']/a").click()

            await page.wait_for_load_state("networkidle", timeout=20_000)

            await page.locator("//input[@id='mainForm:btnVisualizar']").click()

            await page.wait_for_load_state("networkidle", timeout=20_000)

            await asyncio.sleep(1)

            pdf_bytes = await page.pdf()

            logger.info(f"FGTS scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="FGTS",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da FGTS",
                cnpj=cnpj,
                tipo_cnd="FGTS",
                url=page.url,
            ) from e
