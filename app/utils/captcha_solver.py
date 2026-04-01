import base64
from urllib.parse import urlparse, parse_qs
from playwright.async_api import Page
from twocaptcha import AsyncTwoCaptcha
from app.config import logger
from typing import List


class CaptchaSolver:
    """Classe para resolver CAPTCHAs usando o servico 2captcha."""

    def __init__(self, api_key: str, page):
        """
        Params:
            api_key str:
                A chave de API do 2captcha.

            page Page:
                A instancia de pagina do Playwright.
        """
        self.solver: AsyncTwoCaptcha = AsyncTwoCaptcha(api_key)
        self.page: Page = page

    async def v2_sitekey(self, x_path: str = None) -> List[str]:
        """
        Retorna Lista de sitekeys encontrado em iframes de reCAPTCHA na pagina.

        Params:
            x_path Optional[str]:
                O XPath para localizar os iframes de reCAPPTCHA.
                Default: "//iframe[@title='reCAPTCHA']"
        """
        if not x_path:
            x_path = "//iframe[@title='reCAPTCHA']"

        locator = self.page.locator(x_path)

        try:
            await locator.first.wait_for(timeout=30000)
        except TimeoutError:
            return []

        elements = await locator.all()

        key_list: List[str] = []

        for el in elements:
            src = await el.get_attribute("src")
            if not src:
                continue

            query = parse_qs(urlparse(src).query)
            key = query.get("k")

            if key and key[0]:
                key_list.append(key[0])

        return key_list

    async def auto_solve_v2(self) -> dict:
        """
        Soluciona automaticamente o CAPTCHA reCAPTCHA v2 presente na pagina.
        - Warning: Pode nao funcionar corretamente caso tenha mais de um CAPTCHA na pagina
        """
        key_list = await self.v2_sitekey()

        if not key_list:
            logger.error("[CaptchaSolver] Nao foi possivel encontrar o site-key")
            return {"success": False, "error": "site-key nao encontrado"}

        if len(key_list) > 1:
            logger.warning(
                f"[CaptchaSolver] Foram encontrados {len(key_list)} site-keys. Utilizando o primeiro."
            )

        sitekey = key_list[0]

        logger.debug(
            f"[CaptchaSolver] Solicitando token de CAPTCHA v2 para o 2captcha (sitekey={sitekey[:8]}...{sitekey[-8:]})"
        )

        try:
            result = await self.solver.recaptcha(sitekey=sitekey, url=self.page.url)
            token = result["code"]
        except Exception as e:
            logger.error(f"[CaptchaSolver] Erro ao resolver CAPTCHA: {e}")
            return {"success": False, "error": "Falha ao resolver CAPTCHA"}

        logger.debug(f"[CaptchaSolver] Token recebido com sucesso {token[:4]}...)")

        textarea_locator = self.page.locator("//textarea[@id='g-recaptcha-response']")
        count = await textarea_locator.count()

        if count == 0:
            logger.error("[CaptchaSolver] Textarea g-recaptcha-response nao encontrado")
            return {"success": False, "error": "Campo de resposta nao encontrado"}

        if count > 1:
            logger.warning(
                f"[CaptchaSolver] Foram encontrados {count} textareas. Utilizando o primeiro."
            )

        textarea = textarea_locator.first

        await textarea.evaluate("(el, token) => el.value = token", token)

        return {"success": True, "token": token}

    async def solve_normal(self, img_xpath, input_xpath):
        img_locator = self.page.locator(img_xpath)
        img_count = await img_locator.count()
        if img_count == 0:
            logger.error(
                f"[CaptchaSolver] imagem do CAPTCHA nao encontrada (xpath={img_xpath})"
            )
            return {"success": False, "error": "Imagem do CAPTCHA nao encontrada"}
        if img_count > 1:
            logger.warning(
                f"[CaptchaSolver] foram encontradas {img_count} imagens. utilizando a primeira."
            )

        screenshot: bytes = await img_locator.first.screenshot()

        img_b64 = base64.b64encode(screenshot).decode("utf-8")

        try:
            logger.debug(
                "[CaptchaSolver] Solicitando token de normal CAPTCHA para o 2captcha"
            )

            result = await self.solver.normal(img_b64, caseSensitive=1)
            code = result["code"]

            logger.debug(f"[CaptchaSolver] Codigo recebido do provedor ({code[:4]}...)")
        except Exception as e:
            logger.error(f"[CaptchaSolver] Falha ao resolver CAPTCHA: {e}")
            return {"success": False, "error": "Erro ao resolver CAPTCHA"}

        input_locator = self.page.locator(input_xpath)
        input_count = await input_locator.count()

        if input_count == 0:
            logger.error(
                f"[CaptchaSolver] Campo de input para CAPTCHA nao encontrado (xpath={input_xpath})"
            )
            return {
                "success": False,
                "error": "Campo de input do CAPTCHA nao encontrado",
            }

        if input_count > 1:
            logger.warning(
                f"[CaptchaSolver] Foram encontrados {input_count} campos de input. Utilizando o primeiro."
            )

        await input_locator.first.fill(code)
        return {"success": True, "code": code}
