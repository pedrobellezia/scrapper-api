import os
from dotenv import load_dotenv

# Carregar variaveis de ambiente
load_dotenv()

# Configuracoes de autenticacao
SECRET_KEY = os.environ.get("SECRET_KEY")
CAPTCHA_API_KEY = os.environ.get("CAPTCHA_API_KEY")


# Configuracoes do Playwright
PLAYWRIGHT_ARGS = [
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-infobars",
]
HEADLESS = os.environ.get("HEADLESS", "False").lower() == "true"

# Configurações de Concorrência
MAX_CONCURRENT_BROWSERS = int(os.environ.get("MAX_CONCURRENT_BROWSERS", "3"))

# Validacoes obrigatorias
_missing_vars = []
if not SECRET_KEY:
    _missing_vars.append("SECRET_KEY")
if not CAPTCHA_API_KEY:
    _missing_vars.append("CAPTCHA_API_KEY")

if _missing_vars:
    missing = ", ".join(_missing_vars)
    raise RuntimeError(
        f"Variáveis de ambiente obrigatórias não configuradas: {missing}. "
        f"Verifique o arquivo .env baseado em .env.example"
    )

__all__ = [
    "SECRET_KEY",
    "CAPTCHA_API_KEY",
    "HEADLESS",
    "PLAYWRIGHT_ARGS",
    "MAX_CONCURRENT_BROWSERS",
]
