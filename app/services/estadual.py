from playwright.async_api import (
    Page,
    BrowserContext,
    TimeoutError as PlaywrightTimeout,
    Download,
)
from app.exceptions import ScrapError, CaptchaError
from app.config import logger, CAPTCHA_API_KEY
from app.utils.captcha_solver import CaptchaSolver
from pathlib import Path
import asyncio


class Estadual:
    @staticmethod
    async def _execute_scrap(
        page: Page, context: BrowserContext, cnpj: str, uf: str
    ) -> bytes | None:
        logger.info(f"Starting Estadual scrape for CNPJ: {cnpj}, UF: {uf}")

        method = getattr(Estadual, uf, None)
        if not callable(method) or uf.startswith("_"):
            return None

        return await method(page=page, context=context, cnpj=cnpj)

    @staticmethod
    async def sp(page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            logger.info(f"Starting Estadual SP scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://www10.fazenda.sp.gov.br/CertidaoNegativaDeb/Pages/EmissaoCertidaoNegativa.aspx",
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            await page.locator("//*[@id='MainContent_cnpjradio']").click()
            await page.locator("//*[@id='MainContent_txtDocumento']").fill(cnpj)

            solver = CaptchaSolver(api_key=CAPTCHA_API_KEY, page=page)
            result = await solver.auto_solve_v2()

            if not result.get("success", False):
                raise CaptchaError(
                    result.get("error") or CaptchaError.default_message,
                    cnpj=cnpj,
                    tipo_cnd="Estadual SP",
                )

            await page.locator("//*[@id='MainContent_btnPesquisar']").click()
            await asyncio.sleep(5)

            if await page.locator("//*[@class='bg-danger']").is_visible():
                raise ScrapError(
                    f"Nao foi possivel obter a certidao para o CNPJ {cnpj} em SP"
                )

            async with page.expect_download(timeout=30_000) as dl:
                await page.locator("//*[@id='MainContent_btnImpressao']").click()
            download = await dl.value
            download_path = await download.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF Estadual SP para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Estadual SP scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except ScrapError:
            raise
        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Estadual SP",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Estadual SP",
                url=page.url,
            ) from e

    @staticmethod
    async def sc(page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            logger.info(f"Starting Estadual SC scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://sat.sef.sc.gov.br/tax.NET/Sat.CtaCte.Web/SolicitacaoCnd.aspx"
            )

            await page.locator(
                "//*[@id='Body_Main_Main_sepBusca_idnCnd_MaskedField']"
            ).fill(cnpj)

            solver = CaptchaSolver(api_key=CAPTCHA_API_KEY, page=page)
            result = await solver.auto_solve_v2()

            if not result.get("success", False):
                raise CaptchaError(
                    result.get("error") or CaptchaError.default_message,
                    cnpj=cnpj,
                    tipo_cnd="Estadual SC",
                )

            await page.locator(
                "//a[.//span[contains(normalize-space(), 'Buscar')]]"
            ).click()

            rows = page.locator(
                "//table[@id='Body_Main_Main_ctnResultado_grpCnd_gridView']"
            ).locator("tbody tr")

            await asyncio.sleep(1)

            count = await rows.count()
            logger.info(f"Found {count} CND rows for CNPJ {cnpj}")

            try:
                download_task = asyncio.create_task(page.wait_for_event("download"))
                popup_task = asyncio.create_task(page.wait_for_event("popup"))

                await page.click('//*[@id="Body_Main_Main_ctnResultado_btnGerarCnd"]')

                done, _ = await asyncio.wait(
                    [download_task, popup_task], return_when=asyncio.FIRST_COMPLETED
                )

                if download_task in done:
                    download: Download = await download_task
                    popup_task.cancel()

                else:
                    popup: Page = await popup_task
                    download_task.cancel()
                    await popup.emulate_media(media="print")
                    return await popup.pdf()

            except PlaywrightTimeout as e:
                e: PlaywrightTimeout
                link = page.locator('//ul[@class="sat-vs-success"]/li[3]/a')

                async with page.expect_download(timeout=30_000) as dl:
                    await link.click()

                download = await dl.value

            download_path = await download.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF Estadual SC para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Estadual SC scrape completed for CNPJ: {cnpj}")

            return pdf_bytes

        except ScrapError:
            raise
        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Estadual SC",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Estadual SC",
                url=page.url,
            ) from e
