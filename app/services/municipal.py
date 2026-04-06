from typing import Callable, Awaitable

from playwright.async_api import (
    Page,
    BrowserContext,
    TimeoutError as PlaywrightTimeout,
    Download,
)
import httpx

from app.exceptions import ScrapError, CaptchaError
from app.config import logger, CAPTCHA_API_KEY
from app.utils.captcha_solver import CaptchaSolver
from pathlib import Path
import asyncio
import random

from app.utils.pdf_handler import add_cnpj


class Municipal:
    @staticmethod
    async def _execute_scrap(
        page: Page, context: BrowserContext, cnpj: str, uf: str, municipio: str
    ) -> bytes | None:
        logger.info(f"Starting Municipal scrape for CNPJ: {cnpj}, {municipio}/{uf}")

        method_name = f"{uf}_{municipio}"
        #tipagem pro pycharm parar de reclamar
        method: Callable[..., Awaitable[bytes]] | None = getattr(Municipal, method_name, None)

        if not callable(method):
            return None

        return await method(page, context, cnpj)

    @staticmethod
    async def __solve_betha(
        page: Page,
        context: BrowserContext,
        cnpj: str,
        municipio_id: str,
        estado_id: str,
    ) -> Download:
        await page.goto(
            "https://e-gov.betha.com.br/cdweb/",
            wait_until="domcontentloaded",
            timeout=30_000,
        )
        await page.locator("//select[@id='mainForm:estados']").select_option(estado_id)
        await page.locator("//select[@id='mainForm:municipios']").select_option(
            municipio_id
        )
        await page.locator("//*[@id='mainForm:selecionar']").click()
        await page.locator("//div[contains(@class, 'cndContr')]").click()
        await page.locator("//a[contains(@class, 'cnpj')]").click()
        await asyncio.sleep(1)
        await page.locator("//*[@id='mainForm:cnpj']").fill(cnpj)
        await asyncio.sleep(1)
        await page.locator("//*[@id='mainForm:btCnpj']").click()

        t = page.locator('//strong[@class="fieldError"]')

        if await t.count() > 0:
            await asyncio.sleep(1)
            await page.locator("//*[@id='mainForm:cnpj']").fill(cnpj)
            await asyncio.sleep(1)
            await page.locator("//*[@id='mainForm:btCnpj']").click()

        await page.locator(
            "//*[@id='mainForm:t-contribuinte']/tbody/tr/td[3]/img"
        ).click()

        async with page.expect_download(timeout=30_000) as dl:
            await (
                page.frame_locator("//iframe[@class='fancybox-iframe']")
                .locator("//*[@id='download']")
                .click()
            )
        return await dl.value

    @staticmethod
    async def sc_blumenau(page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            logger.info(f"Starting Municipal SC/Blumenau scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://www.blumenau.sc.gov.br/cidadao/pages/siatu/cnd/EmissaoCND.aspx",
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            await page.locator(
                "//*[@name='ctl00$ContentBody$cbkEmissaoCND$txtCpfCnpj']"
            ).fill(cnpj)

            solver = CaptchaSolver(api_key=CAPTCHA_API_KEY, page=page)

            result = await solver.solve_normal(
                img_xpath="//*[@id='ctl00_ContentBody_cbkEmissaoCND_ImageCaptcha']",
                input_xpath="//*[@id='ctl00_ContentBody_cbkEmissaoCND_tbCaptcha_I']",
            )

            if not result.get("success", False):
                raise CaptchaError(
                    result.get("error") or CaptchaError.default_message,
                    cnpj=cnpj,
                    tipo_cnd="Municipal - SC/Blumenau",
                )

            await page.locator(
                "//*[@id='ctl00_ContentBody_cbkEmissaoCND_btPesquisar']"
            ).click()

            await asyncio.sleep(5)

            async with page.expect_download(timeout=30_000) as dl:
                await page.locator("//*[@id='ctl00_ContentBody_btnImprimir']").click()
            download = await dl.value

            download_path = await download.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF a para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Municipal SC/Blumenau scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except CaptchaError:
            raise
        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Blumenau",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Blumenau",
                url=page.url,
            ) from e

    @classmethod
    async def sc_florianopolis(
        cls, page: Page, context: BrowserContext, cnpj: str
    ) -> bytes:
        try:
            download_info = await cls.__solve_betha(
                page, context, cnpj, municipio_id="94", estado_id="22"
            )

            download_path = await download_info.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Municipal SC/Florianopolis scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Florianopolis",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Florianopolis",
                url=page.url,
            ) from e

    @classmethod
    async def sc_lages(cls, page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            download_info = await cls.__solve_betha(
                page, context, cnpj, municipio_id="35", estado_id="22"
            )

            download_path = await download_info.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Municipal SC/Lages scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Lages",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Lages",
                url=page.url,
            ) from e

    @classmethod
    async def sc_braco_do_norte(
        cls, page: Page, context: BrowserContext, cnpj: str
    ) -> bytes:
        try:
            download_info = await cls.__solve_betha(
                page, context, cnpj, municipio_id="91", estado_id="22"
            )

            download_path = await download_info.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(
                f"Municipal SC/Braco do Norte scrape completed for CNPJ: {cnpj}"
            )
            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Braco do Norte",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Braco do Norte",
                url=page.url,
            ) from e

    @classmethod
    async def sc_criciuma(cls, page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            download_info = await cls.__solve_betha(
                page, context, cnpj, municipio_id="29", estado_id="22"
            )

            download_path = await download_info.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Municipal SC/Criciuma scrape completed for CNPJ: {cnpj}")
            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Criciuma",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Criciuma",
                url=page.url,
            ) from e

    @staticmethod
    async def sc_itapema(page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            logger.info(f"Starting Municipal SC/Itapema scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://itapema-sc.prefeituramoderna.com.br/meuiptu/index.php",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await asyncio.sleep(0.5)
            await page.locator("//a[@id='cnd']").click()
            await page.locator("//input[@name='nrcpfcnpj']").fill(cnpj)
            await page.locator("//input[@name='nmrequerente']").fill("segredo")
            await page.locator("//input[@name='nrdocumento']").fill("52998224725")

            async with page.expect_popup() as popup_info:
                await page.locator("//input[@value='Emitir a Certidão']").click()
            popup = await popup_info.value

            await popup.emulate_media(media="print")
            pdf_bytes = await popup.pdf(format="A4")

            logger.info(f"Municipal SC/Itapema scrape completed for CNPJ: {cnpj}")

            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Itapema",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Itapema",
                url=page.url,
            ) from e

    @staticmethod
    async def sc_balneario_camboriu(
        page: Page, context: BrowserContext, cnpj: str
    ) -> bytes:
        try:
            logger.info(f"Starting Municipal SC/Camboriu scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://cidadao.bc.sc.gov.br/cidadao/balneario_camboriu/portal/servicos/certidoes/emissao?params=MTU%3D",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await page.locator(
                "//select[@formcontrolname='idFinalidade']"
            ).select_option(value="1: 5")

            await page.locator("//input[@formcontrolname='cpfCnpj']").fill(cnpj)

            await page.locator("//cidadao-button[@type='submit']").click()

            async with page.expect_download(timeout=30_000) as dl:
                await page.locator("//cidadao-button[@icon='fa fa-download']").click()
            download = await dl.value

            download_path = await download.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF para {cnpj}")
            pdf_bytes = Path(download_path).read_bytes()

            logger.info(f"Municipal SC/Camboriu scrape completed for CNPJ: {cnpj}")

            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Camboriu",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Camboriu",
                url=page.url,
            ) from e

    @staticmethod
    async def sc_joinville(page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            logger.info(f"Starting Municipal SC/Joinville scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://tmiweb.joinville.sc.gov.br/sefaz/jsp/cnd/index.jsp"
            )

            await page.locator("//select[@id='finalidade']").select_option(value="6")

            await page.locator("//input[@name='cnpj']").fill(cnpj)

            await page.locator("//input[@value='Pesquisar']").click()

            await page.locator("//select[@id='ctp_codigo']").select_option(value="8")

            await page.locator("//input[contains(@value, 'Gerar cert')]").click()

            await asyncio.sleep(1)
            url = page.url

            reponse = httpx.get(url)
            if reponse.status_code != 200:
                raise ScrapError(
                    f"Falha ao obter PDF Municipal SC/Joinville para {cnpj}, status code: {reponse.status_code}"
                )

            pdf_bytes = reponse.content

            logger.info(f"Municipal SC/Joinville scrape completed for CNPJ: {cnpj}")

            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Joinville",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Joinville",
                url=page.url,
            ) from e

    @staticmethod
    async def sp_sao_paulo(page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            logger.info(f"Starting Municipal SP/Sao Paulo scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://duc.prefeitura.sp.gov.br/certidoes/forms_anonimo/frmConsultaEmissaoCertificado.aspx"
            )
            await asyncio.sleep(random.uniform(1, 2))

            await page.locator(
                '//*[@id="ctl00_ConteudoPrincipal_ddlTipoCertidao"]'
            ).select_option(value="1")

            await asyncio.sleep(random.uniform(1, 2))

            await page.locator('//*[@id="ctl00_ConteudoPrincipal_txtCNPJ"]').fill(cnpj)

            await asyncio.sleep(random.uniform(1, 2))
            imgpath = '//*[@id="ctl00_ConteudoPrincipal_imgCaptcha"]'
            input_path = '//*[@id="ctl00_ConteudoPrincipal_txtValorCaptcha"]'

            solver = CaptchaSolver(api_key=CAPTCHA_API_KEY, page=page)

            result_1 = await solver.solve_normal(
                img_xpath=imgpath,
                input_xpath=input_path,
            )

            if not result_1.get("success", False):
                raise CaptchaError(
                    result_1.get("error") or CaptchaError.default_message,
                    cnpj=cnpj,
                    tipo_cnd="Municipal - SP/Sao Paulo",
                )

            await asyncio.sleep(random.uniform(1, 2))

            await page.click('//*[@id="ctl00_ConteudoPrincipal_btnEmitir"]')

            result_2 = await solver.solve_normal(
                img_xpath="xpath=/html/body/img[1]",
                input_xpath='//*[@id="ans"]',
            )

            if not result_2.get("success", False):
                raise CaptchaError(
                    result_2.get("error") or CaptchaError.default_message,
                    cnpj=cnpj,
                    tipo_cnd="Municipal - SP/Sao Paulo",
                )

            async with page.expect_download(timeout=30_000) as dl:
                await page.click('//*[@id="jar"]')

            download = await dl.value

            download_path = await download.path()
            if not download_path:
                raise ScrapError(f"Falha ao obter PDF para {cnpj}")
            pdf_bytes = await add_cnpj(Path(download_path).read_bytes(), cnpj)


            logger.info(f"Municipal SP/Sao Paulo scrape completed for CNPJ: {cnpj}")

            return pdf_bytes

        except CaptchaError:
            raise
        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SP/Sao Paulo",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SP/Sao Paulo",
                url=page.url,
            ) from e

    @staticmethod
    async def sc_icara(page: Page, context: BrowserContext, cnpj: str) -> bytes:
        try:
            logger.info(f"Starting Municipal SC/Icara scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://icara-sc.prefeituramoderna.com.br/meuiptu/index.php",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await asyncio.sleep(1)
            await page.locator("//a[@id='cnd']").click()
            await page.locator("//input[@name='nrcpfcnpj']").fill(cnpj)
            await page.locator("//input[@name='nmrequerente']").fill("segredo")
            await page.locator("//input[@name='nrdocumento']").fill("52998224725")

            async with page.expect_popup() as popup_info:
                await page.locator("//input[@value='Emitir a Certidão']").click()
            popup = await popup_info.value

            await popup.emulate_media(media="print")
            pdf_bytes = await popup.pdf(format="A4")

            logger.info(f"Municipal SC/Icara scrape completed for CNPJ: {cnpj}")

            return pdf_bytes

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Icara",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Municipal - SC/Icara",
                url=page.url,
            ) from e
