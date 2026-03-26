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


# Validacoes obrigatorias
if not all([SECRET_KEY, CAPTCHA_API_KEY]):
    raise Exception(
        "SECRET_KEY and CAPTCHA_API_KEY are required in environment variables"
    )

__all__ = [
    "SECRET_KEY",
    "CAPTCHA_API_KEY",
    "HEADLESS",
    "PLAYWRIGHT_ARGS",
]
