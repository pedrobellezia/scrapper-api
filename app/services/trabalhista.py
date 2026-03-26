from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout
from app.exceptions import ScrapError, CaptchaError
from app.config import logger, CAPTCHA_API_KEY
from app.utils.captcha_solver import CaptchaSolver
from pathlib import Path
import asyncio


class Trabalhista:
    @staticmethod
    async def execute_scrap(page: Page, context: BrowserContext, cnpj: str):
        try:
            logger.info(f"Starting Trabalhista scrape for CNPJ: {cnpj}")

            await page.goto(
                "https://cndt-certidao.tst.jus.br/inicio.faces",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await page.locator("//*[@id='corpo']/div/div[2]/input[1]").click()
            await page.locator("//*[@id='gerarCertidaoForm:cpfCnpj']").fill(cnpj)
            await asyncio.sleep(5)

            solver = CaptchaSolver(api_key=CAPTCHA_API_KEY, page=page)

            result = await solver.solve_normal(
                img_xpath="//*[@id='idImgBase64']",
                input_xpath="//*[@id='idCampoResposta']",
            )

            if not result.get("success", False):
                raise CaptchaError(
                    result.get("error") or CaptchaError.default_message,
                    cnpj=cnpj,
                    tipo_cnd="trabalhista",
                )

            async with page.expect_download(timeout=30_000) as download_info:
                await page.locator(
                    "//*[@id='gerarCertidaoForm:btnEmitirCertidao']"
                ).click()
            download = await download_info.value

            download_path = await download.path()
            if not download_path:
                raise ScrapError(
                    f"Falha ao obter PDF da certidao Trabalhista para {cnpj}"
                )
            pdf_buffer = Path(download_path).read_bytes()

            logger.info(f"Trabalhista scrape completed for CNPJ: {cnpj}")
            return pdf_buffer

        except PlaywrightTimeout as e:
            e: PlaywrightTimeout
            raise ScrapError(
                message="Timeout durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Trabalhista",
                details=e.message,
                url=page.url,
            ) from e
        except Exception as e:
            raise ScrapError(
                message="Erro inesperado durante Scrap da CND",
                cnpj=cnpj,
                tipo_cnd="Trabalhista",
                url=page.url,
            ) from e
