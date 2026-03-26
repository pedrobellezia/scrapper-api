from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout
from app.config import logger
from app.exceptions import ScrapError


class Fgts:
    URL = "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf"

    @staticmethod
    async def execute_scrap(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting FGTS scrape for CNPJ: {cnpj}")

            await page.goto(Fgts.URL, wait_until="domcontentloaded", timeout=30_000)

            await page.locator("//input[@id='mainForm:txtInscricao1']").fill(cnpj)

            await page.locator("//input[@id='mainForm:btnConsultar']").click()

            await page.wait_for_load_state("networkidle", timeout=20_000)

            await page.locator("//a[@id='mainForm:j_id51']").click()

            await page.wait_for_load_state("networkidle", timeout=20_000)

            await page.locator("//input[@id='mainForm:btnVisualizar']").click()

            await page.wait_for_load_state("networkidle", timeout=20_000)

            pdf_bytes = await page.pdf()

            logger.info(f"FGTS scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap do FGTS",
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
