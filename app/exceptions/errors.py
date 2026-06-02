from __future__ import annotations

from typing import Any, Optional


class AppBaseError(Exception):
    """Classe base para todos os erros da aplicação."""

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


class ConfigError(AppBaseError):
    """Erro de configuração da aplicação."""

    status_code = 500
    error_code = "config_error"
    default_message = "Erro de configuração da aplicação."


class ScrapError(AppBaseError):
    """Erro durante o web scraping."""

    status_code = 502
    error_code = "scrap_error"
    default_message = "Houve um erro ao tentar realizar o scrap."

    def __init__(self, *args, url: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url


class CaptchaError(ScrapError):
    """Erro ao resolver CAPTCHA."""

    status_code = 502
    error_code = "captcha_error"
    default_message = "Houve um erro ao tentar resolver o CAPTCHA."
