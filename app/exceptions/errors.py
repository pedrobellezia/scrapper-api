from __future__ import annotations

from typing import Any, Optional


class AppBaseError(Exception):
    status_code = 500
    error_code = "internal_error"
    default_message = "Ocorreu um erro interno."

    def __init__(
        self,
        message: str | None = None,
        *,
        cnpj: str | None = None,
        tipo_cnd: str | None = None,
        details: Any | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.cnpj = cnpj
        self.tipo_cnd = tipo_cnd
        self.details = details
        super().__init__(self.message)


class ScrapError(AppBaseError):
    def __init__(self, *args, url: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url

    status_code = 502
    error_code = "scrap_error"
    default_message = "Houve um erro ao tentar realizar o scrap."


class CaptchaError(ScrapError):
    status_code = 502
    error_code = "captcha_error"
    default_message = "Houve um erro ao tentar resolver o CAPTCHA."
